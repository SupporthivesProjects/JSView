import { t } from '@lingui/core/macro';
import { Alert, Button, Center, Loader } from '@mantine/core';
import { IconPrinter } from '@tabler/icons-react';
import { useCallback, useEffect, useState } from 'react';
import { useParams, useSearchParams } from 'react-router-dom';

import PurchaseOrderVendorSheet from '@components/print/purchase-order/PurchaseOrderVendorSheet';
import { takePrintPayload } from '@components/print/purchase-order/printPayload';
import type { PurchaseOrderPrintPayload } from '@components/print/purchase-order/types';
import { useApi } from '@context/ApiContext';
import { ApiEndpoints } from '@lib/enums/ApiEndpoints';
import { apiUrl } from '@lib/functions/Api';
import '@components/print/purchase-order/purchaseOrderPrint.css';

/**
 * Standalone (layout-free) print view for a purchase order.
 *
 * The payload is normally handed over in temporary storage by the page which
 * opened this tab; if that hand-off is missing (e.g. the link was reloaded or
 * bookmarked) the payload is fetched again from the print endpoint.
 */
export default function PurchaseOrderPrintPage() {
  const { id } = useParams();
  const [searchParams] = useSearchParams();
  const api = useApi();

  const printType = searchParams.get('type') ?? 'vendor';

  // Consume the handed-over payload on first render
  const [data, setData] = useState<PurchaseOrderPrintPayload | null>(() =>
    takePrintPayload(searchParams.get('key'))
  );

  const [error, setError] = useState<string>('');
  const [loading, setLoading] = useState<boolean>(false);

  useEffect(() => {
    if (data || !id) {
      return;
    }

    setLoading(true);

    api
      .get(`${apiUrl(ApiEndpoints.purchase_api, id)}print/`, {
        params: { type: printType }
      })
      .then((response: any) => setData(response.data))
      .catch(() => setError(t`Could not load the purchase order print data`))
      .finally(() => setLoading(false));
  }, [api, data, id, printType]);

  useEffect(() => {
    if (data?.po?.pono) {
      document.title = `${data.po.pono} - ${printType}`;
    }
  }, [data, printType]);

  const printSheet = useCallback(() => window.print(), []);

  if (loading) {
    return (
      <Center h='100vh'>
        <Loader />
      </Center>
    );
  }

  if (error) {
    return (
      <Alert color='red' title={t`Error`} m='md'>
        {error}
      </Alert>
    );
  }

  if (!data) {
    return null;
  }

  if (printType !== 'vendor') {
    return (
      <Alert color='yellow' title={t`Not available`} m='md'>
        {t`This print format is not available yet`}
      </Alert>
    );
  }

  return (
    <div className='po-print-page'>
      <div className='po-print-toolbar po-print-no-print'>
        <span className='po-print-toolbar-title'>
          {t`Purchase Order`}: {data.po.pono}
        </span>
        <Button leftSection={<IconPrinter size={16} />} onClick={printSheet}>
          {t`Print`}
        </Button>
      </div>
      <PurchaseOrderVendorSheet data={data} />
    </div>
  );
}
