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
import { colorStoneQualityFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

/**
 * Table for displaying, creating, editing and deleting Metal Type records
 */
export default function ColorStoneQualityTable() {
  const table = useTable("stone-quality");

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
  const newStoneQuality = useCreateApiFormModal({
    url: ApiEndpoints.color_stone_quality_list,
    title: t`Add Stone Quality`,
    fields: colorStoneQualityFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedStoneQuality, setSelectedStoneQuality] = useState<
    number | undefined
  >(undefined);

  const editStoneQuality = useEditApiFormModal({
    url: ApiEndpoints.color_stone_quality_list,
    pk: selectedStoneQuality,
    title: t`Edit Stone Quality`,
    fields: colorStoneQualityFields(),
    table: table,
  });

  const deleteStoneQuality = useDeleteApiFormModal({
    url: ApiEndpoints.color_stone_quality_list,
    pk: selectedStoneQuality,
    title: t`Delete Stone Quality`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneQuality(record.pk);
            editStoneQuality.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedStoneQuality(record.pk);
            deleteStoneQuality.open();
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
        key="add-stone-quality"
        onClick={() => newStoneQuality.open()}
        tooltip={t`Add Stone Quality`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newStoneQuality.modal}
      {editStoneQuality.modal}
      {deleteStoneQuality.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.color_stone_quality_list)}
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
