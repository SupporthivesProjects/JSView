"""Provides a JSON API for the 'jsreport' app."""

from django.urls import path

from jsreport.views.close_order import CloseOrderReportView
from jsreport.views.costcard import CostCardExportReportView
from jsreport.views.invoice_value import InvoiceValueReportView
from jsreport.views.open_order import OpenOrderReportView
from jsreport.views.po_status import POStatusReportView
from jsreport.views.po_stone_status import POStoneStatusReportView
from jsreport.views.po_stone_valuation import POStoneValuationReportView

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
    path(
        'po-stone-valuation/',
        POStoneValuationReportView.as_view(),
        name='api-jsreport-po-stone-valuation',
    ),
    path(
        'po-stone-status/',
        POStoneStatusReportView.as_view(),
        name='api-jsreport-po-stone-status',
    ),
    path(
        'po-status/',
        POStatusReportView.as_view(),
        name='api-jsreport-po-status',
    ),
    path(
        'costcard/',
        CostCardExportReportView.as_view(),
        name='api-jsreport-costcard',
    ),
]