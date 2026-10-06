"""Serializers for the 'jsreport' app."""

from rest_framework import serializers as drf_serializers

from data_exporter.mixins import DataExportSerializerMixin
from InvenTree.serializers import InvenTreeModelSerializer

from purchase_order.models import PurchaseOrderLine
from vendor_shipment.models import VendorShipmentLine

from jsreport.filters import (
    get_invoice_figures,
    get_po_stone_figures,
    get_stone_valuation_figures,
)

DATE_FMT = '%d %b %Y'  # 15 Jul 2026, same as the client's sheet


def _stone_set(key):
    """Method field returning a stone set count (whole numbers shown without decimals)."""

    def method(self, obj):
        value = getattr(obj, key, None)
        if value is None:
            return 0
        return int(value) if value == value.to_integral_value() else float(value)

    return method


def _stone_date(date_key, set_key):
    """Method field returning the stone date, shown only while the set count is above 0."""

    def method(self, obj):
        date = getattr(obj, date_key, None)
        if date is None or (getattr(obj, set_key, None) or 0) <= 0:
            return None
        return date.strftime(DATE_FMT)

    return method


class OpenOrderSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """One row per open P.O. line. Labels match the Open Order export headers."""

    podate = drf_serializers.DateField(
        source='poid.podate', read_only=True, format=DATE_FMT, label='P.O. Date',
    )
    customer_code = drf_serializers.CharField(
        source='poid.customerid.code', read_only=True, default=None, label='Customer Code',
    )
    vendor_code = drf_serializers.CharField(
        source='poid.vendorid.name', read_only=True, default=None, label='Vendor Code',
    )
    pono = drf_serializers.CharField(
        source='poid.pono', read_only=True, label='P.O. No.',
    )
    customer_pono = drf_serializers.CharField(
        source='poid.customer_pono', read_only=True, default=None, label='Customer P.O. No.',
    )
    styleno = drf_serializers.CharField(read_only=True, label='Style No.')
    qty = drf_serializers.IntegerField(read_only=True, label='Qty.')
    balqty = drf_serializers.IntegerField(read_only=True, label='Bal. Qty.')
    ddate = drf_serializers.DateField(
        source='poid.ddate', read_only=True, format=DATE_FMT, default=None, label='Due Date',
    )
    vcsdate = drf_serializers.DateField(
        source='poid.vcsdate', read_only=True, format=DATE_FMT, default=None,
        label='Vendor Confirmed Ship Date',
    )
    side_stone_date = drf_serializers.SerializerMethodField(label='Side Stone Date')
    side_stone_set = drf_serializers.SerializerMethodField(label='Side Stone Set')
    center_stone_date = drf_serializers.SerializerMethodField(label='Center Stone Date')
    center_stone_set = drf_serializers.SerializerMethodField(label='Center Stone Set')
    color_stone_date = drf_serializers.SerializerMethodField(label='Color Stone Date')
    color_stone_set = drf_serializers.SerializerMethodField(label='Color Stone Set')
    acexecutive = drf_serializers.CharField(
        source='poid.acexeid.name', read_only=True, default=None, label='A/C Executive',
    )

    class Meta:
        model = PurchaseOrderLine
        fields = [
            'podate', 'customer_code', 'vendor_code', 'pono', 'customer_pono',
            'styleno', 'qty', 'balqty', 'ddate', 'vcsdate',
            'side_stone_date', 'side_stone_set', 'center_stone_date', 'center_stone_set',
            'color_stone_date', 'color_stone_set', 'acexecutive',
        ]

    get_side_stone_set = _stone_set('side_set')
    get_center_stone_set = _stone_set('center_set')
    get_color_stone_set = _stone_set('color_set')
    get_side_stone_date = _stone_date('side_date', 'side_set')
    get_center_stone_date = _stone_date('center_date', 'center_set')
    get_color_stone_date = _stone_date('color_date', 'color_set')


class CloseOrderSerializer(OpenOrderSerializer):
    """One row per closed (fully shipped) P.O. line.

    Same columns as Open Order, but Bal. Qty. (always 0) is replaced by Shipped Qty.
    """

    balqty = None  # drop inherited column
    shipqty = drf_serializers.IntegerField(read_only=True, label='Shipped Qty.')

    class Meta(OpenOrderSerializer.Meta):
        fields = [
            'podate', 'customer_code', 'vendor_code', 'pono', 'customer_pono',
            'styleno', 'qty', 'shipqty', 'ddate', 'vcsdate', 'acexecutive',
        ]


def _fig(key):
    """Build a method field returning one per-piece figure rounded to 2 places."""

    def method(self, obj):
        return float(round(get_invoice_figures(obj)[key], 2))

    return method


class InvoiceValueSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """One row per shipment line. Labels match the Invoice Value P/C export headers."""

    pono = drf_serializers.CharField(
        source='poid.pono', read_only=True, default=None, label='P.O. No',
    )
    design_no = drf_serializers.CharField(
        source='costcardid.vendor_style_no', read_only=True, default=None, label='Design No.',
    )
    invoice_pcs = drf_serializers.IntegerField(
        source='pcs', read_only=True, label='Invoice Pcs',
    )
    invoice_netwt = drf_serializers.DecimalField(
        source='metalwt', max_digits=10, decimal_places=3, read_only=True, label='Invoice NetWt.',
    )
    invoice_cts = drf_serializers.DecimalField(
        source='diawt', max_digits=10, decimal_places=3, read_only=True, label='Invoice Cts.',
    )
    invoice_labor = drf_serializers.DecimalField(
        source='labour', max_digits=15, decimal_places=2, read_only=True, label='Invoice Labor',
    )
    avg_netwt = drf_serializers.SerializerMethodField(label='Avg NetWt.')
    avg_cts = drf_serializers.SerializerMethodField(label='Avg Cts.')
    avg_labor = drf_serializers.SerializerMethodField(label='Avg Labor')
    avg_cts_value = drf_serializers.SerializerMethodField(label='Avg Cts. Value')
    tr_oz = drf_serializers.DecimalField(
        source='triounce', max_digits=10, decimal_places=4, read_only=True, label='Tr. Oz',
    )
    kt = drf_serializers.IntegerField(
        source='costcardid.karat', read_only=True, default=None, label='KT',
    )
    gold_loss = drf_serializers.DecimalField(
        source='costcardid.metal_loss_pct', max_digits=6, decimal_places=2,
        read_only=True, default=None, label='Gold Loss',
    )
    avg_metal_amt = drf_serializers.SerializerMethodField(label='Avg. Metal Amt.')
    duty = drf_serializers.SerializerMethodField(label='Duty')
    other_exp = drf_serializers.SerializerMethodField(label='Other exp.')
    # TODO: Vendor Metal Amt. / Vendor Diamond Amt. (blank in the sample, source unknown)
    avg_per_pc_value = drf_serializers.SerializerMethodField(label='Avg. Per Pc. Value')

    get_avg_netwt = _fig('avg_netwt')
    get_avg_cts = _fig('avg_cts')
    get_avg_labor = _fig('avg_labor')
    get_avg_cts_value = _fig('avg_cts_value')
    get_avg_metal_amt = _fig('avg_metal')
    get_duty = _fig('duty')
    get_other_exp = _fig('other')
    get_avg_per_pc_value = _fig('per_pc')

    class Meta:
        model = VendorShipmentLine
        fields = [
            'pono', 'design_no', 'invoice_pcs', 'invoice_netwt', 'invoice_cts',
            'invoice_labor', 'avg_netwt', 'avg_cts', 'avg_labor', 'avg_cts_value',
            'tr_oz', 'kt', 'gold_loss', 'avg_metal_amt', 'duty', 'other_exp',
            'avg_per_pc_value',
        ]


def _stone(kind, key):
    """Method field returning one P.O. Stone Valuation figure ('dia' / 'col')."""

    def method(self, obj):
        return float(get_stone_valuation_figures(obj)[kind][key])

    return method


class POStoneValuationSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """One row per P.O. line. Labels match the P.O. Stone Valuation export headers."""

    pono = drf_serializers.CharField(source='poid.pono', read_only=True, label='P.O. No.')
    styleno = drf_serializers.CharField(read_only=True, label='Style No.')
    issue_dia_cts = drf_serializers.SerializerMethodField(label='Issue Dia. Cts.')
    issue_dia_rate = drf_serializers.SerializerMethodField(label='Issue Dia. Rate')
    issue_dia_amount = drf_serializers.SerializerMethodField(label='Issue Dia. Amount')
    rec_dia_cts = drf_serializers.SerializerMethodField(label='Rec. Dia. Cts.')
    issue_bal_dia_cts = drf_serializers.SerializerMethodField(label='Issue Bal. Dia. Cts.')
    dia_rate = drf_serializers.SerializerMethodField(label='Dia. Rate')
    dia_amount = drf_serializers.SerializerMethodField(label='Dia. Amount')
    issue_col_cts = drf_serializers.SerializerMethodField(label='Issue Col. Cts.')
    issue_col_rate = drf_serializers.SerializerMethodField(label='Issue Col. Rate')
    issue_col_amount = drf_serializers.SerializerMethodField(label='Issue Col. Amount')
    rec_col_cts = drf_serializers.SerializerMethodField(label='Rec. Col. Cts.')
    bal_col_cts = drf_serializers.SerializerMethodField(label='Bal. Col. Cts.')
    col_rate = drf_serializers.SerializerMethodField(label='Col. Rate')
    col_amount = drf_serializers.SerializerMethodField(label='Col. Amount')
    bal_pcs = drf_serializers.SerializerMethodField(label='Bal. Pcs')

    get_issue_dia_cts = _stone('dia', 'issue_cts')
    get_issue_dia_rate = _stone('dia', 'issue_rate')
    get_issue_dia_amount = _stone('dia', 'issue_amount')
    get_rec_dia_cts = _stone('dia', 'rec_cts')
    get_issue_bal_dia_cts = _stone('dia', 'bal_cts')
    get_dia_rate = _stone('dia', 'issue_rate')
    get_dia_amount = _stone('dia', 'bal_amount')
    get_issue_col_cts = _stone('col', 'issue_cts')
    get_issue_col_rate = _stone('col', 'issue_rate')
    get_issue_col_amount = _stone('col', 'issue_amount')
    get_rec_col_cts = _stone('col', 'rec_cts')
    get_bal_col_cts = _stone('col', 'bal_cts')
    get_col_rate = _stone('col', 'issue_rate')
    get_col_amount = _stone('col', 'bal_amount')

    def get_bal_pcs(self, obj):
        return get_stone_valuation_figures(obj)['bal_pcs']

    class Meta:
        model = PurchaseOrderLine
        fields = [
            'pono', 'styleno', 'issue_dia_cts', 'issue_dia_rate', 'issue_dia_amount',
            'rec_dia_cts', 'issue_bal_dia_cts', 'dia_rate', 'dia_amount',
            'issue_col_cts', 'issue_col_rate', 'issue_col_amount', 'rec_col_cts',
            'bal_col_cts', 'col_rate', 'col_amount', 'bal_pcs',
        ]


def _status(kind, key):
    def method(self, obj):
        return float(get_stone_valuation_figures(obj)[kind][key])

    return method


def _po_figure(kind, key):
    def method(self, obj):
        return float(get_po_stone_figures(obj)[kind][key])

    return method


class POStoneStatusSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    pono = drf_serializers.CharField(source='poid.pono', read_only=True, label='P.O.')
    podate = drf_serializers.DateField(
        source='poid.podate', read_only=True, format=DATE_FMT, label='P.O. Date',
    )
    customer_code = drf_serializers.CharField(
        source='poid.customerid.code', read_only=True, default=None, label='Customer',
    )
    vendor_code = drf_serializers.CharField(
        source='poid.vendorid.name', read_only=True, default=None, label='Vendor',
    )
    po_dia_cts = drf_serializers.SerializerMethodField(label='P.O. Dia. Cts.')
    po_dia_amount = drf_serializers.SerializerMethodField(label='P.O. Dia. Amount.')
    issue_dia_cts = drf_serializers.SerializerMethodField(label='Issue Dia. Cts.')
    issue_dia_amount = drf_serializers.SerializerMethodField(label='Issue Dia. Amount')
    rec_dia_cts = drf_serializers.SerializerMethodField(label='Rec. Dia. Cts.')
    issue_bal_dia_cts = drf_serializers.SerializerMethodField(label='Issue Bal. Dia. Cts.')
    po_col_cts = drf_serializers.SerializerMethodField(label='P.O. Col. Cts.')
    po_col_amount = drf_serializers.SerializerMethodField(label='P.O. Col. Amount.')
    issue_col_cts = drf_serializers.SerializerMethodField(label='Issue Col. Cts.')
    issue_col_amount = drf_serializers.SerializerMethodField(label='Issue Col. Amount')
    rec_col_cts = drf_serializers.SerializerMethodField(label='Rec. Col. Cts.')
    issue_bal_col_cts = drf_serializers.SerializerMethodField(label='Issue Bal. Col. Cts.')

    get_po_dia_cts = _po_figure('dia', 'cts')
    get_po_dia_amount = _po_figure('dia', 'amount')
    get_issue_dia_cts = _status('dia', 'issue_cts')
    get_issue_dia_amount = _status('dia', 'issue_amount')
    get_rec_dia_cts = _status('dia', 'rec_cts')
    get_issue_bal_dia_cts = _status('dia', 'bal_cts')
    get_po_col_cts = _po_figure('col', 'cts')
    get_po_col_amount = _po_figure('col', 'amount')
    get_issue_col_cts = _status('col', 'issue_cts')
    get_issue_col_amount = _status('col', 'issue_amount')
    get_rec_col_cts = _status('col', 'rec_cts')
    get_issue_bal_col_cts = _status('col', 'bal_cts')

    class Meta:
        model = PurchaseOrderLine
        fields = [
            'pono', 'podate', 'customer_code', 'vendor_code',
            'po_dia_cts', 'po_dia_amount', 'issue_dia_cts', 'issue_dia_amount',
            'rec_dia_cts', 'issue_bal_dia_cts',
            'po_col_cts', 'po_col_amount', 'issue_col_cts', 'issue_col_amount',
            'rec_col_cts', 'issue_bal_col_cts',
        ]


def _po_num(key):
    def method(self, obj):
        value = getattr(obj, key, None)
        if value is None:
            return 0
        value = float(value)
        return int(value) if value == int(value) else round(value, 3)

    return method


def _po_date(key):
    def method(self, obj):
        date = getattr(obj, key, None)
        return date.strftime(DATE_FMT) if date else None

    return method


def _po_text(key):
    def method(self, obj):
        return getattr(obj, key, None) or None

    return method


class POStatusSerializer(DataExportSerializerMixin, InvenTreeModelSerializer):
    """One row per style of the selected P.O. Labels match the P.O. Status export headers."""

    styleno = drf_serializers.CharField(read_only=True, label='Style')
    sets = drf_serializers.IntegerField(source='qty', read_only=True, label='# Of Sets')
    dia_sent_date = drf_serializers.SerializerMethodField(label='Diamond Sent Date')
    dia_sent_sets = drf_serializers.SerializerMethodField(label='Diamond Sent # Of Sets')
    dia_sent_cts = drf_serializers.SerializerMethodField(label='Diamond Sent Cts.')
    dia_sent_inv = drf_serializers.SerializerMethodField(label='Diamond Sent Inv.#')
    col_sent_date = drf_serializers.SerializerMethodField(label='Color Stone Sent Date')
    col_sent_sets = drf_serializers.SerializerMethodField(label='Color Stone Sent # Of Sets')
    col_sent_cts = drf_serializers.SerializerMethodField(label='Color Stone Sent Cts.')
    col_sent_inv = drf_serializers.SerializerMethodField(label='Color Stone Sent Inv.#')
    rec_date = drf_serializers.SerializerMethodField(label='Received Date')
    rec_sets = drf_serializers.SerializerMethodField(label='Received # Of Sets')
    rec_dia_cts = drf_serializers.SerializerMethodField(label='Received Diamond Cts.')
    rec_col_cts = drf_serializers.SerializerMethodField(label='Received Color Stone Cts.')
    rec_inv = drf_serializers.SerializerMethodField(label='Received Inv.#')
    bal_sets = drf_serializers.SerializerMethodField(label='Balance # Of Sets')
    bal_dia_cts = drf_serializers.SerializerMethodField(label='Balance Diamond Cts.')
    bal_col_cts = drf_serializers.SerializerMethodField(label='Balance Color Stone Cts.')

    get_dia_sent_date = _po_date('dia_sent_date')
    get_dia_sent_sets = _po_num('dia_sent_sets')
    get_dia_sent_cts = _po_num('dia_sent_cts')
    get_dia_sent_inv = _po_text('dia_sent_inv')
    get_col_sent_date = _po_date('col_sent_date')
    get_col_sent_sets = _po_num('col_sent_sets')
    get_col_sent_cts = _po_num('col_sent_cts')
    get_col_sent_inv = _po_text('col_sent_inv')
    get_rec_date = _po_date('rec_date')
    get_rec_sets = _po_num('rec_sets')
    get_rec_dia_cts = _po_num('rec_dia_cts')
    get_rec_col_cts = _po_num('rec_col_cts')
    get_rec_inv = _po_text('rec_inv')
    get_bal_sets = _po_num('bal_sets')
    get_bal_dia_cts = _po_num('bal_dia_cts')
    get_bal_col_cts = _po_num('bal_col_cts')

    class Meta:
        model = PurchaseOrderLine
        fields = [
            'styleno', 'sets',
            'dia_sent_date', 'dia_sent_sets', 'dia_sent_cts', 'dia_sent_inv',
            'col_sent_date', 'col_sent_sets', 'col_sent_cts', 'col_sent_inv',
            'rec_date', 'rec_sets', 'rec_dia_cts', 'rec_col_cts', 'rec_inv',
            'bal_sets', 'bal_dia_cts', 'bal_col_cts',
        ]