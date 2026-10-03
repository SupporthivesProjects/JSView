import { t } from "@lingui/core/macro";
import {
  Alert,
  Box,
  Button,
  Group,
  Stack,
  Text,
  TextInput,
} from "@mantine/core";
import { useDebouncedValue, useId } from "@mantine/hooks";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";
import Select from "react-select";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { apiUrl } from "@lib/functions/Api";
import { useApi } from "@context/ApiContext";
import {
  selectFieldStyles,
  useSelectFieldColors,
} from "../../forms/fields/SelectFieldTheme";
import ConfirmShipmentTable, {
  type ConfirmShipmentLine,
} from "./ConfirmShipmentTable";

interface Option {
  value: string;
  label: string;
}

/**
 * Confirm Shipment panel
 *
 * The user picks a vendor, then one of that vendor's shipment invoices and
 * an optional tracking number, before fetching the shipment data.
 */
export default function ConfirmShipmentPanel() {
  const api = useApi();
  const colors = useSelectFieldColors();
  const vendorFieldId = useId();
  const invoiceFieldId = useId();

  const [vendor, setVendor] = useState<Option | null>(null);
  const [invoice, setInvoice] = useState<Option | null>(null);
  const [trackingNo, setTrackingNo] = useState("");

  const [vendorSearch, setVendorSearch] = useState("");
  const [debouncedVendorSearch] = useDebouncedValue(vendorSearch, 300);

  const selectTheme = (theme: any) => ({
    ...theme,
    colors: { ...theme.colors, ...colors },
  });

  // --- Vendor options --------------------------------------------------
  const vendorQuery = useQuery({
    queryKey: ["confirm-shipment-vendor-search", debouncedVendorSearch],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.master_vendor_customer), {
          params: {
            is_supplier: true,
            active: true,
            search: debouncedVendorSearch,
            limit: 50,
          },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
  });

  const vendorOptions: Option[] = useMemo(
    () =>
      (vendorQuery.data ?? []).map((company: any) => ({
        value: String(company.pk),
        label: company.code ?? company.name ?? `#${company.pk}`,
      })),
    [vendorQuery.data],
  );

  // --- Invoice options (shipments of the selected vendor) ---------------
  const invoiceQuery = useQuery({
    queryKey: ["confirm-shipment-invoices", vendor?.value],
    enabled: !!vendor,
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.vendor_shipment_confirm_invoices), {
          params: { vendorid: vendor?.value },
        })
        .then((response) => response.data ?? []),
  });

  const invoiceOptions: Option[] = useMemo(
    () =>
      (invoiceQuery.data ?? []).map((shipment: any) => ({
        value: String(shipment.vendorshipid),
        label: shipment.vsno,
      })),
    [invoiceQuery.data],
  );

  const handleVendorChange = (option: Option | null) => {
    setVendor(option);
    // Invoices belong to a vendor, so a new vendor clears the selection
    setInvoice(null);
  };

  // --- Shipment lines ----------------------------------------------------
  // The vendor / invoice the data on screen was fetched with
  const [fetched, setFetched] = useState<{
    vendorid: string;
    vendorshipid: string;
  } | null>(null);

  const dataQuery = useQuery<ConfirmShipmentLine[]>({
    queryKey: ["confirm-shipment-data", fetched],
    enabled: !!fetched,
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.vendor_shipment_confirm_data), {
          params: fetched ?? {},
        })
        .then((response) => response.data ?? []),
  });

  const handleGetData = () => {
    if (vendor && invoice) {
      setFetched({ vendorid: vendor.value, vendorshipid: invoice.value });
    }
  };

  return (
    <Stack gap="md">
      <Group align="flex-end" gap="md" wrap="nowrap">
        <Box style={{ flex: 1 }}>
          <Select
            id={vendorFieldId}
            aria-label={t`Vendor`}
            isClearable
            options={vendorOptions}
            value={vendor}
            onChange={(option: any) => handleVendorChange(option ?? null)}
            inputValue={vendorSearch}
            onInputChange={(input, { action }) => {
              // Keep the typed search when the menu closes on a selection
              if (action === "input-change") setVendorSearch(input);
            }}
            filterOption={null}
            isLoading={vendorQuery.isFetching}
            placeholder={t`Vendor`}
            noOptionsMessage={() => t`No vendors found`}
            menuPortalTarget={document.body}
            menuPosition="fixed"
            styles={selectFieldStyles}
            theme={selectTheme}
          />
        </Box>
        <Box style={{ flex: 1 }}>
          <Select
            id={invoiceFieldId}
            aria-label={t`Invoice No`}
            isClearable
            isDisabled={!vendor}
            options={invoiceOptions}
            value={invoice}
            onChange={(option: any) => setInvoice(option ?? null)}
            isLoading={invoiceQuery.isFetching}
            placeholder={t`Invoice No`}
            noOptionsMessage={() => t`No invoices found`}
            menuPortalTarget={document.body}
            menuPosition="fixed"
            styles={selectFieldStyles}
            theme={selectTheme}
          />
        </Box>
        <Box style={{ flex: 1 }}>
          <TextInput
            aria-label={t`Tracking Number`}
            placeholder={t`Tracking Number`}
            value={trackingNo}
            onChange={(event) => setTrackingNo(event.currentTarget.value)}
          />
        </Box>
        <Button
          onClick={handleGetData}
          loading={dataQuery.isFetching}
          disabled={!vendor || !invoice}
        >
          {t`Get Data`}
        </Button>
      </Group>

      {dataQuery.isError && (
        <Alert color="red" title={t`Error`}>
          {(dataQuery.error as any)?.response?.data?.detail ??
            t`Failed to load the shipment data`}
        </Alert>
      )}

      {dataQuery.data &&
        (dataQuery.data.length ? (
          <ConfirmShipmentTable lines={dataQuery.data} />
        ) : (
          <Text c="dimmed">{t`No lines found for the selected invoice`}</Text>
        ))}
    </Stack>
  );
}
