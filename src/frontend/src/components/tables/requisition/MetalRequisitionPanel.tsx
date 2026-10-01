import { t } from "@lingui/core/macro";
import { Alert, Box, Button, Group, Stack, Text } from "@mantine/core";
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
import MetalRequisitionTable from "./MetalRequisitionTable";
import "./stoneRequisition.css";
import type { MetalRequisitionResponse } from "./types";

interface Option {
  value: string;
  label: string;
}

export default function MetalRequisitionPanel() {
  const [poIds, setPoIds] = useState<string[]>([]);
  // The P.O. ids the data on screen was fetched with
  const [fetchedPoIds, setFetchedPoIds] = useState<string[] | null>(null);

  const api = useApi();
  const poFieldId = useId();
  const colors = useSelectFieldColors();

  const [poSearch, setPoSearch] = useState("");
  const [debouncedPoSearch] = useDebouncedValue(poSearch, 300);
  const [poLabels, setPoLabels] = useState<Record<string, string>>({});

  const poQuery = useQuery({
    queryKey: ["requisition-metal-po-search", debouncedPoSearch],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.purchase_api), {
          params: { potype: "ORDER", search: debouncedPoSearch, limit: 50 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
  });

  const poOptions: Option[] = useMemo(
    () =>
      (poQuery.data ?? []).map((po: any) => ({
        value: String(po.pk),
        label: po.pono || `#${po.pk}`,
      })),
    [poQuery.data],
  );

  const poValue = useMemo(
    () => poIds.map((po) => ({ value: po, label: poLabels[po] ?? po })),
    [poIds, poLabels],
  );

  const handlePoChange = (options: readonly Option[]) => {
    setPoIds(options.map((option) => option.value));
    setPoLabels((previous) => ({
      ...previous,
      ...Object.fromEntries(options.map((o) => [o.value, o.label])),
    }));
  };

  const dataQuery = useQuery<MetalRequisitionResponse>({
    queryKey: ["requisition-metal", fetchedPoIds],
    enabled: !!fetchedPoIds,
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.requisition_metal), {
          params: { po: (fetchedPoIds ?? []).join(",") },
        })
        .then((response) => response.data),
  });

  const handleGetData = () => {
    setFetchedPoIds(poIds);
  };

  const result = dataQuery.data;

  return (
    <Stack gap="md">
      <Group align="flex-end" gap="md" wrap="nowrap">
        <Box style={{ flex: 1 }}>
          <Select
            id={poFieldId}
            aria-label={t`P.O.`}
            isMulti
            isClearable
            options={poOptions}
            value={poValue}
            onChange={(options: any) => handlePoChange(options ?? [])}
            inputValue={poSearch}
            onInputChange={(input, { action }) => {
              // Keep the typed search when the menu closes on a selection
              if (action === "input-change") setPoSearch(input);
            }}
            filterOption={null}
            isLoading={poQuery.isFetching}
            placeholder={t`P.O.`}
            noOptionsMessage={() => t`No purchase orders found`}
            menuPortalTarget={document.body}
            menuPosition="fixed"
            styles={selectFieldStyles}
            theme={(theme) => ({
              ...theme,
              colors: { ...theme.colors, ...colors },
            })}
          />
        </Box>
        <Button
          onClick={handleGetData}
          loading={dataQuery.isFetching}
          disabled={poIds.length == 0}
        >
          {t`Get Data`}
        </Button>
      </Group>

      <div className="sr-title">{t`Metal Order Requisition`}</div>

      {dataQuery.isError && (
        <Alert color="red" title={t`Error`}>
          {(dataQuery.error as any)?.response?.data?.detail ??
            t`Failed to load the metal requisition data`}
        </Alert>
      )}

      {result &&
        (result.data.length ? (
          <MetalRequisitionTable
            data={result.data}
            grandTotals={result.grand_totals}
            poLabels={poLabels}
          />
        ) : (
          <Text c="dimmed">{t`No metal found for the selected P.O.`}</Text>
        ))}
    </Stack>
  );
}
