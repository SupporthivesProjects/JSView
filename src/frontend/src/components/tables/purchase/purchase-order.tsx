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
import { BooleanColumn, DateColumn, UpdatedAtColumn } from "../ColumnRenderers";
import { useColumnFilters } from "../ColumnFilters";
import { InvenTreeTable } from "../InvenTreeTable";
import {
  PO_CATEGORY_CHOICES,
  PURCHASE_ORDER_FORM_GRID_COLUMNS,
  PURCHASE_ORDER_MODAL_SIZE,
  processPurchaseRequestData,
  purchaseOrderFields,
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

/**
 * Table for displaying, creating, editing and deleting Purchase Order records
 *
 * A purchase order is a purchase order record with `potype = ORDER`.
 */
export default function PurchaseOrderTable() {
  const table = useTable("purchase-order");

  const user = useUserState();
  const api = useApi();

  // Per-column search boxes, applied together (multi-level / AND filtering)
  const { activeColumnFilters, columnFilter, clearColumnFiltersAction } =
    useColumnFilters(table);

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "pono",
        title: t`P.O. No.`,
        sortable: false,
        switchable: false,
        ...columnFilter("pono_search", t`P.O. No.`),
      },
      DateColumn({
        accessor: "podate",
        title: t`P.O. Date`,
        sortable: true,
        switchable: false,
        ...columnFilter("podate_search", t`P.O. Date`, "YYYY-MM-DD"),
      }),
      {
        accessor: "customer_name",
        title: t`Customer`,
        sortable: false,
        ...columnFilter("customer_search", t`Customer`),
      },
      {
        accessor: "vendor_name",
        title: t`Vendor`,
        sortable: false,
        ...columnFilter("vendor_search", t`Vendor`),
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
  }, [columnFilter]);

  // --- Create modal ----------------------------------------------------
  const newPurchaseOrder = useCreateApiFormModal({
    url: ApiEndpoints.purchase_api,
    title: t`Create New Purchase Order`,
    fields: purchaseOrderFields(),
    validateFormData: validatePurchaseRequestLines("items", true),
    processFormData: processPurchaseRequestData,
    successMessage: t`Purchase order created`,
    gridColumns: PURCHASE_ORDER_FORM_GRID_COLUMNS,
    size: PURCHASE_ORDER_MODAL_SIZE,
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedPurchaseOrder, setSelectedPurchaseOrder] = useState<
    number | undefined
  >(undefined);

  // The line items the edit modal was opened with, used to work out which
  // rows the user deleted from the grid
  const [selectedLines, setSelectedLines] = useState<any[]>([]);

  const editPurchaseOrder = useEditApiFormModal({
    url: ApiEndpoints.purchase_api,
    pk: selectedPurchaseOrder,
    title: t`Edit Purchase Order`,
    fields: purchaseOrderFields(true),
    validateFormData: validatePurchaseRequestLines("lines"),
    successMessage: t`Purchase order updated`,
    gridColumns: PURCHASE_ORDER_FORM_GRID_COLUMNS,
    size: PURCHASE_ORDER_MODAL_SIZE,
    // The header endpoint ignores line data, so the edited rows are written
    // separately once the header itself has saved
    onFormSuccess: (data: any, form: any) => {
      savePurchaseRequestLines({
        api: api,
        poPk: data?.pk ?? selectedPurchaseOrder,
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

  const deletePurchaseOrder = useDeleteApiFormModal({
    url: ApiEndpoints.purchase_api,
    pk: selectedPurchaseOrder,
    title: t`Delete Purchase Order`,
    successMessage: t`Purchase order deleted`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedPurchaseOrder(record.pk);
            setSelectedLines(record.lines ?? []);
            editPurchaseOrder.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedPurchaseOrder(record.pk);
            deletePurchaseOrder.open();
          },
        }),
      ];
    },
    [user, editPurchaseOrder.open, deletePurchaseOrder.open],
  );

  // --- Table-level filters ----------------------------------------------
  const tableFilters: TableFilter[] = useMemo(() => {
    return [
      {
        name: "active",
        label: t`Active`,
        description: t`Show active purchase orders`,
        type: "boolean",
      },
      {
        name: "pocategory",
        label: t`Category`,
        description: t`Filter by purchase order category`,
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
      clearColumnFiltersAction,
      <AddItemButton
        key="add-purchase-order"
        onClick={() => newPurchaseOrder.open()}
        tooltip={t`Add Purchase Order`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user, newPurchaseOrder.open, clearColumnFiltersAction]);

  return (
    <>
      {newPurchaseOrder.modal}
      {editPurchaseOrder.modal}
      {deletePurchaseOrder.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.purchase_api)}
        tableState={table}
        columns={columns}
        props={{
          params: {
            potype: "ORDER",
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
