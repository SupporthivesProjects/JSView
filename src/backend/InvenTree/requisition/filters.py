"""Custom query filters for the Requisition app."""

from django.db.models import DecimalField, F, Func, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet

import requisition.models


def annotate_metal_sent_count(reference: str = '') -> QuerySet:
    """Count MetalSent entries for a PurchaseOrder."""
    subquery = requisition.models.MetalSent.objects.filter(
        purchase_order=OuterRef(f'{reference}pk')
    )

    return Coalesce(
        Subquery(
            subquery
            .annotate(total=Func(F('pk'), function='COUNT', output_field=IntegerField()))
            .values('total')
            .order_by()
        ),
        0,
        output_field=IntegerField(),
    )


def annotate_total_metal_sent_gms(reference: str = '') -> QuerySet:
    """Sum total metal grams sent for a PurchaseOrder."""
    subquery = requisition.models.MetalSent.objects.filter(
        purchase_order=OuterRef(f'{reference}pk')
    )

    return Coalesce(
        Subquery(
            subquery
            .annotate(total=Func(F('metal_gms'), function='SUM', output_field=DecimalField()))
            .values('total')
            .order_by()
        ),
        0,
        output_field=DecimalField(),
    )


def annotate_total_metal_sent_amount(reference: str = '') -> QuerySet:
    """Sum total metal amount sent for a PurchaseOrder."""
    subquery = requisition.models.MetalSent.objects.filter(
        purchase_order=OuterRef(f'{reference}pk')
    )

    return Coalesce(
        Subquery(
            subquery
            .annotate(total=Func(F('metal_amount'), function='SUM', output_field=DecimalField()))
            .values('total')
            .order_by()
        ),
        0,
        output_field=DecimalField(),
    )