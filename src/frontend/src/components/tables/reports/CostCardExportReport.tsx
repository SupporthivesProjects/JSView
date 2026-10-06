import { t } from "@lingui/core/macro";
import { Box, Button, Group, SimpleGrid, TextInput } from "@mantine/core";
import { useDebouncedValue, useId } from "@mantine/hooks";
import { notifications } from "@mantine/notifications";
import { IconFileSpreadsheet, IconSearch } from "@tabler/icons-react";
import { useQuery } from "@tanstack/react-query";
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

interface LookupOption {
  value: string;
  label: string;
}

/** Searchable dropdown backed by a list endpoint (companies or master data) */
function LookupSelect({
  label,
  endpoint,
  params,
  optionLabel,
  value,
  onChange,
}: {
  label: string;
  endpoint: ApiEndpoints;
  params?: Record<string, any>;
  optionLabel: (item: any) => string;
  value: LookupOption | null;
  onChange: (option: LookupOption | null) => void;
}) {
  const api = useApi();
  const colors = useSelectFieldColors();
  const fieldId = useId();

  const [search, setSearch] = useState("");
  const [debouncedSearch] = useDebouncedValue(search, 300);

  const query = useQuery({
    queryKey: ["cost-card-export-lookup", endpoint, params, debouncedSearch],
    queryFn: () =>
      api
        .get(apiUrl(endpoint), {
          params: {
            ...params,
            active: true,
            search: debouncedSearch,
            limit: 50,
          },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
  });

  const options: LookupOption[] = useMemo(
    () =>
      (query.data ?? []).map((item: any) => ({
        value: String(item.pk),
        label: optionLabel(item) ?? `#${item.pk}`,
      })),
    [query.data, optionLabel],
  );

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
      noOptionsMessage={() => t`No results found`}
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

const companyName = (company: any) => company.name ?? company.code;
const masterName = (item: any) => item.name;

export default function CostCardExportReport() {
  const api = useApi();
  const table = useTable("cost-card-export", { idAccessor: "_row" });

  const [costCardNo, setCostCardNo] = useState("");
  const [ourStyleNo, setOurStyleNo] = useState("");
  const [vendorStyleNo, setVendorStyleNo] = useState("");
  const [customer, setCustomer] = useState<LookupOption | null>(null);
  const [vendor, setVendor] = useState<LookupOption | null>(null);
  const [category, setCategory] = useState<LookupOption | null>(null);
  const [subCategory, setSubCategory] = useState<LookupOption | null>(null);
  const [metalPurity, setMetalPurity] = useState<LookupOption | null>(null);

  const [exporting, setExporting] = useState(false);
  const [exportId, setExportId] = useState<number | undefined>(undefined);

  useDataOutput({
    title: t`Exporting Cost Card Export Report`,
    id: exportId,
  });

  // Filter params shared by the table and the export
  const filterParams = useMemo(() => {
    const params: Record<string, any> = {};

    if (costCardNo.trim()) params.cost_card_no = costCardNo.trim();
    if (ourStyleNo.trim()) params.our_style_no = ourStyleNo.trim();
    if (vendorStyleNo.trim()) params.vendor_style_no = vendorStyleNo.trim();
    if (customer) params.customer = customer.value;
    if (vendor) params.vendor = vendor.value;
    if (category) params.category = category.value;
    if (subCategory) params.sub_category = subCategory.value;
    if (metalPurity) params.metal_purity = metalPurity.value;

    return params;
  }, [
    costCardNo,
    ourStyleNo,
    vendorStyleNo,
    customer,
    vendor,
    category,
    subCategory,
    metalPurity,
  ]);

  // Sub categories are listed for the chosen category, so a sub category
  // from another category no longer applies
  const handleCategoryChange = (option: LookupOption | null) => {
    setCategory(option);
    if (option?.value !== category?.value) setSubCategory(null);
  };

  const subCategoryParams = useMemo(
    () => (category ? { category: category.value } : undefined),
    [category],
  );

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

    const figure = (accessor: string, title: string, ordering?: string) => ({
      accessor,
      title,
      sortable: !!ordering,
      ordering,
      textAlign: "right" as const,
    });

    return [
      text("cost_card_no", t`Cost Card No.`, "cost_card_no"),
      text("customer", t`Customer`),
      text("vendor", t`Vendor`),
      text("style", t`Style`, "our_style_no"),
      text("v_style", t`V.Style`),
      text("category", t`Category`),
      text("sub_category", t`Sub Category`),
      text("date", t`Date`, "created_at"),
      text("metal", t`Metal`),
      figure("tr_oz", t`Tr.Oz`),
      figure("kt", t`Kt`),
      figure("net_wt", t`Net Wt.`),
      figure("metal_loss_pct", t`Metal Loss %`),
      figure("metal_amount", t`Metal Amount`),
      figure("dia_pcs", t`Dia. Pcs`),
      figure("dia_cts", t`Dia. Cts`),
      figure("dia_amount", t`Dia. Amount`),
      figure("col_pcs", t`Col. Pcs`),
      figure("col_cts", t`Col. Cts`),
      figure("col_amount", t`Col. Amount`),
      figure("studding", t`Studding`),
      figure("labour", t`Labour`),
      text("finding", t`Finding`),
      figure("finding_amount", t`Finding Amount`),
      figure("markup_pct", t`Markup%`),
      figure("with_markup", t`With Markup%`),
      figure("fob", t`FOB`),
      figure("duty_pct", t`Duty%`),
      figure("with_duty", t`With Duty`),
      figure("margin_pct", t`Margin%`),
      figure("final_amount", t`Final Amount`, "final_amount"),
    ];
  }, []);

  /* The export builds the workbook server side and returns a DataOutput
   * record, which is then monitored until the file can be downloaded.
   */
  const handleExport = () => {
    setExporting(true);
    api
      .get(apiUrl(ApiEndpoints.reports_cost_card_export), {
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
          message: t`Could not export the cost card report`,
          color: "red",
        });
      })
      .finally(() => setExporting(false));
  };

  // The filters the data on screen was searched with; nothing loads until
  // the first search
  const [searched, setSearched] = useState<Record<string, any> | null>(null);

  const handleSearch = () => {
    setSearched(filterParams);
    // Reload even when searching again with unchanged filters
    table.refreshTable();
  };

  const searchOnEnter = (event: React.KeyboardEvent) => {
    if (event.key === "Enter") handleSearch();
  };

  return (
    <>
      <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="sm" mb="sm">
        <TextInput
          aria-label={t`Cost Card No`}
          placeholder={t`Cost Card No`}
          value={costCardNo}
          onChange={(event) => setCostCardNo(event.currentTarget.value)}
          onKeyDown={searchOnEnter}
        />
        <TextInput
          aria-label={t`Our Style No`}
          placeholder={t`Our Style No`}
          value={ourStyleNo}
          onChange={(event) => setOurStyleNo(event.currentTarget.value)}
          onKeyDown={searchOnEnter}
        />
        <TextInput
          aria-label={t`Vendor Style No`}
          placeholder={t`Vendor Style No`}
          value={vendorStyleNo}
          onChange={(event) => setVendorStyleNo(event.currentTarget.value)}
          onKeyDown={searchOnEnter}
        />
        <Box>
          <LookupSelect
            label={t`Customer`}
            endpoint={ApiEndpoints.master_vendor_customer}
            params={{ is_customer: true }}
            optionLabel={companyName}
            value={customer}
            onChange={setCustomer}
          />
        </Box>
        <Box>
          <LookupSelect
            label={t`Vendor`}
            endpoint={ApiEndpoints.master_vendor_customer}
            params={{ is_supplier: true }}
            optionLabel={companyName}
            value={vendor}
            onChange={setVendor}
          />
        </Box>
        <Box>
          <LookupSelect
            label={t`Jewelry Category`}
            endpoint={ApiEndpoints.jewellery_category}
            optionLabel={masterName}
            value={category}
            onChange={handleCategoryChange}
          />
        </Box>
        <Box>
          <LookupSelect
            label={t`Jewelry Sub Category`}
            endpoint={ApiEndpoints.jewellery_sub_category}
            params={subCategoryParams}
            optionLabel={masterName}
            value={subCategory}
            onChange={setSubCategory}
          />
        </Box>
        <Box>
          <LookupSelect
            label={t`Metal Purity`}
            endpoint={ApiEndpoints.metal_purity_list}
            optionLabel={masterName}
            value={metalPurity}
            onChange={setMetalPurity}
          />
        </Box>
      </SimpleGrid>

      <Group justify="flex-end" gap="sm" mb="md">
        <Button leftSection={<IconSearch size={18} />} onClick={handleSearch}>
          {t`Search`}
        </Button>
        <Button
          variant="light"
          leftSection={<IconFileSpreadsheet size={18} />}
          onClick={handleExport}
          loading={exporting}
        >
          {t`Download Excel`}
        </Button>
      </Group>

      {searched && (
        <InvenTreeTable
          url={apiUrl(ApiEndpoints.reports_cost_card_export)}
          tableState={table}
          columns={columns}
          props={{
            params: searched,
            dataFormatter: dataFormatter,
            enableFilters: false,
            enableDownload: false,
            enableColumnCaching: false,
            noRecordsText: t`No cost cards found for the selected filters`,
          }}
        />
      )}
    </>
  );
}
