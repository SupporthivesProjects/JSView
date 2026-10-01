import { t } from "@lingui/core/macro";
import { useCallback, useMemo, useState } from "react";

import { AddItemButton } from "@lib/components/AddItemButton";
import {
  type RowAction,
  RowDeleteAction,
  RowEditAction,
} from "@lib/components/RowActions";
import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { ModelType } from "@lib/enums/ModelType";
import { UserRoles } from "@lib/enums/Roles";
import { apiUrl } from "@lib/functions/Api";
import useTable from "@lib/hooks/UseTable";
import type { TableFilter } from "@lib/index";
import type { TableColumn } from "@lib/types/Tables";
import { BooleanColumn, DateColumn, UpdatedAtColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import {
  VENDOR_SHIPMENT_FORM_GRID_COLUMNS,
  VENDOR_SHIPMENT_MODAL_SIZE,
  processVendorShipmentData,
  processVendorShipmentHeaderData,
  saveVendorShipmentLines,
  validateVendorShipmentLines,
  vendorShipmentFields,
} from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useApi } from "@context/ApiContext";
import { showApiErrorMessage } from "@helpers/notifications";
import { useUserState } from "@store/UserState";

/** Sum one numeric column over the lines of a shipment */
function sumLines(record: any, key: string): number {
  return (record?.lines ?? []).reduce(
    (total: number, line: any) => total + (Number(line?.[key]) || 0),
    0,
  );
}

/**
 * Table for displaying, creating, editing and deleting Vendor Shipment records
 *
 * A shipment header is created together with its lines in a single request.
 * On edit the header is saved first, then the line grid is written to the
 * line endpoint - the same flow as the purchase order table.
 */
export default function VendorShipmentTable() {
  const table = useTable("vendor-shipment");

  const user = useUserState();
  const api = useApi();

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "vsno",
        title: t`Shipment No.`,
        sortable: false,
        switchable: false,
      },
      DateColumn({
        accessor: "vsdate",
        title: t`Shipment Date`,
        sortable: true,
        switchable: false,
      }),
      {
        accessor: "vendor_name",
        title: t`Vendor`,
        sortable: false,
      },
      // {
      //   accessor: "courier_name",
      //   title: t`Courier`,
      //   sortable: false,
      // },
      {
        accessor: "trackref",
        title: t`Tracking Ref.`,
        sortable: false,
      },
      // {
      //   accessor: "pono_list",
      //   title: t`P.O. No.`,
      //   sortable: false,
      //   render: (record: any) =>
      //     Array.from(
      //       new Set(
      //         (record.lines ?? [])
      //           .map((line: any) => line.pono)
      //           .filter((pono: any) => !!pono),
      //       ),
      //     ).join(", "),
      // },
      // {
      //   accessor: "total_pcs",
      //   title: t`Total Pcs`,
      //   sortable: false,
      //   render: (record: any) => sumLines(record, "pcs"),
      // },
      // {
      //   accessor: "total_metalwt",
      //   title: t`Metal Wt.`,
      //   sortable: false,
      //   render: (record: any) => sumLines(record, "metalwt").toFixed(3),
      // },
      // {
      //   accessor: "confirmed",
      //   title: t`Confirmed`,
      //   sortable: false,
      //   render: (record: any) => {
      //     const lines = record.lines ?? [];
      //     const confirmed = lines.filter((line: any) => !!line.confrm).length;
      //     return `${confirmed} / ${lines.length}`;
      //   },
      // },
      // {
      //   accessor: "luser",
      //   title: t`Last User`,
      //   sortable: false,
      //   defaultVisible: false,
      // },
      // BooleanColumn({
      //   accessor: "active",
      // }),
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
  const newShipment = useCreateApiFormModal({
    url: ApiEndpoints.vendor_shipment,
    title: t`Create New Shipment`,
    fields: vendorShipmentFields(),
    validateFormData: validateVendorShipmentLines(true),
    processFormData: processVendorShipmentData,
    successMessage: t`Shipment created`,
    gridColumns: VENDOR_SHIPMENT_FORM_GRID_COLUMNS,
    size: VENDOR_SHIPMENT_MODAL_SIZE,
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedShipment, setSelectedShipment] = useState<
    number | undefined
  >(undefined);

  // The line items the edit modal was opened with, used to work out which
  // rows the user deleted from the grid
  const [selectedLines, setSelectedLines] = useState<any[]>([]);

  const editShipment = useEditApiFormModal({
    url: ApiEndpoints.vendor_shipment,
    pk: selectedShipment,
    title: t`Edit Vendor Shipment`,
    fields: vendorShipmentFields(true),
    validateFormData: validateVendorShipmentLines(),
    processFormData: processVendorShipmentHeaderData,
    successMessage: t`Vendor shipment updated`,
    gridColumns: VENDOR_SHIPMENT_FORM_GRID_COLUMNS,
    size: VENDOR_SHIPMENT_MODAL_SIZE,
    // The header endpoint ignores line data, so the edited rows are written
    // separately once the header itself has saved
    onFormSuccess: (data: any, form: any) => {
      saveVendorShipmentLines({
        api: api,
        shipmentPk: data?.pk ?? selectedShipment,
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

  const deleteShipment = useDeleteApiFormModal({
    url: ApiEndpoints.vendor_shipment,
    pk: selectedShipment,
    title: t`Delete Vendor Shipment`,
    successMessage: t`Vendor shipment deleted`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            setSelectedShipment(record.pk);
            setSelectedLines(record.lines ?? []);
            editShipment.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedShipment(record.pk);
            deleteShipment.open();
          },
        }),
      ];
    },
    [user, editShipment.open, deleteShipment.open],
  );

  // --- Table-level filters ----------------------------------------------
  const tableFilters: TableFilter[] = useMemo(() => {
    return [
      {
        name: "active",
        label: t`Active`,
        description: t`Show active vendor shipments`,
        type: "boolean",
      },
      {
        name: "vendorid",
        label: t`Vendor`,
        description: t`Filter by vendor`,
        type: "api",
        apiUrl: apiUrl(ApiEndpoints.master_vendor_customer),
        apiFilter: { is_supplier: true, active: true },
        model: ModelType.company,
        modelRenderer: (instance: any) => instance.code ?? instance.name,
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <AddItemButton
        key="add-vendor-shipment"
        onClick={() => newShipment.open()}
        tooltip={t`Add Vendor Shipment`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user, newShipment.open]);

  return (
    <>
      {newShipment.modal}
      {editShipment.modal}
      {deleteShipment.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.vendor_shipment)}
        tableState={table}
        columns={columns}
        props={{
          defaultSortColumn: "vsdate",
          rowActions: rowActions,
          tableActions: tableActions,
          tableFilters: tableFilters,
          enableDownload: true,
        }}
      />
    </>
  );
}
