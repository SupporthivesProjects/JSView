"""Custom query filters for the Cards app."""

from django.db.models import F, Func, IntegerField, OuterRef, Subquery
from django.db.models.functions import Coalesce
from django.db.models.query import QuerySet

import costcard.models


def annotate_diamond_line_count(reference: str = '') -> QuerySet:
    """Count CostCardDiamondLine entries for a CostCard."""
    subquery = costcard.models.CostCardDiamondLine.objects.filter(
        cost_card=OuterRef(f'{reference}pk')
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


def annotate_colorstone_line_count(reference: str = '') -> QuerySet:
    """Count CostCardColorStoneLine entries for a CostCard."""
    subquery = costcard.models.CostCardColorStoneLine.objects.filter(
        cost_card=OuterRef(f'{reference}pk')
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


def annotate_finish_line_count(reference: str = '') -> QuerySet:
    """Count CostCardFinishLine entries for a CostCard."""
    subquery = costcard.models.CostCardFinishLine.objects.filter(
        cost_card=OuterRef(f'{reference}pk')
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


def annotate_stone_place_diamond_usage_count(reference: str = '') -> QuerySet:
    """Count CostCardDiamondLine entries using a given StonePlace."""
    subquery = costcard.models.CostCardDiamondLine.objects.filter(
        stone_place=OuterRef(f'{reference}pk')
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


def annotate_stone_place_colorstone_usage_count(reference: str = '') -> QuerySet:
    """Count CostCardColorStoneLine entries using a given StonePlace."""
    subquery = costcard.models.CostCardColorStoneLine.objects.filter(
        stone_place=OuterRef(f'{reference}pk')
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