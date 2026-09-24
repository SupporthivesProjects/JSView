from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from company.models import Company
from costcard.models import CostCard, CostCardDiamondLine, CostCardFinishLine
from InvenTree.unit_test import InvenTreeAPITestCase
from master.models import (
    ACExecutive,
    FinishType,
    JewelryCategory,
    JewelrySubCategory,
    MetalPurity,
    MetalType,
    Stamp,
    Terms,
)
from properties.models import DiamondShape, DiamondStone

from .models import POCostCard, POCostCardLine, PurchaseOrder, PurchaseOrderLine


class POCostCardSnapshotTests(TestCase):
    def setUp(self):
        # Pre-set pono to avoid generate_po_number's lookup
        self.order = PurchaseOrder.objects.create(
            potype='ORDER',
            podate='2026-08-26',
            pono='TEST-0001 P',
            npono=1,
        )
        self.request = PurchaseOrder.objects.create(
            potype='REQUEST',
            podate='2026-08-26',
            pono='TEST-0002 S',
            npono=2,
        )
        self.card = CostCard.objects.create(
            our_style_no='JS-001',
            karat='18KT',
            metal_grams=10.500,
        )

    def _add_lines(self):
        stone, _ = DiamondStone.objects.get_or_create(name='Natural')
        shape, _ = DiamondShape.objects.get_or_create(name='Round')
        finish, _ = FinishType.objects.get_or_create(name='Matte')

        from costcard.models import CostCardDiamondLine

        CostCardDiamondLine.objects.create(
            cost_card=self.card,
            stone=stone,
            shape=shape,
            pcs=2,
            cts=0.5000,
            rate=1000,
            amount=500,
        )
        CostCardFinishLine.objects.create(
            cost_card=self.card,
            finish_type=finish,
            rate=250,
        )

    def test_order_creates_snapshot(self):
        self._add_lines()
        line = PurchaseOrderLine.objects.create(
            poid=self.order,
            costcardid=self.card,
            styleno='JS-001',
            qty=5,
        )

        snapshots = POCostCard.objects.filter(poid=self.order, costcard=self.card)
        self.assertEqual(snapshots.count(), 1)

        snap = snapshots.get()
        self.assertEqual(snap.costcardno, self.card.cost_card_no)
        self.assertEqual(snap.our_style_no, 'JS-001')

        # 1 diamond + 1 finish line frozen, names stored as strings
        self.assertEqual(snap.lines.count(), 2)
        dia = snap.lines.get(etype='DIAMOND')
        self.assertEqual(dia.stone, 'Natural')
        self.assertEqual(dia.shape, 'Round')
        self.assertEqual(dia.pcs, 2)
        fin = snap.lines.get(etype='FINISHTYPE')
        self.assertEqual(fin.stone, 'Matte')
        self.assertEqual(fin.rate, 250)

    def test_request_does_not_snapshot(self):
        PurchaseOrderLine.objects.create(
            poid=self.request,
            costcardid=self.card,
            qty=3,
        )
        self.assertFalse(POCostCard.objects.exists())

    def test_resave_does_not_duplicate(self):
        line = PurchaseOrderLine.objects.create(
            poid=self.order,
            costcardid=self.card,
            qty=5,
        )
        line.qty = 7
        line.save()
        self.assertEqual(POCostCard.objects.filter(poid=self.order).count(), 1)

    def test_line_without_costcard_skips(self):
        PurchaseOrderLine.objects.create(poid=self.order, qty=1)
        self.assertFalse(POCostCard.objects.exists())


class POPrintViewTests(InvenTreeAPITestCase):
    """Tests for the four PO print/report formats."""

    superuser = True

    @classmethod
    def setUpTestData(cls):
        """Build a cost card, a matching ORDER and its line (snapshot source)."""
        super().setUpTestData()

        cls.customer = Company.objects.create(name='Ascend', code='ASC', is_customer=True)
        cls.vendor = Company.objects.create(name='Omnia Jewels LLP', is_supplier=True)

        metal = MetalType.objects.create(name='Sterling Silver')
        cls.purity = MetalPurity.objects.create(name='STERLING SILVER', metal_type=metal)
        cls.category = JewelryCategory.objects.create(name='EARRING')
        cls.sub_category = JewelrySubCategory.objects.create(
            name='STUDS', category=cls.category
        )
        cls.stamp = Stamp.objects.create(name='AA LOGO, KT, COO - LGD')
        cls.acexe = ACExecutive.objects.create(name='SHEKHAR')
        cls.terms = Terms.objects.create(name='Net 30', days=30)

        cls.card = CostCard.objects.create(
            our_style_no='AAE075A0664',
            vendor_style_no='OE1801075',
            vendor=cls.vendor,
            customer=cls.customer,
            category=cls.category,
            sub_category=cls.sub_category,
            metal_purity=cls.purity,
            karat=24,
            metal_grams=Decimal('1.000'),
            net_weight=Decimal('1.000'),
            metal_loss_pct=Decimal('10'),
            metal_amount=Decimal('0'),
            stone_pcs=2,
            stone_cts=Decimal('0.7600'),
            stone_amount=Decimal('34.20'),
            labour_amount=Decimal('4.50'),
            fob=Decimal('38.70'),
            duty_pct=Decimal('30'),
            margin_pct=Decimal('45'),
            final_amount=Decimal('72.95'),
            design_note='Set the stones tight',
        )

        CostCardDiamondLine.objects.create(
            cost_card=cls.card,
            stone=DiamondStone.objects.create(name='DIAMOND'),
            shape=DiamondShape.objects.create(name='ROUND'),
            pointer=Decimal('0.38'),
            pcs=2,
            cts=Decimal('0.7600'),
            pc='C',
            rate=Decimal('45'),
            amount=Decimal('34.20'),
            labour_rate=Decimal('0'),
            labour_amount=Decimal('0'),
        )
        CostCardFinishLine.objects.create(
            cost_card=cls.card,
            finish_type=FinishType.objects.create(name='PRONG'),
            rate=Decimal('4.50'),
        )

        cls.order = PurchaseOrder.objects.create(
            potype='ORDER',
            pono='ASC 2025-0570 P',
            npono=570,
            podate='2025-09-16',
            ddate='2025-09-27',
            pocategory='Master Sample',
            customerid=cls.customer,
            vendorid=cls.vendor,
            stampid=cls.stamp,
            acexeid=cls.acexe,
            termsid=cls.terms,
            prepby=cls.user,
            rem='DIRECT SHIPMENT TO CANADA',
        )
        PurchaseOrderLine.objects.create(
            poid=cls.order,
            costcardid=cls.card,
            styleno='AAE075A0664',
            vstyleno='OE1801075',
            qty=2,
            size='N A',
            spcs='2',
        )

    def _print(self, print_type, po=None):
        url = reverse('api-po-print', kwargs={'pk': (po or self.order).pk})
        data = {} if print_type is None else {'type': print_type}
        expected = 200 if print_type in ('vendor', 'self', 'vendor_costcard', 'self_costcard') else 400
        return self.get(url, data, expected_code=expected)

    def test_missing_type_is_rejected(self):
        """A request without a `type` parameter is a 400."""
        response = self._print(None)
        self.assertIn('Invalid type', str(response.data['error']))

    def test_invalid_type_is_rejected(self):
        """An unknown `type` value is a 400 and lists the valid options."""
        response = self._print('nonsense')
        self.assertIn('Invalid type', str(response.data['error']))

    def test_vendor_format(self):
        """The vendor sheet exposes lines but never the order value."""
        response = self._print('vendor')
        self.assertEqual(response.data['type'], 'vendor')

        po = response.data['po']
        self.assertEqual(po['pono'], 'ASC 2025-0570 P')
        self.assertEqual(po['podate'], '2025-09-16')
        self.assertEqual(po['customer'], 'ASC')
        self.assertEqual(po['vendor'], 'Omnia Jewels LLP')
        self.assertEqual(po['prepby'], self.user.get_username())
        self.assertEqual(po['stamp'], 'AA LOGO, KT, COO - LGD')
        self.assertEqual(po['rem'], 'DIRECT SHIPMENT TO CANADA')

        line = response.data['lines'][0]
        self.assertEqual(line['sr'], 1)
        self.assertEqual(line['style_no'], 'AAE075A0664')
        self.assertEqual(line['v_style_no'], 'OE1801075')
        self.assertEqual(line['qty'], 2)
        self.assertEqual(line['size'], 'N A')
        self.assertEqual(line['size_pcs'], '2')
        self.assertEqual(line['metal_color_kt'], 'STERLING SILVER')

        totals = response.data['totals']
        self.assertEqual(totals['total_qty'], 2)
        self.assertAlmostEqual(float(totals['metal_value']), 0.0)
        self.assertAlmostEqual(float(totals['labour_value']), 4.5)

        # The vendor sheet must never expose the order value
        self.assertNotIn('order_value', totals)

    def test_self_format_reveals_order_value(self):
        """The internal (self) sheet additionally reports the order value."""
        response = self._print('self')
        totals = response.data['totals']
        self.assertEqual(totals['total_qty'], 2)
        self.assertAlmostEqual(float(totals['order_value']), 72.95)

    def test_vendor_costcard_hides_amounts(self):
        """The vendor cost sheet masks amounts but keeps the piece data."""
        response = self._print('vendor_costcard')
        self.assertEqual(response.data['type'], 'vendor_costcard')

        cards = response.data['costcards']
        self.assertEqual(len(cards), 1)
        card = cards[0]

        self.assertEqual(card['cc_no'], self.card.cost_card_no)
        self.assertEqual(card['style_no'], 'AAE075A0664')
        self.assertEqual(card['customer'], 'ASC')
        self.assertEqual(card['category'], 'EARRING')
        self.assertEqual(card['sub_category'], 'STUDS')
        self.assertEqual(card['metal']['type'], 'STERLING SILVER')

        # Amounts are masked on the vendor sheet
        self.assertIsNone(card['stone_lines'][0]['amount'])
        self.assertIsNone(card['stone_lines'][0]['labour_rate'])
        self.assertIsNone(card['stone_lines'][0]['labour_amount'])
        self.assertIsNone(card['stone_totals']['total_amount'])
        self.assertNotIn('fob', card['summary'])
        self.assertNotIn('final_price', card['summary'])

        # Non-pricing data stays visible
        self.assertEqual(card['stone_totals']['total_pcs'], 2)
        self.assertAlmostEqual(float(card['stone_totals']['total_cts']), 0.76)
        self.assertAlmostEqual(float(card['labour']['finish']), 4.5)
        self.assertEqual(card['images'], {'front': None, 'side': None, 'back': None})

    def test_self_costcard_shows_amounts(self):
        """The internal cost sheet reports amounts and the full summary."""
        response = self._print('self_costcard')
        card = response.data['costcards'][0]

        self.assertAlmostEqual(float(card['stone_lines'][0]['amount']), 34.2)
        self.assertAlmostEqual(float(card['stone_totals']['total_amount']), 34.2)

        summary = card['summary']
        self.assertAlmostEqual(float(summary['metal']), 0.0)
        self.assertAlmostEqual(float(summary['studding']), 34.2)
        self.assertAlmostEqual(float(summary['labour']), 4.5)
        self.assertAlmostEqual(float(summary['fob']), 38.7)
        self.assertAlmostEqual(float(summary['duty_pct']), 30.0)
        self.assertAlmostEqual(float(summary['with_duty']), 50.31)
        self.assertAlmostEqual(float(summary['margin_pct']), 45.0)
        self.assertAlmostEqual(float(summary['final_price']), 72.95)

    def test_request_prints_from_live_cost_card(self):
        """A REQUEST never freezes a snapshot, so the live cost card is used."""
        request_po = PurchaseOrder.objects.create(
            potype='REQUEST',
            pono='ASC 2025-0001 S',
            npono=1,
            podate='2025-09-16',
            customerid=self.customer,
            prepby=self.user,
        )
        PurchaseOrderLine.objects.create(
            poid=request_po,
            costcardid=self.card,
            styleno='AAE075A0664',
            qty=1,
        )
        self.assertFalse(POCostCard.objects.filter(poid=request_po).exists())

        response = self._print('self_costcard', po=request_po)
        cards = response.data['costcards']

        self.assertEqual(len(cards), 1)
        self.assertEqual(cards[0]['cc_no'], self.card.cost_card_no)
        self.assertAlmostEqual(float(cards[0]['stone_totals']['total_amount']), 34.2)
        self.assertAlmostEqual(float(cards[0]['summary']['final_price']), 72.95)
