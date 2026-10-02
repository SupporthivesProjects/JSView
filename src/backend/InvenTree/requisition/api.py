"""Provides a JSON API for the 'requisition' app."""

from django.urls import path

from .views.flute import (
    FluteEntryDetail,
    FluteEntryLineDetail,
    FluteEntryList,
)
from .views.metal import MetalOrderRequisitionView
from .views.metal_sent import MetalSentDetail, MetalSentList
from .views.stone import StoneOrderListView

requisition_api_urls = [
    # Flute entries
    path(
        'flute-entry/<int:pk>/',
        FluteEntryDetail.as_view(),
        name='api-flute-entry-detail',
    ),
    path(
        'flute-entry/',
        FluteEntryList.as_view(),
        name='api-flute-entry-list',
    ),
    path(
        'flute-entry/<int:flute_entry_id>/lines/<int:line_id>/',
        FluteEntryLineDetail.as_view(),
        name='api-flute-entry-line-detail',
    ),

    # Metal sent
    path(
        'metal-sent/<int:pk>/',
        MetalSentDetail.as_view(),
        name='api-metal-sent-detail',
    ),
    path(
        'metal-sent/',
        MetalSentList.as_view(),
        name='api-metal-sent-list',
    ),

    # Requisition reports
    path(
        'metal/',
        MetalOrderRequisitionView.as_view(),
        name='api-metal',
    ),
    path(
        'stone/',
        StoneOrderListView.as_view(),
        name='api-stone',
    ),
]