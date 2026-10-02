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
import type { TableColumn } from "@lib/types/Tables";
import { BooleanColumn, DateColumn, UpdatedAtColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import {
  FLUTE_ENTRY_FORM_GRID_COLUMNS,
  FLUTE_ENTRY_MODAL_SIZE,
  fluteEntryFields,
  processFluteEntryData,
  remapFluteEntryLineErrors,
  validateFluteEntryLines,
} from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";

/** Sum one numeric column across the lines of an entry */
function sumLines(record: any, key: string): number {
  return (record?.lines ?? []).reduce((total: number, line: any) => {
    const value = Number.parseFloat(line?.[key]);
    return Number.isFinite(value) ? total + value : total;
  }, 0);
}

/**
 * Table for displaying, creating, editing and deleting Flute Entry records
 *
 * A flute entry is an invoice header with its stone lines nested. The
 * endpoint is a plain API view without OPTIONS metadata, so every form here
 * defines its fields in full and skips the permission (OPTIONS) check.
 */
export default function FluteEntryTable() {
  const table = useTable("flute-entry");

  const user = useUserState();

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "invoice_no",
        title: t`Invoice No.`,
        sortable: false,
        switchable: false,
      },
      DateColumn({
        accessor: "flute_date",
        title: t`Flute Date`,
        sortable: false,
        switchable: false,
      }),
      {
        accessor: "line_count",
        title: t`Lines`,
        sortable: false,
        render: (record: any) => record.lines?.length ?? 0,
      },
      {
        accessor: "total_cts",
        title: t`Total Cts.`,
        sortable: false,
        render: (record: any) => sumLines(record, "cts").toFixed(4),
      },
      {
        accessor: "total_amount",
        title: t`Total Amount`,
        sortable: false,
        render: (record: any) => sumLines(record, "amount").toFixed(2),
      },
      BooleanColumn({
        accessor: "active",
        sortable: false,
      }),
      DateColumn({
        accessor: "created_at",
        title: t`Created`,
        sortable: false,
        defaultVisible: false,
        extra: { showTime: true },
      }),
      UpdatedAtColumn({ sortable: false }),
    ];
  }, []);

  // --- Create modal ----------------------------------------------------
  const newFluteEntry = useCreateApiFormModal({
    url: ApiEndpoints.requisition_flute_entry,
    title: t`Create New Flute Entry`,
    fields: fluteEntryFields(),
    ignorePermissionCheck: true,
    validateFormData: validateFluteEntryLines(true),
    processFormData: processFluteEntryData,
    onFormError: remapFluteEntryLineErrors,
    successMessage: t`Flute entry created`,
    gridColumns: FLUTE_ENTRY_FORM_GRID_COLUMNS,
    size: FLUTE_ENTRY_MODAL_SIZE,
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedFluteEntry, setSelectedFluteEntry] = useState<
    number | undefined
  >(undefined);

  const editFluteEntry = useEditApiFormModal({
    url: ApiEndpoints.requisition_flute_entry,
    pk: selectedFluteEntry,
    title: t`Edit Flute Entry`,
    fields: fluteEntryFields(),
    ignorePermissionCheck: true,
    validateFormData: validateFluteEntryLines(),
    processFormData: processFluteEntryData,
    onFormError: remapFluteEntryLineErrors,
    successMessage: t`Flute entry updated`,
    gridColumns: FLUTE_ENTRY_FORM_GRID_COLUMNS,
    size: FLUTE_ENTRY_MODAL_SIZE,
    table: table,
  });

  const deleteFluteEntry = useDeleteApiFormModal({
    url: ApiEndpoints.requisition_flute_entry,
    pk: selectedFluteEntry,
    title: t`Delete Flute Entry`,
    ignorePermissionCheck: true,
    successMessage: t`Flute entry deleted`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedFluteEntry(record.pk);
            editFluteEntry.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedFluteEntry(record.pk);
            deleteFluteEntry.open();
          },
        }),
      ];
    },
    [user, editFluteEntry.open, deleteFluteEntry.open],
  );

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-flute-entry"
        onClick={() => newFluteEntry.open()}
        tooltip={t`Add Flute Entry`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user, newFluteEntry.open]);

  return (
    <>
      {newFluteEntry.modal}
      {editFluteEntry.modal}
      {deleteFluteEntry.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.requisition_flute_entry)}
        tableState={table}
        columns={columns}
        props={{
          rowActions: rowActions,
          tableActions: tableActions,
        }}
      />
    </>
  );
}
