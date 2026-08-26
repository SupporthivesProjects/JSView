from django.test import TestCase

from cards.models import CostCard, CostCardFinishLine
from company.models import Company
from master.models import FinishType
from properties.models import DiamondShape, DiamondStone

from .models import (
    POCostCard,
    POCostCardLine,
    PurchaseOrder,
    PurchaseOrderLine,
)


class POCostCardSnapshotTests(TestCase):
    def setUp(self):
        # Pre-set pono to avoid generate_po_number's tbledger lookup
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

        from cards.models import CostCardDiamondLine

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
