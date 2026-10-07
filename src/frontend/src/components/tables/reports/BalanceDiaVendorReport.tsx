import { t } from "@lingui/core/macro";
import {
  Button,
  Group,
  Paper,
  SimpleGrid,
  Stack,
  Text,
  Title,
} from "@mantine/core";
import { DateInput } from "@mantine/dates";
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

const DATE_FORMAT = "YYYY-MM-DD";

interface VendorOption {
  value: string;
  label: string;
}

/** Searchable vendor dropdown; selected vendors are shown as chips */
function VendorMultiSelect({
  value,
  onChange,
}: {
  value: VendorOption[];
  onChange: (options: VendorOption[]) => void;
}) {
  const api = useApi();
  const colors = useSelectFieldColors();
  const fieldId = useId();

  const [search, setSearch] = useState("");
  const [debouncedSearch] = useDebouncedValue(search, 300);

  const query = useQuery({
    queryKey: ["bal-dia-vendor-company", debouncedSearch],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.master_vendor_customer), {
          params: {
            is_supplier: true,
            active: true,
            search: debouncedSearch,
            limit: 50,
          },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
  });

  const options: VendorOption[] = useMemo(
    () =>
      (query.data ?? []).map((company: any) => ({
        value: String(company.pk),
        label: company.name ?? company.code ?? `#${company.pk}`,
      })),
    [query.data],
  );

  return (
    <Select
      id={fieldId}
      aria-label={t`Vendor`}
      isMulti
      isClearable
      closeMenuOnSelect={false}
      options={options}
      value={value}
      onChange={(selected: any) => onChange([...(selected ?? [])])}
      inputValue={search}
      onInputChange={(input, { action }) => {
        // Keep the typed search when the menu closes on a selection
        if (action === "input-change") setSearch(input);
      }}
      filterOption={null}
      isLoading={query.isFetching}
      placeholder={t`All vendors`}
      noOptionsMessage={() => t`No vendors found`}
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

export default function BalanceDiaVendorReport() {
  const api = useApi();

  const [vendors, setVendors] = useState<VendorOption[]>([]);
  const [dateFrom, setDateFrom] = useState<string | null>(null);
  const [dateTo, setDateTo] = useState<string | null>(null);

  const [exporting, setExporting] = useState(false);
  const [exportId, setExportId] = useState<number | undefined>(undefined);

  useDataOutput({
    title: t`Exporting Balance Dia. With Vendor Report`,
    id: exportId,
  });

  const invalidRange =
    !!dateFrom && !!dateTo && dayjs(dateFrom).isAfter(dayjs(dateTo));

  /* The export builds the workbook server side and returns a DataOutput
   * record, which is then monitored until the file can be downloaded.
   */
  const handleExport = () => {
    if (invalidRange) return;

    const params: Record<string, any> = {
      export: true,
      export_format: "xlsx",
    };

    // The API accepts several vendors as a comma separated vendorid
    if (vendors.length > 0) {
      params.vendorid = vendors.map((vendor) => vendor.value).join(",");
    }
    if (dateFrom) params.date_from = dayjs(dateFrom).format(DATE_FORMAT);
    if (dateTo) params.date_to = dayjs(dateTo).format(DATE_FORMAT);

    setExporting(true);
    api
      .get(apiUrl(ApiEndpoints.reports_bal_dia_with_vendor), { params })
      .then((response) => setExportId(response.data?.pk))
      .catch(() => {
        notifications.show({
          title: t`Export failed`,
          message: t`Could not export the balance dia. with vendor report`,
          color: "red",
        });
      })
      .finally(() => setExporting(false));
  };

  return (
    <Paper withBorder p="lg" radius="md" maw={720}>
      <Stack gap="md">
        <div>
          <Title order={4}>{t`Balance Dia. With Vendor`}</Title>
          <Text size="sm" c="dimmed">
            {t`Download the diamond balance held with vendors as an Excel file. Leave the filters empty to include all vendors and dates.`}
          </Text>
        </div>

        <Stack gap={4}>
          <Text size="sm" fw={500}>{t`Vendor`}</Text>
          <VendorMultiSelect value={vendors} onChange={setVendors} />
        </Stack>

        <SimpleGrid cols={{ base: 1, sm: 2 }} spacing="md">
          <DateInput
            label={t`P.O. Date From`}
            placeholder={t`Select date`}
            value={dateFrom}
            onChange={setDateFrom}
            valueFormat="DD MMM YYYY"
            maxDate={dateTo ?? undefined}
            clearable
          />
          <DateInput
            label={t`P.O. Date To`}
            placeholder={t`Select date`}
            value={dateTo}
            onChange={setDateTo}
            valueFormat="DD MMM YYYY"
            minDate={dateFrom ?? undefined}
            error={invalidRange ? t`Must be after the From date` : undefined}
            clearable
          />
        </SimpleGrid>

        <Group justify="flex-end">
          <Button
            leftSection={<IconFileSpreadsheet size={18} />}
            onClick={handleExport}
            loading={exporting}
            disabled={invalidRange}
          >
            {t`Download Excel`}
          </Button>
        </Group>
      </Stack>
    </Paper>
  );
}
