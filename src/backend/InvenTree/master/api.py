"""Provides a JSON API for the 'master' app."""

from django.urls import include, path

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
    POMail,
    Setting,
    Stamp,
    Templates,
    Terms,
)


class MasterPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class MetalTypeList(ListCreateAPI):
    queryset = MetalType.objects.all()
    serializer_class = master_serializers.MetalTypeSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['code', 'name', 'description']
    ordering_fields = ['code', 'name', 'active']
    ordering = 'name'


class MetalTypeDetail(RetrieveUpdateDestroyAPI):
    queryset = MetalType.objects.all()
    serializer_class = master_serializers.MetalTypeSerializer
    permission_classes = [MasterDataPermission]


class MetalPurityList(ListCreateAPI):
    queryset = MetalPurity.objects.all()
    serializer_class = master_serializers.MetalPuritySerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['metal_type', 'active']
    search_fields = ['name', 'metal_type__name']
    ordering_fields = ['metal_type', 'name', 'purity']
    ordering = 'name'


class MetalPurityDetail(RetrieveUpdateDestroyAPI):
    queryset = MetalPurity.objects.all()
    serializer_class = master_serializers.MetalPuritySerializer
    permission_classes = [MasterDataPermission]


class MetalRateList(ListCreateAPI):
    queryset = MetalRate.objects.all()
    serializer_class = master_serializers.MetalRateSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['metal_type', 'active']
    search_fields = ['metal_type__name']
    ordering_fields = ['date', 'rate']
    ordering = '-date'


class MetalRateDetail(RetrieveUpdateDestroyAPI):
    queryset = MetalRate.objects.all()
    serializer_class = master_serializers.MetalRateSerializer
    permission_classes = [MasterDataPermission]


class FindingTypeList(ListCreateAPI):
    queryset = FindingType.objects.all()
    serializer_class = master_serializers.FindingTypeSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['type', 'active']
    search_fields = ['name', 'type', 'metal', 'description']
    ordering_fields = ['name', 'type', 'weight', 'price', 'active']
    ordering = 'name'


class FindingTypeDetail(RetrieveUpdateDestroyAPI):
    queryset = FindingType.objects.all()
    serializer_class = master_serializers.FindingTypeSerializer
    permission_classes = [MasterDataPermission]


class FinishTypeList(ListCreateAPI):
    queryset = FinishType.objects.all()
    serializer_class = master_serializers.FinishTypeSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class FinishTypeDetail(RetrieveUpdateDestroyAPI):
    queryset = FinishType.objects.all()
    serializer_class = master_serializers.FinishTypeSerializer
    permission_classes = [MasterDataPermission]


class SettingList(ListCreateAPI):
    queryset = Setting.objects.all()
    serializer_class = master_serializers.SettingSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class SettingDetail(RetrieveUpdateDestroyAPI):
    queryset = Setting.objects.all()
    serializer_class = master_serializers.SettingSerializer
    permission_classes = [MasterDataPermission]


class LabourSettingList(ListCreateAPI):
    queryset = LabourSetting.objects.all()
    serializer_class = master_serializers.LabourSettingSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['setting', 'charge_type', 'active']
    search_fields = ['name', 'setting__name']
    ordering_fields = ['name', 'charge_type', 'rate', 'active']
    ordering = 'name'


class LabourSettingDetail(RetrieveUpdateDestroyAPI):
    queryset = LabourSetting.objects.all()
    serializer_class = master_serializers.LabourSettingSerializer
    permission_classes = [MasterDataPermission]


class DutyList(ListCreateAPI):
    queryset = Duty.objects.all()
    serializer_class = master_serializers.DutySerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['description', 'metal_type__name']
    ordering_fields = ['metal_type', 'duty', 'markup']
    ordering = 'metal_type'


class DutyDetail(RetrieveUpdateDestroyAPI):
    queryset = Duty.objects.all()
    serializer_class = master_serializers.DutySerializer
    permission_classes = [MasterDataPermission]


class StampList(ListCreateAPI):
    queryset = Stamp.objects.all()
    serializer_class = master_serializers.StampSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name', 'description', 'customers__name']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class StampDetail(RetrieveUpdateDestroyAPI):
    queryset = Stamp.objects.all()
    serializer_class = master_serializers.StampSerializer
    permission_classes = [MasterDataPermission]


class ACExecutiveList(ListCreateAPI):
    queryset = ACExecutive.objects.all()
    serializer_class = master_serializers.ACExecutiveSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name', 'code', 'email', 'phone']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class ACExecutiveDetail(RetrieveUpdateDestroyAPI):
    queryset = ACExecutive.objects.all()
    serializer_class = master_serializers.ACExecutiveSerializer
    permission_classes = [MasterDataPermission]


class TermsList(ListCreateAPI):
    queryset = Terms.objects.all()
    serializer_class = master_serializers.TermsSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name', 'description', 'vendors__name']
    ordering_fields = ['name', 'days']
    ordering = 'name'


class TermsDetail(RetrieveUpdateDestroyAPI):
    queryset = Terms.objects.all()
    serializer_class = master_serializers.TermsSerializer
    permission_classes = [MasterDataPermission]


class CourierServiceList(ListCreateAPI):
    queryset = CourierService.objects.all()
    serializer_class = master_serializers.CourierServiceSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name', 'contact_person', 'email', 'phone']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class CourierServiceDetail(RetrieveUpdateDestroyAPI):
    queryset = CourierService.objects.all()
    serializer_class = master_serializers.CourierServiceSerializer
    permission_classes = [MasterDataPermission]


class JewelryCategoryList(ListCreateAPI):
    queryset = JewelryCategory.objects.all()
    serializer_class = master_serializers.JewelryCategorySerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class JewelryCategoryDetail(RetrieveUpdateDestroyAPI):
    queryset = JewelryCategory.objects.all()
    serializer_class = master_serializers.JewelryCategorySerializer
    permission_classes = [MasterDataPermission]


class JewelrySubCategoryList(ListCreateAPI):
    queryset = JewelrySubCategory.objects.all()
    serializer_class = master_serializers.JewelrySubCategorySerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['category', 'active']
    search_fields = ['name', 'description', 'category__name']
    ordering_fields = ['name', 'category', 'active']
    ordering = 'name'


class JewelrySubCategoryDetail(RetrieveUpdateDestroyAPI):
    queryset = JewelrySubCategory.objects.all()
    serializer_class = master_serializers.JewelrySubCategorySerializer
    permission_classes = [MasterDataPermission]


class TemplatesList(ListCreateAPI):
    queryset = Templates.objects.all()
    serializer_class = master_serializers.TemplatesSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name', 'subject']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class TemplatesDetail(RetrieveUpdateDestroyAPI):
    queryset = Templates.objects.all()
    serializer_class = master_serializers.TemplatesSerializer
    permission_classes = [MasterDataPermission]


class POMailList(ListCreateAPI):
    queryset = POMail.objects.all()
    serializer_class = master_serializers.POMailSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'order', 'active']
    ordering = 'order'


class POMailDetail(RetrieveUpdateDestroyAPI):
    queryset = POMail.objects.all()
    serializer_class = master_serializers.POMailSerializer
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
        path('<int:pk>/', JewelryCategoryDetail.as_view(), name='api-jewelry-category-detail'),
        path('', JewelryCategoryList.as_view(), name='api-jewelry-category-list'),
    ])),

    path('jewelry-sub-category/', include([
        path('<int:pk>/', JewelrySubCategoryDetail.as_view(), name='api-jewelry-sub-category-detail'),
        path('', JewelrySubCategoryList.as_view(), name='api-jewelry-sub-category-list'),
    ])),

    path('templates/', include([
        path('<int:pk>/', TemplatesDetail.as_view(), name='api-templates-detail'),
        path('', TemplatesList.as_view(), name='api-templates-list'),
    ])),

    path('po-mail/', include([
        path('<int:pk>/', POMailDetail.as_view(), name='api-po-mail-detail'),
        path('', POMailList.as_view(), name='api-po-mail-list'),
    ])),
]