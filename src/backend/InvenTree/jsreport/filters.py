"""Custom query filters for the Requisition app."""

from django.db.models import (
    DecimalField,
    F,
    Func,
    IntegerField,
    OuterRef,
    Subquery,
)
from django.db.models.functions import Coalesce

import requisition.models


def _metal_sent_aggregate(reference, function, field, output_field):
    """Aggregate MetalSent rows per PurchaseOrder.

    reference is the lookup prefix leading to the PurchaseOrder,
    e.g. 'purchase_order__' when annotating from a related model.
    """

    subquery = requisition.models.MetalSent.objects.filter(
        purchase_order=OuterRef(f'{reference}pk')
    )

    return Coalesce(
        Subquery(
            subquery
            .annotate(
                total=Func(
                    F(field),
                    function=function,
                    output_field=output_field,
                )
            )
            .values('total')
            .order_by()
        ),
        0,
        output_field=output_field,
    )


def _decimal_field():
    return DecimalField(max_digits=15, decimal_places=2)


def annotate_metal_sent_count(reference: str = '') -> Coalesce:
    return _metal_sent_aggregate(reference, 'COUNT', 'pk', IntegerField())


def annotate_total_metal_sent_gms(reference: str = '') -> Coalesce:
    return _metal_sent_aggregate(
        reference,
        'SUM',
        'metal_gms',
        _decimal_field(),
    )


def annotate_total_metal_sent_amount(reference: str = '') -> Coalesce:
    return _metal_sent_aggregate(
        reference,
        'SUM',
        'metal_amount',
        _decimal_field(),
    )