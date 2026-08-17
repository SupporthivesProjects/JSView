"""URL definitions for the 'properties' app."""

from django.urls import include, path

from . import views

urlpatterns = [
    path('diamond-stone/', include([
        path('<int:pk>/', views.DiamondStoneDetail.as_view(), name='api-diamond-stone-detail'),
        path('', views.DiamondStoneList.as_view(), name='api-diamond-stone-list'),
    ])),
    path('diamond-cut/', include([
        path('<int:pk>/', views.DiamondCutDetail.as_view(), name='api-diamond-cut-detail'),
        path('', views.DiamondCutList.as_view(), name='api-diamond-cut-list'),
    ])),
    path('diamond-shape/', include([
        path('<int:pk>/', views.DiamondShapeDetail.as_view(), name='api-diamond-shape-detail'),
        path('', views.DiamondShapeList.as_view(), name='api-diamond-shape-list'),
    ])),
    path('diamond-color/', include([
        path('<int:pk>/', views.DiamondColorDetail.as_view(), name='api-diamond-color-detail'),
        path('', views.DiamondColorList.as_view(), name='api-diamond-color-list'),
    ])),
    path('diamond-size/', include([
        path('<int:pk>/', views.DiamondSizeDetail.as_view(), name='api-diamond-size-detail'),
        path('', views.DiamondSizeList.as_view(), name='api-diamond-size-list'),
    ])),
    path('diamond-quality/', include([
        path('<int:pk>/', views.DiamondQualityDetail.as_view(), name='api-diamond-quality-detail'),
        path('', views.DiamondQualityList.as_view(), name='api-diamond-quality-list'),
    ])),
    path('colorstone/', include([
        path('<int:pk>/', views.ColorStoneDetail.as_view(), name='api-colorstone-detail'),
        path('', views.ColorStoneList.as_view(), name='api-colorstone-list'),
    ])),
    path('colorstone-cut/', include([
        path('<int:pk>/', views.ColorStoneCutDetail.as_view(), name='api-colorstone-cut-detail'),
        path('', views.ColorStoneCutList.as_view(), name='api-colorstone-cut-list'),
    ])),
    path('colorstone-shape/', include([
        path('<int:pk>/', views.ColorStoneShapeDetail.as_view(), name='api-colorstone-shape-detail'),
        path('', views.ColorStoneShapeList.as_view(), name='api-colorstone-shape-list'),
    ])),
    path('colorstone-color/', include([
        path('<int:pk>/', views.ColorStoneColorDetail.as_view(), name='api-colorstone-color-detail'),
        path('', views.ColorStoneColorList.as_view(), name='api-colorstone-color-list'),
    ])),
    path('colorstone-size/', include([
        path('<int:pk>/', views.ColorStoneSizeDetail.as_view(), name='api-colorstone-size-detail'),
        path('', views.ColorStoneSizeList.as_view(), name='api-colorstone-size-list'),
    ])),
]
