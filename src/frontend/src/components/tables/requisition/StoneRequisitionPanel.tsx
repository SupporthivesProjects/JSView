import { t } from "@lingui/core/macro";
import { Box, Button, Group, Input, Stack, Text } from "@mantine/core";
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

export type StoneViewType = "details" | "summary";
export type StoneType = "DIAMOND" | "COLOURSTONE";
export type StonePlace = "NONE" | "SIDE" | "CENTER";

export interface StoneRequisitionFilters {
  view_type: StoneViewType;
  stone_place: StonePlace;
  stone_type: StoneType;
  show_rate: boolean;
  po: string[];
}

interface Option {
  value: string;
  label: string;
}

const FILTER_COL = { flex: "1 1 160px", minWidth: 160 };

function FilterSelect({
  label,
  options,
  value,
  onChange,
}: Readonly<{
  label: string;
  options: Option[];
  value: string;
  onChange: (value: string) => void;
}>) {
  const fieldId = useId();
  const colors = useSelectFieldColors();

  const currentValue = useMemo(
    () => options.find((option) => option.value === value) ?? null,
    [options, value],
  );

  return (
    <Input.Wrapper label={label}>
      <Select
        id={fieldId}
        aria-label={label}
        options={options}
        value={currentValue}
        onChange={(option: any) => option?.value && onChange(option.value)}
        isClearable={false}
        isSearchable={false}
        menuPortalTarget={document.body}
        menuPosition="fixed"
        styles={selectFieldStyles}
        theme={(theme) => ({
          ...theme,
          colors: { ...theme.colors, ...colors },
        })}
      />
    </Input.Wrapper>
  );
}

export default function StoneRequisitionPanel() {
  const [viewType, setViewType] = useState<StoneViewType>("details");
  const [stonePlace, setStonePlace] = useState<StonePlace>("NONE");
  const [stoneType, setStoneType] = useState<StoneType>("DIAMOND");
  const [showRate, setShowRate] = useState<"yes" | "no">("no");
  const [poIds, setPoIds] = useState<string[]>([]);

  const [, setFilters] = useState<StoneRequisitionFilters | null>(null);

  const api = useApi();
  const poFieldId = useId();
  const colors = useSelectFieldColors();

  // P.O. search is run against the API, so the labels of the selected orders
  // are kept here - a new search replaces the available options
  const [poSearch, setPoSearch] = useState("");
  const [debouncedPoSearch] = useDebouncedValue(poSearch, 300);
  const [poLabels, setPoLabels] = useState<Record<string, string>>({});

  const poQuery = useQuery({
    queryKey: ["requisition-stone-po-search", debouncedPoSearch],
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

  const currentFilters = (): StoneRequisitionFilters => ({
    view_type: viewType,
    stone_place: stonePlace,
    stone_type: stoneType,
    show_rate: showRate === "yes",
    po: poIds,
  });

  const handleGetData = () => {
    setFilters(currentFilters());
  };

  const handleExport = () => {
    currentFilters();
  };

  const listTitle =
    stoneType === "DIAMOND"
      ? t`Diamond Order List`
      : t`Colour Stone Order List`;

  return (
    <Stack gap="md">
      <Group align="flex-end" gap="md" wrap="wrap">
        <Box style={FILTER_COL}>
          <FilterSelect
            label={t`View Type`}
            options={[
              { value: "details", label: t`Details` },
              { value: "summary", label: t`Summary` },
            ]}
            value={viewType}
            onChange={(value) => setViewType(value as StoneViewType)}
          />
        </Box>
        <Box style={FILTER_COL}>
          <FilterSelect
            label={t`Stone Place`}
            options={[
              { value: "NONE", label: t`None` },
              { value: "SIDE", label: t`Side` },
              { value: "CENTER", label: t`Center` },
            ]}
            value={stonePlace}
            onChange={(value) => setStonePlace(value as StonePlace)}
          />
        </Box>
        <Box style={FILTER_COL}>
          <FilterSelect
            label={t`Stone Type`}
            options={[
              { value: "DIAMOND", label: t`Diamond` },
              { value: "COLOURSTONE", label: t`Colour Stone` },
            ]}
            value={stoneType}
            onChange={(value) => setStoneType(value as StoneType)}
          />
        </Box>
        <Box style={FILTER_COL}>
          <FilterSelect
            label={t`Show Rate`}
            options={[
              { value: "no", label: t`No` },
              { value: "yes", label: t`Yes` },
            ]}
            value={showRate}
            onChange={(value) => setShowRate(value as "yes" | "no")}
          />
        </Box>
        <Button onClick={handleGetData}>{t`Get Data`}</Button>
      </Group>
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
        <Button variant="outline" onClick={handleExport}>
          {t`Export`}
        </Button>
      </Group>

      <Text fw={700} td="underline" tt="uppercase">
        {listTitle}
      </Text>
    </Stack>
  );
}
