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
import { diamondSizeFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

export default function DiamondSizeTable() {
  const table = useTable("diamond-size");
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
  const newDiamondSize = useCreateApiFormModal({
    url: ApiEndpoints.diamond_size_list,
    title: t`Add Diamond Size`,
    fields: diamondSizeFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedDiamondSize, setSelectedDiamondSize] = useState<
    number | undefined
  >(undefined);

  const editDiamondSize = useEditApiFormModal({
    url: ApiEndpoints.diamond_size_list,
    pk: selectedDiamondSize,
    title: t`Edit Diamond Size`,
    fields: diamondSizeFields(),
    table: table,
  });

  const deleteDiamondSize = useDeleteApiFormModal({
    url: ApiEndpoints.diamond_size_list,
    pk: selectedDiamondSize,
    title: t`Delete Diamond Size`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedDiamondSize(record.pk);
            editDiamondSize.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedDiamondSize(record.pk);
            deleteDiamondSize.open();
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
        description: t`Show active diamond size`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-diamond-size"
        onClick={() => newDiamondSize.open()}
        tooltip={t`Add Diamond Size`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newDiamondSize.modal}
      {editDiamondSize.modal}
      {deleteDiamondSize.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.diamond_size_list)}
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
