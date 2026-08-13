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
import { metalPurityFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

/**
 * Table for displaying, creating, editing and deleting Metal Type records
 */
export default function MetalTypeTable() {
  const table = useTable("metal-types");

  const user = useUserState();

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "code",
        sortable: true,
        switchable: false,
      },
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
  const newMetalType = useCreateApiFormModal({
    url: ApiEndpoints.metal_purity_list,
    title: t`Add Metal Type`,
    fields: metalPurityFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedMetalType, setSelectedMetalType] = useState<
    number | undefined
  >(undefined);

  const editMetalType = useEditApiFormModal({
    url: ApiEndpoints.metal_purity_list,
    pk: selectedMetalType,
    title: t`Edit Metal Type`,
    fields: metalPurityFields(),
    table: table,
  });

  const deleteMetalType = useDeleteApiFormModal({
    url: ApiEndpoints.metal_purity_list,
    pk: selectedMetalType,
    title: t`Delete Metal Type`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedMetalType(record.pk);
            editMetalType.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedMetalType(record.pk);
            deleteMetalType.open();
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
        description: t`Show active metal types`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-metal-type"
        onClick={() => newMetalType.open()}
        tooltip={t`Add Metal Type`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newMetalType.modal}
      {editMetalType.modal}
      {deleteMetalType.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.metal_purity_list)}
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
