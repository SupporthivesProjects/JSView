import { t } from "@lingui/core/macro";
import {
  type ReactNode,
  useCallback,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useNavigate } from "react-router-dom";

import { AddItemButton } from "@lib/components/AddItemButton";
import { StylishText } from "@lib/components/StylishText";
import {
  type RowAction,
  RowDeleteAction,
  RowDuplicateAction,
  RowEditAction,
} from "@lib/components/RowActions";
import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { UserRoles } from "@lib/enums/Roles";
import { apiUrl } from "@lib/functions/Api";
import useTable from "@lib/hooks/UseTable";
import type { TableFilter } from "@lib/index";
import type { ApiFormFieldSet } from "@lib/types/Forms";
import { useStoredTableState } from "@lib/states/StoredTableState";
import type { TableColumn } from "@lib/types/Tables";
import { BooleanColumn } from "../ColumnRenderers";
import { ColumnSearchInput } from "../ColumnSearchInput";
import { InvenTreeTable } from "../InvenTreeTable";
import {
  PURCHASE_ORDER_FORM_GRID_COLUMNS,
  PURCHASE_ORDER_MODAL_SIZE,
  PURCHASE_REQUEST_FORM_GRID_COLUMNS,
  PURCHASE_REQUEST_MODAL_SIZE,
  findingTypeItems,
  picturePresentationFields,
  processPurchaseRequestData,
  purchaseOrderFields,
  purchaseRequestFields,
  purchaseRequestLineFromCostCard,
  validatePurchaseRequestLines,
} from "../../forms/CommonForms";
import {
  useCreateApiFormModal,
  useDeleteApiFormModal,
} from "../../../hooks/UseForm";
import useDataOutput from "../../../hooks/UseDataOutput";
import useNameLookup from "../../../hooks/UseNameLookup";
import { useUserState } from "@store/UserState";
import { ApiImage } from "@components/shared/images/ApiImage";
import {
  ActionIcon,
  Box,
  Button,
  Checkbox,
  Group,
  HoverCard,
  Menu,
  Stack,
  Text,
  Tooltip,
} from "@mantine/core";
import { modals } from "@mantine/modals";
import { showNotification } from "@mantine/notifications";
import {
  IconChevronDown,
  IconFileInvoice,
  IconFilterOff,
  IconPresentation,
  IconShoppingCart,
} from "@tabler/icons-react";
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

const COST_CARD_IMAGE_VIEWS: { field: string; label: () => string }[] = [
  { field: "front_view", label: () => t`Front View` },
  { field: "side_view", label: () => t`Side View` },
  { field: "back_view", label: () => t`Back View` },
];

const BLANK_IMAGE = "/static/img/blank_image.png";

// Accessor for the row selection checkbox column
const SELECT_COLUMN_ACCESSOR = "select";

// Bulk actions available for the selected cost cards
const COST_CARD_BULK_ACTIONS: {
  key: string;
  label: () => string;
  icon: ReactNode;
}[] = [
  { key: "po-request", label: () => t`PO Request`, icon: <IconFileInvoice /> },
  { key: "po-place", label: () => t`PO Place`, icon: <IconShoppingCart /> },
  {
    key: "picture-presentation",
    label: () => t`Presentation`,
    icon: <IconPresentation />,
  },
];

/*
 * Resolved display names for the property tables a stone line points at.
 *
 * Diamond lines and color stone lines reference different sets of tables
 * (DiamondShape vs ColorStoneShape, and so on), so each kind of line is
 * rendered with its own maps.
 */
type StoneNameMaps = {
  stone: Record<number, string>;
  shape: Record<number, string>;
  mm_size: Record<number, string>;
  color: Record<number, string>;
  cut: Record<number, string>;
  quality: Record<number, string>;
};

/*
 * Turn one diamond / color stone line into a row of the Picture Presentation
 * stone listing: the foreign keys on the line are swapped for the names they
 * point at, and the cost card's style number is carried along so that rows
 * coming from different cards can be told apart.
 *
 * `id` is what the form's table field keys the row on, so it has to stay
 * unique across both line types (their primary keys are independent).
 */
function picturePresentationStoneRow(
  line: any,
  names: StoneNameMaps,
  styleNo: string,
  id: string,
) {
  const label = (field: keyof StoneNameMaps) =>
    names[field][line[field]] ?? line[field] ?? "";

  return {
    id: id,
    style_no: styleNo,
    shape: label("shape"),
    mm_size: label("mm_size"),
    sieve_size: line.sieve_size ?? "",
    stone: label("stone"),
    color: label("color"),
    cut: label("cut"),
    quality: label("quality"),
    pointer: line.pointer ?? "",
    rate: line.rate ?? "",
  };
}

/*
 * Only the front view is shown in the table cell - hovering it previews
 * whichever of the front / side / back views the cost card actually has.
 */
function CostCardImagePreview({ record }: Readonly<{ record: any }>) {
  const images = COST_CARD_IMAGE_VIEWS.filter(({ field }) => !!record[field]);

  return (
    <HoverCard
      disabled={images.length === 0}
      withinPortal
      shadow="xs"
      openDelay={300}
      closeDelay={50}
    >
      <HoverCard.Target>
        <Box w={24}>
          <ApiImage
            src={record.front_view || BLANK_IMAGE}
            aria-label={t`Front View`}
            w={24}
            fit="contain"
            radius="xs"
            style={{ maxHeight: 24, height: 24 }}
          />
        </Box>
      </HoverCard.Target>
      <HoverCard.Dropdown>
        <Group gap="sm" wrap="nowrap" align="flex-start">
          {images.map(({ field, label }) => (
            <Stack key={field} gap={4} align="center">
              <Text size="xs" c="dimmed">
                {label()}
              </Text>
              <ApiImage
                src={record[field]}
                aria-label={label()}
                w={128}
                fit="contain"
                style={{ maxHeight: 128 }}
              />
            </Stack>
          ))}
        </Group>
      </HoverCard.Dropdown>
    </HoverCard>
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

  // Metal purity - only needed to tell gold apart from silver when pre-filling
  // the troy ounce price on the Picture Presentation form
  const metalPurityQuery = useQuery({
    queryKey: ["cost-card-metal-purity-lookup"],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.metal_purity_list), {
          params: { limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    staleTime: 5 * 60 * 1000,
  });
  const metalPurityNameByPk = useMemo(() => {
    const map: Record<number, string> = {};
    (metalPurityQuery.data ?? []).forEach((purity: any) => {
      map[purity.pk] = purity.name;
    });
    return map;
  }, [metalPurityQuery.data]);

  /*
   * Stone line properties, used to render the Picture Presentation stone
   * listing: the lines nested on a cost card record hold primary keys, so the
   * names they point at are pulled in separately. The query keys are shared
   * with the cost card Diamond / Color Stone tabs, so the lookups are only
   * fetched once between them.
   */
  const { nameByPk: diamondStoneByPk } = useNameLookup(
    ApiEndpoints.diamond_stone_list,
    "cost-card-diamond-stone-lookup",
  );
  const { nameByPk: diamondShapeByPk } = useNameLookup(
    ApiEndpoints.diamond_shape_list,
    "cost-card-diamond-shape-lookup",
  );
  const { nameByPk: diamondSizeByPk } = useNameLookup(
    ApiEndpoints.diamond_size_list,
    "cost-card-diamond-size-lookup",
    "mm_size",
  );
  const { nameByPk: diamondColorByPk } = useNameLookup(
    ApiEndpoints.diamond_color_list,
    "cost-card-diamond-color-lookup",
  );
  const { nameByPk: diamondCutByPk } = useNameLookup(
    ApiEndpoints.diamond_cut_list,
    "cost-card-diamond-cut-lookup",
  );
  const { nameByPk: diamondQualityByPk } = useNameLookup(
    ApiEndpoints.diamond_quality_list,
    "cost-card-diamond-quality-lookup",
  );

  const { nameByPk: colorStoneByPk } = useNameLookup(
    ApiEndpoints.color_stone_type_list,
    "cost-card-colorstone-stone-lookup",
  );
  const { nameByPk: colorStoneShapeByPk } = useNameLookup(
    ApiEndpoints.color_stone_shape_list,
    "cost-card-colorstone-shape-lookup",
  );
  const { nameByPk: colorStoneSizeByPk } = useNameLookup(
    ApiEndpoints.color_stone_size_list,
    "cost-card-colorstone-size-lookup",
  );
  const { nameByPk: colorStoneColorByPk } = useNameLookup(
    ApiEndpoints.color_stone_color_list,
    "cost-card-colorstone-color-lookup",
  );
  const { nameByPk: colorStoneCutByPk } = useNameLookup(
    ApiEndpoints.color_stone_cut_list,
    "cost-card-colorstone-cut-lookup",
  );
  const { nameByPk: colorStoneQualityByPk } = useNameLookup(
    ApiEndpoints.color_stone_quality_list,
    "cost-card-colorstone-quality-lookup",
  );

  const diamondStoneNames: StoneNameMaps = useMemo(
    () => ({
      stone: diamondStoneByPk,
      shape: diamondShapeByPk,
      mm_size: diamondSizeByPk,
      color: diamondColorByPk,
      cut: diamondCutByPk,
      quality: diamondQualityByPk,
    }),
    [
      diamondStoneByPk,
      diamondShapeByPk,
      diamondSizeByPk,
      diamondColorByPk,
      diamondCutByPk,
      diamondQualityByPk,
    ],
  );

  const colorStoneNames: StoneNameMaps = useMemo(
    () => ({
      stone: colorStoneByPk,
      shape: colorStoneShapeByPk,
      mm_size: colorStoneSizeByPk,
      color: colorStoneColorByPk,
      cut: colorStoneCutByPk,
      quality: colorStoneQualityByPk,
    }),
    [
      colorStoneByPk,
      colorStoneShapeByPk,
      colorStoneSizeByPk,
      colorStoneColorByPk,
      colorStoneCutByPk,
      colorStoneQualityByPk,
    ],
  );

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
      customer_name: customerNameByPk[record.customer] ?? record.customer ?? "",
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

  // --- Row selection -----------------------------------------------------
  // Tracked locally (by pk) so that selection persists across pages
  const { pageSize } = useStoredTableState();

  const [selectedPks, setSelectedPks] = useState<Set<number>>(new Set());

  const toggleSelected = useCallback((pk: number, checked: boolean) => {
    setSelectedPks((current) => {
      const updated = new Set(current);

      if (checked) {
        updated.add(pk);
      } else {
        updated.delete(pk);
      }

      return updated;
    });
  }, []);

  // Only count selections which are still present in the loaded data
  const selectedRecords = useMemo(
    () => allRecords.filter((record: any) => selectedPks.has(record.pk)),
    [allRecords, selectedPks],
  );

  // "Select all" applies to every record matching the current column filters
  const allFilteredSelected =
    filteredRecords.length > 0 &&
    filteredRecords.every((record: any) => selectedPks.has(record.pk));

  const someFilteredSelected =
    !allFilteredSelected &&
    filteredRecords.some((record: any) => selectedPks.has(record.pk));

  const toggleSelectAll = useCallback(
    (checked: boolean) => {
      setSelectedPks((current) => {
        const updated = new Set(current);

        filteredRecords.forEach((record: any) => {
          if (checked) {
            updated.add(record.pk);
          } else {
            updated.delete(record.pk);
          }
        });

        return updated;
      });
    },
    [filteredRecords],
  );

  // --- "PO Request" / "PO Place" bulk actions ----------------------------
  // The selected cost cards are turned into line item rows and handed to the
  // same create form the Purchase Request / Purchase Order tables use, so the
  // record is reviewed (quantities, sizes, header fields) before it is saved.
  // A request and an order take identical rows, so both share this state.
  const [purchaseLines, setPurchaseLines] = useState<any[]>([]);

  // Only carried over when every selected card belongs to the same customer
  const [purchaseCustomer, setPurchaseCustomer] = useState<number | null>(null);

  // Apply the prefilled rows (and customer) to either form's field set
  const withSelectedCards = useCallback(
    (fields: ApiFormFieldSet): ApiFormFieldSet => {
      const populated: ApiFormFieldSet = {
        ...fields,
        items: { ...fields.items, value: purchaseLines },
      };

      if (purchaseCustomer) {
        populated.customerid = {
          ...fields.customerid,
          value: purchaseCustomer,
        };
      }

      return populated;
    },
    [purchaseLines, purchaseCustomer],
  );

  const newPurchaseRequest = useCreateApiFormModal({
    url: ApiEndpoints.purchase_api,
    title: t`Create New Purchase Request`,
    fields: withSelectedCards(purchaseRequestFields()),
    validateFormData: validatePurchaseRequestLines("items", true),
    processFormData: processPurchaseRequestData,
    successMessage: t`Purchase request created`,
    gridColumns: PURCHASE_REQUEST_FORM_GRID_COLUMNS,
    size: PURCHASE_REQUEST_MODAL_SIZE,
    onFormSuccess: () => setSelectedPks(new Set()),
  });

  const newPurchaseOrder = useCreateApiFormModal({
    url: ApiEndpoints.purchase_api,
    title: t`Create New Purchase Order`,
    fields: withSelectedCards(purchaseOrderFields()),
    validateFormData: validatePurchaseRequestLines("items", true),
    processFormData: processPurchaseRequestData,
    successMessage: t`Purchase order created`,
    gridColumns: PURCHASE_ORDER_FORM_GRID_COLUMNS,
    size: PURCHASE_ORDER_MODAL_SIZE,
    onFormSuccess: () => setSelectedPks(new Set()),
  });

  const openPurchaseForm = useCallback(
    (open: () => void) => {
      setPurchaseLines(
        selectedRecords.map((record: any) =>
          purchaseRequestLineFromCostCard(record),
        ),
      );

      const customers = new Set(
        selectedRecords
          .map((record: any) => record.customer)
          .filter((customer: any) => !!customer),
      );

      setPurchaseCustomer(
        customers.size === 1
          ? (customers.values().next().value as number)
          : null,
      );

      open();
    },
    [selectedRecords],
  );

  const [exportId, setExportId] = useState<number | undefined>(undefined);

  useDataOutput({
    title: t`Exporting Picture Presentation`,
    id: exportId,
  });

  // `cost_card_ids` is not set here: it is assembled at submit time from the
  // style numbers shown on the form (which are pre-filled from the ticked rows).
  const picturePresentationParams = useMemo(
    () => new URLSearchParams({ export: "true" }),
    [],
  );

  const [picturePresentationOpen, setPicturePresentationOpen] =
    useState<boolean>(false);

  // The cost cards the modal is currently working with. Seeded from the ticked
  // rows when the form is opened, and kept in step with the style-number picker
  // afterwards, so the stone preview always matches what will be exported.
  const [picturePresentationCards, setPicturePresentationCards] = useState<
    number[]
  >([]);

  // The purchase order selected on the form (if any). It restricts the
  // style-number picker to the cost cards linked to that order.
  const [picturePresentationPo, setPicturePresentationPo] = useState<
    number | null
  >(null);

  /*
   * Cost cards picked on the form which the table has not loaded. The style
   * picker is filtered independently of the table (and, with a P.O. selected,
   * lists that order's line items instead), so it can offer cards the current
   * table filters exclude - fetch those individually so their stone lines are
   * listed too. A card which cannot be fetched is simply left out.
   */
  const missingCardPks = useMemo(() => {
    const loaded = new Set(allRecords.map((record: any) => record.pk));
    return picturePresentationCards.filter((pk) => !loaded.has(pk));
  }, [allRecords, picturePresentationCards]);

  const missingCardsQuery = useQuery({
    queryKey: ["picture-presentation-cards", missingCardPks.join(",")],
    enabled: picturePresentationOpen && missingCardPks.length > 0,
    staleTime: 60 * 1000,
    queryFn: () =>
      Promise.all(
        missingCardPks.map((pk) =>
          api
            .get(apiUrl(ApiEndpoints.cost_card, pk))
            .then((response) => response.data)
            .catch(() => null),
        ),
      ).then((records) => records.filter((record) => !!record)),
  });

  /*
   * Every stone line on the selected cost cards, one row each.
   *
   * The export endpoint also returns a stone summary, but it pools the lines
   * and keeps only one row per distinct combination - two cards carrying the
   * same stone would show up once. The rows are built here instead, from the
   * lines the cost card records already carry, so nothing is collapsed.
   */
  const picturePresentationStones = useMemo(() => {
    const cardByPk: Record<number, any> = {};

    for (const record of [...allRecords, ...(missingCardsQuery.data ?? [])]) {
      cardByPk[record.pk] = record;
    }

    const rows: any[] = [];

    for (const pk of picturePresentationCards) {
      const card = cardByPk[pk];

      if (!card) {
        continue;
      }

      const styleNo = card.our_style_no ?? "";

      (card.diamond_lines ?? []).forEach((line: any, index: number) =>
        rows.push(
          picturePresentationStoneRow(
            line,
            diamondStoneNames,
            styleNo,
            `${pk}-diamond-${line.id ?? index}`,
          ),
        ),
      );

      (card.colorstone_lines ?? []).forEach((line: any, index: number) =>
        rows.push(
          picturePresentationStoneRow(
            line,
            colorStoneNames,
            styleNo,
            `${pk}-colorstone-${line.id ?? index}`,
          ),
        ),
      );
    }

    return rows;
  }, [
    allRecords,
    missingCardsQuery.data,
    picturePresentationCards,
    diamondStoneNames,
    colorStoneNames,
  ]);

  /*
   * The pricing inputs apply to the export as a whole, so a figure is only
   * pre-filled when every selected card agrees on it - otherwise the field is
   * left empty rather than presenting one card's number as if it covered all
   * of them. The troy ounce price is split by metal the same way the export
   * itself splits it: on the metal purity name.
   */
  const picturePresentationValues = useMemo(() => {
    const isSilver = (record: any) =>
      (metalPurityNameByPk[record.metal_purity] ?? "")
        .toLowerCase()
        .includes("silver");

    const sharedValue = (records: any[], field: string) => {
      let shared: any;

      for (const record of records) {
        const value = record?.[field];

        if (value === null || value === undefined || value === "") {
          return undefined;
        }

        if (shared === undefined) {
          shared = value;
        } else if (String(shared) !== String(value)) {
          return undefined;
        }
      }

      return shared;
    };

    return {
      // Always handed to the field (even when empty), so that dropping the
      // cards which do not belong to a newly selected P.O. also clears them
      // from the picker
      stylenumber: picturePresentationCards,
      duty_pct: sharedValue(selectedRecords, "duty_pct"),
      margin_pct: sharedValue(selectedRecords, "margin_pct"),
      gold_troy_ounce: sharedValue(
        selectedRecords.filter((record: any) => !isSilver(record)),
        "troy_ounce_price",
      ),
      silver_troy_ounce: sharedValue(
        selectedRecords.filter((record: any) => isSilver(record)),
        "troy_ounce_price",
      ),
    };
  }, [selectedRecords, picturePresentationCards, metalPurityNameByPk]);

  const picturePresentationFormFields = useMemo((): ApiFormFieldSet => {
    const fields = picturePresentationFields(picturePresentationPo);

    const values: Record<string, any> = {
      ...picturePresentationValues,
      stones: picturePresentationStones,
    };

    const prefilled: ApiFormFieldSet = {};

    for (const [name, field] of Object.entries(fields)) {
      const value = values[name];
      prefilled[name] = value === undefined ? field : { ...field, value };
    }

    // Track the picker, so removing a style from the form also removes its
    // stones from the preview (and the card from the export)
    prefilled.stylenumber = {
      ...prefilled.stylenumber,
      onValueChange: (value: any) => {
        const ids = Array.isArray(value) ? value : value ? [value] : [];
        setPicturePresentationCards(ids.map((pk: any) => Number(pk)));
      },
    };

    /*
     * Selecting a P.O. narrows the style picker to the cost cards that order
     * is linked to. The order carries its line items with it, so the cards
     * already picked which are *not* on the order are dropped here - leaving
     * them selected would export styles the order does not cover.
     */
    prefilled.ponumber = {
      ...prefilled.ponumber,
      onValueChange: (value: any, record?: any) => {
        const pk = value ? Number(value) : null;

        setPicturePresentationPo(pk);

        if (!pk) {
          return;
        }

        const linked = new Set<number>(
          (record?.lines ?? [])
            .map((line: any) => line?.costcardid)
            .filter((id: any) => !!id)
            .map((id: any) => Number(id)),
        );

        setPicturePresentationCards((current) =>
          current.filter((id) => linked.has(id)),
        );
      },
    };

    return prefilled;
  }, [
    picturePresentationValues,
    picturePresentationStones,
    picturePresentationPo,
  ]);

  // The export view filters on `cost_card_ids`, and the style-number picker
  // returns cost card PKs - so fold them together into that one parameter.
  const processPicturePresentationData = useCallback(
    (data: any) => {
      const { stylenumber, ...rest } = data;

      const picked = Array.isArray(stylenumber)
        ? stylenumber
        : stylenumber
          ? [stylenumber]
          : [];

      // The picker starts out holding the ticked rows, so it is what the user
      // last said should be exported; fall back to the selection only if they
      // emptied it entirely. With a P.O. selected there is no fallback: the
      // ticked rows are not necessarily linked to that order.
      const ids =
        picked.length > 0 || rest.ponumber ? picked : Array.from(selectedPks);

      if (ids.length === 0) {
        return rest;
      }

      return { ...rest, cost_card_ids: Array.from(new Set(ids)).join(",") };
    },
    [selectedPks],
  );

  const picturePresentationModal = useCreateApiFormModal({
    url: ApiEndpoints.cost_card_picture_presentation,
    queryParams: picturePresentationParams,
    method: "GET",
    title: t`Presentation`,
    fields: picturePresentationFormFields,
    processFormData: processPicturePresentationData,
    submitText: t`Picture Presentation`,
    successMessage: null,
    timeout: 30 * 1000,
    gridColumns: PURCHASE_REQUEST_FORM_GRID_COLUMNS,
    size: "80rem",
    alwaysEnableSubmit: true,
    onOpen: () => setPicturePresentationOpen(true),
    onClose: () => setPicturePresentationOpen(false),
    onFormSuccess: (response: any) => setExportId(response.pk),
  });

  // Seed the form from the ticked rows *before* it mounts, so the fields come
  // up already filled in rather than being populated a render later
  const openPicturePresentation = useCallback(() => {
    setPicturePresentationCards(Array.from(selectedPks));
    // The form comes up with an empty P.O. field, so the filter it drives
    // starts out cleared too
    setPicturePresentationPo(null);
    picturePresentationModal.open();
  }, [selectedPks, picturePresentationModal.open]);

  const runBulkAction = useCallback(
    (action: { key: string; label: () => string }) => {
      switch (action.key) {
        case "po-request":
          openPurchaseForm(newPurchaseRequest.open);
          return;
        case "po-place":
          openPurchaseForm(newPurchaseOrder.open);
          return;
        case "picture-presentation":
          openPicturePresentation();
          return;
        default:
          // TODO: hook up to the relevant workflow once available
          showNotification({
            title: action.label(),
            message: t`${selectedRecords.length} cost card(s) selected`,
            color: "blue",
          });
      }
    },
    [
      selectedRecords,
      openPurchaseForm,
      newPurchaseRequest.open,
      newPurchaseOrder.open,
      openPicturePresentation,
    ],
  );

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
            onChange={(value: string) =>
              setColumnFilter(entry.searchKey, value)
            }
          />
        ),
      };
    };

    return [
      {
        accessor: "row_number",
        title: t`#`,
        sortable: false,
        switchable: false,
        resizable: false,
        width: 50,
        minWidth: 50,
        render: (_record: any, index?: number) =>
          (Math.max(1, table.page) - 1) * pageSize + (index ?? 0) + 1,
      },
      {
        accessor: SELECT_COLUMN_ACCESSOR,
        title: "",
        sortable: false,
        switchable: false,
        resizable: false,
        width: 40,
        minWidth: 40,
        render: (record: any) => (
          <Checkbox
            size="xs"
            aria-label={t`Select cost card`}
            checked={selectedPks.has(record.pk)}
            onClick={(event) => event.stopPropagation()}
            onChange={(event) =>
              toggleSelected(record.pk, event.currentTarget.checked)
            }
          />
        ),
      },
      {
        accessor: "image",
        title: t`Image`,
        sortable: false,
        switchable: true,
        render: (record: any) => <CostCardImagePreview record={record} />,
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
  }, [
    columnFilters,
    setColumnFilter,
    table.page,
    pageSize,
    selectedPks,
    toggleSelected,
  ]);

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
        // Asks for confirmation, then opens the create view pre-filled from
        // this card - nothing is created until the General tab is saved
        RowDuplicateAction({
          hidden: !user.hasAddRole(UserRoles.part),
          onClick: () => {
            modals.openConfirmModal({
              title: (
                <StylishText size="xl">{t`Duplicate Cost Card`}</StylishText>
              ),
              children: (
                <Text>
                  {t`Are you sure you want to duplicate this cost card:`}{" "}
                  <Text span fw={700}>
                    {record.cost_card_no}
                  </Text>
                </Text>
              ),
              labels: { confirm: t`Duplicate`, cancel: t`Cancel` },
              onConfirm: () => {
                navigate(`/cards/cost-card/new?duplicate=${record.pk}`);
              },
            });
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
      <Checkbox
        key="select-all"
        size="sm"
        label={t`Select All`}
        aria-label="select-all-cost-cards"
        checked={allFilteredSelected}
        indeterminate={someFilteredSelected}
        disabled={filteredRecords.length === 0}
        onChange={(event) => toggleSelectAll(event.currentTarget.checked)}
      />,
      <Menu key="bulk-actions" position="bottom-end" withinPortal>
        <Menu.Target>
          <Button
            size="xs"
            variant="light"
            aria-label="cost-card-actions"
            disabled={selectedRecords.length === 0}
            rightSection={<IconChevronDown size={16} stroke={1.5} />}
          >
            {selectedRecords.length > 0
              ? t`Actions (${selectedRecords.length})`
              : t`Actions`}
          </Button>
        </Menu.Target>
        <Menu.Dropdown>
          {COST_CARD_BULK_ACTIONS.map((action) => (
            <Menu.Item
              key={action.key}
              leftSection={action.icon}
              onClick={() => runBulkAction(action)}
            >
              {action.label()}
            </Menu.Item>
          ))}
        </Menu.Dropdown>
      </Menu>,
    ];
  }, [
    user,
    navigate,
    activeColumnFilters.length,
    allFilteredSelected,
    someFilteredSelected,
    filteredRecords.length,
    toggleSelectAll,
    selectedRecords.length,
    runBulkAction,
  ]);

  return (
    <>
      {picturePresentationModal.modal}
      {deleteStamp.modal}
      {newPurchaseRequest.modal}
      {newPurchaseOrder.modal}
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
          // Clicking in the selection column must not open the cost card
          onCellClick: ({ record, column }: any) => {
            if (column?.accessor === SELECT_COLUMN_ACCESSOR) {
              toggleSelected(record.pk, !selectedPks.has(record.pk));
              return;
            }

            navigate(`/cards/cost-card/${record.pk}`);
          },
        }}
      />
    </>
  );
}
