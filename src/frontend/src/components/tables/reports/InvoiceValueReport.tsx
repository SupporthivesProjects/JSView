import { t } from "@lingui/core/macro";
import { Alert, Box, Button, Group, Stack, Text } from "@mantine/core";
import { useDebouncedValue, useId } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { IconFileSpreadsheet } from "@tabler/icons-react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { useMemo, useState } from "react";
import Select from "react-select";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { apiUrl } from "@lib/functions/Api";
import { useApi } from "@context/ApiContext";
import {
  selectFieldStyles,
  useSelectFieldColors,
} from "../../forms/fields/SelectFieldTheme";
import useDataOutput from "../../../hooks/UseDataOutput";

import "./invoiceValue.css";

type Value = number | string | null | undefined;

interface VendorOption {
  value: string;
  label: string;
}

interface InvoiceOption {
  value: string;
  label: string;
  vsdate: string | null;
  vendorName: string | null;
}

/** A shipment line as returned by the invoice value endpoint */
interface InvoiceValueLine {
  pono: string | null;
  design_no: string | null;
  invoice_pcs: Value;
  invoice_netwt: Value;
  invoice_cts: Value;
  invoice_labor: Value;
  avg_netwt: Value;
  avg_cts: Value;
  avg_labor: Value;
  avg_cts_value: Value;
  tr_oz: Value;
  kt: Value;
  gold_loss: Value;
  avg_metal_amt: Value;
  duty: Value;
  other_exp: Value;
  vendor_metal_amt?: Value;
  vendor_diamond_amt?: Value;
  avg_per_pc_value: Value;
}

type Column = {
  key: keyof InvoiceValueLine;
  title: string;
  digits?: number;
};

// Rows are capped by the report pagination, so ask for the largest page
const ROW_LIMIT = 500;

/** Show a figure without trailing zeros, e.g. "0.000" -> "0" */
function figure(value: Value, digits = 2): string {
  if (value === null || value === undefined || value === "") return "";
  const number = Number(value);
  if (Number.isNaN(number)) return String(value);
  return String(Number(number.toFixed(digits)));
}

/**
 * Invoice Value P/C report
 *
 * The user picks a vendor and one of its shipment invoices, then either views
 * the per piece values on screen or exports them as an Excel workbook. The
 * export also works from the invoice number alone.
 */
export default function InvoiceValueReport() {
  const api = useApi();
  const colors = useSelectFieldColors();
  const vendorFieldId = useId();
  const invoiceFieldId = useId();

  const [vendor, setVendor] = useState<VendorOption | null>(null);
  const [invoice, setInvoice] = useState<InvoiceOption | null>(null);

  const [vendorSearch, setVendorSearch] = useState("");
  const [debouncedVendorSearch] = useDebouncedValue(vendorSearch, 300);
  const [invoiceSearch, setInvoiceSearch] = useState("");
  const [debouncedInvoiceSearch] = useDebouncedValue(invoiceSearch, 300);

  const [exporting, setExporting] = useState(false);
  const [exportId, setExportId] = useState<number | undefined>(undefined);

  useDataOutput({
    title: t`Exporting Invoice Value P/C Report`,
    id: exportId,
  });

  const selectTheme = (theme: any) => ({
    ...theme,
    colors: { ...theme.colors, ...colors },
  });

  const columns: Column[] = [
    { key: "pono", title: t`P.O. No` },
    { key: "design_no", title: t`Design No.` },
    { key: "invoice_pcs", title: t`Invoice Pcs` },
    { key: "invoice_netwt", title: t`Invoice NetWt.`, digits: 3 },
    { key: "invoice_cts", title: t`Invoice Cts.` },
    { key: "invoice_labor", title: t`Invoice Labor` },
    { key: "avg_netwt", title: t`Avg NetWt.`, digits: 3 },
    { key: "avg_cts", title: t`Avg Cts.` },
    { key: "avg_labor", title: t`Avg Labor` },
    { key: "avg_cts_value", title: t`Avg Cts. Value` },
    { key: "tr_oz", title: t`Tr. Oz`, digits: 4 },
    { key: "kt", title: t`KT` },
    { key: "gold_loss", title: t`Gold Loss` },
    { key: "avg_metal_amt", title: t`Avg. Metal Amt.` },
    { key: "duty", title: t`Duty` },
    { key: "other_exp", title: t`Other exp.` },
    { key: "vendor_metal_amt", title: t`Vendor Metal Amt.` },
    { key: "vendor_diamond_amt", title: t`Vendor Diamond Amt.` },
    { key: "avg_per_pc_value", title: t`Avg. Per Pc. Value` },
  ];

  // --- Vendor options --------------------------------------------------
  const vendorQuery = useQuery({
    queryKey: ["invoice-value-vendor-search", debouncedVendorSearch],
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

  const vendorOptions: VendorOption[] = useMemo(
    () =>
      (vendorQuery.data ?? []).map((company: any) => ({
        value: String(company.pk),
        label: company.name ?? company.code ?? `#${company.pk}`,
      })),
    [vendorQuery.data],
  );

  // --- Invoice options (shipments, of the selected vendor if any) --------
  const invoiceQuery = useQuery({
    queryKey: ["invoice-value-invoices", vendor?.value, debouncedInvoiceSearch],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.vendor_shipment), {
          params: {
            vendorid: vendor?.value,
            search: debouncedInvoiceSearch,
            ordering: "-vsdate",
            limit: 100,
          },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
  });

  const invoiceOptions: InvoiceOption[] = useMemo(
    () =>
      (invoiceQuery.data ?? []).map((shipment: any) => ({
        value: String(shipment.pk),
        label: shipment.vsno,
        vsdate: shipment.vsdate ?? null,
        vendorName: shipment.vendor_name ?? null,
      })),
    [invoiceQuery.data],
  );

  const handleVendorChange = (option: VendorOption | null) => {
    setVendor(option);
    // Invoices belong to a vendor, so a new vendor clears the selection
    setInvoice(null);
    setInvoiceSearch("");
  };

  // --- Report lines -------------------------------------------------------
  // The vendor / invoice the data on screen was fetched with
  const [fetched, setFetched] = useState<{
    vendor: VendorOption;
    invoice: InvoiceOption;
  } | null>(null);

  const dataQuery = useQuery<InvoiceValueLine[]>({
    queryKey: [
      "invoice-value-data",
      fetched?.vendor.value,
      fetched?.invoice.label,
    ],
    enabled: !!fetched,
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.reports_invoice_value), {
          params: {
            vendorid: fetched?.vendor.value,
            vsno: fetched?.invoice.label,
            limit: ROW_LIMIT,
          },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
  });

  const handleGetData = () => {
    if (vendor && invoice) {
      setFetched({ vendor, invoice });
    }
  };

  /* The export builds the workbook server side and returns a DataOutput
   * record, which is then monitored until the file can be downloaded.
   * Without a vendor the export covers the invoice number alone.
   */
  const handleExport = () => {
    if (!invoice) return;

    setExporting(true);
    api
      .get(apiUrl(ApiEndpoints.reports_invoice_value), {
        params: {
          ...(vendor ? { vendorid: vendor.value } : {}),
          vsno: invoice.label,
          export: true,
          export_format: "xlsx",
        },
      })
      .then((response) => setExportId(response.data?.pk))
      .catch(() => {
        notifications.show({
          title: t`Export failed`,
          message: t`Could not export the invoice value report`,
          color: "red",
        });
      })
      .finally(() => setExporting(false));
  };

  const invoiceDate = fetched?.invoice.vsdate
    ? dayjs(fetched.invoice.vsdate).format("DD MMM YYYY")
    : "";

  return (
    <Stack gap="md">
      <Group align="flex-end" gap="md" wrap="nowrap">
        <Box style={{ flex: 2 }}>
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
            aria-label={t`Invoice No.`}
            isClearable
            options={invoiceOptions}
            value={invoice}
            onChange={(option: any) => setInvoice(option ?? null)}
            inputValue={invoiceSearch}
            onInputChange={(input, { action }) => {
              if (action === "input-change") setInvoiceSearch(input);
            }}
            filterOption={null}
            formatOptionLabel={(option: InvoiceOption, { context }) =>
              // Without a vendor, invoices of every vendor are listed
              context === "menu" && !vendor && option.vendorName
                ? `${option.label} (${option.vendorName})`
                : option.label
            }
            isLoading={invoiceQuery.isFetching}
            placeholder={t`Invoice No.`}
            noOptionsMessage={() => t`No invoices found`}
            menuPortalTarget={document.body}
            menuPosition="fixed"
            styles={selectFieldStyles}
            theme={selectTheme}
          />
        </Box>
        <Button
          onClick={handleGetData}
          loading={dataQuery.isFetching}
          disabled={!vendor || !invoice}
        >
          {t`Get Data`}
        </Button>
        <Button
          variant="light"
          leftSection={<IconFileSpreadsheet size={18} />}
          onClick={handleExport}
          loading={exporting}
          disabled={!invoice}
        >
          {t`Download Excel`}
        </Button>
      </Group>

      {dataQuery.isError && (
        <Alert color="red" title={t`Error`}>
          {(dataQuery.error as any)?.response?.data?.detail ??
            t`Failed to load the invoice value report`}
        </Alert>
      )}

      {fetched &&
        dataQuery.data &&
        (dataQuery.data.length ? (
          <div className="iv-sheet">
            <table className="iv-table">
              <thead>
                <tr>
                  <th colSpan={2}>{t`Invoice No.`}</th>
                  <th colSpan={2} className="iv-value">
                    {fetched.invoice.label}
                  </th>
                  <th colSpan={2}>{t`Vendor`}</th>
                  <th colSpan={5} className="iv-value">
                    {fetched.vendor.label}
                  </th>
                  <th colSpan={4}>{t`Invoice Date`}</th>
                  <th colSpan={3} className="iv-value">
                    {invoiceDate}
                  </th>
                  <th colSpan={2} />
                </tr>
                <tr>
                  <th>#</th>
                  {columns.map((column) => (
                    <th key={column.key}>{column.title}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {dataQuery.data.map((line, index) => (
                  <tr key={index}>
                    <td>{index + 1}</td>
                    {columns.map((column) => (
                      <td key={column.key}>
                        {column.key === "pono" || column.key === "design_no"
                          ? (line[column.key] ?? "")
                          : figure(line[column.key], column.digits)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <Text c="dimmed">{t`No lines found for the selected invoice`}</Text>
        ))}
    </Stack>
  );
}
