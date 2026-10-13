"""Provides a JSON API for the 'master' app."""

import hashlib
import json

from django.core.cache import cache
from django.urls import include, path

from data_exporter.mixins import DataExportViewMixin

from InvenTree.filters import SEARCH_ORDER_FILTER
from InvenTree.mixins import ListCreateAPI, RetrieveUpdateDestroyAPI
from rest_framework import status
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from master.permissions import MasterDataPermission

from . import serializers as master_serializers
from .models import (
    ACExecutive,
    CourierService,
    Duty,
    FindingItem,
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
from .po_mail import active_mail, get_order, mail_options, order_blocked, order_choices, send_selected

PO_MAIL_LOCK_SECONDS = 15


def fill_template_attachments(data):
    """Fill empty 'attachments' of each mail format from its Template's attachments field."""
    formats = data.get('formats') if isinstance(data, dict) else None

    if not formats:
        return data

    template_ids = [f.get('template') for f in formats if f.get('template')]

    saved = dict(
        Templates.objects.filter(pk__in=template_ids).values_list('pk', 'attachments')
    )

    for fmt in formats:
        if not fmt.get('attachments'):
            fmt['attachments'] = saved.get(fmt.get('template')) or ''

    return data


class MasterPagination(LimitOffsetPagination):
    default_limit = 10
    max_limit = 100


class MetalTypeList(DataExportViewMixin, ListCreateAPI):
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


class MetalPurityList(DataExportViewMixin, ListCreateAPI):
    queryset = MetalPurity.objects.all()
    serializer_class = master_serializers.MetalPuritySerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['metal_type', 'active']
    search_fields = ['name', 'metal_type__name']
    ordering_fields = ['metal_type', 'name', 'purity', 'karat']
    ordering = 'name'


class MetalPurityDetail(RetrieveUpdateDestroyAPI):
    queryset = MetalPurity.objects.all()
    serializer_class = master_serializers.MetalPuritySerializer
    permission_classes = [MasterDataPermission]


class MetalRateList(DataExportViewMixin, ListCreateAPI):
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


class FindingTypeList(DataExportViewMixin, ListCreateAPI):
    queryset = FindingType.objects.all()
    serializer_class = master_serializers.FindingTypeSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class FindingTypeDetail(RetrieveUpdateDestroyAPI):
    queryset = FindingType.objects.all()
    serializer_class = master_serializers.FindingTypeSerializer
    permission_classes = [MasterDataPermission]


class FindingItemList(DataExportViewMixin, ListCreateAPI):
    queryset = FindingItem.objects.all()
    serializer_class = master_serializers.FindingItemSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['finding_type', 'metal', 'active']
    search_fields = ['name', 'metal__name', 'finding_type__name']
    ordering_fields = ['name', 'weight', 'price', 'active']
    ordering = 'name'


class FindingItemDetail(RetrieveUpdateDestroyAPI):
    queryset = FindingItem.objects.all()
    serializer_class = master_serializers.FindingItemSerializer
    permission_classes = [MasterDataPermission]


class FinishTypeList(DataExportViewMixin, ListCreateAPI):
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


class SettingList(DataExportViewMixin, ListCreateAPI):
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


class LabourSettingList(DataExportViewMixin, ListCreateAPI):
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


class DutyList(DataExportViewMixin, ListCreateAPI):
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


class StampList(DataExportViewMixin, ListCreateAPI):
    queryset = Stamp.objects.all()
    serializer_class = master_serializers.StampSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active', 'all_customers']
    search_fields = ['name', 'description', 'customers__name']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class StampDetail(RetrieveUpdateDestroyAPI):
    queryset = Stamp.objects.all()
    serializer_class = master_serializers.StampSerializer
    permission_classes = [MasterDataPermission]


class ACExecutiveList(DataExportViewMixin, ListCreateAPI):
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


class TermsList(DataExportViewMixin, ListCreateAPI):
    queryset = Terms.objects.all()
    serializer_class = master_serializers.TermsSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active', 'all_vendors']
    search_fields = ['name', 'description', 'vendors__name']
    ordering_fields = ['name', 'days']
    ordering = 'name'


class TermsDetail(RetrieveUpdateDestroyAPI):
    queryset = Terms.objects.all()
    serializer_class = master_serializers.TermsSerializer
    permission_classes = [MasterDataPermission]


class CourierServiceList(DataExportViewMixin, ListCreateAPI):
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


class JewelryCategoryList(DataExportViewMixin, ListCreateAPI):
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


class JewelrySubCategoryList(DataExportViewMixin, ListCreateAPI):
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


class TemplatesList(DataExportViewMixin, ListCreateAPI):
    queryset = Templates.objects.all()
    serializer_class = master_serializers.TemplatesSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name', 'subject', 'recipients', 'attachments']
    ordering_fields = ['name', 'active']
    ordering = 'name'


class TemplatesDetail(RetrieveUpdateDestroyAPI):
    queryset = Templates.objects.all()
    serializer_class = master_serializers.TemplatesSerializer
    permission_classes = [MasterDataPermission]


class POMailList(DataExportViewMixin, ListCreateAPI):
    queryset = POMail.objects.select_related('format1', 'format2', 'format3', 'format4')
    serializer_class = master_serializers.POMailSerializer
    pagination_class = MasterPagination
    permission_classes = [MasterDataPermission]
    filter_backends = SEARCH_ORDER_FILTER
    filterset_fields = ['active']
    search_fields = ['name']
    ordering_fields = ['name', 'order', 'active']
    ordering = 'order'


class POMailDetail(RetrieveUpdateDestroyAPI):
    queryset = POMail.objects.select_related('format1', 'format2', 'format3', 'format4')
    serializer_class = master_serializers.POMailSerializer
    permission_classes = [MasterDataPermission]


class POMailOrderList(APIView):
    queryset = POMail.objects.all()
    permission_classes = [MasterDataPermission]

    def get(self, request):
        return Response(
            order_choices(
                request.query_params.get('search', ''),
                request.query_params.get('type', ''),
            )
        )


class POMailOrderDetail(APIView):
    queryset = POMail.objects.all()
    permission_classes = [MasterDataPermission]

    def get(self, request, pk):
        order = get_order(pk)

        if order is None:
            return Response({'detail': 'Purchase order not found.'}, status=status.HTTP_404_NOT_FOUND)

        mail = active_mail(request.query_params.get('mail'))

        return Response(fill_template_attachments(mail_options(order, mail)))


class POMailSend(APIView):
    queryset = POMail.objects.all()
    permission_classes = [MasterDataPermission]

    def post(self, request):
        order = get_order(request.data.get('po_number'))

        if order is None:
            return Response({'detail': 'Purchase order not found.'}, status=status.HTTP_404_NOT_FOUND)

        blocked = order_blocked(order)

        if blocked:
            return Response({'detail': blocked}, status=status.HTTP_400_BAD_REQUEST)

        selections = request.data.get('formats')

        if not isinstance(selections, list) or not selections:
            return Response({'detail': 'Select at least one mail type.'}, status=status.HTTP_400_BAD_REQUEST)

        fingerprint = hashlib.md5(
            json.dumps(
                [request.user.pk, request.data.get('po_number'), request.data.get('mail'), selections],
                sort_keys=True,
                default=str,
            ).encode()
        ).hexdigest()
        lock_key = f'po-mail-send:{fingerprint}'

        if not cache.add(lock_key, 1, PO_MAIL_LOCK_SECONDS):
            return Response(
                {'detail': 'This mail request was already submitted. Please wait a few seconds.'},
                status=status.HTTP_409_CONFLICT,
            )

        mail = active_mail(request.data.get('mail'))

        try:
            result = send_selected(order, mail, selections)
        except Exception:
            cache.delete(lock_key)
            raise

        if not result['sent']:
            cache.delete(lock_key)

        return Response(
            result,
            status=status.HTTP_200_OK if result['sent'] else status.HTTP_400_BAD_REQUEST,
        )


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

    path('finding-item/', include([
        path('<int:pk>/', FindingItemDetail.as_view(), name='api-finding-item-detail'),
        path('', FindingItemList.as_view(), name='api-finding-item-list'),
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
        path('send/', POMailSend.as_view(), name='api-po-mail-send'),
        path('orders/', POMailOrderList.as_view(), name='api-po-mail-order-list'),
        path('order/<int:pk>/', POMailOrderDetail.as_view(), name='api-po-mail-order'),
        path('<int:pk>/', POMailDetail.as_view(), name='api-po-mail-detail'),
        path('', POMailList.as_view(), name='api-po-mail-list'),
    ])),
]