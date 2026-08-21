"""Utility functions for the purchase_order app.

Replicates the fn_getpono PostgreSQL function in pure Python/Django ORM.
"""

from datetime import date

from django.db import connection
from django.db.models import Max

from .models import PurchaseOrder

# POCategories treated as "sample" for numbering purposes
SAMPLE_CATEGORIES = [
    'Sample',
    'CZ Sample',
    'CZ Host Sample',
    'Photo Sample',
]


def generate_po_number(
    potype: str,
    pocategory: str,
    customerid: int | None,
    podate: date,
) -> tuple[str, int]:
    """
    Replicate fn_getpono PostgreSQL function.

    Generates a PO number in the format: ``{ccode} {year}-{npono:04d} {prefix}``

    Returns:
        Tuple of (pono: str, npono: int)
    """
    # Get ccode from tbledger via raw SQL
    ccode = 'UNK'
    if customerid is not None:
        with connection.cursor() as cursor:
            cursor.execute(
                'SELECT ccode FROM tbledger WHERE ledgerid = %s',
                [customerid],
            )
            row = cursor.fetchone()
            if row and row[0]:
                ccode = row[0]

    # Determine the year from podate
    nyear = podate.year if podate else date.today().year

    # Determine prefix and filter
    is_sample = pocategory in SAMPLE_CATEGORIES

    if is_sample:
        prefix = 'S'
    else:
        prefix = 'P'

    # Find the max npono for the same year, potype, and sample/non-sample group
    queryset = PurchaseOrder.objects.filter(
        nyear=nyear,
        potype=potype,
    )

    if is_sample:
        queryset = queryset.filter(pocategory__in=SAMPLE_CATEGORIES)
    else:
        queryset = queryset.exclude(pocategory__in=SAMPLE_CATEGORIES)

    max_npono = queryset.aggregate(max_npono=Max('npono'))['max_npono']

    if max_npono is not None:
        npono = max_npono + 1
    else:
        npono = 1

    pono = f'{ccode} {nyear}-{npono:04d} {prefix}'

    return pono, npono
