import { t } from "@lingui/core/macro";
import { useCallback, useMemo, useState } from "react";

import { AddItemButton } from "@lib/components/AddItemButton";
import {
  type RowAction,
  RowDeleteAction,
  RowEditAction,
} from "@lib/components/RowActions";
import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { UserRoles } from "@lib/enums/Roles";
import { apiUrl } from "@lib/functions/Api";
import useTable from "@lib/hooks/UseTable";
import type { TableColumn } from "@lib/types/Tables";
import { InvenTreeTable } from "../InvenTreeTable";
import { costCardColorStoneLineFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import useNameLookup from "../../../hooks/UseNameLookup";
import { useUserState } from "@store/UserState";

/**
 * Color Stone tab — one row per color stone entry on a cost card.
 */
export default function CostCardColorStoneLineTable({
  costCardId,
}: Readonly<{ costCardId: number }>) {
  const table = useTable("cost-card-colorstone-line");
  const user = useUserState();

  const { nameByPk: stoneByPk } = useNameLookup(
    ApiEndpoints.color_stone_type_list,
    "cost-card-colorstone-stone-lookup",
  );
  const { nameByPk: shapeByPk } = useNameLookup(
    ApiEndpoints.color_stone_shape_list,
    "cost-card-colorstone-shape-lookup",
  );
  const { nameByPk: sizeByPk } = useNameLookup(
    ApiEndpoints.color_stone_size_list,
    "cost-card-colorstone-size-lookup",
  );
  const { nameByPk: colorByPk } = useNameLookup(
    ApiEndpoints.color_stone_color_list,
    "cost-card-colorstone-color-lookup",
  );
  const { nameByPk: cutByPk } = useNameLookup(
    ApiEndpoints.color_stone_cut_list,
    "cost-card-colorstone-cut-lookup",
  );
  const { nameByPk: qualityByPk } = useNameLookup(
    ApiEndpoints.color_stone_quality_list,
    "cost-card-colorstone-quality-lookup",
  );
  const { nameByPk: settingByPk } = useNameLookup(
    ApiEndpoints.master_setting,
    "cost-card-colorstone-setting-lookup",
  );
  const { nameByPk: stonePlaceByPk } = useNameLookup(
    ApiEndpoints.stone_place,
    "cost-card-colorstone-stone-place-lookup",
  );

  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "stone",
        title: t`Stone`,
        sortable: false,
        switchable: false,
        render: (record: any) => stoneByPk[record.stone] ?? record.stone,
      },
      {
        accessor: "shape",
        title: t`Shape`,
        sortable: false,
        switchable: false,
        render: (record: any) => shapeByPk[record.shape] ?? record.shape,
      },
      {
        accessor: "mm_size",
        title: t`MM Size`,
        sortable: false,
        switchable: true,
        render: (record: any) => sizeByPk[record.mm_size] ?? record.mm_size,
      },
      {
        accessor: "sieve_size",
        title: t`Sieve Size`,
        sortable: false,
        switchable: true,
      },
      {
        accessor: "color",
        title: t`Color`,
        sortable: false,
        switchable: true,
        render: (record: any) => colorByPk[record.color] ?? record.color,
      },
      {
        accessor: "cut",
        title: t`Cut`,
        sortable: false,
        switchable: true,
        render: (record: any) => cutByPk[record.cut] ?? record.cut,
      },
      {
        accessor: "quality",
        title: t`Quality`,
        sortable: false,
        switchable: true,
        render: (record: any) => qualityByPk[record.quality] ?? record.quality,
      },
      {
        accessor: "pointer",
        title: t`Pointer`,
        sortable: false,
        switchable: true,
      },
      {
        accessor: "pcs",
        title: t`Pcs`,
        sortable: true,
        switchable: false,
      },
      {
        accessor: "cts",
        title: t`Cts`,
        sortable: true,
        switchable: false,
      },
      {
        accessor: "default_rate",
        title: t`D.R.`,
        sortable: false,
        switchable: true,
        render: (record: any) => (record.default_rate ? t`Y` : t`N`),
      },
      {
        accessor: "rate",
        title: t`Rate`,
        sortable: true,
        switchable: false,
      },
      {
        accessor: "pc",
        title: t`P/C`,
        sortable: false,
        switchable: true,
      },
      {
        accessor: "amount",
        title: t`Amount`,
        sortable: true,
        switchable: false,
      },
      {
        accessor: "setting",
        title: t`Setting`,
        sortable: false,
        switchable: true,
        render: (record: any) => settingByPk[record.setting] ?? record.setting,
      },
      {
        accessor: "labour_rate",
        title: t`L.Rate`,
        sortable: false,
        switchable: true,
      },
      {
        accessor: "labour_amount",
        title: t`L.Amount`,
        sortable: false,
        switchable: true,
      },
      {
        accessor: "stone_place",
        title: t`Stone Place`,
        sortable: false,
        switchable: true,
        render: (record: any) =>
          stonePlaceByPk[record.stone_place] ?? record.stone_place,
      },
    ];
  }, [
    stoneByPk,
    shapeByPk,
    sizeByPk,
    colorByPk,
    cutByPk,
    qualityByPk,
    settingByPk,
    stonePlaceByPk,
  ]);

  // --- Create modal ----------------------------------------------------
  const newLine = useCreateApiFormModal({
    url: ApiEndpoints.cost_card_colorstone_line,
    title: t`Add Color Stone Line`,
    fields: costCardColorStoneLineFields(costCardId),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedLine, setSelectedLine] = useState<number | undefined>(
    undefined,
  );

  const editLine = useEditApiFormModal({
    url: ApiEndpoints.cost_card_colorstone_line,
    pk: selectedLine,
    title: t`Edit Color Stone Line`,
    fields: costCardColorStoneLineFields(costCardId),
    table: table,
  });

  const deleteLine = useDeleteApiFormModal({
    url: ApiEndpoints.cost_card_colorstone_line,
    pk: selectedLine,
    title: t`Delete Color Stone Line`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedLine(record.pk);
            editLine.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedLine(record.pk);
            deleteLine.open();
          },
        }),
      ];
    },
    [user],
  );

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-colorstone-line"
        onClick={() => newLine.open()}
        tooltip={t`Add Color Stone Line`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newLine.modal}
      {editLine.modal}
      {deleteLine.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.cost_card_colorstone_line)}
        tableState={table}
        columns={columns}
        props={{
          params: { cost_card: costCardId },
          rowActions: rowActions,
          tableActions: tableActions,
        }}
      />
    </>
  );
}
