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
import { stoneTypeFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

/**
 * Table for displaying, creating, editing and deleting Metal Type records
 */
export default function ColorStoneTable() {
  const table = useTable("stone-types");

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
  const newStoneType = useCreateApiFormModal({
    url: ApiEndpoints.color_stone_type_list,
    title: t`Add Stone Type`,
    fields: stoneTypeFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedStoneType, setSelectedStoneType] = useState<
    number | undefined
  >(undefined);

  const editStoneType = useEditApiFormModal({
    url: ApiEndpoints.color_stone_type_list,
    pk: selectedStoneType,
    title: t`Edit Stone Type`,
    fields: stoneTypeFields(),
    table: table,
  });

  const deleteStoneType = useDeleteApiFormModal({
    url: ApiEndpoints.color_stone_type_list,
    pk: selectedStoneType,
    title: t`Delete Stone Type`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneType(record.pk);
            editStoneType.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneType(record.pk);
            deleteStoneType.open();
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
        key="add-stone-type"
        onClick={() => newStoneType.open()}
        tooltip={t`Add Stone Type`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newStoneType.modal}
      {editStoneType.modal}
      {deleteStoneType.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.color_stone_type_list)}
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
