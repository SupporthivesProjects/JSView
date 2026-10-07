"""P.O. Stone Status report view for the 'jsreport' app."""

from datetime import timedelta

from django.utils import timezone

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI

from purchase_order.models import PurchaseOrderLine
from users.ruleset import RuleSetEnum

from jsreport.exports import JSReportExportMixin
from jsreport.permissions import JSReportPermission
from jsreport.serializers import POStoneStatusSerializer
from jsreport.filters import get_po_stone_status_queryset
from jsreport.views.open_order import JSReportPagination


class POStoneStatusReportView(JSReportExportMixin, ListAPI):
    """P.O. Stone Status report.

    ?customer=<id>&vendor=<id>&date_range=last_1_month|last_6_month|year_to_date
    &podate_from=YYYY-MM-DD&podate_to=YYYY-MM-DD
    """

    export_name = 'PO_Stone_Status'
    export_plugin = 'jsreport-po-stone-status'
    export_serial = True

    queryset = PurchaseOrderLine.objects.all()
    serializer_class = POStoneStatusSerializer
    pagination_class = JSReportPagination
    permission_classes = [JSReportPermission]
    report_role = RuleSetEnum.REPORT_PO_STONE_STATUS

    filter_backends = SEARCH_ORDER_FILTER
    search_fields = [
        'poid__pono',
        'styleno',
    ]
    ordering_fields = [
        'poid__pono',
        'poid__podate',
    ]

    def get_queryset(self):
        params = self.request.query_params

        date_from = params.get('podate_from')
        date_to = params.get('podate_to')

        today = timezone.localdate()
        date_range = params.get('date_range')

        if date_range == 'last_1_month':
            date_from = str(today - timedelta(days=30))
        elif date_range == 'last_6_month':
            date_from = str(today - timedelta(days=182))
        elif date_range == 'year_to_date':
            date_from = str(today.replace(month=1, day=1))

        return get_po_stone_status_queryset(
            date_from=date_from,
            date_to=date_to,
            vendorid=params.get('vendor'),
            customerid=params.get('customer'),
        )

    def get_export_meta(self, queryset):
        params = self.request.query_params
        line = queryset.first()

        if line is None:
            return []

        meta = []

        if params.get('customer'):
            customer = line.poid.customerid
            meta.append(('Customer', customer.code if customer else ''))

        if params.get('vendor'):
            vendor = line.poid.vendorid
            meta.append(('Vendor', vendor.code if vendor else ''))

        return meta