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
import { BooleanColumn, DateColumn, DescriptionColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { metalRequisitionSentFields } from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
  useEditApiFormModal,
} from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";
import { useColumnFilters } from "../ColumnFilters";
import useNameLookup from "../../../hooks/UseNameLookup";

/**
 * Table for displaying, creating, editing and deleting Metal Type records
 */
export default function MetalRequisitionSentTable() {
  const table = useTable("metal-requisition-sent");

  const user = useUserState();

  // Per-column search boxes, applied together (multi-level / AND filtering)
  const { activeColumnFilters, columnFilter, clearColumnFiltersAction } =
    useColumnFilters(table);

  const { nameByPk: metalRequisitionPurchaseOrderByPk } = useNameLookup(
    ApiEndpoints.purchase_api,
    "metal-requisition-purchase-order-lookup",
    "pono",
  );

  

  // --- Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: "invoice_no",
        title: "Invoice No",
        sortable: true,
        switchable: false,
      },
      DateColumn({
        accessor: "metal_sent_date",
        title: t`Metal Sent Date`,
        sortable: true,
        switchable: false,
        ...columnFilter("metal_sent_date_search", t`Metal Sent. Date`, "YYYY-MM-DD"),
      }),
      {
        accessor: "purchase_order",
        title: "Purchase Order",
        sortable: true,
        switchable: false,
        render: (record: any) => metalRequisitionPurchaseOrderByPk[record.purchase_order] ?? record.purchase_order,
      },
      // {
      //   accessor: "triounce",
      //   title: "Triounce",
      //   sortable: true,
      //   switchable: false,
      // },
      // {
      //   accessor: "metal_gms",
      //   title: "Metal Gms",
      //   sortable: true,
      //   switchable: false,
      // },
      // {
      //   accessor: "metal_amount",
      //   title: "Metal Amount",
      //   sortable: true,
      //   switchable: false,
      // },
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
  }, [metalRequisitionPurchaseOrderByPk]);

  // --- Create modal ----------------------------------------------------
  const newMetalRequisitionSent = useCreateApiFormModal({
    url: ApiEndpoints.requisition_metal_sent,
    title: t`Add Metal Requisition Sent`,
    fields: metalRequisitionSentFields(),
    table: table,
  });

  // --- Edit / Delete modals --------------------------------------------
  const [selectedMetalRequisitionSent, setSelectedMetalRequisitionSent] = useState<
    number | undefined
  >(undefined);

  const editMetalRequisitionSent = useEditApiFormModal({
    url: ApiEndpoints.requisition_metal_sent,
    pk: selectedMetalRequisitionSent,
    title: t`Edit Metal Requisition Sent`,
    fields: metalRequisitionSentFields(),
    table: table,
  });

  const deleteMetalRequisitionSent = useDeleteApiFormModal({
    url: ApiEndpoints.requisition_metal_sent,
    pk: selectedMetalRequisitionSent,
    title: t`Delete Metal Requisition Sent`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.requisition_metal_sent),
          onClick: () => {
            setSelectedMetalRequisitionSent(record.pk);
            editMetalRequisitionSent.open();
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.requisition_metal_sent),
          onClick: () => {
            setSelectedMetalRequisitionSent(record.pk);
            deleteMetalRequisitionSent.open();
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
        onClick={() => newMetalRequisitionSent.open()}
        tooltip={t`Add Metal Requisition Sent`}
        hidden={!user.hasAddRole(UserRoles.requisition_metal_sent)}
      />,
    ];
  }, [user]);

  return (
    <>
      {newMetalRequisitionSent.modal}
      {editMetalRequisitionSent.modal}
      {deleteMetalRequisitionSent.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.requisition_metal_sent)}
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
