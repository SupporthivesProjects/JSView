import { t } from "@lingui/core/macro";
import { useCallback, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

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
import { BooleanColumn, DecimalColumn, DescriptionColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { masterExecutive } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

export default function MasterExecutiveTable() {
  const table = useTable("master-executive");

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
        accessor: "code",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "email",
        sortable: true,
        switchable: false,
      },
      {
        accessor: "phone",
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
  }, []);

  // --- Create modal ----------------------------------------------------
  const newMasterExecutive = useCreateApiFormModal({
    url: ApiEndpoints.master_executive,
    title: t`Add Master Executive`,
    fields: masterExecutive(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedExecutive, setSelectedExecutive] = useState<
    number | undefined
  >(undefined);

  const editMasterExecutive = useEditApiFormModal({
    url: ApiEndpoints.master_executive,
    pk: selectedExecutive,
    title: t`Edit Master Executive`,
    fields: masterExecutive(),
    table: table,
  });

  const deleteMasterExecutive = useDeleteApiFormModal({
    url: ApiEndpoints.master_executive,
    pk: selectedExecutive,
    title: t`Delete Master Executive`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedExecutive(record.pk);
            editMasterExecutive.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedExecutive(record.pk);
            deleteMasterExecutive.open();
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
        description: t`Show active master executive`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-master-executive"
        onClick={() => newMasterExecutive.open()}
        tooltip={t`Add Master Executive`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newMasterExecutive.modal}
      {editMasterExecutive.modal}
      {deleteMasterExecutive.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.master_executive)}
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
