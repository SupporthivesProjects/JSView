"""Tests for the 'vendor_shipment' app.

Covers both sections:

* Shipment — CRUD, nested header + ``lines[]`` create, dropdown helpers
* Confirm  — pending invoice/data endpoints and the bulk ``confrm`` update

The PostgreSQL function replicas in ``utils.py`` are exercised directly as
well as through their API views.
"""

from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from company.models import Company
from costcard.models import CostCard
from InvenTree.unit_test import InvenTreeAPITestCase
from master.models import CourierService
from purchase_order.models import PurchaseOrder, PurchaseOrderLine

from . import utils
from .models import VendorShipment, VendorShipmentLine


def build_scenario(cls):
    """Create the shared master data, cost cards, ORDER and PO lines.

    Returns nothing; every object is attached to ``cls``.
    """
    # credit_limit / rating are required (non-null) as of company migration 0083
    company_defaults = {'credit_limit': Decimal('0'), 'rating': Decimal('0')}
    cls.customer = Company.objects.create(
        name='Ascend', code='ASC', is_customer=True, **company_defaults
    )
    cls.vendor = Company.objects.create(
        name='Omnia Jewels LLP', is_supplier=True, **company_defaults
    )
    cls.other_vendor = Company.objects.create(
        name='Other Vendor', is_supplier=True, **company_defaults
    )

    cls.courier = CourierService.objects.create(name='DHL')

    cls.card1 = CostCard.objects.create(
        our_style_no='JS-001',
        karat=18,
        metal_grams=Decimal('10.500'),
    )
    cls.card2 = CostCard.objects.create(
        our_style_no='JS-002',
        karat=22,
        metal_grams=Decimal('5.000'),
    )

    cls.order = PurchaseOrder.objects.create(
        potype='ORDER',
        pono='ASC 2026-0001 P',
        npono=1,
        podate='2026-01-05',
        customerid=cls.customer,
        vendorid=cls.vendor,
    )

    # Ordered quantities: 10 x JS-001 and 4 x JS-002
    PurchaseOrderLine.objects.create(
        poid=cls.order, costcardid=cls.card1, styleno='JS-001', qty=10,
    )
    PurchaseOrderLine.objects.create(
        poid=cls.order, costcardid=cls.card2, styleno='JS-002', qty=4,
    )


def make_shipment(vendor=None, vsno='INV-0001', **kwargs):
    """Create a shipment header with sensible defaults."""
    return VendorShipment.objects.create(
        vsno=vsno,
        vsdate='2026-02-01',
        vendorid=vendor,
        **kwargs,
    )


class VendorShipmentUtilTests(TestCase):
    """Unit tests for the utils.py function replicas."""

    @classmethod
    def setUpTestData(cls):
        build_scenario(cls)

    # ---- fn_po_vendorstatus ------------------------------------------------

    def test_po_list_all_open_when_nothing_shipped(self):
        result = utils.get_vendor_po_list(self.vendor.pk, is_open=True)
        self.assertEqual(result, [{'poid': self.order.pk, 'pono': self.order.pono}])
        self.assertEqual(utils.get_vendor_po_list(self.vendor.pk, is_open=False), [])

    def test_po_list_partial_shipment_stays_open(self):
        # Ship JS-001 in full, but nothing of JS-002
        shipment = make_shipment(self.vendor)
        VendorShipmentLine.objects.create(
            vendorshipid=shipment,
            poid=self.order,
            costcardid=self.card1,
            pcs=10,
        )

        open_ids = [row['poid'] for row in utils.get_vendor_po_list(self.vendor.pk, True)]
        self.assertEqual(open_ids, [self.order.pk])

    def test_po_list_closed_when_fully_shipped(self):
        shipment = make_shipment(self.vendor)
        for card, pcs in ((self.card1, 10), (self.card2, 4)):
            VendorShipmentLine.objects.create(
                vendorshipid=shipment,
                poid=self.order,
                costcardid=card,
                pcs=pcs,
            )

        self.assertEqual(utils.get_vendor_po_list(self.vendor.pk, True), [])

        closed = utils.get_vendor_po_list(self.vendor.pk, False)
        self.assertEqual([row['poid'] for row in closed], [self.order.pk])

    def test_po_list_ignores_other_vendors(self):
        self.assertEqual(utils.get_vendor_po_list(self.other_vendor.pk, True), [])

    # ---- fn_vendor_style ---------------------------------------------------

    def test_style_list_all_open(self):
        rows = utils.get_vendor_style_list(self.order.pk, is_open=True)
        self.assertEqual(
            {row['styleno'] for row in rows},
            {'JS-001', 'JS-002'},
        )
        self.assertEqual(
            {row['costcardid'] for row in rows},
            {self.card1.pk, self.card2.pk},
        )

    def test_style_list_excludes_fully_shipped_style(self):
        shipment = make_shipment(self.vendor)
        VendorShipmentLine.objects.create(
            vendorshipid=shipment,
            poid=self.order,
            costcardid=self.card1,
            pcs=10,
        )

        open_styles = [row['styleno'] for row in utils.get_vendor_style_list(self.order.pk, True)]
        self.assertEqual(open_styles, ['JS-002'])

        closed_styles = [row['styleno'] for row in utils.get_vendor_style_list(self.order.pk, False)]
        self.assertEqual(closed_styles, ['JS-001'])

    def test_style_list_requires_valid_po(self):
        self.assertEqual(utils.get_vendor_style_list(None), [])

    # ---- fn_tbvendorship1_vendorpo -----------------------------------------

    def test_pending_invoices_lists_unconfirmed(self):
        shipment = make_shipment(self.vendor)
        VendorShipmentLine.objects.create(
            vendorshipid=shipment, poid=self.order, costcardid=self.card1, pcs=1,
        )

        rows = utils.get_confirm_pending_invoices(self.vendor.pk)
        self.assertEqual(rows, [{'vendorshipid': shipment.pk, 'vsno': 'INV-0001'}])

        # Another vendor's pending invoice is not returned
        self.assertEqual(utils.get_confirm_pending_invoices(self.other_vendor.pk), [])

    def test_pending_invoices_excludes_confirmed(self):
        shipment = make_shipment(self.vendor)
        line = VendorShipmentLine.objects.create(
            vendorshipid=shipment,
            poid=self.order,
            costcardid=self.card1,
            pcs=1,
            confrm=True,
        )

        self.assertEqual(utils.get_confirm_pending_invoices(self.vendor.pk), [])

        # Resetting the line to pending brings it back
        line.confrm = None
        line.save()
        self.assertEqual(len(utils.get_confirm_pending_invoices(self.vendor.pk)), 1)

    # ---- fn_tbvendorship_data ----------------------------------------------

    def test_confirm_data_joins_po_and_cost_card(self):
        shipment = make_shipment(self.vendor)
        line = VendorShipmentLine.objects.create(
            vendorshipid=shipment,
            poid=self.order,
            costcardid=self.card1,
            pcs=3,
            metalwt=Decimal('2.500'),
            diawt=Decimal('0.250'),
            colwt=Decimal('0.100'),
            labour=Decimal('5.00'),
            finding=Decimal('2.00'),
            triounce=Decimal('2000.0000'),
        )

        rows = utils.get_confirm_pending_data(self.vendor.pk, shipment.pk)
        self.assertEqual(len(rows), 1)

        row = rows[0]
        self.assertEqual(row['tableid'], line.pk)
        self.assertEqual(row['vendorshipid'], shipment.pk)
        self.assertEqual(row['pono'], self.order.pono)
        self.assertEqual(row['purchaseno'], self.order.pono)
        self.assertEqual(row['styleno'], 'JS-001')
        self.assertEqual(row['coststyle'], 'JS-001')
        self.assertEqual(row['pcs'], 3)
        self.assertEqual(row['metalwt'], Decimal('2.500'))
        self.assertEqual(row['diawt'], Decimal('0.250'))
        self.assertEqual(row['colwt'], Decimal('0.100'))
        self.assertEqual(row['labour'], Decimal('5.00'))
        self.assertEqual(row['finding'], Decimal('2.00'))
        self.assertEqual(row['triounce'], Decimal('2000.0000'))
        self.assertIsNone(row['confrm'])

        # Ordered / frozen cost card values
        self.assertEqual(row['qty'], 10)
        self.assertEqual(row['metalgms'], Decimal('10.500'))
        self.assertEqual(row['touncep'], self.card1.troy_ounce_price)

    def test_confirm_data_respects_vendor(self):
        shipment = make_shipment(self.vendor)
        VendorShipmentLine.objects.create(
            vendorshipid=shipment, poid=self.order, costcardid=self.card1, pcs=1,
        )
        self.assertEqual(
            utils.get_confirm_pending_data(self.other_vendor.pk, shipment.pk), []
        )

    def test_confirm_data_unknown_shipment(self):
        self.assertEqual(utils.get_confirm_pending_data(self.vendor.pk, 999999), [])

    # ---- bulk confirm ------------------------------------------------------

    def test_update_confirm_flags(self):
        shipment = make_shipment(self.vendor)
        line1 = VendorShipmentLine.objects.create(
            vendorshipid=shipment, poid=self.order, costcardid=self.card1, pcs=1,
        )
        line2 = VendorShipmentLine.objects.create(
            vendorshipid=shipment, poid=self.order, costcardid=self.card2, pcs=1,
        )

        updated = utils.update_confirm_flags([
            {'tableid': line1.pk, 'confrm': True},
            {'tableid': line2.pk, 'confrm': False},
        ])
        self.assertEqual(updated, 2)

        line1.refresh_from_db()
        line2.refresh_from_db()
        self.assertIs(line1.confrm, True)
        # Falsy -> back to pending (NULL)
        self.assertIsNone(line2.confrm)

    def test_update_confirm_flags_accepts_legacy_id_key(self):
        """The legacy client used ``id`` instead of ``tableid``."""
        shipment = make_shipment(self.vendor)
        line = VendorShipmentLine.objects.create(
            vendorshipid=shipment, poid=self.order, costcardid=self.card1, pcs=1,
        )

        self.assertEqual(utils.update_confirm_flags([{'id': line.pk, 'confrm': True}]), 1)

        line.refresh_from_db()
        self.assertIs(line.confrm, True)

    def test_update_confirm_flags_ignores_unknown_and_empty(self):
        self.assertEqual(utils.update_confirm_flags([]), 0)
        self.assertEqual(utils.update_confirm_flags([{'tableid': 999999, 'confrm': True}]), 0)
        self.assertEqual(utils.update_confirm_flags([{'confrm': True}]), 0)


class VendorShipmentAPITests(InvenTreeAPITestCase):
    """API tests for the shipment + confirm endpoints."""

    superuser = True

    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        build_scenario(cls)

    def _create_shipment(self, vendor=None, vsno='INV-0001'):
        return make_shipment(vendor or self.vendor, vsno=vsno)

    # ---- Shipment CRUD -----------------------------------------------------

    def test_create_shipment_with_nested_lines(self):
        url = reverse('api-vendor-shipment-list')

        response = self.post(url, {
            'vsno': 'INV-100',
            'vsdate': '2026-02-01',
            'vendorid': self.vendor.pk,
            'courierid': self.courier.pk,
            'trackref': 'TRK-1',
            'lines': [
                {
                    'poid': self.order.pk,
                    'costcardid': self.card1.pk,
                    'pcs': 10,
                    'metalwt': '10.500',
                    'diawt': '0.250',
                    'colwt': '0.000',
                    'labour': '5.00',
                    'finding': '2.00',
                    'triounce': '2000.0000',
                    'stplace': 'Center',
                },
                {
                    'poid': self.order.pk,
                    'costcardid': self.card2.pk,
                    'pcs': 4,
                },
            ],
        }, expected_code=201)

        self.assertEqual(response.data['vendor_name'], 'Omnia Jewels LLP')
        self.assertEqual(response.data['courier_name'], 'DHL')
        self.assertEqual(len(response.data['lines']), 2)

        shipment = VendorShipment.objects.get(pk=response.data['pk'])
        self.assertEqual(shipment.lines.count(), 2)
        self.assertEqual(shipment.luser, self.user.get_username())

        line = shipment.lines.get(costcardid=self.card1)
        self.assertEqual(line.pcs, 10)
        self.assertEqual(line.stplace, 'Center')
        self.assertEqual(line.metalwt, Decimal('10.500'))
        self.assertIsNone(shipment.lines.get(costcardid=self.card2).confrm)

    def test_create_shipment_rolls_back_on_invalid_line(self):
        url = reverse('api-vendor-shipment-list')

        self.post(url, {
            'vsno': 'INV-BAD',
            'vsdate': '2026-02-01',
            'lines': [{'pcs': 'not-a-number'}],
        }, expected_code=400)

        self.assertFalse(VendorShipment.objects.filter(vsno='INV-BAD').exists())

    def test_detail_returns_nested_display_fields(self):
        shipment = self._create_shipment()
        VendorShipmentLine.objects.create(
            vendorshipid=shipment,
            poid=self.order,
            costcardid=self.card1,
            pcs=3,
        )

        response = self.get(
            reverse('api-vendor-shipment-detail', kwargs={'pk': shipment.pk})
        )

        self.assertEqual(response.data['vsno'], 'INV-0001')
        self.assertEqual(response.data['vendor_name'], 'Omnia Jewels LLP')
        self.assertEqual(len(response.data['lines']), 1)

        line = response.data['lines'][0]
        self.assertEqual(line['pono'], self.order.pono)
        self.assertEqual(line['styleno'], 'JS-001')
        self.assertEqual(line['pcs'], 3)

    def test_list_filters_by_vendor(self):
        mine = self._create_shipment(self.vendor, vsno='MINE')
        self._create_shipment(self.other_vendor, vsno='THEIRS')

        url = reverse('api-vendor-shipment-list')
        response = self.get(url, {'vendorid': self.vendor.pk})

        vsnos = [row['vsno'] for row in response.data['results']]
        self.assertEqual(vsnos, ['MINE'])
        self.assertEqual(response.data['results'][0]['pk'], mine.pk)

    def test_post_line_via_nested_route_uses_url_shipment(self):
        """``POST <pk>/lines/`` does not need ``vendorshipid`` in the body."""
        shipment = self._create_shipment()

        response = self.post(
            reverse(
                'api-vendor-shipment-lines-for-shipment',
                kwargs={'pk': shipment.pk},
            ),
            {'poid': self.order.pk, 'costcardid': self.card1.pk, 'pcs': 5},
            expected_code=201,
        )

        self.assertEqual(response.data['vendorshipid'], shipment.pk)
        self.assertEqual(shipment.lines.count(), 1)

    def test_post_line_via_nested_route_forces_url_shipment(self):
        """A conflicting ``vendorshipid`` in the body cannot hijack the row."""
        shipment = self._create_shipment()
        other = self._create_shipment(vsno='INV-0002')

        self.post(
            reverse(
                'api-vendor-shipment-lines-for-shipment',
                kwargs={'pk': shipment.pk},
            ),
            {
                'vendorshipid': other.pk,
                'poid': self.order.pk,
                'costcardid': self.card1.pk,
                'pcs': 5,
            },
            expected_code=201,
        )

        self.assertEqual(shipment.lines.count(), 1)
        self.assertEqual(other.lines.count(), 0)

    def test_post_line_via_flat_route_requires_vendorshipid(self):
        self.post(
            reverse('api-vendor-shipment-line-list'),
            {'poid': self.order.pk, 'costcardid': self.card1.pk, 'pcs': 5},
            expected_code=400,
        )

    def test_lines_scoped_to_shipment(self):
        shipment = self._create_shipment()
        other = self._create_shipment(vsno='INV-0002')

        VendorShipmentLine.objects.create(
            vendorshipid=shipment, poid=self.order, costcardid=self.card1, pcs=1,
        )
        VendorShipmentLine.objects.create(
            vendorshipid=other, poid=self.order, costcardid=self.card2, pcs=1,
        )

        scoped = self.get(
            reverse(
                'api-vendor-shipment-lines-for-shipment',
                kwargs={'pk': shipment.pk},
            )
        )
        self.assertEqual(scoped.data['count'], 1)
        self.assertEqual(
            scoped.data['results'][0]['vendorshipid'], shipment.pk,
        )

        all_lines = self.get(reverse('api-vendor-shipment-line-list'))
        self.assertEqual(all_lines.data['count'], 2)

    def test_line_detail_patch(self):
        shipment = self._create_shipment()
        line = VendorShipmentLine.objects.create(
            vendorshipid=shipment, poid=self.order, costcardid=self.card1, pcs=1,
        )

        self.patch(
            reverse('api-vendor-shipment-line-detail', kwargs={'pk': line.pk}),
            {'pcs': 7},
        )

        line.refresh_from_db()
        self.assertEqual(line.pcs, 7)

    # ---- Dropdown helpers --------------------------------------------------

    def test_po_list_endpoint(self):
        url = reverse('api-vendor-shipment-po-list')

        response = self.get(url, {'vendorid': self.vendor.pk, 'is_open': 'true'})
        self.assertEqual(response.data, [{'poid': self.order.pk, 'pono': self.order.pono}])

        # Nothing shipped yet -> the closed list is empty
        response = self.get(url, {'vendorid': self.vendor.pk, 'is_open': 'false'})
        self.assertEqual(response.data, [])

    def test_style_list_endpoint(self):
        url = reverse('api-vendor-shipment-style-list')

        response = self.get(url, {'poid': self.order.pk, 'is_open': 'true'})
        self.assertEqual({row['styleno'] for row in response.data}, {'JS-001', 'JS-002'})

        # Missing poid is a 400
        self.get(url, {}, expected_code=400)

    # ---- Confirm section ---------------------------------------------------

    def test_confirm_flow_endpoints(self):
        shipment = self._create_shipment()
        line = VendorShipmentLine.objects.create(
            vendorshipid=shipment,
            poid=self.order,
            costcardid=self.card1,
            pcs=3,
        )

        invoices = self.get(
            reverse('api-vendor-shipment-confirm-invoices'),
            {'vendorid': self.vendor.pk},
        )
        self.assertEqual(
            invoices.data, [{'vendorshipid': shipment.pk, 'vsno': 'INV-0001'}]
        )

        data = self.get(
            reverse('api-vendor-shipment-confirm-data'),
            {'vendorid': self.vendor.pk, 'vendorshipid': shipment.pk},
        )
        self.assertEqual(len(data.data), 1)
        self.assertEqual(data.data[0]['tableid'], line.pk)
        self.assertEqual(data.data[0]['qty'], 10)

        # Missing vendorshipid is a 400
        self.get(
            reverse('api-vendor-shipment-confirm-data'),
            {'vendorid': self.vendor.pk},
            expected_code=400,
        )

        updated = self.post(
            reverse('api-vendor-shipment-confirm-update'),
            [{'tableid': line.pk, 'confrm': True}],
            expected_code=200,
        )
        self.assertEqual(updated.data, {'updated': 1})

        line.refresh_from_db()
        self.assertIs(line.confrm, True)

        # No unconfirmed lines remain
        invoices = self.get(
            reverse('api-vendor-shipment-confirm-invoices'),
            {'vendorid': self.vendor.pk},
        )
        self.assertEqual(invoices.data, [])

    def test_confirm_update_accepts_data_wrapper(self):
        """The legacy client posted ``{ data: [...] }``; that shape still works."""
        shipment = self._create_shipment()
        line = VendorShipmentLine.objects.create(
            vendorshipid=shipment,
            poid=self.order,
            costcardid=self.card1,
            pcs=1,
        )

        response = self.post(
            reverse('api-vendor-shipment-confirm-update'),
            {'data': [{'tableid': line.pk, 'confrm': True}]},
            expected_code=200,
        )

        self.assertEqual(response.data, {'updated': 1})

        line.refresh_from_db()
        self.assertIs(line.confrm, True)

    def test_confirm_update_accepts_legacy_client_shape(self):
        """Legacy body: ``{data: [{id, confrm}]}`` — wrapper + ``id`` key."""
        shipment = self._create_shipment()
        line = VendorShipmentLine.objects.create(
            vendorshipid=shipment,
            poid=self.order,
            costcardid=self.card1,
            pcs=1,
        )

        response = self.post(
            reverse('api-vendor-shipment-confirm-update'),
            {'data': [{'id': line.pk, 'confrm': True}]},
            expected_code=200,
        )

        self.assertEqual(response.data, {'updated': 1})

        line.refresh_from_db()
        self.assertIs(line.confrm, True)

    def test_confirm_update_rejects_non_list(self):
        self.post(
            reverse('api-vendor-shipment-confirm-update'),
            'not-a-list',
            expected_code=400,
        )
