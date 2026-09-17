import { t } from "@lingui/core/macro";
import { useCallback, useEffect, useMemo, useState } from "react";

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
import { BooleanColumn, DateColumn, UpdatedAtColumn } from "../ColumnRenderers";
import { ColumnSearchInput } from "../ColumnSearchInput";
import { InvenTreeTable } from "../InvenTreeTable";
import {
  PO_CATEGORY_CHOICES,
  PURCHASE_REQUEST_FORM_GRID_COLUMNS,
  PURCHASE_REQUEST_MODAL_SIZE,
  processPurchaseRequestData,
  purchaseRequestFields,
  savePurchaseRequestLines,
  validatePurchaseRequestLines,
} from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useApi } from "@context/ApiContext";
import { showApiErrorMessage } from "@helpers/notifications";
import { useUserState } from "@store/UserState";
import { ActionIcon, Tooltip } from "@mantine/core";
import { IconFilterOff } from "@tabler/icons-react";

/**
 * Table for displaying, creating, editing and deleting Purchase Request records
 *
 * A purchase request is a purchase order record with `potype = REQUEST`.
 */
export default function PurchaseRequestTable() {
  const table = useTable("purchase-request");

  const user = useUserState();
  const api = useApi();

  // Per-column search terms, keyed by the API query parameter they are sent as.
  // Every active term is applied together (multi-level / AND filtering).
  const [columnFilters, setColumnFilters] = useState<Record<string, string>>(
    {},
  );

  const setColumnFilter = useCallback((key: string, value: string) => {
    setColumnFilters((filters) => {
      if ((filters[key] ?? "") === value) {
        return filters;
      }

      const updated = { ...filters };

      if (value.trim()) {
        updated[key] = value;
      } else {
        delete updated[key];
      }

      return updated;
    });
  }, []);

  const activeColumnFilters = useMemo(() => {
    const active: Record<string, string> = {};

    Object.entries(columnFilters).forEach(([key, value]) => {
      if (value.trim()) {
        active[key] = value.trim();
      }
    });

    return active;
  }, [columnFilters]);

  // Jump back to the first page whenever the column search terms change
  useEffect(() => {
    table.setPage(1);
  }, [activeColumnFilters]);

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    // Build the inline search popover for a given column
    const columnFilter = (key: string, label: string, placeholder?: string) => ({
      filtering: !!activeColumnFilters[key],
      filter: () => (
        <ColumnSearchInput
          label={label}
          placeholder={placeholder}
          value={columnFilters[key] ?? ""}
          onChange={(value: string) => setColumnFilter(key, value)}
        />
      ),
    });

    return [
      {
        accessor: "pono",
        title: t`P.R. No.`,
        sortable: false,
        switchable: false,
        ...columnFilter("pono_search", t`P.R. No.`),
      },
      DateColumn({
        accessor: "podate",
        title: t`P.R. Date`,
        sortable: true,
        switchable: false,
        ...columnFilter("podate_search", t`P.R. Date`, "YYYY-MM-DD"),
      }),
      {
        accessor: "customer_name",
        title: t`Customer`,
        sortable: false,
        ...columnFilter("customer_search", t`Customer`),
      },
      {
        accessor: "pocategory",
        title: t`Category`,
        sortable: false,
        ...columnFilter("pocategory_search", t`Category`),
      },
      {
        accessor: "tqty",
        title: t`Total Qty.`,
        sortable: true,
        ...columnFilter("tqty_search", t`Total Qty.`),
      },
      {
        accessor: "prepby_username",
        title: t`Prepared By`,
        sortable: false,
        ...columnFilter("prepby_search", t`Prepared By`),
      },
      BooleanColumn({
        accessor: "active",
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
  }, [columnFilters, activeColumnFilters, setColumnFilter]);

  // --- Create modal ----------------------------------------------------
  const newPurchaseRequest = useCreateApiFormModal({
    url: ApiEndpoints.purchase_api,
    title: t`Create New Purchase Request`,
    fields: purchaseRequestFields(),
    validateFormData: validatePurchaseRequestLines("items"),
    processFormData: processPurchaseRequestData,
    successMessage: t`Purchase request created`,
    gridColumns: PURCHASE_REQUEST_FORM_GRID_COLUMNS,
    size: PURCHASE_REQUEST_MODAL_SIZE,
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedPurchaseRequest, setSelectedPurchaseRequest] = useState<
    number | undefined
  >(undefined);

  // The line items the edit modal was opened with, used to work out which
  // rows the user deleted from the grid
  const [selectedLines, setSelectedLines] = useState<any[]>([]);

  const editPurchaseRequest = useEditApiFormModal({
    url: ApiEndpoints.purchase_api,
    pk: selectedPurchaseRequest,
    title: t`Edit Purchase Request`,
    fields: purchaseRequestFields(true),
    validateFormData: validatePurchaseRequestLines("lines"),
    successMessage: t`Purchase request updated`,
    gridColumns: PURCHASE_REQUEST_FORM_GRID_COLUMNS,
    size: PURCHASE_REQUEST_MODAL_SIZE,
    // The header endpoint ignores line data, so the edited rows are written
    // separately once the header itself has saved
    onFormSuccess: (data: any, form: any) => {
      savePurchaseRequestLines({
        api: api,
        poPk: data?.pk ?? selectedPurchaseRequest,
        originalLines: selectedLines,
        rows: form?.getValues("lines") ?? [],
      })
        .then(() => table.refreshTable())
        .catch((error: any) => {
          showApiErrorMessage({
            error: error,
            title: t`Error saving line items`,
          });
          table.refreshTable();
        });
    },
  });

  const deletePurchaseRequest = useDeleteApiFormModal({
    url: ApiEndpoints.purchase_api,
    pk: selectedPurchaseRequest,
    title: t`Delete Purchase Request`,
    successMessage: t`Purchase request deleted`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedPurchaseRequest(record.pk);
            setSelectedLines(record.lines ?? []);
            editPurchaseRequest.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedPurchaseRequest(record.pk);
            deletePurchaseRequest.open();
          },
        }),
      ];
    },
    [user, editPurchaseRequest.open, deletePurchaseRequest.open],
  );

  // --- Table-level filters ----------------------------------------------
  const tableFilters: TableFilter[] = useMemo(() => {
    return [
      {
        name: "active",
        label: t`Active`,
        description: t`Show active purchase requests`,
        type: "boolean",
      },
      {
        name: "pocategory",
        label: t`Category`,
        description: t`Filter by purchase request category`,
        type: "choice",
        choices: PO_CATEGORY_CHOICES.map((choice) => ({
          value: choice.value,
          label: choice.display_name,
        })),
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <Tooltip key="clear-column-filters" label={t`Clear column filters`}>
        <ActionIcon
          variant="transparent"
          aria-label="clear-column-filters"
          disabled={Object.keys(activeColumnFilters).length === 0}
          onClick={() => setColumnFilters({})}
        >
          <IconFilterOff />
        </ActionIcon>
      </Tooltip>,
      <AddItemButton
        key="add-purchase-request"
        onClick={() => newPurchaseRequest.open()}
        tooltip={t`Add Purchase Request`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user, newPurchaseRequest.open, activeColumnFilters]);

  return (
    <>
      {newPurchaseRequest.modal}
      {editPurchaseRequest.modal}
      {deletePurchaseRequest.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.purchase_api)}
        tableState={table}
        columns={columns}
        props={{
          params: {
            potype: "REQUEST",
            ...activeColumnFilters,
          },
          defaultSortColumn: "podate",
          rowActions: rowActions,
          tableActions: tableActions,
          tableFilters: tableFilters,
          enableDownload: true,
        }}
      />
    </>
  );
}
