import { t } from '@lingui/core/macro';
import { Anchor, Box, Stack, Text } from '@mantine/core';
import { useCallback, useMemo, useState } from 'react';

import { StylishText } from '@lib/components/StylishText';
import { ApiEndpoints } from '@lib/enums/ApiEndpoints';
import { UserRoles } from '@lib/enums/Roles';
import { apiUrl } from '@lib/functions/Api';
import { cancelEvent } from '@lib/functions/Events';
import useTable from '@lib/hooks/UseTable';
import type { TableColumn } from '@lib/types/Tables';
import { useApi } from '@context/ApiContext';
import { showApiErrorMessage } from '@helpers/notifications';
import { useUserState } from '@store/UserState';
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
import type { DashboardWidgetProps } from '../DashboardWidget';

/**
 * A column which is required by the listing, but for which the purchase order
 * endpoint does not (yet) provide any data.
 */
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

  // The line items the edit modal was opened with, used to work out which
  // rows the user deleted from the grid
  const [selectedLines, setSelectedLines] = useState<any[]>([]);

  const editPurchaseOrder = useEditApiFormModal({
    url: ApiEndpoints.purchase_api,
    pk: selectedPurchaseOrder,
    title: t`Edit Purchase Order`,
    fields: purchaseOrderFields(true),
    validateFormData: validatePurchaseRequestLines('lines'),
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

/**
 * Construct a dashboard widget which displays a listing of purchase orders
 */
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
