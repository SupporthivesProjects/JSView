"""Custom query filters for the Company app."""

from decimal import Decimal

from django.db.models import DecimalField, ExpressionWrapper, F, Q
from django.db.models.functions import Coalesce, Greatest

from sql_util.utils import SubquerySum

from order.status_codes import PurchaseOrderStatusGroups


def annotate_on_order_quantity():
    """Annotate the on-order quantity for each SupplierPart."""

    order_filter = Q(
        order__status__in=PurchaseOrderStatusGroups.OPEN,
        quantity__gt=F('received'),
    )

    return Coalesce(
        SubquerySum(
            Greatest(
                ExpressionWrapper(
                    F('purchase_order_line_items__quantity')
                    - F('purchase_order_line_items__received'),
                    output_field=DecimalField(),
                ),
                0,
                output_field=DecimalField(),
            ),
            filter=order_filter,
        ),
        Decimal(0),
        output_field=DecimalField(),
    )

