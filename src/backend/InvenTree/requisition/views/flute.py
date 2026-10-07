"""Flute entry API views for the 'requisition' app."""

from django.db import transaction
from django.db.models import Prefetch
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from requisition.models import FluteEntry, FluteEntryLine
from requisition.permissions import RequisitionPermission
from requisition.serializers import (
    FluteEntryLineCreateSerializer,
    FluteEntrySerializer,
)
from requisition.views.pagination import RequisitionPagination

HEADER_FIELDS = ('invoice_no', 'flute_date', 'active')


def flute_entry_queryset():
    """Active entries with their active lines prefetched in one query."""

    active_lines = (
        FluteEntryLine.objects
        .filter(active=True)
        .select_related('purchase_order', 'cost_card', 'stone_place')
        .order_by('id')
    )

    return (
        FluteEntry.objects
        .select_related('prepby')
        .prefetch_related(
            Prefetch('lines', queryset=active_lines, to_attr='active_lines')
        )
        .filter(active=True)
    )


def serialize_entry(pk, request):
    """Re-fetch and serialize an entry so its lines are always fresh."""

    entry = flute_entry_queryset().get(pk=pk)

    return FluteEntrySerializer(
        entry,
        context={'request': request},
    ).data


def parse_lines(raw_lines, *, required=True):
    """Validate the basic shape of the 'lines' payload."""

    if raw_lines is None and not required:
        return None

    if not isinstance(raw_lines, list):
        raise ValidationError({'lines': 'lines must be a list.'})

    if not raw_lines:
        raise ValidationError({'lines': 'At least one line is required.'})

    return raw_lines


def create_lines(flute_entry, raw_lines, request):
    """Validate every line first, then create them.

    Errors are reported per line index. Because callers run inside
    transaction.atomic, raising here rolls back the header as well.
    """

    validated = []
    errors = []

    for line_data in raw_lines:
        if not isinstance(line_data, dict):
            errors.append({
                'non_field_errors': ['Each line must be an object.']
            })
            continue

        # flute_entry is always assigned by the backend, never the client.
        serializer = FluteEntryLineCreateSerializer(
            data={
                **line_data,
                'flute_entry': flute_entry.pk,
            },
            context={'request': request},
        )

        if serializer.is_valid():
            validated.append(serializer)
            errors.append({})
        else:
            errors.append(serializer.errors)

    if any(errors):
        raise ValidationError({'lines': errors})

    for serializer in validated:
        serializer.save()


class FluteEntryList(APIView):
    """List and create Flute Entry records."""

    queryset = FluteEntry.objects.none()
    permission_classes = [RequisitionPermission]

    def get(self, request, *args, **kwargs):
        """Return a paginated list of active flute entries."""

        entries = flute_entry_queryset().order_by(
            '-flute_date',
            '-id',
        )

        search = request.query_params.get('search', '').strip()

        if search:
            entries = entries.filter(
                invoice_no__icontains=search
            )

        paginator = RequisitionPagination()
        page = paginator.paginate_queryset(entries, request)

        serializer = FluteEntrySerializer(
            page,
            many=True,
            context={'request': request},
        )

        return paginator.get_paginated_response(serializer.data)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """Create a Flute Entry with multiple lines."""

        lines = parse_lines(
            request.data.get('lines')
        )

        header_data = {
            key: request.data[key]
            for key in HEADER_FIELDS
            if key in request.data
        }

        header = FluteEntrySerializer(
            data=header_data,
            context={'request': request},
        )

        header.is_valid(raise_exception=True)

        flute_entry = header.save(
            prepby=(
                request.user
                if request.user.is_authenticated
                else None
            )
        )

        create_lines(
            flute_entry,
            lines,
            request,
        )

        return Response(
            serialize_entry(
                flute_entry.pk,
                request,
            ),
            status=201,
        )


class FluteEntryLineDetail(APIView):
    """Retrieve, update, or delete a particular Flute Entry line."""

    queryset = FluteEntryLine.objects.none()
    permission_classes = [RequisitionPermission]

    def get_object(self, flute_entry_id, line_id):
        """Return an active line belonging to the specified Flute Entry."""

        try:
            return FluteEntryLine.objects.get(
                pk=line_id,
                flute_entry_id=flute_entry_id,
                active=True,
            )
        except FluteEntryLine.DoesNotExist:
            raise NotFound(
                'Flute entry line not found.'
            )

    def get(
        self,
        request,
        flute_entry_id,
        line_id,
        *args,
        **kwargs,
    ):
        """Return a particular Flute Entry line."""

        line = self.get_object(
            flute_entry_id,
            line_id,
        )

        serializer = FluteEntryLineCreateSerializer(
            line,
            context={'request': request},
        )

        return Response(serializer.data)

    @transaction.atomic
    def patch(
        self,
        request,
        flute_entry_id,
        line_id,
        *args,
        **kwargs,
    ):
        """Update a particular Flute Entry line."""

        # Make sure the parent Flute Entry exists and is active.
        try:
            flute_entry_queryset().get(pk=flute_entry_id)
        except FluteEntry.DoesNotExist:
            raise NotFound(
                'Flute entry not found.'
            )

        line = self.get_object(
            flute_entry_id,
            line_id,
        )

        serializer = FluteEntryLineCreateSerializer(
            line,
            data=request.data,
            partial=True,
            context={'request': request},
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            serialize_entry(
                flute_entry_id,
                request,
            )
        )

    @transaction.atomic
    def delete(
        self,
        request,
        flute_entry_id,
        line_id,
        *args,
        **kwargs,
    ):
        """Soft-delete a particular Flute Entry line."""

        line = self.get_object(
            flute_entry_id,
            line_id,
        )

        line.active = False
        line.save(
            update_fields=[
                'active',
                'updated_at',
            ]
        )

        return Response(status=204)


class FluteEntryDetail(APIView):
    """Retrieve, update, or delete a Flute Entry."""

    queryset = FluteEntry.objects.none()
    permission_classes = [RequisitionPermission]

    def get_object(self, pk):
        """Return the requested active flute entry or raise 404."""

        try:
            return flute_entry_queryset().get(pk=pk)
        except FluteEntry.DoesNotExist:
            raise NotFound(
                'Flute entry not found.'
            )

    def get(self, request, pk, *args, **kwargs):
        """Return a single flute entry."""

        entry = self.get_object(pk)

        return Response(
            FluteEntrySerializer(
                entry,
                context={'request': request},
            ).data
        )

    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        """Update a Flute Entry and optionally add multiple lines."""

        return self._update(
            request,
            pk,
            partial=False,
        )

    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """Partially update a Flute Entry and optionally add lines."""

        return self._update(
            request,
            pk,
            partial=True,
        )

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """Soft-delete a Flute Entry and its lines."""

        flute_entry = self.get_object(pk)

        flute_entry.active = False
        flute_entry.save(
            update_fields=[
                'active',
                'updated_at',
            ]
        )

        flute_entry.lines.update(
            active=False
        )

        return Response(status=204)

    def _update(self, request, pk, partial=False):
        """Update the header and append any new lines.

        Existing lines are NOT deactivated or modified.
        """

        flute_entry = self.get_object(pk)

        lines = parse_lines(
            request.data.get('lines'),
            required=False,
        )

        header_data = {
            key: request.data[key]
            for key in HEADER_FIELDS
            if key in request.data
        }

        header = FluteEntrySerializer(
            flute_entry,
            data=header_data,
            partial=partial,
            context={'request': request},
        )

        header.is_valid(
            raise_exception=True
        )

        header.save()

        if lines is not None:
            create_lines(
                flute_entry,
                lines,
                request,
            )

        return Response(
            serialize_entry(
                flute_entry.pk,
                request,
            )
        )