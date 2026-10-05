"""Provides a JSON API for the 'jsreport' app."""

from django.urls import path

from jsreport.views.close_order import CloseOrderReportView
from jsreport.views.invoice_value import InvoiceValueReportView
from jsreport.views.open_order import OpenOrderReportView

jsreport_api_urls = [
    path(
        'open-order/',
        OpenOrderReportView.as_view(),
        name='api-jsreport-open-order',
    ),
    path(
        'close-order/',
        CloseOrderReportView.as_view(),
        name='api-jsreport-close-order',
    ),
    path(
        'invoice-value/',
        InvoiceValueReportView.as_view(),
        name='api-jsreport-invoice-value',
    ),
]