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
import type { TableFilter } from "@lib/index";
import type { TableColumn } from "@lib/types/Tables";
import { BooleanColumn, DescriptionColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { colorStoneRateFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useApi } from "@context/ApiContext";
import { useUserState } from "@store/UserState";
import { useQuery } from "@tanstack/react-query";
import { useStoneColorLookup, useStoneCutLookup, useStoneQualityLookup, useStoneShapeLookup, useStoneSizeLookup, useStoneStoneLookup } from "./sharedFunctions/LookupFunctions";

/**
 * Table for displaying, creating, editing and deleting Metal Type records
 */
export default function ColorStoneRateTable() {
  const table = useTable("stone-rate");

  const user = useUserState();

  const { stoneShapeNameByPk } = useStoneShapeLookup();
  const { stoneSizeNameByPk } = useStoneSizeLookup();
  const { stoneStoneNameByPk } = useStoneStoneLookup();
  const { stoneColorNameByPk } = useStoneColorLookup();
  const { stoneCutNameByPk } = useStoneCutLookup();
  const { stoneQualityNameByPk } = useStoneQualityLookup();

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "shape",
        sortable: true,
        switchable: false,
        render: (record: any) =>
          stoneShapeNameByPk[record.shape] ?? record.shape,
      },
      {
        accessor: "mm_size",
        title: t`Size in mm`,
        sortable: true,
        switchable: false,
        render: (record: any) =>
          stoneSizeNameByPk[record.mm_size] ?? record.mm_size,
      },
      {
        accessor: "stone",
        sortable: true,
        switchable: false,
        render: (record: any) =>
          stoneStoneNameByPk[record.stone] ?? record.stone,
      },
      {
        accessor: "color",
        sortable: true,
        switchable: false,
        render: (record: any) => stoneColorNameByPk[record.color] ?? record.color,
      },
      {
        accessor: "cut",
        sortable: true,
        switchable: false,
        render: (record: any) => stoneCutNameByPk[record.cut] ?? record.cut,
      },
      {
        accessor: "quality",
        sortable: true,
        switchable: false,
        render: (record: any) => stoneQualityNameByPk[record.quality] ?? record.quality,
      },
      {
        accessor: "pointer",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "rate",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "pc",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "customer_id",
        sortable: true,
        switchable: false,
      },
      BooleanColumn({
        accessor: "active",
      }),
      {
        accessor: "created_at",
        title: t`Created`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "updated_at",
        title: t`Updated`,
        sortable: true,
        switchable: true,
      },
    ];
  }, [stoneShapeNameByPk, stoneSizeNameByPk, stoneStoneNameByPk, stoneColorNameByPk, stoneCutNameByPk, stoneQualityNameByPk]);

  // --- Create modal ----------------------------------------------------
  const newStoneRate = useCreateApiFormModal({
    url: ApiEndpoints.color_stone_rate_list,
    title: t`Add Stone Rate`,
    fields: colorStoneRateFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedStoneRate, setSelectedStoneRate] = useState<
    number | undefined
  >(undefined);

  const editStoneRate = useEditApiFormModal({
    url: ApiEndpoints.color_stone_rate_list,
    pk: selectedStoneRate,
    title: t`Edit Stone Rate`,
    fields: colorStoneRateFields(),
    table: table,
  });

  const deleteStoneRate = useDeleteApiFormModal({
    url: ApiEndpoints.color_stone_rate_list,
    pk: selectedStoneRate,
    title: t`Delete Stone Rate`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneRate(record.pk);
            editStoneRate.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneRate(record.pk);
            deleteStoneRate.open();
          },
        }),
      ];
    },
    [user],
  );

  // --- Table-level filters ----------------------------------------------
  const tableFilters: TableFilter[] = useMemo(() => {
    return [
      {
        name: "active",
        label: t`Active`,
        description: t`Show active stone qualities`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-stone-rate"
        onClick={() => newStoneRate.open()}
        tooltip={t`Add Stone Rate`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newStoneRate.modal}
      {editStoneRate.modal}
      {deleteStoneRate.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.color_stone_rate_list)}
        tableState={table}
        columns={columns}
        props={{
          rowActions: rowActions,
          tableActions: tableActions,
          tableFilters: tableFilters,
          enableDownload: true,
        }}
      />
    </>
  );
}
