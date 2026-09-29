"""Pagination classes for the 'requisition' app."""

from rest_framework.pagination import LimitOffsetPagination


class RequisitionPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100