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
import { colorStoneSizeFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

/**
 * Table for displaying, creating, editing and deleting Metal Type records
 */
export default function ColorStoneSizeTable() {
  const table = useTable("stone-size");

  const user = useUserState();

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "name",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "mm_size",
        title: t`Size in mm`,
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
  const newStoneSize = useCreateApiFormModal({
    url: ApiEndpoints.color_stone_size_list,
    title: t`Add Stone Size`,
    fields: colorStoneSizeFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedStoneSize, setSelectedStoneSize] = useState<
    number | undefined
  >(undefined);

  const editStoneSize = useEditApiFormModal({
    url: ApiEndpoints.color_stone_size_list,
    pk: selectedStoneSize,
    title: t`Edit Stone Size`,
    fields: colorStoneSizeFields(),
    table: table,
  });

  const deleteStoneSize = useDeleteApiFormModal({
    url: ApiEndpoints.color_stone_size_list,
    pk: selectedStoneSize,
    title: t`Delete Stone Size`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneSize(record.pk);
            editStoneSize.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneSize(record.pk);
            deleteStoneSize.open();
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
        description: t`Show active stone sizes`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-stone-size"
        onClick={() => newStoneSize.open()}
        tooltip={t`Add Stone Size`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newStoneSize.modal}
      {editStoneSize.modal}
      {deleteStoneSize.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.color_stone_size_list)}
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
