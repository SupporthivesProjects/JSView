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
import { colorStoneCutFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";
import { useQueryClient } from "@tanstack/react-query";

/**
 * Table for displaying, creating, editing and deleting Metal Type records
 */
export default function ColorStoneCutTable() {
  const table = useTable("stone-cuts");

  const user = useUserState();
  const queryClient = useQueryClient();

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "name",
        sortable: true,
        switchable: false,
      },
      DescriptionColumn({}),
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
  }, []);

  // --- Create modal ----------------------------------------------------
  const newStoneCutType = useCreateApiFormModal({
    url: ApiEndpoints.color_stone_cut_list,
    title: t`Add Stone Cut Type`,
    fields: colorStoneCutFields(),
    table: table,
    onFormSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stone-cut-lookup"] });
    },
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedStoneCutType, setSelectedStoneCutType] = useState<
    number | undefined
  >(undefined);

  const editStoneCutType = useEditApiFormModal({
    url: ApiEndpoints.color_stone_cut_list,
    pk: selectedStoneCutType,
    title: t`Edit Stone Cut Type`,
    fields: colorStoneCutFields(),
    table: table,
    onFormSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stone-cut-lookup"] });
    },
  });

  const deleteStoneCutType = useDeleteApiFormModal({
    url: ApiEndpoints.color_stone_cut_list,
    pk: selectedStoneCutType,
    title: t`Delete Stone Cut Type`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneCutType(record.pk);
            editStoneCutType.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneCutType(record.pk);
            deleteStoneCutType.open();
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
        description: t`Show active stone types`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-stone-cut"
        onClick={() => newStoneCutType.open()}
        tooltip={t`Add Stone Cut Type`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newStoneCutType.modal}
      {editStoneCutType.modal}
      {deleteStoneCutType.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.color_stone_cut_list)}
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
