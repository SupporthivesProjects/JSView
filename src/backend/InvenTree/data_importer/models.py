"""Model definitions for the data_importer app."""

from typing import Optional

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


class DataImportSession(models.Model):
    """Tracks a single data import session (upload -> map -> validate -> save)."""

    class ImportStatus(models.IntegerChoices):
        INITIAL = 0, _('Initial')
        MAPPING = 10, _('Mapping Columns')
        IMPORTING = 20, _('Importing')
        COMPLETE = 30, _('Complete')
        FAILED = 40, _('Failed')

    created = models.DateField(auto_now_add=True, editable=False)

    user = models.ForeignKey(
        User, on_delete=models.SET_NULL, blank=True, null=True, related_name='+'
    )

    status = models.PositiveIntegerField(
        choices=ImportStatus.choices, default=ImportStatus.INITIAL
    )

    data_file = models.FileField(upload_to='data_import', blank=True, null=True)

    columns = models.JSONField(blank=True, null=True)

    field_mapping = models.JSONField(blank=True, null=True)

    row_count = models.PositiveIntegerField(default=0)

    completed_count = models.PositiveIntegerField(default=0)

    progress = models.PositiveIntegerField(default=0)

    plugin = models.CharField(max_length=100, blank=True, null=True)

    errors = models.JSONField(blank=True, null=True)

    def mark_importing(self):
        """Mark session as actively importing."""
        self.status = self.ImportStatus.IMPORTING
        self.save()

    def mark_complete(self, with_errors: bool = False):
        """Mark session as complete."""
        self.status = self.ImportStatus.COMPLETE
        self.progress = 100
        self.save()

    def mark_failure(
        self, error: Optional[str] = None, error_dict: Optional[dict] = None
    ):
        """Mark session as failed, logging the error."""
        self.status = self.ImportStatus.FAILED
        self.errors = error_dict or {'error': str(error or _('An error occurred'))}
        self.save()