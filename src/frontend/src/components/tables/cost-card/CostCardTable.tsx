import { t } from "@lingui/core/macro";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useNavigate } from "react-router-dom";

import { AddItemButton } from "@lib/components/AddItemButton";
import {
  type RowAction,
  RowDeleteAction,
  RowEditAction,
} from "@lib/components/RowActions";
import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { UserRoles } from "@lib/enums/Roles";
import { apiUrl } from "@lib/functions/Api";
import useTable from "@lib/hooks/UseTable";
import type { TableFilter } from "@lib/index";
import type { TableColumn } from "@lib/types/Tables";
import { BooleanColumn } from "../ColumnRenderers";
import { InvenTreeTable } from "../InvenTreeTable";
import { useDeleteApiFormModal } from "../../../hooks/UseForm";
import { useUserState } from "@store/UserState";
import { Thumbnail } from "@components/shared/images/Thumbnail";
import {
  ActionIcon,
  Group,
  Stack,
  Text,
  TextInput,
  Tooltip,
} from "@mantine/core";
import { IconFilterOff, IconSearch, IconX } from "@tabler/icons-react";
import { useApi } from "@context/ApiContext";
import { useQuery } from "@tanstack/react-query";

// Maximum number of cost card records fetched for client-side filtering
const MAX_RECORDS = 10000;

// Number of records requested per page (the server caps this at 100)
const FETCH_LIMIT = 100;

/*
 * The cost card list endpoint only supports a single combined "search" term
 * (across cost_card_no / our_style_no / vendor_style_no) and exact-match filters
 * for the related fields - so it cannot express "filter column A by X *and*
 * column B by Y". To support multi-level filtering, the full record set is
 * pulled down once and filtered in the browser instead.
 */
const FILTERABLE_COLUMNS: { accessor: string; searchKey: string }[] = [
  { accessor: "cost_card_no", searchKey: "cost_card_no" },
  { accessor: "our_style_no", searchKey: "our_style_no" },
  { accessor: "vendor_style_no", searchKey: "vendor_style_no" },
  { accessor: "customer", searchKey: "customer_name" },
  { accessor: "vendor", searchKey: "vendor_name" },
  { accessor: "category", searchKey: "category_name" },
  { accessor: "sub_category", searchKey: "sub_category_name" },
  { accessor: "karat", searchKey: "karat" },
];

/*
 * Search box rendered inside a column header filter popover.
 *
 * The typed value is held locally and pushed upwards after a short delay, so
 * that re-rendering the (filtered) table does not interfere with typing.
 */
function ColumnSearchInput({
  label,
  value,
  onChange,
}: Readonly<{
  label: string;
  value: string;
  onChange: (value: string) => void;
}>) {
  const [text, setText] = useState<string>(value);

  const onChangeRef = useRef(onChange);
  onChangeRef.current = onChange;

  useEffect(() => {
    if (text === value) {
      return;
    }

    const timer = setTimeout(() => onChangeRef.current(text), 250);

    return () => clearTimeout(timer);
  }, [text, value]);

  return (
    <Stack gap={5} p={3} miw={230}>
      <Text size="sm" fw={600}>
        {label}
      </Text>
      <TextInput
        autoFocus
        value={text}
        placeholder={t`Search`}
        aria-label={`column-search-${label}`}
        leftSection={<IconSearch size={14} />}
        onChange={(event) => setText(event.currentTarget.value)}
        rightSection={
          text ? (
            <ActionIcon
              color="red"
              variant="transparent"
              size="sm"
              aria-label="clear-column-search"
              onClick={() => setText("")}
            >
              <IconX size={14} />
            </ActionIcon>
          ) : null
        }
      />
    </Stack>
  );
}

export default function CostCardTable() {
  const table = useTable("cost-card");
  const user = useUserState();
  const api = useApi();
  const navigate = useNavigate();

  // Per-column search terms, keyed by the entries in FILTERABLE_COLUMNS
  const [columnFilters, setColumnFilters] = useState<Record<string, string>>(
    {},
  );

  const setColumnFilter = useCallback((key: string, value: string) => {
    setColumnFilters((filters) => {
      if ((filters[key] ?? "") === value) {
        return filters;
      }

      const updated = { ...filters };

      if (value) {
        updated[key] = value;
      } else {
        delete updated[key];
      }

      return updated;
    });
  }, []);

  const activeColumnFilters = useMemo(() => {
    return Object.entries(columnFilters)
      .map(([key, value]): [string, string] => [
        key,
        value.trim().toLowerCase(),
      ])
      .filter(([, value]) => value.length > 0);
  }, [columnFilters]);

  // Customer / Vendor (both are Company records)
  const companyQuery = useQuery({
    queryKey: ["cost-card-customer-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.master_vendor_customer), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });
  const customerNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (companyQuery.data ?? []).forEach((company: any) => {
      if (company.is_customer) {
        map[company.pk] = company.name;
      }
    });
    return map;
  }, [companyQuery.data]);

  const vendorNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (companyQuery.data ?? []).forEach((company: any) => {
      if (company.is_supplier) {
        map[company.pk] = company.name;
      }
    });
    return map;
  }, [companyQuery.data]);

  // Jewel Category
  const jewelCategoryQuery = useQuery({
    queryKey: ["cost-card-jewel-category-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.jewellery_category), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });
  const jewelCategoryNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (jewelCategoryQuery.data ?? []).forEach((category: any) => {
      map[category.pk] = category.name;
    });
    return map;
  }, [jewelCategoryQuery.data]);

  // Jewel Sub Category
  const jewelSubCategoryQuery = useQuery({
    queryKey: ["cost-card-jewel-sub-category-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.jewellery_sub_category), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
    refetchOnMount: "always",
  });
  const jewelSubCategoryNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (jewelSubCategoryQuery.data ?? []).forEach((subCategory: any) => {
      map[subCategory.pk] = subCategory.name;
    });
    return map;
  }, [jewelSubCategoryQuery.data]);

  // Table-level filters (e.g. "active") are still applied by the server
  const serverParams = useMemo(() => {
    const params: Record<string, any> = {};

    table.filterSet.activeFilters?.forEach((flt) => {
      params[flt.name] = flt.value;
    });

    return params;
  }, [table.filterSet.activeFilters]);

  // Fetch the complete (server-filtered) record set, one page at a time
  const costCardQuery = useQuery({
    queryKey: ["cost-card-records", serverParams, table.tableKey],
    staleTime: 30 * 1000,
    queryFn: async () => {
      const records: any[] = [];
      let offset = 0;

      while (records.length < MAX_RECORDS) {
        const response = await api.get(apiUrl(ApiEndpoints.cost_card), {
          params: { ...serverParams, limit: FETCH_LIMIT, offset: offset },
        });

        const results = response.data?.results ?? response.data ?? [];

        if (!Array.isArray(results) || results.length === 0) {
          break;
        }

        records.push(...results);

        const count = response.data?.count;

        if (count == null || records.length >= count) {
          break;
        }

        offset += FETCH_LIMIT;
      }

      return records;
    },
  });

  /*
   * Attach the resolved display names to each record, so that the column search
   * boxes (and column sorting) operate on what the user actually sees, rather
   * than on the underlying primary keys.
   */
  const allRecords = useMemo(() => {
    return (costCardQuery.data ?? []).map((record: any) => ({
      ...record,
      customer_name:
        customerNameByPk[record.customer] ?? record.customer ?? "",
      vendor_name: vendorNameByPk[record.vendor] ?? record.vendor ?? "",
      category_name:
        jewelCategoryNameByPk[record.category] ?? record.category ?? "",
      sub_category_name:
        jewelSubCategoryNameByPk[record.sub_category] ??
        record.sub_category ??
        "",
    }));
  }, [
    costCardQuery.data,
    customerNameByPk,
    vendorNameByPk,
    jewelCategoryNameByPk,
    jewelSubCategoryNameByPk,
  ]);

  // Apply every active column search term (multi-level / AND filtering)
  const filteredRecords = useMemo(() => {
    if (activeColumnFilters.length === 0) {
      return allRecords;
    }

    return allRecords.filter((record: any) =>
      activeColumnFilters.every(([key, value]) =>
        String(record[key] ?? "")
          .toLowerCase()
          .includes(value),
      ),
    );
  }, [allRecords, activeColumnFilters]);

  // Jump back to the first page whenever the column search terms change
  useEffect(() => {
    table.setPage(1);
  }, [activeColumnFilters]);

  // --- new Table columns -------------------------------------------------
  const columns: TableColumn[] = useMemo(() => {
    // Build the inline search popover for a given column
    const columnFilter = (accessor: string, label: string) => {
      const entry = FILTERABLE_COLUMNS.find((c) => c.accessor === accessor);

      if (!entry) {
        return {};
      }

      return {
        filtering: !!columnFilters[entry.searchKey]?.trim(),
        filter: () => (
          <ColumnSearchInput
            label={label}
            value={columnFilters[entry.searchKey] ?? ""}
            onChange={(value: string) => setColumnFilter(entry.searchKey, value)}
          />
        ),
      };
    };

    return [
      {
        accessor: "image",
        title: t`Image`,
        sortable: false,
        switchable: true,
        render: (record: any) => (
          <Group gap="xs" wrap="nowrap">
            <Thumbnail
              src={record.front_view}
              alt={t`Front View`}
              size={24}
              hover
            />
          </Group>
        ),
      },
      {
        accessor: "cost_card_no",
        title: t`Cost Card Number`,
        sortable: true,
        switchable: false,
        ...columnFilter("cost_card_no", t`Cost Card Number`),
      },
      {
        accessor: "our_style_no",
        title: t`Our Style Number`,
        sortable: true,
        switchable: false,
        ...columnFilter("our_style_no", t`Our Style Number`),
      },
      {
        accessor: "vendor_style_no",
        title: t`Vendor Style Number`,
        sortable: true,
        switchable: false,
        ...columnFilter("vendor_style_no", t`Vendor Style Number`),
      },
      {
        accessor: "customer",
        title: t`Customer`,
        ordering: "customer_name",
        sortable: true,
        switchable: false,
        render: (record: any) => record.customer_name,
        ...columnFilter("customer", t`Customer`),
      },
      {
        accessor: "vendor",
        title: t`Vendor`,
        ordering: "vendor_name",
        sortable: true,
        switchable: false,
        render: (record: any) => record.vendor_name,
        ...columnFilter("vendor", t`Vendor`),
      },
      {
        accessor: "category",
        title: t`Jewel Category`,
        ordering: "category_name",
        sortable: true,
        switchable: false,
        render: (record: any) => record.category_name,
        ...columnFilter("category", t`Jewel Category`),
      },
      {
        accessor: "sub_category",
        title: t`Sub Category`,
        ordering: "sub_category_name",
        sortable: true,
        switchable: false,
        render: (record: any) => record.sub_category_name,
        ...columnFilter("sub_category", t`Sub Category`),
      },
      {
        accessor: "karat",
        title: t`Metal`,
        sortable: true,
        switchable: false,
        ...columnFilter("karat", t`Metal`),
      },
      BooleanColumn({
        accessor: "active",
      }),
      {
        accessor: "created_at",
        title: t`Created`,
        sortable: true,
        switchable: true,
      },
      {
        accessor: "updated_at",
        title: t`Updated`,
        sortable: true,
        switchable: true,
      },
    ];
  }, [columnFilters, setColumnFilter]);

  // --- Delete modal ------------------------------------------------------
  // Create and edit now happen on a dedicated tabbed page (see
  // containers/cost-card-detail) rather than in a modal, since a cost card
  // has line items (finish/diamond/color stone) and images that need their
  // own endpoints. Delete remains a modal since it's a single confirmation.
  const [selectedStamp, setSelectedStamp] = useState<number | undefined>(
    undefined,
  );

  const deleteStamp = useDeleteApiFormModal({
    url: ApiEndpoints.cost_card,
    pk: selectedStamp,
    title: t`Delete Stamp`,
    table: table,
  });

  // --- Row actions (edit / delete) -------------------------------------
  const rowActions = useCallback(
    (record: any): RowAction[] => {
      return [
        RowEditAction({
          hidden: !user.hasChangeRole(UserRoles.part),
          onClick: () => {
            navigate(`/cards/cost-card/${record.pk}`);
          },
        }),
        RowDeleteAction({
          hidden: !user.hasDeleteRole(UserRoles.part),
          onClick: () => {
            setSelectedStamp(record.pk);
            deleteStamp.open();
          },
        }),
      ];
    },
    [user, navigate],
  );

  // --- Table-level filters ----------------------------------------------
  const tableFilters: TableFilter[] = useMemo(() => {
    return [
      {
        name: "active",
        label: t`Active`,
        description: t`Show active stamp`,
        type: "boolean",
      },
    ];
  }, []);

  // --- Toolbar actions (Add button) --------------------------------------
  const tableActions = useMemo(() => {
    return [
      <Tooltip key="clear-column-filters" label={t`Clear column filters`}>
        <ActionIcon
          variant="transparent"
          aria-label="clear-column-filters"
          disabled={activeColumnFilters.length === 0}
          onClick={() => setColumnFilters({})}
        >
          <IconFilterOff />
        </ActionIcon>
      </Tooltip>,
      <AddItemButton
        key="add-stamp"
        onClick={() => navigate("/cards/cost-card/new")}
        tooltip={t`Add Stamp`}
        hidden={!user.hasAddRole(UserRoles.part)}
      />,
    ];
  }, [user, navigate, activeColumnFilters.length]);

  return (
    <>
      {deleteStamp.modal}
      <InvenTreeTable
        url={apiUrl(ApiEndpoints.cost_card)}
        tableState={table}
        tableData={filteredRecords}
        columns={columns}
        props={{
          rowActions: rowActions,
          tableActions: tableActions,
          tableFilters: tableFilters,
          enableDownload: true,
          dataLoading: costCardQuery.isFetching,
          onRowClick: (record: any) =>
            navigate(`/cards/cost-card/${record.pk}`),
        }}
      />
    </>
  );
}
