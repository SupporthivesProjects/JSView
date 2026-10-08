"""Permission-only models for JS Reports (no database tables)."""

from django.db import models


class ReportPermissionBase(models.Model):
    """Base for report permission models. Has no table."""

    class Meta:
        abstract = True
        managed = False


class OpenOrderReport(ReportPermissionBase):
    """Permission model for the Open Order report."""

    class Meta(ReportPermissionBase.Meta):
        abstract = False
        verbose_name = 'Open Order Report'


class CloseOrderReport(ReportPermissionBase):
    """Permission model for the Close Order report."""

    class Meta(ReportPermissionBase.Meta):
        abstract = False
        verbose_name = 'Close Order Report'


class InvoiceValueReport(ReportPermissionBase):
    """Permission model for the Invoice Value P/C report."""

    class Meta(ReportPermissionBase.Meta):
        abstract = False
        verbose_name = 'Invoice Value Report'


class PicturePresentationReport(ReportPermissionBase):
    """Permission model for the Picture Presentation report."""

    class Meta(ReportPermissionBase.Meta):
        abstract = False
        verbose_name = 'Picture Presentation Report'
        

class POStoneValuationReport(ReportPermissionBase):
    """Permission model for the P.O. Stone Valuation report."""

    class Meta(ReportPermissionBase.Meta):
        abstract = False
        verbose_name = 'PO Stone Valuation Report'


class POStoneStatusReport(ReportPermissionBase):
    """Permission model for the P.O. Stone Status report."""

    class Meta(ReportPermissionBase.Meta):
        abstract = False
        verbose_name = 'PO Stone Status Report'


class POStatusReport(ReportPermissionBase):
    """Permission model for the P.O. Status report."""

    class Meta(ReportPermissionBase.Meta):
        abstract = False
        verbose_name = 'PO Status Report'


class BalanceDiaVendorReport(ReportPermissionBase):
    """Permission model for the Balance Dia. With Vendor report."""

    class Meta(ReportPermissionBase.Meta):
        abstract = False
        verbose_name = 'Balance Dia With Vendor Report'


class CostCardExportReport(ReportPermissionBase):
    """Permission model for the Cost Card Export report."""

    class Meta(ReportPermissionBase.Meta):
        abstract = False
        verbose_name = 'Cost Card Export Report'