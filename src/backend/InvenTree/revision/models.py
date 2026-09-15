from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class RevisionFieldsMixin(models.Model):
    """Common fields for revision tables."""

    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='%(class)s_created', verbose_name=_('Created By'), help_text=_('User who created this revision.'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'), help_text=_('Date and time when this revision was created.'))
    active = models.BooleanField(default=True, verbose_name=_('Active'), help_text=_('Whether this revision is currently active.'))

    class Meta:
        abstract = True


class CostCardVersion(RevisionFieldsMixin):
    """Historical version of a cost card."""

    cost_card = models.ForeignKey('costcard.CostCard', on_delete=models.CASCADE, related_name='versions', verbose_name=_('Cost Card'), help_text=_('Cost card associated with this version.'))
    version = models.PositiveIntegerField(verbose_name=_('Version'), help_text=_('Sequential version number of the cost card.'))
    data = models.JSONField(verbose_name=_('Data'), help_text=_('Complete snapshot of the cost card and its related data.'))

    class Meta:
        verbose_name = _('Cost Card Version')
        verbose_name_plural = _('Cost Card Versions')
        ordering = ['-version']
        constraints = [
            models.UniqueConstraint(fields=['cost_card', 'version'], name='unique_cost_card_version'),
        ]
        indexes = [
            models.Index(fields=['cost_card']),
            models.Index(fields=['version']),
            models.Index(fields=['active']),
        ]

    def __str__(self):
        return f'{self.cost_card} - V{self.version}'