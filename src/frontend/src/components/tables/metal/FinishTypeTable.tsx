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
import { finishTypeFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

export default function FinishTypeTable() {
  const table = useTable("finish-type");
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
  const newFinishType = useCreateApiFormModal({
    url: ApiEndpoints.finish_type,
    title: t`Add Finish Type`,
    fields: finishTypeFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedFinishQuery, setSelectedFinishQuery] = useState<
    number | undefined
  >(undefined);

  const editFinishType = useEditApiFormModal({
    url: ApiEndpoints.finish_type,
    pk: selectedFinishQuery,
    title: t`Edit Finish Type`,
    fields: finishTypeFields(),
    table: table,
  });

  const deleteFinishType = useDeleteApiFormModal({
    url: ApiEndpoints.finish_type,
    pk: selectedFinishQuery,
    title: t`Delete Finish Type`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedFinishQuery(record.pk);
            editFinishType.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedFinishQuery(record.pk);
            deleteFinishType.open();
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
        description: t`Show active finish type`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-finish-type"
        onClick={() => newFinishType.open()}
        tooltip={t`Add Finish Type`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newFinishType.modal}
      {editFinishType.modal}
      {deleteFinishType.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.finish_type)}
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
