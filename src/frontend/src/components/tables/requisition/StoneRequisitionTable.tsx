import { t } from "@lingui/core/macro";
import {
  Alert,
  Box,
  Button,
  Group,
  Loader,
  MultiSelect,
  Paper,
  ScrollArea,
  Select,
  SimpleGrid,
  Stack,
  Table,
  Text,
} from "@mantine/core";
import { useDebouncedValue } from "@mantine/hooks";
import { useQuery } from "@tanstack/react-query";
import { useMemo, useState } from "react";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { apiUrl } from "@lib/functions/Api";
import { ApiImage } from "@components/shared/images/ApiImage";
import { useApi } from "@context/ApiContext";
import useDataOutput from "../../../hooks/UseDataOutput";

type ViewType = "details" | "summary";

interface StoneFilters {
  po: string[];
  view_type: ViewType;
  stone_type: string;
  stone_place: string | null;
  show_rate: boolean;
}

interface Column {
  accessor: string;
  title: string;
  image?: boolean;
}

const BLANK_IMAGE = "/static/img/blank_image.png";

function detailColumns(showRate: boolean): Column[] {
  return [
    { accessor: "sr_no", title: t`Sr. No.` },
    { accessor: "style_no", title: t`Style No.` },
    { accessor: "front_view", title: t`Image`, image: true },
    { accessor: "category", title: t`Category` },
    { accessor: "setting", title: t`Setting` },
    { accessor: "stone", title: t`Stone` },
    { accessor: "shape", title: t`Shape` },
    { accessor: "cut", title: t`Cut` },
    { accessor: "colour", title: t`Colour` },
    { accessor: "quality", title: t`Quality` },
    { accessor: "mm_size", title: t`MM Size` },
    { accessor: "sieve_size", title: t`Sieve Size` },
    { accessor: "pointer", title: t`Pointer` },
    { accessor: "pcs", title: t`Pcs` },
    { accessor: "cts", title: t`Cts` },
    { accessor: "po_qty", title: t`P.O. Qty` },
    { accessor: "total_pcs", title: t`Total Pcs` },
    { accessor: "total_cts", title: t`Total Cts` },
    ...(showRate
      ? [
          { accessor: "rate", title: t`Rate` },
          { accessor: "amount", title: t`Amount` },
        ]
      : []),
  ];
}

function summaryColumns(): Column[] {
  return [
    { accessor: "sr_no", title: t`Sr. No.` },
    { accessor: "stone", title: t`Stone` },
    { accessor: "shape", title: t`Shape` },
    { accessor: "cut", title: t`Cut` },
    { accessor: "colour", title: t`Colour` },
    { accessor: "quality", title: t`Quality` },
    { accessor: "mm_size", title: t`MM Size` },
    { accessor: "sieve_size", title: t`Sieve Size` },
    { accessor: "pointer", title: t`Pointer` },
    { accessor: "total_pcs", title: t`Total Pcs` },
    { accessor: "total_cts", title: t`Total Cts` },
  ];
}

function buildParams(filters: StoneFilters, exportData = false) {
  const params: Record<string, string> = {
    po: filters.po.join(","),
    stone_type: filters.stone_type,
    view_type: filters.view_type,
  };

  if (filters.stone_place) params.stone_place = filters.stone_place;
  if (filters.show_rate) params.show_rate = "yes";
  if (exportData) params.export = "true";

  return params;
}

function display(value: any) {
  return value === null || value === undefined || value === "" ? "-" : value;
}

/**
 * Plain table for requisition rows, with an optional totals footer.
 */
function RequisitionRowsTable({
  columns,
  rows,
  totals,
}: {
  columns: Column[];
  rows: any[];
  totals?: { pcs: any; cts: any };
}) {
  return (
    <ScrollArea type="auto">
      <Table striped withTableBorder withColumnBorders highlightOnHover>
        <Table.Thead>
          <Table.Tr>
            {columns.map((col) => (
              <Table.Th key={col.accessor} style={{ whiteSpace: "nowrap" }}>
                {col.title}
              </Table.Th>
            ))}
          </Table.Tr>
        </Table.Thead>
        <Table.Tbody>
          {rows.map((row, idx) => (
            <Table.Tr key={`${row.sr_no}-${idx}`}>
              {columns.map((col) => (
                <Table.Td key={col.accessor} style={{ whiteSpace: "nowrap" }}>
                  {col.image ? (
                    <Box w={32}>
                      <ApiImage
                        src={row[col.accessor] || BLANK_IMAGE}
                        w={32}
                        h={32}
                        fit="contain"
                        radius="xs"
                      />
                    </Box>
                  ) : (
                    display(row[col.accessor])
                  )}
                </Table.Td>
              ))}
            </Table.Tr>
          ))}
        </Table.Tbody>
        {totals && (
          <Table.Tfoot>
            <Table.Tr>
              {columns.map((col, idx) => (
                <Table.Th key={col.accessor}>
                  {idx === 0
                    ? t`Total`
                    : col.accessor === "total_pcs"
                      ? totals.pcs
                      : col.accessor === "total_cts"
                        ? totals.cts
                        : ""}
                </Table.Th>
              ))}
            </Table.Tr>
          </Table.Tfoot>
        )}
      </Table>
    </ScrollArea>
  );
}

function PoHeader({ po }: { po: any }) {
  const fields: [string, any][] = [
    [t`P.O. No.`, po.po_no],
    [t`P.O. Date`, po.po_date],
    [t`Due Date`, po.due_date],
    [t`Customer`, po.customer],
    [t`Vendor`, po.vendor],
    [t`Stone Ship Date`, po.stone_ship_date],
    [t`Prepared By`, po.prepared],
    [t`A/C Exe.`, po.ac_exe],
    [t`Category`, po.category],
    [t`Remarks`, po.remarks],
  ];

  return (
    <SimpleGrid cols={{ base: 2, sm: 3, lg: 5 }} spacing="xs" verticalSpacing={4}>
      {fields.map(([label, value]) => (
        <Text size="sm" key={label}>
          <Text span fw={600}>
            {label}:
          </Text>{" "}
          {display(value)}
        </Text>
      ))}
    </SimpleGrid>
  );
}

export default function StoneRequisitionTable() {
  const api = useApi();

  const [viewType, setViewType] = useState<ViewType>("details");
  const [stonePlace, setStonePlace] = useState<string | null>(null);
  const [stoneType, setStoneType] = useState<string>("DIAMOND");
  const [showRate, setShowRate] = useState<string>("no");
  const [poIds, setPoIds] = useState<string[]>([]);

  // Filters are only applied when "Get Data" is pressed
  const [filters, setFilters] = useState<StoneFilters | null>(null);

  // P.O. search: keep labels of selected orders so they survive new searches
  const [poSearch, setPoSearch] = useState("");
  const [debouncedPoSearch] = useDebouncedValue(poSearch, 300);
  const [poLabels, setPoLabels] = useState<Record<string, string>>({});

  const poQuery = useQuery({
    queryKey: ["requisition-stone-po-search", debouncedPoSearch],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.purchase_api), {
          params: { search: debouncedPoSearch, limit: 50 },
        })
        .then((res) => res.data?.results ?? res.data ?? []),
  });

  const poOptions = useMemo(() => {
    const options: Record<string, string> = { ...poLabels };
    (poQuery.data ?? []).forEach((po: any) => {
      options[String(po.pk)] = po.pono || `#${po.pk}`;
    });
    return Object.entries(options).map(([value, label]) => ({ value, label }));
  }, [poQuery.data, poLabels]);

  const stonePlaceQuery = useQuery({
    queryKey: ["requisition-stone-place-options"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.stone_place), { params: { limit: 1000 } })
        .then((res) => res.data?.results ?? res.data ?? []),
    staleTime: 5 * 60 * 1000,
  });

  // The backend filters on the frozen stone place *name*
  const stonePlaceOptions = useMemo(
    () =>
      (stonePlaceQuery.data ?? []).map((place: any) => ({
        value: place.name,
        label: place.name,
      })),
    [stonePlaceQuery.data],
  );

  const dataQuery = useQuery({
    queryKey: ["requisition-stone", filters],
    enabled: !!filters,
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.requisition_stone), {
          params: buildParams(filters!),
        })
        .then((res) => res.data),
  });

  const [exportId, setExportId] = useState<number | undefined>(undefined);
  const [exporting, setExporting] = useState(false);

  useDataOutput({
    title: t`Exporting Stone Requisition`,
    id: exportId,
  });

  const currentFilters = (): StoneFilters => ({
    po: poIds,
    view_type: viewType,
    stone_type: stoneType,
    stone_place: stonePlace,
    show_rate: showRate === "yes",
  });

  const handleExport = () => {
    setExporting(true);
    api
      .get(apiUrl(ApiEndpoints.requisition_stone), {
        params: buildParams(currentFilters(), true),
      })
      .then((res) => setExportId(res.data?.pk))
      .finally(() => setExporting(false));
  };

  const handlePoChange = (values: string[]) => {
    setPoIds(values);
    setPoLabels((prev) => {
      const next: Record<string, string> = {};
      const all = Object.fromEntries(poOptions.map((o) => [o.value, o.label]));
      values.forEach((v) => {
        next[v] = all[v] ?? prev[v] ?? v;
      });
      return next;
    });
  };

  const result = dataQuery.data;
  const hasPo = poIds.length > 0;

  return (
    <Stack gap="md">
      <Paper p="md" radius="sm" withBorder>
        <Group align="center" gap="xl" wrap="nowrap">
          <Stack gap="xs" style={{ flex: 1 }}>
            <SimpleGrid cols={{ base: 1, sm: 2, md: 4 }} spacing="md">
              <Select
                label={t`View Type`}
                data={[
                  { value: "details", label: t`Details` },
                  { value: "summary", label: t`Summary` },
                ]}
                value={viewType}
                onChange={(v) => setViewType((v as ViewType) ?? "details")}
                allowDeselect={false}
              />
              <Select
                label={t`Stone Place`}
                placeholder={t`Stone Place`}
                data={stonePlaceOptions}
                value={stonePlace}
                onChange={setStonePlace}
                clearable
                searchable
              />
              <Select
                label={t`Stone Type`}
                data={[
                  { value: "DIAMOND", label: t`Diamond` },
                  { value: "COLOURSTONE", label: t`Colour Stone` },
                ]}
                value={stoneType}
                onChange={(v) => setStoneType(v ?? "DIAMOND")}
                allowDeselect={false}
              />
              <Select
                label={t`Show Rate`}
                data={[
                  { value: "no", label: t`No` },
                  { value: "yes", label: t`Yes` },
                ]}
                value={showRate}
                onChange={(v) => setShowRate(v ?? "no")}
                allowDeselect={false}
                disabled={viewType === "summary"}
              />
            </SimpleGrid>
            <MultiSelect
              placeholder={t`P.O.`}
              aria-label={t`P.O.`}
              data={poOptions}
              value={poIds}
              onChange={handlePoChange}
              searchable
              searchValue={poSearch}
              onSearchChange={setPoSearch}
              filter={({ options }) => options}
              rightSection={poQuery.isFetching ? <Loader size="xs" /> : null}
              nothingFoundMessage={t`No purchase orders found`}
              clearable
            />
          </Stack>
          <Stack gap="xs">
            <Button
              onClick={() => setFilters(currentFilters())}
              disabled={!hasPo}
              loading={dataQuery.isFetching}
            >
              {t`Get Data`}
            </Button>
            <Button
              variant="outline"
              onClick={handleExport}
              disabled={!hasPo}
              loading={exporting}
            >
              {t`Export`}
            </Button>
          </Stack>
        </Group>
      </Paper>

      {dataQuery.isError && (
        <Alert color="red" title={t`Error`}>
          {(dataQuery.error as any)?.response?.data?.detail ??
            t`Failed to load stone requisition data`}
        </Alert>
      )}

      {result && result.view_type === "summary" && (
        result.data.length ? (
          <RequisitionRowsTable
            columns={summaryColumns()}
            rows={result.data}
            totals={result.totals}
          />
        ) : (
          <Text c="dimmed">{t`No stones found for the selected filters`}</Text>
        )
      )}

      {result && result.view_type === "details" && (
        result.data.length ? (
          result.data.map((po: any) => (
            <Paper key={po.po_id} p="md" radius="sm" withBorder>
              <Stack gap="sm">
                <PoHeader po={po} />
                <RequisitionRowsTable
                  columns={detailColumns(!!filters?.show_rate)}
                  rows={po.lines}
                  totals={po.totals}
                />
              </Stack>
            </Paper>
          ))
        ) : (
          <Text c="dimmed">{t`No stones found for the selected filters`}</Text>
        )
      )}
    </Stack>
  );
}
