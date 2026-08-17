"""Provides a JSON API for the 'master' app."""

from django.urls import include, path

from data_exporter.mixins import DataExportViewMixin
from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveUpdateDestroyAPI
from rest_framework.pagination import LimitOffsetPagination
from master.permissions import MasterDataPermission

from . import serializers as master_serializers
from .models import (
    ACExecutive,
    CourierService,
    Duty,
    FindingType,
    FinishType,
    JewelryCategory,
    JewelrySubCategory,
    LabourSetting,
    MetalPurity,
    MetalRate,
    MetalType,
    Setting,
    Stamp,
    Terms,
)


class MasterPagination(LimitOffsetPagination):
    """Default pagination for master app list endpoints."""

    default_limit = 10
    max_limit = 100


class MetalTypeList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating MetalType objects."""

    queryset = MetalType.objects.all()
    serializer_class = master_serializers.MetalTypeSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'active']
    ordering = 'name'


class MetalTypeDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single MetalType object."""

    queryset = MetalType.objects.all()
    serializer_class = master_serializers.MetalTypeSerializer
    permission_classes = [MasterDataPermission]


class MetalPurityList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating MetalPurity objects."""

    queryset = MetalPurity.objects.all()
    serializer_class = master_serializers.MetalPuritySerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['metal_type']
    search_fields = ['name']
    ordering_fields = ['metal_type', 'name', 'purity']
    ordering = 'name'


class MetalPurityDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single MetalPurity object."""

    queryset = MetalPurity.objects.all()
    serializer_class = master_serializers.MetalPuritySerializer
    permission_classes = [MasterDataPermission]


class MetalRateList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating MetalRate objects."""

    queryset = MetalRate.objects.all()
    serializer_class = master_serializers.MetalRateSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['metal_type']
    ordering_fields = ['date', 'rate']
    ordering = '-date'


class MetalRateDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single MetalRate object."""

    queryset = MetalRate.objects.all()
    serializer_class = master_serializers.MetalRateSerializer
    permission_classes = [MasterDataPermission]


class FindingTypeList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating FindingType objects."""

    queryset = FindingType.objects.all()
    serializer_class = master_serializers.FindingTypeSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class FindingTypeDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single FindingType object."""

    queryset = FindingType.objects.all()
    serializer_class = master_serializers.FindingTypeSerializer
    permission_classes = [MasterDataPermission]


class FinishTypeList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating FinishType objects."""

    queryset = FinishType.objects.all()
    serializer_class = master_serializers.FinishTypeSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class FinishTypeDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single FinishType object."""

    queryset = FinishType.objects.all()
    serializer_class = master_serializers.FinishTypeSerializer
    permission_classes = [MasterDataPermission]


class SettingList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating Setting objects."""

    queryset = Setting.objects.all()
    serializer_class = master_serializers.SettingSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class SettingDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single Setting object."""

    queryset = Setting.objects.all()
    serializer_class = master_serializers.SettingSerializer
    permission_classes = [MasterDataPermission]


class LabourSettingList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating LabourSetting objects."""

    queryset = LabourSetting.objects.all()
    serializer_class = master_serializers.LabourSettingSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['setting', 'charge_type']
    search_fields = ['name']
    ordering_fields = ['name', 'charge_type', 'rate', 'active']
    ordering = 'name'


class LabourSettingDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single LabourSetting object."""

    queryset = LabourSetting.objects.all()
    serializer_class = master_serializers.LabourSettingSerializer
    permission_classes = [MasterDataPermission]


class DutyList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating Duty objects."""

    queryset = Duty.objects.all()
    serializer_class = master_serializers.DutySerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    search_fields = ['description']
    ordering_fields = ['metal_type', 'duty', 'markup']
    ordering = 'metal_type'


class DutyDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single Duty object."""

    queryset = Duty.objects.all()
    serializer_class = master_serializers.DutySerializer
    permission_classes = [MasterDataPermission]


class StampList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating Stamp objects."""

    queryset = Stamp.objects.all()
    serializer_class = master_serializers.StampSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class StampDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single Stamp object."""

    queryset = Stamp.objects.all()
    serializer_class = master_serializers.StampSerializer
    permission_classes = [MasterDataPermission]


class ACExecutiveList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating ACExecutive objects."""

    queryset = ACExecutive.objects.all()
    serializer_class = master_serializers.ACExecutiveSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    search_fields = ['name', 'code', 'email']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class ACExecutiveDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single ACExecutive object."""

    queryset = ACExecutive.objects.all()
    serializer_class = master_serializers.ACExecutiveSerializer
    permission_classes = [MasterDataPermission]


class TermsList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating Terms objects."""

    queryset = Terms.objects.all()
    serializer_class = master_serializers.TermsSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'days']
    ordering = 'name'


class TermsDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single Terms object."""

    queryset = Terms.objects.all()
    serializer_class = master_serializers.TermsSerializer
    permission_classes = [MasterDataPermission]


class CourierServiceList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating CourierService objects."""

    queryset = CourierService.objects.all()
    serializer_class = master_serializers.CourierServiceSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    search_fields = ['name', 'contact_person']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class CourierServiceDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single CourierService object."""

    queryset = CourierService.objects.all()
    serializer_class = master_serializers.CourierServiceSerializer
    permission_classes = [MasterDataPermission]


class JewelryCategoryList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating JewelryCategory objects."""

    queryset = JewelryCategory.objects.all()
    serializer_class = master_serializers.JewelryCategorySerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class JewelryCategoryDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single JewelryCategory object."""

    queryset = JewelryCategory.objects.all()
    serializer_class = master_serializers.JewelryCategorySerializer
    permission_classes = [MasterDataPermission]


class JewelrySubCategoryList(DataExportViewMixin, ListCreateAPI):
    """API endpoint for listing / creating JewelrySubCategory objects."""

    queryset = JewelrySubCategory.objects.all()
    serializer_class = master_serializers.JewelrySubCategorySerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['category']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'category', 'active']
    ordering = 'name'


class JewelrySubCategoryDetail(RetrieveUpdateDestroyAPI):
    """API endpoint for detail view of a single JewelrySubCategory object."""

    queryset = JewelrySubCategory.objects.all()
    serializer_class = master_serializers.JewelrySubCategorySerializer
    permission_classes = [MasterDataPermission]


master_api_urls = [
    path('metal-type/', include([
        path('<int:pk>/', MetalTypeDetail.as_view(), name='api-metal-type-detail'),
        path('', MetalTypeList.as_view(), name='api-metal-type-list'),
    ])),

    path('metal-purity/', include([
        path('<int:pk>/', MetalPurityDetail.as_view(), name='api-metal-purity-detail'),
        path('', MetalPurityList.as_view(), name='api-metal-purity-list'),
    ])),

    path('metal-rate/', include([
        path('<int:pk>/', MetalRateDetail.as_view(), name='api-metal-rate-detail'),
        path('', MetalRateList.as_view(), name='api-metal-rate-list'),
    ])),

    path('finding-type/', include([
        path('<int:pk>/', FindingTypeDetail.as_view(), name='api-finding-type-detail'),
        path('', FindingTypeList.as_view(), name='api-finding-type-list'),
    ])),

    path('finish-type/', include([
        path('<int:pk>/', FinishTypeDetail.as_view(), name='api-finish-type-detail'),
        path('', FinishTypeList.as_view(), name='api-finish-type-list'),
    ])),

    path('setting/', include([
        path('<int:pk>/', SettingDetail.as_view(), name='api-setting-detail'),
        path('', SettingList.as_view(), name='api-setting-list'),
    ])),

    path('labour-setting/', include([
        path('<int:pk>/', LabourSettingDetail.as_view(), name='api-labour-setting-detail'),
        path('', LabourSettingList.as_view(), name='api-labour-setting-list'),
    ])),

    path('duty/', include([
        path('<int:pk>/', DutyDetail.as_view(), name='api-duty-detail'),
        path('', DutyList.as_view(), name='api-duty-list'),
    ])),

    path('stamp/', include([
        path('<int:pk>/', StampDetail.as_view(), name='api-stamp-detail'),
        path('', StampList.as_view(), name='api-stamp-list'),
    ])),

    path('ac-executive/', include([
        path('<int:pk>/', ACExecutiveDetail.as_view(), name='api-ac-executive-detail'),
        path('', ACExecutiveList.as_view(), name='api-ac-executive-list'),
    ])),

    path('terms/', include([
        path('<int:pk>/', TermsDetail.as_view(), name='api-terms-detail'),
        path('', TermsList.as_view(), name='api-terms-list'),
    ])),

    path('courier-service/', include([
        path('<int:pk>/', CourierServiceDetail.as_view(), name='api-courier-service-detail'),
        path('', CourierServiceList.as_view(), name='api-courier-service-list'),
    ])),

    path('jewelry-category/', include([
        path( '<int:pk>/', JewelryCategoryDetail.as_view(),name='api-jewelry-category-detail',),
        path('',JewelryCategoryList.as_view(),name='api-jewelry-category-list',),
    ])),

    path('jewelry-sub-category/', include([
        path('<int:pk>/',JewelrySubCategoryDetail.as_view(),name='api-jewelry-sub-category-detail',),
        path('',JewelrySubCategoryList.as_view(),name='api-jewelry-sub-category-list',),
    ])),
]