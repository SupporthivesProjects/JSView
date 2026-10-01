import { t } from "@lingui/core/macro";
import { Box, Button, Group, Input, Stack, Text } from "@mantine/core";
import { useId } from "@mantine/hooks";
import { useMemo, useState } from "react";
import Select from "react-select";
import CreatableSelect from "react-select/creatable";

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

  const poFieldId = useId();
  const colors = useSelectFieldColors();

  const poValue = useMemo(
    () => poIds.map((po) => ({ value: po, label: po })),
    [poIds],
  );

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
        <Button onClick={handleGetData} >
          {t`Get Data`}
        </Button>
      </Group>
      <Group align="flex-end" gap="md" wrap="nowrap">
        <Box style={{ flex: 1 }}>
          <CreatableSelect
            id={poFieldId}
            aria-label={t`P.O.`}
            isMulti
            isClearable
            options={[]}
            value={poValue}
            onChange={(options: any) =>
              setPoIds((options ?? []).map((option: any) => option.value))
            }
            placeholder={t`P.O.`}
            formatCreateLabel={(input: string) => t`Add P.O. ${input}`}
            noOptionsMessage={() => t`Type a P.O. number to add it`}
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
          variant="outline"
          onClick={handleExport}
        >
          {t`Export`}
        </Button>
      </Group>

      <Text fw={700} td="underline" tt="uppercase">
        {listTitle}
      </Text>
    </Stack>
  );
}
