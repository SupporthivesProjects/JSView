"""Picture Presentation report (reuses costcard picture presentation logic)."""

from costcard.api import CostCardPicturePresentation  # adjust to the module holding your costcard views
from jsreport.permissions import JSReportPermission  # adjust to where JSReportPermission lives
from users.ruleset import RuleSetEnum


class PicturePresentationReportView(CostCardPicturePresentation):
    """Same data/export as costcard picture-presentation, guarded by report permission."""

    # permission_classes = [CostCardPermission]  # old (inherited)
    permission_classes = [JSReportPermission]
    report_role = RuleSetEnum.REPORT_PICTURE_PRESENTATION