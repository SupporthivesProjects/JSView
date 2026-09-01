import { t } from "@lingui/core/macro";
import {
  ActionIcon,
  LoadingOverlay,
  Paper,
  Stack,
  Tabs,
  Tooltip,
} from "@mantine/core";
import {
  IconArrowLeft,
  IconBrush,
  IconCoin,
  IconDiamond,
  IconId,
  IconMessage,
  IconPalette,
  IconPhoto,
  IconTools,
} from "@tabler/icons-react";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { UserRoles } from "@lib/enums/Roles";
import { apiUrl } from "@lib/functions/Api";
import PermissionDenied from "@components/shared/errors/PermissionDenied";
import { PageDetail } from "@components/nav/PageDetail";
import { CreateApiForm, EditApiForm } from "@components/forms/ApiForm";
import {
  costCardCostFields,
  costCardGeneralFields,
  costCardLabourFields,
  costCardRemarksFields,
} from "@components/forms/CommonForms";
import CostCardFinishLineTable from "@components/tables/cost-card/CostCardFinishLineTable";
import CostCardDiamondLineTable from "@components/tables/cost-card/CostCardDiamondLineTable";
import CostCardColorStoneLineTable from "@components/tables/cost-card/CostCardColorStoneLineTable";
import CostCardImagesPanel from "@components/tables/cost-card/CostCardImagesPanel";
import { useApi } from "@context/ApiContext";
import { useUserState } from "@store/UserState";

const DETAIL_QUERY_KEY = "cost-card-detail-instance";

// General/Cost/Labour Details forms lay their fields out in a responsive
// grid instead of one long vertical stack.
const FORM_GRID_COLUMNS = { base: 1, sm: 2, lg: 3 };

/**
 * Cost Card create/edit view — rendered in the same "Cost Card" page as the
 * table (same title, same Paper container), with a horizontal row of tabs
 * (General / Finish Type / Diamond / Color Stone / Labour Details / Images /
 * Cost / Remarks) instead of a separate detail page.
 *
 * While creating a new cost card, only the General tab is available - the
 * remaining tabs need a real primary key to attach lines and images to.
 * Saving the General tab creates the record and this view then behaves as
 * the edit view for it.
 */
export default function CostCardDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const api = useApi();
  const queryClient = useQueryClient();
  const user = useUserState();

  const isNew = !id || id === "new";
  const costCardId = isNew ? undefined : Number(id);

  const [activeTab, setActiveTab] = useState<string>("general");

  const instanceQuery = useQuery({
    enabled: !isNew,
    queryKey: [DETAIL_QUERY_KEY, costCardId],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.cost_card, costCardId))
        .then((response) => response.data),
  });

  const instance = instanceQuery.data;

  const setInstanceData = (data: any) => {
    queryClient.setQueryData([DETAIL_QUERY_KEY, costCardId], data);
  };

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack pos="relative">
      <PageDetail
        title={t`Cost Card`}
        subtitle={
          isNew ? t`New` : (instance?.cost_card_no ?? instance?.our_style_no)
        }
        actions={[
          <Tooltip label={t`Back to Cost Cards`} key="back">
            <ActionIcon
              variant="subtle"
              onClick={() => navigate("/cards/cost-card/")}
            >
              <IconArrowLeft />
            </ActionIcon>
          </Tooltip>,
        ]}
      />
      <Paper p="sm" radius="xs" shadow="xs" pos="relative">
        <LoadingOverlay visible={!isNew && instanceQuery.isLoading} />
        <Tabs value={activeTab} onChange={(value) => value && setActiveTab(value)}>
          <Tabs.List>
            <Tabs.Tab value="general" leftSection={<IconId size={16} />}>
              {t`General`}
            </Tabs.Tab>
            <Tabs.Tab
              value="finish-type"
              leftSection={<IconBrush size={16} />}
              disabled={isNew}
            >
              {t`Finish Type`}
            </Tabs.Tab>
            <Tabs.Tab
              value="diamond"
              leftSection={<IconDiamond size={16} />}
              disabled={isNew}
            >
              {t`Diamond`}
            </Tabs.Tab>
            <Tabs.Tab
              value="color-stone"
              leftSection={<IconPalette size={16} />}
              disabled={isNew}
            >
              {t`Color Stone`}
            </Tabs.Tab>
            <Tabs.Tab
              value="labour-details"
              leftSection={<IconTools size={16} />}
              disabled={isNew}
            >
              {t`Labour Details`}
            </Tabs.Tab>
            <Tabs.Tab
              value="images"
              leftSection={<IconPhoto size={16} />}
              disabled={isNew}
            >
              {t`Images`}
            </Tabs.Tab>
            <Tabs.Tab
              value="cost"
              leftSection={<IconCoin size={16} />}
              disabled={isNew}
            >
              {t`Cost`}
            </Tabs.Tab>
            <Tabs.Tab
              value="remarks"
              leftSection={<IconMessage size={16} />}
              disabled={isNew}
            >
              {t`Remarks`}
            </Tabs.Tab>
          </Tabs.List>

          <Tabs.Panel value="general" p="sm">
            {isNew ? (
              <CreateApiForm
                props={{
                  url: ApiEndpoints.cost_card,
                  fields: costCardGeneralFields(),
                  submitText: t`Create`,
                  gridColumns: FORM_GRID_COLUMNS,
                  onFormSuccess: (data: any) => {
                    navigate(`/cards/cost-card/${data.pk}`);
                  },
                }}
              />
            ) : (
              <EditApiForm
                props={{
                  url: ApiEndpoints.cost_card,
                  pk: costCardId,
                  fields: costCardGeneralFields(),
                  submitText: t`Save`,
                  gridColumns: FORM_GRID_COLUMNS,
                  onFormSuccess: (data: any) => setInstanceData(data),
                }}
              />
            )}
          </Tabs.Panel>

          <Tabs.Panel value="finish-type" p="sm">
            {costCardId && <CostCardFinishLineTable costCardId={costCardId} />}
          </Tabs.Panel>

          <Tabs.Panel value="diamond" p="sm">
            {costCardId && <CostCardDiamondLineTable costCardId={costCardId} />}
          </Tabs.Panel>

          <Tabs.Panel value="color-stone" p="sm">
            {costCardId && (
              <CostCardColorStoneLineTable costCardId={costCardId} />
            )}
          </Tabs.Panel>

          <Tabs.Panel value="labour-details" p="sm">
            {costCardId && (
              <EditApiForm
                props={{
                  url: ApiEndpoints.cost_card,
                  pk: costCardId,
                  fields: costCardLabourFields(),
                  submitText: t`Save`,
                  gridColumns: FORM_GRID_COLUMNS,
                  onFormSuccess: (data: any) => setInstanceData(data),
                }}
              />
            )}
          </Tabs.Panel>

          <Tabs.Panel value="images" p="sm">
            {costCardId && (
              <CostCardImagesPanel
                costCardId={costCardId}
                instance={instance}
                onUpdated={setInstanceData}
              />
            )}
          </Tabs.Panel>

          <Tabs.Panel value="cost" p="sm">
            {costCardId && (
              <EditApiForm
                props={{
                  url: ApiEndpoints.cost_card,
                  pk: costCardId,
                  fields: costCardCostFields(),
                  submitText: t`Save`,
                  gridColumns: FORM_GRID_COLUMNS,
                  onFormSuccess: (data: any) => setInstanceData(data),
                }}
              />
            )}
          </Tabs.Panel>

          <Tabs.Panel value="remarks" p="sm">
            {costCardId && (
              <EditApiForm
                props={{
                  url: ApiEndpoints.cost_card,
                  pk: costCardId,
                  fields: costCardRemarksFields(),
                  submitText: t`Save`,
                  onFormSuccess: (data: any) => setInstanceData(data),
                }}
              />
            )}
          </Tabs.Panel>
        </Tabs>
      </Paper>
    </Stack>
  );
}
