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
import { colorStoneColorFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

/**
 * Table for displaying, creating, editing and deleting Metal Type records
 */
export default function ColorStoneColorTable() {
  const table = useTable("stone-color");

  const user = useUserState();

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
  const newStoneColor = useCreateApiFormModal({
    url: ApiEndpoints.color_stone_color_list,
    title: t`Add Stone Color`,
    fields: colorStoneColorFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedStoneColor, setSelectedStoneColor] = useState<
    number | undefined
  >(undefined);

  const editStoneColor = useEditApiFormModal({
    url: ApiEndpoints.color_stone_color_list,
    pk: selectedStoneColor,
    title: t`Edit Stone Color`,
    fields: colorStoneColorFields(),
    table: table,
  });

  const deleteStoneColor = useDeleteApiFormModal({
    url: ApiEndpoints.color_stone_color_list,
    pk: selectedStoneColor,
    title: t`Delete Stone Color`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneColor(record.pk);
            editStoneColor.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneColor(record.pk);
            deleteStoneColor.open();
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
        description: t`Show active stone colors`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-stone-color"
        onClick={() => newStoneColor.open()}
        tooltip={t`Add Stone Color`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newStoneColor.modal}
      {editStoneColor.modal}
      {deleteStoneColor.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.color_stone_color_list)}
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
