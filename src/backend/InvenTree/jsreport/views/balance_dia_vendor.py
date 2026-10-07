"""Balance Dia. With Vendor report view for the 'jsreport' app."""

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListAPI

from purchase_order.models import PurchaseOrderLine

from jsreport.exports import JSReportExportMixin
from jsreport.filters import get_balance_dia_queryset
from jsreport.permissions import JSReportPermission
from jsreport.serializers import BalanceDiaSerializer
from jsreport.views.open_order import JSReportPagination


class BalanceDiaReportView(JSReportExportMixin, ListAPI):
    """Balance Dia. With Vendor report.

    ?vendorid=<id>  (repeat for several: ?vendorid=1&vendorid=2, or ?vendorid=1,2)
    ?date_from=YYYY-MM-DD  ?date_to=YYYY-MM-DD  (all optional)
    """

    export_name = 'Balance_Dia_With_Vendor'
    export_plugin = 'jsreport-balance-dia-with-vendor'
    export_serial = True

    queryset = PurchaseOrderLine.objects.all()
    serializer_class = BalanceDiaSerializer
    pagination_class = JSReportPagination
    permission_classes = [JSReportPermission]

    filter_backends = SEARCH_ORDER_FILTER
    search_fields = [
        'styleno',
        'poid__pono',
    ]
    ordering_fields = [
        'styleno',
        'poid__pono',
        'poid__podate',
    ]

    def get_vendor_ids(self):
        """Vendor ids from repeated and/or comma separated vendorid params."""
        ids = []
        for value in self.request.query_params.getlist('vendorid'):
            ids.extend(v.strip() for v in value.split(',') if v.strip())
        return ids

    def get_queryset(self):
        params = self.request.query_params

        return get_balance_dia_queryset(
            date_from=params.get('date_from'),
            date_to=params.get('date_to'),
            vendorid=self.get_vendor_ids(),
        )

    def get_export_sheet_title(self, instance):
        """One sheet per vendor."""
        vendor = instance.poid.vendorid
        return vendor.name if vendor else None