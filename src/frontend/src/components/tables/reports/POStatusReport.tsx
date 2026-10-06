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
import { generateUrl } from "@helpers/urls";
import {
  selectFieldStyles,
  useSelectFieldColors,
} from "../../forms/fields/SelectFieldTheme";

import "./poStatus.css";

type Value = number | string | null | undefined;

interface POOption {
  value: string;
  label: string;
  podate: string | null;
  vendorName: string | null;
}

/** A P.O. line (one style) as returned by the P.O. status endpoint */
interface POStatusLine {
  image: string | null;
  styleno: string | null;
  sets: Value;
  dia_sent_date: string | null;
  dia_sent_sets: Value;
  dia_sent_cts: Value;
  dia_sent_inv: string | null;
  col_sent_date: string | null;
  col_sent_sets: Value;
  col_sent_cts: Value;
  col_sent_inv: string | null;
  rec_date: string | null;
  rec_sets: Value;
  rec_dia_cts: Value;
  rec_col_cts: Value;
  rec_inv: string | null;
  bal_sets: Value;
  bal_dia_cts: Value;
  bal_col_cts: Value;
}

type Column = {
  key: keyof POStatusLine;
  title: string;
  tint?: boolean;
};

const ROW_LIMIT = 500;

function cell(value: Value): string {
  return value === null || value === undefined ? "" : String(value);
}


export default function POStatusReport() {
  const api = useApi();
  const colors = useSelectFieldColors();
  const poFieldId = useId();

  const [po, setPo] = useState<POOption | null>(null);
  const [poSearch, setPoSearch] = useState("");
  const [debouncedPoSearch] = useDebouncedValue(poSearch, 300);

  const [exporting, setExporting] = useState(false);

  const selectTheme = (theme: any) => ({
    ...theme,
    colors: { ...theme.colors, ...colors },
  });

  // Data columns after "#", "Image", "Style" and "# Of Sets"
  const columns: Column[] = [
    { key: "dia_sent_date", title: t`Date`, tint: true },
    { key: "dia_sent_sets", title: t`# Of Sets`, tint: true },
    { key: "dia_sent_cts", title: t`Cts.`, tint: true },
    { key: "dia_sent_inv", title: t`Inv.#`, tint: true },
    { key: "col_sent_date", title: t`Date` },
    { key: "col_sent_sets", title: t`# Of Sets` },
    { key: "col_sent_cts", title: t`Cts.` },
    { key: "col_sent_inv", title: t`Inv.#` },
    { key: "rec_date", title: t`Date`, tint: true },
    { key: "rec_sets", title: t`# Of Sets`, tint: true },
    { key: "rec_dia_cts", title: t`Diamond Cts.`, tint: true },
    { key: "rec_col_cts", title: t`Color Stone Cts.`, tint: true },
    { key: "rec_inv", title: t`Inv.#`, tint: true },
    { key: "bal_sets", title: t`# Of Sets` },
    { key: "bal_dia_cts", title: t`Diamond Cts.` },
    { key: "bal_col_cts", title: t`Color Stone Cts.` },
  ];

  // --- P.O. options ------------------------------------------------------
  const poQuery = useQuery({
    queryKey: ["po-status-po-search", debouncedPoSearch],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.purchase_api), {
          params: {
            potype: "ORDER",
            active: true,
            search: debouncedPoSearch,
            ordering: "-podate",
            limit: 100,
          },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
  });

  const poOptions: POOption[] = useMemo(
    () =>
      (poQuery.data ?? []).map((order: any) => ({
        value: String(order.pk),
        label: order.pono ?? `#${order.pk}`,
        podate: order.podate ?? null,
        vendorName: order.vendor_name ?? null,
      })),
    [poQuery.data],
  );

  // --- Report lines -------------------------------------------------------
  // The P.O. the data on screen was fetched with
  const [fetched, setFetched] = useState<POOption | null>(null);

  const dataQuery = useQuery<POStatusLine[]>({
    queryKey: ["po-status-data", fetched?.value],
    enabled: !!fetched,
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.reports_po_status), {
          params: {
            poid: fetched?.value,
            limit: ROW_LIMIT,
            offset: 0,
          },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
  });

  const handleGetData = () => {
    if (po) setFetched(po);
  };

  /* The export builds the workbook server side and returns a DataOutput
   * record, whose "output" holds the file to download.
   */
  const handleExport = () => {
    if (!po) return;

    setExporting(true);
    api
      .get(apiUrl(ApiEndpoints.reports_po_status), {
        params: {
          poid: po.value,
          export: true,
          export_format: "xlsx",
        },
      })
      .then((response) => {
        const output = response.data?.output;
        if (!output) throw new Error("No output file");
        window.open(generateUrl(output), "_blank");
      })
      .catch(() => {
        notifications.show({
          title: t`Export failed`,
          message: t`Could not export the P.O. status report`,
          color: "red",
        });
      })
      .finally(() => setExporting(false));
  };

  const poDate = fetched?.podate
    ? dayjs(fetched.podate).format("DD MMM YYYY")
    : "";

  return (
    <Stack gap="md">
      <Group align="flex-end" gap="md" wrap="nowrap">
        <Box style={{ flex: 1, maxWidth: 420 }}>
          <Select
            id={poFieldId}
            aria-label={t`P.O. No.`}
            isClearable
            options={poOptions}
            value={po}
            onChange={(option: any) => setPo(option ?? null)}
            inputValue={poSearch}
            onInputChange={(input, { action }) => {
              // Keep the typed search when the menu closes on a selection
              if (action === "input-change") setPoSearch(input);
            }}
            filterOption={null}
            formatOptionLabel={(option: POOption, { context }) =>
              context === "menu" && option.vendorName
                ? `${option.label} (${option.vendorName})`
                : option.label
            }
            isLoading={poQuery.isFetching}
            placeholder={t`P.O. No.`}
            noOptionsMessage={() => t`No P.O.s found`}
            menuPortalTarget={document.body}
            menuPosition="fixed"
            styles={selectFieldStyles}
            theme={selectTheme}
          />
        </Box>
        <Button
          onClick={handleGetData}
          loading={dataQuery.isFetching}
          disabled={!po}
        >
          {t`Get Data`}
        </Button>
        <Button
          variant="light"
          leftSection={<IconFileSpreadsheet size={18} />}
          onClick={handleExport}
          loading={exporting}
          disabled={!po}
        >
          {t`Download Excel`}
        </Button>
      </Group>

      {dataQuery.isError && (
        <Alert color="red" title={t`Error`}>
          {(dataQuery.error as any)?.response?.data?.detail ??
            t`Failed to load the P.O. status report`}
        </Alert>
      )}

      {fetched &&
        dataQuery.data &&
        (dataQuery.data.length ? (
          <div className="ps-sheet">
            <table className="ps-table">
              <thead>
                <tr>
                  <th colSpan={columns.length + 4} className="ps-details">
                    <span className="ps-detail">
                      <b>{t`P.O.# :`}</b>
                      {fetched.label}
                    </span>
                    <span className="ps-detail">
                      <b>{t`P.O. Date:`}</b>
                      {poDate}
                    </span>
                    <span className="ps-detail">
                      <b>{t`Vendor :`}</b>
                      {fetched.vendorName ?? ""}
                    </span>
                  </th>
                </tr>
                <tr>
                  <th rowSpan={2}>#</th>
                  <th rowSpan={2}>{t`Image`}</th>
                  <th rowSpan={2}>{t`Style`}</th>
                  <th rowSpan={2}>{t`# Of Sets`}</th>
                  <th colSpan={4} className="ps-tint">
                    {t`Diamond Sent`}
                  </th>
                  <th colSpan={4}>{t`Color Stone Sent`}</th>
                  <th colSpan={5} className="ps-tint">
                    {t`Received`}
                  </th>
                  <th colSpan={3}>{t`Balance`}</th>
                </tr>
                <tr>
                  {columns.map((column) => (
                    <th
                      key={column.key}
                      className={column.tint ? "ps-tint" : undefined}
                    >
                      {column.title}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {dataQuery.data.map((line, index) => (
                  <tr key={index}>
                    <td>{index + 1}</td>
                    <td>
                      {line.image && (
                        <img
                          className="ps-image"
                          src={generateUrl(line.image)}
                          alt={line.styleno ?? ""}
                          loading="lazy"
                        />
                      )}
                    </td>
                    <td>{cell(line.styleno)}</td>
                    <td>{cell(line.sets)}</td>
                    {columns.map((column) => (
                      <td
                        key={column.key}
                        className={column.tint ? "ps-tint" : undefined}
                      >
                        {cell(line[column.key])}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <Text c="dimmed">{t`No lines found for the selected P.O.`}</Text>
        ))}
    </Stack>
  );
}
