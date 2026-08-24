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
import { diamondColorFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

export default function DiamondColorTable() {
  const table = useTable("diamond-color");
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
  const newDiamondColor = useCreateApiFormModal({
    url: ApiEndpoints.diamond_color_list,
    title: t`Add Diamond Color`,
    fields: diamondColorFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedDiamondColor, setSelectedDiamondColor] = useState<
    number | undefined
  >(undefined);

  const editDiamondColor = useEditApiFormModal({
    url: ApiEndpoints.diamond_color_list,
    pk: selectedDiamondColor,
    title: t`Edit Diamond Color`,
    fields: diamondColorFields(),
    table: table,
  });

  const deleteDiamondColor = useDeleteApiFormModal({
    url: ApiEndpoints.diamond_color_list,
    pk: selectedDiamondColor,
    title: t`Delete Diamond Color`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedDiamondColor(record.pk);
            editDiamondColor.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedDiamondColor(record.pk);
            deleteDiamondColor.open();
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
        description: t`Show active diamond color`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-diamond-color"
        onClick={() => newDiamondColor.open()}
        tooltip={t`Add Diamond Color`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newDiamondColor.modal}
      {editDiamondColor.modal}
      {deleteDiamondColor.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.diamond_color_list)}
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
