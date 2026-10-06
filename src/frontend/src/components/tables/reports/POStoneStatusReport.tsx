import { t } from "@lingui/core/macro";
import { ActionIcon, Box, Button, Group, Tooltip } from "@mantine/core";
import { DateInput } from "@mantine/dates";
import { useDebouncedValue, useId } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { IconFileSpreadsheet, IconSearch } from "@tabler/icons-react";
import { useQuery } from "@tanstack/react-query";
import dayjs from "dayjs";
import { useCallback, useMemo, useState } from "react";
import Select from "react-select";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { apiUrl } from "@lib/functions/Api";
import useTable from "@lib/hooks/UseTable";
import type { TableColumn } from "@lib/types/Tables";
import { useApi } from "@context/ApiContext";
import { InvenTreeTable } from "../InvenTreeTable";
import {
  selectFieldStyles,
  useSelectFieldColors,
} from "../../forms/fields/SelectFieldTheme";
import useDataOutput from "../../../hooks/UseDataOutput";

const DATE_FORMAT = "YYYY-MM-DD";

// "Select Date" switches to the custom From / To dates
const CUSTOM_RANGE = "custom";

interface CompanyOption {
  value: string;
  label: string;
}

/** Searchable company dropdown (customers or vendors) */
function CompanySelect({
  kind,
  value,
  onChange,
}: {
  kind: "customer" | "vendor";
  value: CompanyOption | null;
  onChange: (option: CompanyOption | null) => void;
}) {
  const api = useApi();
  const colors = useSelectFieldColors();
  const fieldId = useId();

  const [search, setSearch] = useState("");
  const [debouncedSearch] = useDebouncedValue(search, 300);

  const query = useQuery({
    queryKey: ["po-stone-status-company", kind, debouncedSearch],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.master_vendor_customer), {
          params: {
            ...(kind === "customer"
              ? { is_customer: true }
              : { is_supplier: true }),
            active: true,
            search: debouncedSearch,
            limit: 50,
          },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
  });

  const options: CompanyOption[] = useMemo(
    () =>
      (query.data ?? []).map((company: any) => ({
        value: String(company.pk),
        // The report shows customers by code and vendors by name
        label:
          (kind === "customer"
            ? (company.code ?? company.name)
            : (company.name ?? company.code)) ?? `#${company.pk}`,
      })),
    [query.data, kind],
  );

  const label = kind === "customer" ? t`Customer` : t`Vendor`;

  return (
    <Select
      id={fieldId}
      aria-label={label}
      isClearable
      options={options}
      value={value}
      onChange={(option: any) => onChange(option ?? null)}
      inputValue={search}
      onInputChange={(input, { action }) => {
        // Keep the typed search when the menu closes on a selection
        if (action === "input-change") setSearch(input);
      }}
      filterOption={null}
      isLoading={query.isFetching}
      placeholder={label}
      noOptionsMessage={() =>
        kind === "customer" ? t`No customers found` : t`No vendors found`
      }
      menuPortalTarget={document.body}
      menuPosition="fixed"
      styles={selectFieldStyles}
      theme={(theme: any) => ({
        ...theme,
        colors: { ...theme.colors, ...colors },
      })}
    />
  );
}


export default function POStoneStatusReport() {
  const api = useApi();
  const table = useTable("po-stone-status", { idAccessor: "_row" });
  const colors = useSelectFieldColors();
  const dateFieldId = useId();

  const selectTheme = (theme: any) => ({
    ...theme,
    colors: { ...theme.colors, ...colors },
  });

  const [customer, setCustomer] = useState<CompanyOption | null>(null);
  const [vendor, setVendor] = useState<CompanyOption | null>(null);
  const [dateRange, setDateRange] = useState<string | null>(null);
  const [dateFrom, setDateFrom] = useState<string | null>(null);
  const [dateTo, setDateTo] = useState<string | null>(null);

  const [exporting, setExporting] = useState(false);
  const [exportId, setExportId] = useState<number | undefined>(undefined);

  useDataOutput({
    title: t`Exporting P.O. Stone Status Report`,
    id: exportId,
  });

  const dateRangeOptions = [
    { value: CUSTOM_RANGE, label: t`Select Date` },
    { value: "last_1_month", label: t`Last 1 Month` },
    { value: "last_6_month", label: t`Last 6 Months` },
    { value: "year_to_date", label: t`Year To Date` },
  ];

  const customRange = dateRange === CUSTOM_RANGE;
  const invalidRange =
    customRange &&
    !!dateFrom &&
    !!dateTo &&
    dayjs(dateFrom).isAfter(dayjs(dateTo));

  // Filter params shared by the table and the export
  const filterParams = useMemo(() => {
    const params: Record<string, any> = {};

    if (customer) params.customer = customer.value;
    if (vendor) params.vendor = vendor.value;

    if (customRange) {
      if (!invalidRange) {
        if (dateFrom) params.podate_from = dayjs(dateFrom).format(DATE_FORMAT);
        if (dateTo) params.podate_to = dayjs(dateTo).format(DATE_FORMAT);
      }
    } else if (dateRange) {
      params.date_range = dateRange;
    }

    return params;
  }, [customer, vendor, dateRange, customRange, dateFrom, dateTo, invalidRange]);

  const handleDateRangeChange = (value: string | null) => {
    setDateRange(value);
    if (value !== CUSTOM_RANGE) {
      setDateFrom(null);
      setDateTo(null);
    }
  };

  // Rows have no primary key, so number them for the table row ids
  const dataFormatter = useCallback(
    (data: any[]) =>
      Array.isArray(data)
        ? data.map((row, index) => ({ ...row, _row: index }))
        : data,
    [],
  );

  const columns: TableColumn[] = useMemo(() => {
    const text = (accessor: string, title: string, ordering?: string) => ({
      accessor,
      title,
      sortable: !!ordering,
      ordering,
      switchable: false,
    });

    const figure = (accessor: string, title: string) => ({
      accessor,
      title,
      sortable: false,
      textAlign: "right" as const,
    });

    return [
      text("pono", t`P.O.`, "poid__pono"),
      text("podate", t`P.O. Date`, "poid__podate"),
      text("customer_code", t`Customer`),
      text("vendor_code", t`Vendor`),
      figure("po_dia_cts", t`P.O. Dia. Cts.`),
      figure("po_dia_amount", t`P.O. Dia. Amount.`),
      figure("issue_dia_cts", t`Issue Dia. Cts.`),
      figure("issue_dia_amount", t`Issue Dia. Amount`),
      figure("rec_dia_cts", t`Rec. Dia. Cts.`),
      figure("issue_bal_dia_cts", t`Issue Bal. Dia. Cts.`),
      figure("po_col_cts", t`P.O. Col. Cts.`),
      figure("po_col_amount", t`P.O. Col. Amount.`),
      figure("issue_col_cts", t`Issue Col. Cts.`),
      figure("issue_col_amount", t`Issue Col. Amount`),
      figure("rec_col_cts", t`Rec. Col. Cts.`),
      figure("issue_bal_col_cts", t`Issue Bal. Col. Cts.`),
    ];
  }, []);

  /* The export builds the workbook server side and returns a DataOutput
   * record, which is then monitored until the file can be downloaded.
   */
  const handleExport = () => {
    if (invalidRange) return;

    setExporting(true);
    api
      .get(apiUrl(ApiEndpoints.reports_po_stone_status), {
        params: {
          ...filterParams,
          export: true,
          export_format: "xlsx",
        },
      })
      .then((response) => setExportId(response.data?.pk))
      .catch(() => {
        notifications.show({
          title: t`Export failed`,
          message: t`Could not export the P.O. stone status report`,
          color: "red",
        });
      })
      .finally(() => setExporting(false));
  };

  // The filters the data on screen was searched with; nothing loads until
  // the first search
  const [searched, setSearched] = useState<Record<string, any> | null>(null);

  const handleSearch = () => {
    if (invalidRange) return;
    setSearched(filterParams);
    // Reload even when searching again with unchanged filters
    table.refreshTable();
  };

  return (
    <>
      <Group align="flex-end" gap="sm" mb="md" wrap="nowrap">
        <Box style={{ flex: 1, minWidth: 0 }}>
          <CompanySelect
            kind="customer"
            value={customer}
            onChange={setCustomer}
          />
        </Box>
        <Box style={{ flex: 1, minWidth: 0 }}>
          <CompanySelect kind="vendor" value={vendor} onChange={setVendor} />
        </Box>
        <Box style={{ width: 170, flexShrink: 0 }}>
          <Select
            id={dateFieldId}
            aria-label={t`Date`}
            isClearable
            isSearchable={false}
            options={dateRangeOptions}
            value={
              dateRangeOptions.find((option) => option.value === dateRange) ??
              null
            }
            onChange={(option: any) =>
              handleDateRangeChange(option?.value ?? null)
            }
            placeholder={t`Date`}
            menuPortalTarget={document.body}
            menuPosition="fixed"
            styles={selectFieldStyles}
            theme={selectTheme}
          />
        </Box>
        {customRange && (
          <>
            <DateInput
              aria-label={t`P.O. Date From`}
              placeholder={t`P.O. Date From`}
              value={dateFrom}
              onChange={setDateFrom}
              valueFormat="DD MMM YYYY"
              maxDate={dateTo ?? undefined}
              clearable
              w={150}
              style={{ flexShrink: 0 }}
            />
            <DateInput
              aria-label={t`P.O. Date To`}
              placeholder={t`P.O. Date To`}
              value={dateTo}
              onChange={setDateTo}
              valueFormat="DD MMM YYYY"
              minDate={dateFrom ?? undefined}
              error={invalidRange ? t`Must be after the From date` : undefined}
              clearable
              w={150}
              style={{ flexShrink: 0 }}
            />
          </>
        )}
        <Button
          style={{ flexShrink: 0 }}
          leftSection={<IconSearch size={18} />}
          onClick={handleSearch}
          disabled={invalidRange}
        >
          {t`Search`}
        </Button>
        {customRange ? (
          // Icon only, so the date inputs still fit on the same row
          <Tooltip label={t`Download Excel`}>
            <ActionIcon
              variant="light"
              size={36}
              aria-label={t`Download Excel`}
              onClick={handleExport}
              loading={exporting}
              disabled={invalidRange}
            >
              <IconFileSpreadsheet size={18} />
            </ActionIcon>
          </Tooltip>
        ) : (
          <Button
            style={{ flexShrink: 0 }}
            variant="light"
            leftSection={<IconFileSpreadsheet size={18} />}
            onClick={handleExport}
            loading={exporting}
            disabled={invalidRange}
          >
            {t`Download Excel`}
          </Button>
        )}
      </Group>

      {searched && (
        <InvenTreeTable
          url={apiUrl(ApiEndpoints.reports_po_stone_status)}
          tableState={table}
          columns={columns}
          props={{
            params: searched,
            dataFormatter: dataFormatter,
            enableFilters: false,
            enableDownload: false,
            enableColumnCaching: false,
            noRecordsText: t`No P.O. lines found for the selected filters`,
          }}
        />
      )}
    </>
  );
}
