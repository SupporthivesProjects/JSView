import { t } from "@lingui/core/macro";
import { useCallback, useEffect, useMemo, useState } from "react";

import { ActionIcon, Tooltip } from "@mantine/core";
import { IconFilterOff } from "@tabler/icons-react";

import type { TableState } from "@lib/types/Tables";
import { ColumnSearchInput } from "./ColumnSearchInput";

/**
 * Per-column search terms for a table, keyed by the API query parameter each
 * term is sent as. Every active term is applied together, so that several
 * columns can be searched at once (multi-level / AND filtering).
 *
 * @param table : The table state the filters belong to
 */
export function useColumnFilters(table: TableState) {
  const [columnFilters, setColumnFilters] = useState<Record<string, string>>(
    {},
  );

  const setColumnFilter = useCallback((key: string, value: string) => {
    setColumnFilters((filters) => {
      if ((filters[key] ?? "") === value) {
        return filters;
      }

      const updated = { ...filters };

      if (value.trim()) {
        updated[key] = value;
      } else {
        delete updated[key];
      }

      return updated;
    });
  }, []);

  const clearColumnFilters = useCallback(() => setColumnFilters({}), []);

  const activeColumnFilters = useMemo(() => {
    const active: Record<string, string> = {};

    Object.entries(columnFilters).forEach(([key, value]) => {
      if (value.trim()) {
        active[key] = value.trim();
      }
    });

    return active;
  }, [columnFilters]);

  // Jump back to the first page whenever the column search terms change
  useEffect(() => {
    table.setPage(1);
  }, [activeColumnFilters]);

  // Build the inline search popover for a given column
  const columnFilter = useCallback(
    (key: string, label: string, placeholder?: string) => ({
      filtering: !!activeColumnFilters[key],
      filter: () => (
        <ColumnSearchInput
          label={label}
          placeholder={placeholder}
          value={columnFilters[key] ?? ""}
          onChange={(value: string) => setColumnFilter(key, value)}
        />
      ),
    }),
    [columnFilters, activeColumnFilters, setColumnFilter],
  );

  // Toolbar action which drops every active column search term at once
  const clearColumnFiltersAction = useMemo(
    () => (
      <Tooltip key="clear-column-filters" label={t`Clear column filters`}>
        <ActionIcon
          variant="transparent"
          aria-label="clear-column-filters"
          disabled={Object.keys(activeColumnFilters).length === 0}
          onClick={clearColumnFilters}
        >
          <IconFilterOff />
        </ActionIcon>
      </Tooltip>
    ),
    [activeColumnFilters, clearColumnFilters],
  );

  return {
    activeColumnFilters,
    columnFilter,
    clearColumnFilters,
    clearColumnFiltersAction,
  };
}
