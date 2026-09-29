"""Provides a JSON API for the 'requisition' app."""

from django.urls import include, path

from .views.metal import MetalOrderRequisitionView
from .views.metal_sent import MetalSentDetail, MetalSentList
from .views.stone import StoneOrderListView

requisition_api_urls = [
    path('metal-sent/', include([
        path('<int:pk>/', MetalSentDetail.as_view(), name='api-metal-sent-detail'),
        path('', MetalSentList.as_view(), name='api-metal-sent-list'),
    ])),
    path('stone/', StoneOrderListView.as_view(), name='api-stone'),
    path('metal/', MetalOrderRequisitionView.as_view(), name='api-metal'),
]