import { t } from '@lingui/core/macro';
import { Anchor, Box, Stack, Text } from '@mantine/core';
import { useCallback, useMemo, useState } from 'react';

import { StylishText } from '@lib/components/StylishText';
import { ApiEndpoints } from '@lib/enums/ApiEndpoints';
import { UserRoles } from '@lib/enums/Roles';
import { apiUrl } from '@lib/functions/Api';
import { cancelEvent } from '@lib/functions/Events';
import { getBaseUrl } from '@lib/functions/Navigation';
import useTable from '@lib/hooks/UseTable';
import type { TableColumn } from '@lib/types/Tables';
import { useApi } from '@context/ApiContext';
import { showApiErrorMessage } from '@helpers/notifications';
import { useUserState } from '@store/UserState';
import { stashPrintPayload } from '../../../print/purchase-order/printPayload';
import {
  PURCHASE_ORDER_FORM_GRID_COLUMNS,
  PURCHASE_ORDER_MODAL_SIZE,
  purchaseOrderFields,
  savePurchaseRequestLines,
  validatePurchaseRequestLines
} from '../../../forms/CommonForms';
import { useEditApiFormModal } from '../../../../hooks/UseForm';
import { DateColumn } from '../../../tables/ColumnRenderers';
import { InvenTreeTable } from '../../../tables/InvenTreeTable';
import type { ApiFormAction } from '@lib/types/Forms';
import type { DashboardWidgetProps } from '../DashboardWidget';


const PO_PRINT_TYPES: { type: string; label: () => string }[] = [
  { type: 'vendor', label: () => t`Vendor` },
  { type: 'self', label: () => t`Self` },
  { type: 'vendor_costcard', label: () => t`Vendor Costcard` },
  { type: 'self_costcard', label: () => t`Self Costcard` }
];


function PlaceholderColumn(accessor: string, title: string): TableColumn {
  return {
    accessor: accessor,
    title: title,
    sortable: false,
    switchable: true,
    render: () => null
  };
}

function PurchaseOrderListWidget() {
  const table = useTable('dashboard-purchase-order');

  const user = useUserState();
  const api = useApi();

  const canEdit: boolean = user.hasChangeRole(UserRoles.part);

  const [selectedPurchaseOrder, setSelectedPurchaseOrder] = useState<
    number | undefined
  >(undefined);

  
  const [selectedLines, setSelectedLines] = useState<any[]>([]);


  /*
   * Fetch the print payload for the selected order, park it in temporary
   * storage and hand it to a standalone print view in a new tab.
   */
  const openPrintView = useCallback(
    async (printType: string) => {
      if (!selectedPurchaseOrder) {
        return;
      }

      try {
        const response = await api.get(
          `${apiUrl(ApiEndpoints.purchase_api, selectedPurchaseOrder)}print/`,
          { params: { type: printType } }
        );

        const key = stashPrintPayload(response.data);

        const url = new URL(
          `/${getBaseUrl()}/print/purchase-order/${selectedPurchaseOrder}`,
          window.location.origin
        );

        url.searchParams.set('type', printType);

        if (key) {
          url.searchParams.set('key', key);
        }

        window.open(url.toString(), '_blank', 'noopener,noreferrer');
      } catch (error: any) {
        showApiErrorMessage({
          error: error,
          title: t`Error loading purchase order print data`
        });
      }
    },
    [api, selectedPurchaseOrder]
  );

  const printActions: ApiFormAction[] = useMemo(() => {
    return PO_PRINT_TYPES.map((printType) => ({
      text: printType.label(),
      onClick:
        printType.type === 'vendor'
          ? () => openPrintView(printType.type)
          : () => {}
    }));
  }, [openPrintView]);

  const editPurchaseOrder = useEditApiFormModal({
    url: ApiEndpoints.purchase_api,
    pk: selectedPurchaseOrder,
    title: t`Edit Purchase Order`,
    fields: purchaseOrderFields(true),
    actions: printActions,
    validateFormData: validatePurchaseRequestLines('lines'),
    successMessage: t`Purchase order updated`,
    gridColumns: PURCHASE_ORDER_FORM_GRID_COLUMNS,
    size: PURCHASE_ORDER_MODAL_SIZE,
   
    onFormSuccess: (data: any, form: any) => {
      savePurchaseRequestLines({
        api: api,
        poPk: data?.pk ?? selectedPurchaseOrder,
        originalLines: selectedLines,
        rows: form?.getValues('lines') ?? []
      })
        .then(() => table.refreshTable())
        .catch((error: any) => {
          showApiErrorMessage({
            error: error,
            title: t`Error saving line items`
          });
          table.refreshTable();
        });
    }
  });

  const openPurchaseOrder = useCallback(
    (record: any, event: any) => {
      cancelEvent(event);
      setSelectedPurchaseOrder(record.pk);
      setSelectedLines(record.lines ?? []);
      editPurchaseOrder.open();
    },
    [editPurchaseOrder.open]
  );

  const columns: TableColumn[] = useMemo(() => {
    return [
      {
        accessor: 'pono',
        title: t`P.O. #`,
        sortable: false,
        switchable: false,
        noWrap: true,
        render: (record: any) =>
          canEdit ? (
            <Anchor
              href='#'
              onClick={(event: any) => openPurchaseOrder(record, event)}
            >
              {record.pono}
            </Anchor>
          ) : (
            <Text>{record.pono}</Text>
          )
      },
      DateColumn({
        accessor: 'podate',
        title: t`P.O. Place Date`,
        sortable: true
      }),
      DateColumn({
        accessor: 'ddate',
        title: t`P.O. Due Date`,
        sortable: false
      }),
      DateColumn({
        accessor: 'esdstone',
        title: t`Stone Due Date`,
        sortable: false
      }),
      {
        accessor: 'customer_name',
        title: t`Customer`,
        sortable: false
      },
      {
        accessor: 'tqty',
        title: t`Placed Qty.`,
        sortable: true
      },
      PlaceholderColumn('open_qty', t`Open Qty`),
      PlaceholderColumn('diamond', t`Diamond`),
      PlaceholderColumn('color_stone', t`Color Stone`),
      PlaceholderColumn('stone_status_note', t`Stone Status Note`),
      PlaceholderColumn('po_status', t`P.O. Status`)
    ];
  }, [openPurchaseOrder, canEdit]);

  return (
    <Stack gap='xs' style={{ height: '100%' }}>
      {editPurchaseOrder.modal}
      <StylishText size='md'>{t`Purchase Orders`}</StylishText>
      <Box style={{ flex: 1, overflowY: 'auto' }}>
        <InvenTreeTable
          url={apiUrl(ApiEndpoints.purchase_api)}
          tableState={table}
          columns={columns}
          props={{
            params: {
              potype: 'ORDER'
            },
            defaultSortColumn: 'podate',
            enableDownload: false,
            enableSelection: false
          }}
        />
      </Box>
    </Stack>
  );
}

export default function PurchaseOrderListDashboardWidget(): DashboardWidgetProps {
  const user = useUserState();

  return {
    label: 'po-list',
    title: t`Purchase Order List`,
    description: t`Display a list of purchase orders`,
    minWidth: 8,
    minHeight: 6,
    icon: 'purchase_orders',
    enabled: user.hasViewRole(UserRoles.part),
    render: () => <PurchaseOrderListWidget />
  };
}
