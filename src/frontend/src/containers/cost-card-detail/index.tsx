import { t } from "@lingui/core/macro";
import {
  ActionIcon,
  LoadingOverlay,
  Paper,
  Stack,
  Tabs,
  Text,
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
import { notifications } from "@mantine/notifications";
import { useEffect, useMemo, useRef, useState } from "react";
import { useNavigate, useParams, useSearchParams } from "react-router-dom";
import { useQuery, useQueryClient } from "@tanstack/react-query";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { UserRoles } from "@lib/enums/Roles";
import { apiUrl } from "@lib/functions/Api";
import { generateUrl } from "@helpers/urls";
import PermissionDenied from "@components/shared/errors/PermissionDenied";
import { PageDetail } from "@components/nav/PageDetail";
import {
  CreateApiForm,
  EditApiForm,
  PatchApiForm,
} from "@components/forms/ApiForm";
import {
  COST_CARD_FORM_GRID_COLUMNS,
  costCardCostFields,
  costCardRemarksFields,
  useCostCardGeneralFields,
  useCostCardLabourFields,
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
const FORM_GRID_COLUMNS = COST_CARD_FORM_GRID_COLUMNS;

// The page itself must not scroll: the tab strip and the form's Save button
// stay put and only the field area scrolls. The subtracted height is the
// chrome above the fields (app header, page title, tab strip, padding) plus
// the chrome below them (button row, footer), with a floor so the field area
// stays usable on a short screen.
const FORM_BODY_MAX_HEIGHT = "clamp(18rem, calc(100vh - 24rem), 100vh)";

// Fields of the source card that are never copied into a duplicate: they are
// either assigned by the server or (for the images) uploaded separately.
const DUPLICATE_EXCLUDED_FIELDS = [
  "pk",
  "cost_card_no",
  "front_view",
  "side_view",
  "back_view",
  "created_at",
  "updated_at",
];

// General tab fields whose value is derived live from another field (via the
// general fields hook) - these are seeded through that hook rather than as
// initial data, since initial data would pin them and stop them following
// later changes to the field they are derived from.
const DUPLICATE_DERIVED_FIELDS = [
  "karat",
  "finding_price",
  "gross_weight",
  "net_weight",
];

const IMAGE_FIELDS = ["front_view", "side_view", "back_view"];

// Line items are re-created on the new card, so their ids must not be sent
function copyLines(lines: any[] | undefined) {
  return (lines ?? []).map(({ id, ...line }: any) => line);
}

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
 *
 * Duplicating a cost card opens this create view with `?duplicate=<pk>`: the
 * General tab is pre-filled from the source card, and nothing is created
 * until it is saved. The new card then also receives the source card's line
 * items, the values from its other tabs, and its images.
 */
export default function CostCardDetail() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const api = useApi();
  const queryClient = useQueryClient();
  const user = useUserState();

  const isNew = !id || id === "new";
  const costCardId = isNew ? undefined : Number(id);

  const duplicateFromId = isNew
    ? Number(searchParams.get("duplicate")) || undefined
    : undefined;

  const [activeTab, setActiveTab] = useState<string>("general");

  const generalFields = useCostCardGeneralFields();
  const labourFields = useCostCardLabourFields(
    costCardId,
    activeTab === "labour-details",
  );

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

  // --- Duplicate -----------------------------------------------------------
  const sourceQuery = useQuery({
    enabled: !!duplicateFromId,
    queryKey: ["cost-card-duplicate-source", duplicateFromId],
    gcTime: 0,
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.cost_card, duplicateFromId))
        .then((response) => response.data),
  });

  const source = duplicateFromId ? sourceQuery.data : undefined;

  // Seed the derived General tab fields once the source card has loaded, the
  // same way the edit view has them populated from the fetched record. The
  // form is only rendered after this, so it never shows them empty.
  const [seededSourceId, setSeededSourceId] = useState<number | undefined>(
    undefined,
  );
  const generalFieldsRef = useRef(generalFields);
  generalFieldsRef.current = generalFields;

  useEffect(() => {
    if (!source || seededSourceId === source.pk) {
      return;
    }

    const fields = generalFieldsRef.current;

    fields.metal_grams?.onValueChange?.(source.metal_grams);
    fields.metal_purity?.onValueChange?.(source.metal_purity, {
      pk: source.metal_purity,
      karat: source.karat,
    });
    fields.finding_item?.onValueChange?.(source.finding_item, {
      price: source.finding_price,
    });

    setSeededSourceId(source.pk);
  }, [source, seededSourceId]);

  const duplicateReady = !!source && seededSourceId === source.pk;

  const duplicateInitialData = useMemo(() => {
    if (!source) {
      return undefined;
    }

    const data: Record<string, any> = { ...source };

    [...DUPLICATE_EXCLUDED_FIELDS, ...DUPLICATE_DERIVED_FIELDS].forEach(
      (field) => delete data[field],
    );

    return data;
  }, [source]);

  // The General tab only submits its own fields - everything else on the
  // source card (other tabs, line items) is carried over alongside them
  const processDuplicateData = (data: any) => {
    const payload: Record<string, any> = { ...source };

    DUPLICATE_EXCLUDED_FIELDS.forEach((field) => delete payload[field]);

    return {
      ...payload,
      diamond_lines: copyLines(source?.diamond_lines),
      colorstone_lines: copyLines(source?.colorstone_lines),
      finish_lines: copyLines(source?.finish_lines),
      ...data,
    };
  };

  // Images are uploaded through their own endpoint, so they are copied
  // across once the new card exists
  const copyImages = async (sourceCard: any, newCardId: number) => {
    const formData = new FormData();
    let imageCount = 0;

    for (const field of IMAGE_FIELDS) {
      const src = sourceCard?.[field];

      if (!src) {
        continue;
      }

      const url = generateUrl(src);
      const response = await api.get(url, { responseType: "blob" });
      const fileName =
        decodeURIComponent(url.split("?")[0].split("/").pop() ?? "") || field;

      formData.append(field, new File([response.data], fileName));
      imageCount++;
    }

    if (imageCount === 0) {
      return;
    }

    const response = await api.patch(
      apiUrl(ApiEndpoints.cost_card_images, newCardId),
      formData,
    );

    queryClient.setQueryData([DETAIL_QUERY_KEY, newCardId], response.data);
  };

  const onDuplicateCreated = (data: any) => {
    const sourceCard = source;

    navigate(`/cards/cost-card/${data.pk}`);

    copyImages(sourceCard, data.pk).catch(() => {
      notifications.show({
        title: t`Warning`,
        message: t`Cost card created, but its images could not be copied`,
        color: "orange",
      });
    });
  };

  if (!user.hasViewRole(UserRoles.part)) {
    return <PermissionDenied />;
  }

  return (
    <Stack pos="relative">
      <PageDetail
        title={t`Cost Card`}
        subtitle={
          duplicateFromId
            ? source
              ? t`Duplicate of ${source.cost_card_no ?? source.our_style_no}`
              : t`Duplicate`
            : isNew
              ? t`New`
              : (instance?.cost_card_no ?? instance?.our_style_no)
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
        <LoadingOverlay
          visible={
            isNew
              ? !!duplicateFromId && !duplicateReady && !sourceQuery.isError
              : instanceQuery.isLoading
          }
        />
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
            {duplicateFromId ? (
              sourceQuery.isError ? (
                <Text c="red">{t`Could not load the cost card to duplicate`}</Text>
              ) : (
                duplicateReady && (
                  <CreateApiForm
                    props={{
                      url: ApiEndpoints.cost_card,
                      fields: generalFields,
                      initialData: duplicateInitialData,
                      submitText: t`Save`,
                      gridColumns: FORM_GRID_COLUMNS,
                      bodyMaxHeight: FORM_BODY_MAX_HEIGHT,
                      processFormData: processDuplicateData,
                      onFormSuccess: onDuplicateCreated,
                    }}
                  />
                )
              )
            ) : isNew ? (
              <CreateApiForm
                props={{
                  url: ApiEndpoints.cost_card,
                  fields: generalFields,
                  submitText: t`Create`,
                  gridColumns: FORM_GRID_COLUMNS,
                  bodyMaxHeight: FORM_BODY_MAX_HEIGHT,
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
                  fields: generalFields,
                  submitText: t`Save`,
                  gridColumns: FORM_GRID_COLUMNS,
                  bodyMaxHeight: FORM_BODY_MAX_HEIGHT,
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
              <PatchApiForm
                props={{
                  url: ApiEndpoints.cost_card,
                  pk: costCardId,
                  fields: labourFields,
                  submitText: t`Save`,
                  gridColumns: FORM_GRID_COLUMNS,
                  bodyMaxHeight: FORM_BODY_MAX_HEIGHT,
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
              <PatchApiForm
                props={{
                  url: ApiEndpoints.cost_card,
                  pk: costCardId,
                  fields: costCardCostFields(),
                  submitText: t`Save`,
                  gridColumns: FORM_GRID_COLUMNS,
                  bodyMaxHeight: FORM_BODY_MAX_HEIGHT,
                  onFormSuccess: (data: any) => setInstanceData(data),
                }}
              />
            )}
          </Tabs.Panel>

          <Tabs.Panel value="remarks" p="sm">
            {costCardId && (
              <PatchApiForm
                props={{
                  url: ApiEndpoints.cost_card,
                  pk: costCardId,
                  fields: costCardRemarksFields(),
                  submitText: t`Save`,
                  bodyMaxHeight: FORM_BODY_MAX_HEIGHT,
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
