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
import { colorStoneShapeFields } from "../../forms/CommonForms";
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
export default function ColorStoneShapeTable() {
  const table = useTable("stone-shape");

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
  const newStoneShape = useCreateApiFormModal({
    url: ApiEndpoints.color_stone_shape_list,
    title: t`Add Stone Shape`,
    fields: colorStoneShapeFields(),
    table: table,
    onFormSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stone-shape-lookup"] });
    },
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedStoneShape, setSelectedStoneShape] = useState<
    number | undefined
  >(undefined);

  const editStoneShape = useEditApiFormModal({
    url: ApiEndpoints.color_stone_shape_list,
    pk: selectedStoneShape,
    title: t`Edit Stone Shape`,
    fields: colorStoneShapeFields(),
    table: table,
    onFormSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["stone-shape-lookup"] });
    },
  });

  const deleteStoneShape = useDeleteApiFormModal({
    url: ApiEndpoints.color_stone_shape_list,
    pk: selectedStoneShape,
    title: t`Delete Stone Shape`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneShape(record.pk);
            editStoneShape.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneShape(record.pk);
            deleteStoneShape.open();
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
        description: t`Show active stone shapes`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-stone-shape"
        onClick={() => newStoneShape.open()}
        tooltip={t`Add Stone Shape`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newStoneShape.modal}
      {editStoneShape.modal}
      {deleteStoneShape.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.color_stone_shape_list)}
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
