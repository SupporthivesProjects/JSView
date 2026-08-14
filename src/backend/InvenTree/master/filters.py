"""Custom query filters for the Master app."""

from django.db.models import (
    DecimalField,
    F,
    Func,
    IntegerField,
    OuterRef,
    Subquery,
)
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet

import master.models


def annotate_purity_count(reference: str = '') -> QuerySet:
    """Count MetalPurity entries for a MetalType."""
    subquery = master.models.MetalPurity.objects.filter(
        metal_type=OuterRef(f'{reference}pk')
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


def annotate_labour_setting_count(reference: str = '') -> QuerySet:
    """Count LabourSetting entries for a Setting."""
    subquery = master.models.LabourSetting.objects.filter(
        setting=OuterRef(f'{reference}pk')
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


def annotate_labour_setting_rate(reference: str = '') -> QuerySet:
    """Get the latest LabourSetting rate for a Setting."""
    subquery = master.models.LabourSetting.objects.filter(
        setting=OuterRef(f'{reference}pk')
    ).order_by('-pk')

    return Subquery(
        subquery.values('rate')[:1],
        output_field=DecimalField(),
    )


def annotate_metal_rate_count(reference: str = '') -> QuerySet:
    """Count MetalRate entries for a MetalType."""
    subquery = master.models.MetalRate.objects.filter(
        metal_type=OuterRef(f'{reference}pk')
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


def annotate_latest_metal_rate(reference: str = '') -> QuerySet:
    """Get the most recent MetalRate rate for a MetalType."""
    subquery = master.models.MetalRate.objects.filter(
        metal_type=OuterRef(f'{reference}pk')
    ).order_by('-date')

    return Subquery(
        subquery.values('rate')[:1],
        output_field=DecimalField(),
    )

