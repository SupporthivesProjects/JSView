from django.urls import include, path

from . import views

vendor_shipment_api_urls = [
    # Dropdown helpers (must precede the <int:pk> detail route)
    path(
        'po-list/',
        views.VendorPOListView.as_view(),
        name='api-vendor-shipment-po-list',
    ),
    path(
        'style-list/',
        views.VendorStyleListView.as_view(),
        name='api-vendor-shipment-style-list',
    ),
    # Confirm shipment section
    path('confirm/', include([
        path(
            'invoices/',
            views.ConfirmPendingInvoiceView.as_view(),
            name='api-vendor-shipment-confirm-invoices',
        ),
        path(
            'data/',
            views.ConfirmPendingDataView.as_view(),
            name='api-vendor-shipment-confirm-data',
        ),
        path(
            'update/',
            views.ConfirmUpdateView.as_view(),
            name='api-vendor-shipment-confirm-update',
        ),
    ])),
    # Standalone shipment lines
    path('lines/', include([
        path(
            '<int:pk>/',
            views.VendorShipmentLineDetail.as_view(),
            name='api-vendor-shipment-line-detail',
        ),
        path(
            '',
            views.VendorShipmentLineList.as_view(),
            name='api-vendor-shipment-line-list',
        ),
    ])),
    # Shipment detail + lines of a single shipment
    path(
        '<int:pk>/lines/',
        views.VendorShipmentLineList.as_view(),
        name='api-vendor-shipment-lines-for-shipment',
    ),
    path(
        '<int:pk>/',
        views.VendorShipmentDetail.as_view(),
        name='api-vendor-shipment-detail',
    ),
    path(
        '',
        views.VendorShipmentList.as_view(),
        name='api-vendor-shipment-list',
    ),
]
