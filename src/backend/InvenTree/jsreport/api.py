"""Provides a JSON API for the 'jsreport' app."""

from django.urls import path

from jsreport.views.open_order import OpenOrderReportView
from jsreport.views.close_order import CloseOrderReportView

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
]