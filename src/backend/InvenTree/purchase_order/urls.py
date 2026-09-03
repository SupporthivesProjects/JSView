from django.urls import include, path

from . import views


purchase_order_api_urls = [
    path('po/', include([
        path(
            '<int:pk>/lines/',
            views.PurchaseOrderLineList.as_view(),
            name='api-po-lines-for-order',
        ),
        path(
            '<int:pk>/',
            views.PurchaseOrderDetail.as_view(),
            name='api-purchase-order-detail',
        ),
        path(
            '',
            views.PurchaseOrderList.as_view(),
            name='api-purchase-order-list',
        ),
    ])),
    path('po-line/', include([
        path(
            '<int:pk>/',
            views.PurchaseOrderLineDetail.as_view(),
            name='api-purchase-order-line-detail',
        ),
        path(
            '',
            views.PurchaseOrderLineList.as_view(),
            name='api-purchase-order-line-list',
        ),
    ])),
]
