"""Admin class definitions for the 'jsreport' app."""

from django.contrib import admin

from jsreport import models


class ReportPermissionAdmin(admin.ModelAdmin):
    """Base admin for permission-only report models (no database table)."""

    def get_model_perms(self, request):
        """Hide from the admin index."""
        return {}

    def has_view_permission(self, request, obj=None):
        """No table, so nothing to view."""
        return False

    def has_add_permission(self, request):
        """No table, so nothing to add."""
        return False

    def has_change_permission(self, request, obj=None):
        """No table, so nothing to change."""
        return False

    def has_delete_permission(self, request, obj=None):
        """No table, so nothing to delete."""
        return False


@admin.register(models.OpenOrderReport)
class OpenOrderReportAdmin(ReportPermissionAdmin):
    """Admin class for the OpenOrderReport model."""


@admin.register(models.CloseOrderReport)
class CloseOrderReportAdmin(ReportPermissionAdmin):
    """Admin class for the CloseOrderReport model."""


@admin.register(models.InvoiceValueReport)
class InvoiceValueReportAdmin(ReportPermissionAdmin):
    """Admin class for the InvoiceValueReport model."""


@admin.register(models.POStoneValuationReport)
class POStoneValuationReportAdmin(ReportPermissionAdmin):
    """Admin class for the POStoneValuationReport model."""


@admin.register(models.POStoneStatusReport)
class POStoneStatusReportAdmin(ReportPermissionAdmin):
    """Admin class for the POStoneStatusReport model."""


@admin.register(models.POStatusReport)
class POStatusReportAdmin(ReportPermissionAdmin):
    """Admin class for the POStatusReport model."""


@admin.register(models.BalanceDiaVendorReport)
class BalanceDiaVendorReportAdmin(ReportPermissionAdmin):
    """Admin class for the BalanceDiaVendorReport model."""


@admin.register(models.CostCardExportReport)
class CostCardExportReportAdmin(ReportPermissionAdmin):
    """Admin class for the CostCardExportReport model."""


@admin.register(models.PicturePresentationReport)
class PicturePresentationReportAdmin(ReportPermissionAdmin):
    """Admin class for the PicturePresentationReport model."""