
from django.urls import include, path

from data_exporter.mixins import DataExportViewMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveUpdateDestroyAPI
from rest_framework.pagination import LimitOffsetPagination
from cards.permissions import MasterDataPermission


order_cards_urls = [

    path('cost-cards/', include([
        # path('<int:pk>/', MetalTypeDetail.as_view(), name='api-metal-type-detail'),
        # path('', MetalTypeList.as_view(), name='api-metal-type-list'),
    ])),
    
]