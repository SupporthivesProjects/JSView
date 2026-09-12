import { IconUsers } from "@tabler/icons-react";
import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { ApiEndpoints } from "@lib/enums/ApiEndpoints";
import { ModelType } from "@lib/enums/ModelType";
import { apiUrl } from "@lib/functions/Api";
import type {
  ApiFormFieldChoice,
  ApiFormFieldSet,
  ApiFormFieldType,
} from "@lib/types/Forms";
import type {
  StatusCodeInterface,
  StatusCodeListInterface,
} from "../shared/render/StatusRenderer";
import { useApi } from "@context/ApiContext";
import { useGlobalStatusState } from "@store/GlobalStatusState";
import { useUserState } from "@store/UserState";
import { ProjectCodeField } from "./CommonFields";

export function projectCodeFields(): ApiFormFieldSet {
  return {
    code: {},
    description: {},
    responsible: {
      icon: <IconUsers />,
    },
    active: { boxed: true },
  };
}

export function metalTypeFields(): ApiFormFieldSet {
  return {
    code: {},
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function stonePlaceFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function metalPurityFields(): ApiFormFieldSet {
  return {
    metal_type: {
      api_url: `${apiUrl(ApiEndpoints.metal_type_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    name: {},
    // purity: {},
    karat: {},
    active: { boxed: true },
  };
}

export function metalRate(): ApiFormFieldSet {
  return {
    metal_type: {
      api_url: `${apiUrl(ApiEndpoints.metal_type_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    rate: {},
    date: {},
    active: { boxed: true },
  };
}

export function masterTerms(): ApiFormFieldSet {
  return {
    name: {},
    days: {},
    description: {},
    vendors: {
      field_type: "related field",
      model: ModelType.company,
      multiple: true,
      api_url: apiUrl(ApiEndpoints.company_list),
      filters: { is_supplier: true },
      disableWhen: (values: any) => !!values?.all_vendors,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.code ?? "";
      },
    },
    all_vendors: { boxed: true },
    active: { boxed: true },
  };
}

export function masterCourierService(): ApiFormFieldSet {
  return {
    name: {},
    contact_person: {},
    phone: {},
    email: {},
    tracking_url: {},
    active: { boxed: true },
  };
}

export function masterExecutive(): ApiFormFieldSet {
  return {
    name: {},
    code: {},
    email: {},
    phone: {},
    active: { boxed: true },
  };
}
export function findingTypeFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function findingTypeItems(): ApiFormFieldSet {
  return {
    finding_type: {
      api_url: `${apiUrl(ApiEndpoints.finding_type)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    name: {},
    type: {},
    weight: {},
    metal: {},
    price: {},
    active: { boxed: true },
  };
}

export function finishTypeFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function ListDutyFields(): ApiFormFieldSet {
  return {
    metal_type: {
      api_url: `${apiUrl(ApiEndpoints.metal_type_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        // return instance?.name ?? (instance?.pk ? `#${instance.pk}` : "");
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    duty: {},
    markup: {},
    description: {},
    active: { boxed: true },
  };
}

export function MasterSettingFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function LabourSettingFields(): ApiFormFieldSet {
  return {
    name: {},
    setting: {
      api_url: apiUrl(ApiEndpoints.master_setting),
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    charge_type: {},
    rate: {},
    active: { boxed: true },
  };
}

export function masterVendors(): ApiFormFieldSet {
  return {
    code: {},
    name: {},
    description: {},
    website: {},
    phone: {},
    email: {},
    contact: {},
    link: {},
    is_customer: {
      hidden: true,
      value: false,
    },
    is_supplier: {
      hidden: true,
      value: true,
    },
    is_manufacturer: {
      hidden: true,
      value: false,
    },
    tax_id: {},
    fax: {},
    city: {},
    state: {},
    country: {},
    rating: {},
    credit_limit: {},
    ref_by: {},
    active: { boxed: true },
  };
}
export function vendorContactFields(): ApiFormFieldSet {
  return {
    company: { hidden: true },
    name: {},
    phone: {},
    mobile: {},
    email: {},
    role: {},
  };
}

export function customerContactFields(): ApiFormFieldSet {
  return {
    company: { hidden: true },
    name: {},
    phone: {},
    mobile: {},
    email: {},
    role: {},
  };
}

export function masterCustomer(): ApiFormFieldSet {
  return {
    code: {},
    name: {},
    description: {},
    website: {},
    phone: {},
    email: {},
    contact: {},
    link: {},
    is_customer: {
      hidden: true,
      value: true,
    },
    is_supplier: {
      hidden: true,
      value: false,
    },
    is_manufacturer: {
      hidden: true,
      value: false,
    },
    tax_id: {},
    fax: {},
    city: {},
    state: {},
    country: {},
    rating: {},
    credit_limit: {},
    ref_by: {},
    active: { boxed: true },
  };
}

export function jewelleryCategoryFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function jewellerySubCategoryFields(): ApiFormFieldSet {
  return {
    category: {
      api_url: apiUrl(ApiEndpoints.jewellery_category),
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function colorStoneTypeFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function colorStoneCutFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function colorStoneShapeFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function colorStoneColorFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function colorStoneSizeFields(): ApiFormFieldSet {
  return {
    name: {},
    mm_size: {},
    sieve_size: {},
    description: {},
    active: { boxed: true },
  };
}

export function colorStoneQualityFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function colorStoneRateFields(): ApiFormFieldSet {
  return {
    shape: {
      api_url: `${apiUrl(ApiEndpoints.color_stone_shape_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    mm_size: {
      api_url: `${apiUrl(ApiEndpoints.color_stone_size_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    stone: {
      api_url: `${apiUrl(ApiEndpoints.color_stone_type_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    color: {
      api_url: `${apiUrl(ApiEndpoints.color_stone_color_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    cut: {
      api_url: `${apiUrl(ApiEndpoints.color_stone_cut_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    quality: {
      api_url: `${apiUrl(ApiEndpoints.color_stone_quality_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    pointer: {},
    rate: {},
    pc: {},
    customers: {
      field_type: "related field",
      model: ModelType.company,
      multiple: true,
      api_url: apiUrl(ApiEndpoints.company_list),
      filters: { is_customer: true },
      disableWhen: (values: any) => !!values?.all_customers,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.code ?? "";
      },
    },
    all_customers: { boxed: true },
    active: { boxed: true },
  };
}

export function stampFields(
  includeImage: boolean = true,
  onImageChange?: (file: File | null) => void,
): ApiFormFieldSet {
  const fields: ApiFormFieldSet = {
    name: {},
    description: {},
  };

  if (includeImage) {
    fields.image = {
      field_type: "file upload",
      onValueChange: (value: any) => {
        onImageChange?.(value instanceof File ? value : null);
      },
    };
  }

  {
    fields.customer = {
      label: "Customer",
      description: "Customers assigned to this stamp.",
      field_type: "related field",
      model: ModelType.company,
      multiple: true,
      api_url: apiUrl(ApiEndpoints.company_list),
      filters: { is_customer: true },
      disableWhen: (values: any) => !!values?.all_customers,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.code ?? "";
      },
    };
  }

  {
    fields.all_customers = {
      field_type: "boolean",
      boxed: true,
    };
  }
  {
    fields.active = {
      field_type: "boolean",
      boxed: true,
    };
  }

  return fields;
}

// Cost Card is edited as a full page with a tab per section (see
// containers/cost-card-detail) rather than a single modal, so its fields are
// split into one set per tab instead of one flat costCardFields() blob.

/**
 * Cost Card forms carry far too many fields for a single vertical stack, so
 * they lay their fields out in a responsive grid - one column on a phone,
 * three on a wide screen.
 */
export const COST_CARD_FORM_GRID_COLUMNS = { base: 1, sm: 2, lg: 3 };

/** Width of a cost card line modal, sized to hold three columns of fields. */
export const COST_CARD_LINE_MODAL_SIZE = "72rem";

/**
 * General tab — core identity, party, and measurement fields.
 *
 * Metal Grams drives Gross Weight and Net Weight: whatever is typed into
 * Metal Grams is mirrored into both, and those two fields are read-only so
 * they can only ever be set that way.
 *
 * Metal Purity drives Kt in the same way: selecting a purity copies that
 * record's karat into the Kt field, which is read-only so it can only ever be
 * set that way.
 */
export function useCostCardGeneralFields(): ApiFormFieldSet {
  const [metalGrams, setMetalGrams] = useState<any>(undefined);
  const [karat, setKarat] = useState<any>(undefined);
  const [findingPrice, setFindingPrice] = useState<any>(undefined);

  return useMemo(() => {
    return costCardGeneralFieldSet(
      metalGrams,
      setMetalGrams,
      karat,
      setKarat,
      findingPrice,
      setFindingPrice,
    );
  }, [metalGrams, karat, findingPrice]);
}

function costCardGeneralFieldSet(
  metalGrams: any,
  setMetalGrams: (value: any) => void,
  karat: any,
  setKarat: (value: any) => void,
  findingPrice: any,
  setFindingPrice: (value: any) => void,
): ApiFormFieldSet {
  return {
    cost_card_no: { read_only: true },
    our_style_no: {},
    vendor_style_no: {},
    vendor: {
      api_url: `${apiUrl(ApiEndpoints.master_vendor_customer)}?active=true&is_supplier=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.code ?? (instance?.code ? `#${instance.code}` : "");
      },
    },
    customer: {
      api_url: `${apiUrl(ApiEndpoints.master_vendor_customer)}?active=true&is_customer=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.code ?? (instance?.code ? `#${instance.code}` : "");
      },
    },
    category: {
      api_url: `${apiUrl(ApiEndpoints.jewellery_category)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    sub_category: {
      api_url: `${apiUrl(ApiEndpoints.jewellery_sub_category)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    metal_purity: {
      api_url: `${apiUrl(ApiEndpoints.metal_purity_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
      onValueChange: (_value: any, instance?: any) => {
        setKarat(instance?.karat ?? null);
      },
    },
    karat: {
      value: karat,
      read_only: true,
      disabled: true,
    },
    metal_grams: {
      onValueChange: (value: any) => setMetalGrams(value),
    },
    finding_item: {
      api_url: `${apiUrl(ApiEndpoints.finding_item)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
      onValueChange: (_value: any, instance?: any) => {
        setFindingPrice(instance?.price ?? null);
      },
    },
    finding_price: {
      value: findingPrice,
      read_only: true,
      disabled: true,
    },
    gross_weight: {
      value: metalGrams,
      read_only: true,
      disabled: true,
    },
    net_weight: {
      value: metalGrams,
      read_only: true,
      disabled: true,
    },
    troy_ounce_price: {},
    height_mm: {},
    height_inch: {},
    length_mm: {},
    length_inch: {},
    width_mm: {},
    width_inch: {},
    shank_size_mm: {},
    shank_size_inch: {},
    drape_length_mm: {},
    drape_length_inch: {},
    remarks: {},
    active: {
      boxed: true,
    },
    design_note: {
      multiline: true,
    },
    special_note: {
      multiline: true,
    },
  };
}

/**
 * Labour Details tab — read-only rollups from the Finish / Diamond / Color
 * Stone tabs.
 *
 * None of the rollups have server-side computation, so each is summed here
 * from the cost card's own lines (finish lines by `rate`, diamond and color
 * stone lines by `labour_amount`) and mirrored into the matching read-only
 * labour_finish_amount / labour_diamond_amount / labour_colorstone_amount
 * field. Pass `refreshOn` (e.g. whether the Labour Details tab is the
 * active tab) to have it re-fetch those lines - keep-mounted tabs don't
 * remount on switch, so this is what picks up edits made on the Finish
 * Type / Diamond / Color Stone tabs.
 */
export function useCostCardLabourFields(
  costCardId: number | undefined,
  refreshOn?: boolean,
): ApiFormFieldSet {
  const api = useApi();

  const finishLinesQuery = useQuery({
    queryKey: ["cost-card-finish-lines-for-labour", costCardId],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.cost_card_finish_line), {
          params: { cost_card: costCardId, limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    enabled: !!costCardId,
    staleTime: 0,
  });

  const diamondLinesQuery = useQuery({
    queryKey: ["cost-card-diamond-lines-for-labour", costCardId],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.cost_card_diamond_line), {
          params: { cost_card: costCardId, limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    enabled: !!costCardId,
    staleTime: 0,
  });

  const colorstoneLinesQuery = useQuery({
    queryKey: ["cost-card-colorstone-lines-for-labour", costCardId],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.cost_card_colorstone_line), {
          params: { cost_card: costCardId, limit: 1000 },
        })
        .then((response) => response.data?.results ?? response.data ?? []),
    enabled: !!costCardId,
    staleTime: 0,
  });

  useEffect(() => {
    if (refreshOn && costCardId) {
      finishLinesQuery.refetch();
      diamondLinesQuery.refetch();
      colorstoneLinesQuery.refetch();
    }
    // Only re-run when the caller flips the refresh trigger - not on every
    // query identity change (that would refetch in a loop).
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [refreshOn, costCardId]);

  const finishAmount = useMemo(() => {
    if (!finishLinesQuery.data) return undefined;
    return finishLinesQuery.data.reduce(
      (sum: number, line: any) => sum + (Number(line.rate) || 0),
      0,
    );
  }, [finishLinesQuery.data]);

  const diamondAmount = useMemo(() => {
    if (!diamondLinesQuery.data) return undefined;
    return diamondLinesQuery.data.reduce(
      (sum: number, line: any) => sum + (Number(line.labour_amount) || 0),
      0,
    );
  }, [diamondLinesQuery.data]);

  const colorstoneAmount = useMemo(() => {
    if (!colorstoneLinesQuery.data) return undefined;
    return colorstoneLinesQuery.data.reduce(
      (sum: number, line: any) => sum + (Number(line.labour_amount) || 0),
      0,
    );
  }, [colorstoneLinesQuery.data]);

  return useMemo(() => {
    return {
      labour_finish_amount: {
        read_only: true,
        disabled: true,
        value: finishAmount,
      },
      labour_diamond_amount: {
        read_only: true,
        disabled: true,
        value: diamondAmount,
      },
      labour_colorstone_amount: {
        read_only: true,
        disabled: true,
        value: colorstoneAmount,
      },
    };
  }, [finishAmount, diamondAmount, colorstoneAmount]);
}

/** Cost tab — editable percentages plus their computed (read-only) amounts. */
export function costCardCostFields(): ApiFormFieldSet {
  return {
    metal_loss_pct: {},
    metal_loss_amount: { read_only: true },
    metal_amount: { read_only: true },
    dia_pcs: { read_only: true },
    dia_cts: { read_only: true },
    dia_amount: { read_only: true },
    col_pcs: { read_only: true },
    col_cts: { read_only: true },
    col_amount: { read_only: true },
    stone_pcs: { read_only: true },
    stone_cts: { read_only: true },
    stone_amount: { read_only: true },
    labour_amount: { read_only: true },
    finding_price: { read_only: true },
    dia_handling_pct: {},
    dia_handling_amount: { read_only: true },
    col_handling_pct: {},
    col_handling_amount: { read_only: true },
    vendor_markup_pct: {},
    vendor_markup_amount: { read_only: true },
    fob: { read_only: true },
    duty_pct: {},
    duty_amount: { read_only: true },
    margin_pct: {},
    margin_amount: { read_only: true },
    final_amount: { read_only: true },
  };
}

/** Remarks tab — the detailed remarks field (distinct from the short General-tab remarks). */
export function costCardRemarksFields(): ApiFormFieldSet {
  return {
    remarks_full: { multiline: true, minRows: 10 },
  };
}

/** Shared dropdown field definitions for a diamond/color-stone cost card line. */
function costCardStoneLineFields(
  stoneEndpoint: ApiEndpoints,
  shapeEndpoint: ApiEndpoints,
  sizeEndpoint: ApiEndpoints,
  colorEndpoint: ApiEndpoints,
  cutEndpoint: ApiEndpoints,
  qualityEndpoint: ApiEndpoints,
): ApiFormFieldSet {
  const nameRenderer = (arg: any) => {
    const instance = arg?.instance ?? arg;
    return instance?.name ?? "";
  };

  // Field order is the order the form renders in, so keep related fields
  // adjacent - the two linked size fields especially, and the rate fields
  // next to the amounts they feed.
  return {
    stone: {
      api_url: apiUrl(stoneEndpoint),
      filters: { active: true },
      modelRenderer: nameRenderer,
    },
    shape: {
      api_url: apiUrl(shapeEndpoint),
      filters: { active: true },
      modelRenderer: nameRenderer,
    },
    mm_size: {
      api_url: apiUrl(sizeEndpoint),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.mm_size ?? "";
      },
    },
    sieve_size: {
      api_url: apiUrl(sizeEndpoint),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.sieve_size ?? "";
      },
    },
    pointer: {},
    color: {
      api_url: apiUrl(colorEndpoint),
      filters: { active: true },
      modelRenderer: nameRenderer,
    },
    cut: {
      api_url: apiUrl(cutEndpoint),
      filters: { active: true },
      modelRenderer: nameRenderer,
    },
    quality: {
      api_url: apiUrl(qualityEndpoint),
      filters: { active: true },
      modelRenderer: nameRenderer,
    },
    pcs: {},
    cts: {},
    pc: {},
    rate: {},
    amount: {},
    labour_rate: {},
    labour_amount: {},
    setting: {
      api_url: apiUrl(ApiEndpoints.master_setting),
      filters: { active: true },
      modelRenderer: nameRenderer,
    },
    stone_place: {
      api_url: apiUrl(ApiEndpoints.stone_place),
      filters: { active: true },
      modelRenderer: nameRenderer,
    },
    default_rate: { boxed: true },
    active: { boxed: true },
  };
}

/** Coerce a form value (string or number, possibly blank) to a number. */
function toNumber(value: any): number {
  const parsed = Number.parseFloat(value);
  return Number.isFinite(parsed) ? parsed : 0;
}

/** Round to the two decimal places the amount columns are stored with. */
function roundAmount(value: number): number {
  return Math.round(value * 100) / 100;
}

/** The properties endpoints backing one stone tab's dropdowns. */
type CostCardStoneLineEndpoints = {
  stone: ApiEndpoints;
  shape: ApiEndpoints;
  size: ApiEndpoints;
  color: ApiEndpoints;
  cut: ApiEndpoints;
  quality: ApiEndpoints;
  /**
   * The rate table to look the line's Rate up in. A tab that names one gets a
   * read-only Rate filled in from Stone + Shape + MM Size; a tab that leaves
   * it out keeps a hand-entered Rate.
   */
  rate?: ApiEndpoints;
};

const DIAMOND_LINE_ENDPOINTS: CostCardStoneLineEndpoints = {
  stone: ApiEndpoints.diamond_stone_list,
  shape: ApiEndpoints.diamond_shape_list,
  size: ApiEndpoints.diamond_size_list,
  color: ApiEndpoints.diamond_color_list,
  cut: ApiEndpoints.diamond_cut_list,
  quality: ApiEndpoints.diamond_quality_list,
  rate: ApiEndpoints.diamond_rate_list,
};

const COLOR_STONE_LINE_ENDPOINTS: CostCardStoneLineEndpoints = {
  stone: ApiEndpoints.color_stone_type_list,
  shape: ApiEndpoints.color_stone_shape_list,
  size: ApiEndpoints.color_stone_size_list,
  color: ApiEndpoints.color_stone_color_list,
  cut: ApiEndpoints.color_stone_cut_list,
  quality: ApiEndpoints.color_stone_quality_list,
};

/**
 * Line fields for a stone tab (Diamond or Color Stone) - the two tabs behave
 * identically, over their own properties endpoints.
 *
 * Amount and L.Amount are read-only: they are computed live from Pcs, Rate,
 * L.Rate and the P/C (rate unit) selector, and can only ever come from those.
 *
 *   P (per piece): Amount = Pcs × Rate
 *   C (per carat): Amount is blanked out — a per-carat line is not priced by
 *                  piece count. It is stored as 0, see
 *                  processCostCardStoneLineData().
 *
 * L.Amount = Pcs × L.Rate either way.
 *
 * MM Size and Sieve Size are two views of the same size record in Properties
 * (each record pairs an mm size with a sieve size), so both are dropdowns over
 * that master list and each prefills the other. The line stores the sieve size
 * as plain text, so Sieve Size is a choice field over the sieve sizes on those
 * records rather than a related field.
 *
 * Pass `loadsExistingLine` on a form that fetches an existing line (the edit
 * modal), so the stored MM Size arriving on load is not read as the user
 * picking one and does not overwrite the line's stored Sieve Size.
 *
 * This state outlives the modal - the modal unmounts its form on close, but
 * this hook lives in the table - so wire the returned `reset` up to the
 * modal's onClose, or the next line opens with the previous one's values.
 */
function useCostCardStoneLineFields(
  costCardId: number,
  endpoints: CostCardStoneLineEndpoints,
  loadsExistingLine: boolean,
): { fields: ApiFormFieldSet; reset: () => void } {
  const api = useApi();

  const [pcs, setPcs] = useState<any>(undefined);
  const [rate, setRate] = useState<any>(undefined);
  const [labourRate, setLabourRate] = useState<any>(undefined);
  const [pc, setPc] = useState<any>(undefined);

  // The three selections the rate table is keyed on (see rateQuery below).
  const [stonePk, setStonePk] = useState<any>(undefined);
  const [shapePk, setShapePk] = useState<any>(undefined);
  const [mmSizePk, setMmSizePk] = useState<any>(undefined);

  // Values pushed back into the two linked size fields. The seeded sieve size
  // is remembered separately so a value stored on the line but missing from
  // the master list still has an option to display.
  const [mmSize, setMmSize] = useState<any>(undefined);
  const [sieveSize, setSieveSize] = useState<any>(undefined);
  const [seededSieveSize, setSeededSieveSize] = useState<any>(undefined);

  // The MM Size dropdown reports its value both when the user picks one and
  // when it loads an existing selection, so react only to an actual change.
  const lastMmPk = useRef<any>(undefined);
  const mmAwaitingSeed = useRef<boolean>(loadsExistingLine);

  const stoneSizesQuery = useQuery({
    queryKey: ["cost-card-stone-sizes", endpoints.size],
    queryFn: async () => {
      const url = apiUrl(endpoints.size);

      // The properties endpoints cap a page at 100 records, so walk the pages
      // rather than asking for one oversized one and silently losing sizes.
      const pageSize = 100;
      const maxPages = 20;
      const collected: any[] = [];
      let offset = 0;

      for (let page = 0; page < maxPages; page++) {
        const response = await api.get(url, {
          params: { active: true, limit: pageSize, offset: offset },
        });

        const data = response.data;
        const results = Array.isArray(data) ? data : (data?.results ?? []);

        collected.push(...results);

        const count = Array.isArray(data)
          ? collected.length
          : (data?.count ?? collected.length);

        if (results.length === 0 || collected.length >= count) break;

        offset += pageSize;
      }

      return collected;
    },
    staleTime: 5 * 60 * 1000,
  });

  const stoneSizes: any[] = useMemo(
    () => stoneSizesQuery.data ?? [],
    [stoneSizesQuery.data],
  );

  const sieveChoices: ApiFormFieldChoice[] = useMemo(() => {
    const seen = new Set<string>();
    const choices: ApiFormFieldChoice[] = [];

    for (const size of stoneSizes) {
      const value = size?.sieve_size;

      if (!value || seen.has(value)) continue;

      seen.add(value);
      choices.push({ value: value, display_name: value });
    }

    const current = sieveSize || seededSieveSize;

    if (current && !seen.has(current)) {
      choices.push({ value: current, display_name: current });
    }

    return choices;
  }, [stoneSizes, sieveSize, seededSieveSize]);

  // MM Size -> Sieve Size.
  const onMmSizeChange = useCallback((value: any, record: any) => {
    const pk = value ?? null;

    // The rate lookup keys on the selection either way - a seeded MM Size is
    // still the MM Size the line's rate must match.
    setMmSizePk(pk);

    if (mmAwaitingSeed.current) {
      // The stored MM Size of the line being edited, not a user selection.
      mmAwaitingSeed.current = false;
      lastMmPk.current = pk;
      return;
    }

    if (pk === lastMmPk.current) return;

    lastMmPk.current = pk;

    // Push the cleared state back as a blank rather than a null: ApiForm only
    // treats a non-null field value as caller-controlled, and a null one is
    // overwritten again by the data fetched for the line being edited. The
    // field's adjustValue turns the blank back into a null for the form.
    setMmSize(pk ?? "");

    // The two fields are one pair, so clearing MM Size clears Sieve Size.
    if (!pk) {
      setSieveSize("");
      setSeededSieveSize(undefined);
      return;
    }

    setSieveSize(record?.sieve_size ?? "");
  }, []);

  // Sieve Size -> MM Size.
  const onSieveSizeChange = useCallback(
    (value: any, record?: any) => {
      // A choice field is only given a second argument when ApiForm seeds the
      // form from the server - that is not the user picking a sieve size.
      if (record !== undefined) {
        setSeededSieveSize(value ?? undefined);
        return;
      }

      setSieveSize(value ?? "");
      setSeededSieveSize(undefined);

      // ... and clearing Sieve Size clears MM Size.
      if (!value) {
        lastMmPk.current = null;
        mmAwaitingSeed.current = false;
        setMmSize("");
        setMmSizePk(null);
        return;
      }

      const match = stoneSizes.find((size) => size?.sieve_size === value);

      if (!match?.pk) return;

      // Adopt the pk up front, so the dropdown loading it back does not read
      // as a fresh user selection and bounce the sieve size we matched on.
      lastMmPk.current = match.pk;
      mmAwaitingSeed.current = false;
      setMmSize(match.pk);
      setMmSizePk(match.pk);
    },
    [stoneSizes],
  );

  // --- Rate lookup -----------------------------------------------------
  // A rate table row is unique on (stone, shape, mm size), so once all three
  // are picked the line's Rate is that row's rate - the field is read-only and
  // can only ever come from here. A combination with no row priced for it
  // leaves the Rate blank rather than keeping a rate from another combination.
  const hasRateLookup = !!endpoints.rate;

  const rateLookupKeys = useMemo(
    () =>
      hasRateLookup && stonePk && shapePk && mmSizePk
        ? { stone: stonePk, shape: shapePk, mm_size: mmSizePk }
        : null,
    [hasRateLookup, stonePk, shapePk, mmSizePk],
  );

  const rateQuery = useQuery({
    queryKey: ["cost-card-stone-line-rate", endpoints.rate, rateLookupKeys],
    enabled: !!rateLookupKeys,
    queryFn: async () => {
      const response = await api.get(apiUrl(endpoints.rate!), {
        params: { active: true, ...rateLookupKeys, limit: 1, offset: 0 },
      });

      const data = response.data;
      const results = Array.isArray(data) ? data : (data?.results ?? []);

      // null, not undefined: "looked it up, nothing is priced for it".
      return results[0]?.rate ?? null;
    },
    staleTime: 5 * 60 * 1000,
  });

  const lookedUpRate = rateQuery.data;

  useEffect(() => {
    if (!rateLookupKeys || lookedUpRate === undefined) return;

    // Push the blank back as "" rather than null - ApiForm only treats a
    // non-null field value as caller-controlled.
    setRate(lookedUpRate ?? "");
  }, [rateLookupKeys, lookedUpRate]);

  // Clearing any of the three keys clears the rate they produced.
  const onRateKeyChange = useCallback(
    (setKey: (value: any) => void) => (value: any) => {
      const pk = value ?? null;

      setKey(pk);

      if (!pk) setRate("");
    },
    [],
  );

  const onStoneChange = useMemo(
    () => onRateKeyChange(setStonePk),
    [onRateKeyChange],
  );
  const onShapeChange = useMemo(
    () => onRateKeyChange(setShapePk),
    [onRateKeyChange],
  );

  const reset = useCallback(() => {
    setPcs(undefined);
    setRate(undefined);
    setLabourRate(undefined);
    setPc(undefined);
    setMmSize(undefined);
    setSieveSize(undefined);
    setSeededSieveSize(undefined);
    setStonePk(undefined);
    setShapePk(undefined);
    setMmSizePk(undefined);
    lastMmPk.current = undefined;
    mmAwaitingSeed.current = loadsExistingLine;
  }, [loadsExistingLine]);

  const fields: ApiFormFieldSet = useMemo(() => {
    const pcsValue = toNumber(pcs);

    // 'C' is the model default, so an untouched P/C selector counts as C.
    const amount = pc === "P" ? roundAmount(pcsValue * toNumber(rate)) : "";
    const labourAmount = roundAmount(pcsValue * toNumber(labourRate));

    const baseFields = costCardStoneLineFields(
      endpoints.stone,
      endpoints.shape,
      endpoints.size,
      endpoints.color,
      endpoints.cut,
      endpoints.quality,
    );

    return {
      cost_card: { hidden: true, value: costCardId },
      ...baseFields,
      stone: { ...baseFields.stone, onValueChange: onStoneChange },
      shape: { ...baseFields.shape, onValueChange: onShapeChange },
      mm_size: {
        ...baseFields.mm_size,
        value: mmSize,
        adjustValue: (value: any) => (value === "" ? null : value),
        onValueChange: onMmSizeChange,
      },
      sieve_size: {
        field_type: "choice",
        choices: sieveChoices,
        // Match the MM Size dropdown it sits next to, which is a related field.
        searchableSelect: true,
        clearable: true,
        value: sieveSize,
        onValueChange: onSieveSizeChange,
      },
      pcs: { onValueChange: (value: any) => setPcs(value) },
      pc: { onValueChange: (value: any) => setPc(value) },
      rate: hasRateLookup
        ? { value: rate, read_only: true, disabled: true }
        : { onValueChange: (value: any) => setRate(value) },
      amount: { value: amount, read_only: true, disabled: true },
      labour_rate: { onValueChange: (value: any) => setLabourRate(value) },
      labour_amount: {
        value: labourAmount,
        read_only: true,
        disabled: true,
      },
    };
  }, [
    costCardId,
    endpoints,
    pcs,
    rate,
    labourRate,
    pc,
    mmSize,
    sieveSize,
    sieveChoices,
    hasRateLookup,
    onStoneChange,
    onShapeChange,
    onMmSizeChange,
    onSieveSizeChange,
  ]);

  return useMemo(() => ({ fields: fields, reset: reset }), [fields, reset]);
}

/** Diamond tab line fields — one row per diamond entry on the cost card. */
export function useCostCardDiamondLineFields(
  costCardId: number,
  loadsExistingLine: boolean = false,
): { fields: ApiFormFieldSet; reset: () => void } {
  return useCostCardStoneLineFields(
    costCardId,
    DIAMOND_LINE_ENDPOINTS,
    loadsExistingLine,
  );
}

/** Color Stone tab line fields — one row per color stone entry on the card. */
export function useCostCardColorStoneLineFields(
  costCardId: number,
  loadsExistingLine: boolean = false,
): { fields: ApiFormFieldSet; reset: () => void } {
  return useCostCardStoneLineFields(
    costCardId,
    COLOR_STONE_LINE_ENDPOINTS,
    loadsExistingLine,
  );
}

/**
 * A per-carat line shows a blank Amount, and a stone combination with no row
 * in the rate table shows a blank Rate — but both backend columns are non-null
 * decimals, so send those blanks as 0 rather than as an empty string.
 */
export function processCostCardStoneLineData(data: any): any {
  const processed = { ...data };

  for (const field of ["amount", "rate"]) {
    const value = processed[field];

    if (value === "" || value === null || value === undefined) {
      processed[field] = 0;
    }
  }

  return processed;
}

/** Finish Type tab line fields — one row per finish applied to the cost card. */
export function costCardFinishLineFields(costCardId: number): ApiFormFieldSet {
  return {
    cost_card: { hidden: true, value: costCardId },
    finish_type: {
      api_url: `${apiUrl(ApiEndpoints.finish_type)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? "";
      },
    },
    rate: {},
    active: { boxed: true },
  };
}

export function DiamondStoneFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function diamondCutFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function diamondShapeFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function diamondColorFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function diamondSizeFields(): ApiFormFieldSet {
  return {
    name: {},
    mm_size: {},
    sieve_size: {},
    description: {},
    active: { boxed: true },
  };
}

export function diamondQualityFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
  };
}

export function diamondRateFields(): ApiFormFieldSet {
  return {
    shape: {
      api_url: `${apiUrl(ApiEndpoints.diamond_shape_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    mm_size: {
      api_url: `${apiUrl(ApiEndpoints.diamond_size_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    stone: {
      api_url: `${apiUrl(ApiEndpoints.diamond_stone_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    color: {
      api_url: `${apiUrl(ApiEndpoints.diamond_color_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    cut: {
      api_url: `${apiUrl(ApiEndpoints.diamond_cut_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    quality: {
      api_url: `${apiUrl(ApiEndpoints.diamond_quality_list)}?active=true`,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    pointer: {},
    rate: {},
    pc: {
      default: "C",
    },
    customers: {
      field_type: "related field",
      model: ModelType.company,
      multiple: true,
      api_url: apiUrl(ApiEndpoints.company_list),
      filters: { is_customer: true },
      disableWhen: (values: any) => !!values?.all_customers,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.code ?? "";
      },
    },
    all_customers: { boxed: true },
    active: { boxed: true },
  };
}

export function useCustomStateFields(): ApiFormFieldSet {
  // Status codes
  const statusCodes = useGlobalStatusState();

  // Selected base status class
  const [statusClass, setStatusClass] = useState<string>("");

  // Construct a list of status options based on the selected status class
  const statusOptions: any[] = useMemo(() => {
    const options: any[] = [];

    const valuesList = Object.values(statusCodes.status ?? {}).find(
      (value: StatusCodeListInterface) => value.status_class === statusClass,
    );

    Object.values(valuesList?.values ?? {}).forEach(
      (value: StatusCodeInterface) => {
        options.push({
          value: value.key,
          display_name: value.label,
        });
      },
    );

    return options;
  }, [statusCodes, statusClass]);

  return useMemo(() => {
    return {
      reference_status: {
        onValueChange(value) {
          setStatusClass(value);
        },
      },
      logical_key: {
        field_type: "choice",
        choices: statusOptions,
      },
      key: {},
      name: {},
      label: {},
      color: {},
      model: {},
    };
  }, [statusOptions]);
}

export function customUnitsFields(): ApiFormFieldSet {
  return {
    name: {},
    definition: {},
    symbol: {},
  };
}

export function extraLineItemFields(): ApiFormFieldSet {
  return {
    order: {
      hidden: true,
    },
    line: {},
    reference: {},
    description: {},
    quantity: {},
    price: {},
    price_currency: {},
    project_code: ProjectCodeField(),
    notes: {},
    link: {},
  };
}

export function useParameterTemplateFields(): ApiFormFieldSet {
  return useMemo(() => {
    return {
      name: {},
      description: {},
      units: {},
      model_type: {},
      choices: {},
      checkbox: {},
      selectionlist: {
        filters: {
          active: true,
        },
      },
      enabled: {},
    };
  }, []);
}

/**
 * Shared hook for the dynamic "value" field on parameter forms.
 *
 * When the user selects a parameter template, the field type for the
 * corresponding value input (data / default_value) must change to match the
 * template's data type (boolean, choice, related-field selection list, or
 * plain string).  This hook encapsulates that state so it can be reused
 * across the "Add Parameter" and "Add Category Parameter" forms.
 *
 * @param resetDep - When this value changes all internal state is reset to
 *   defaults.  Pass a stringified key derived from the form's context (e.g.
 *   `${modelType}-${modelId}`) so the field resets when the context switches.
 */
export function useDynamicParameterValueField(resetDep?: any): {
  onTemplateValueChange: (value: any, record: any) => void;
  valueFieldConfig: ApiFormFieldType;
  reset: () => void;
} {
  const api = useApi();

  const [selectionListId, setSelectionListId] = useState<number | null>(null);
  const [choices, setChoices] = useState<any[]>([]);
  const [fieldType, setFieldType] = useState<
    "string" | "boolean" | "choice" | "related field"
  >("string");
  const [data, setData] = useState<string>("");

  const reset = useCallback(() => {
    setSelectionListId(null);
    setFieldType("string");
    setChoices([]);
    setData("");
  }, []);

  useEffect(() => {
    reset();
  }, [resetDep, reset]);

  const fetchSelectionEntry = useCallback(
    (value: any) => {
      if (!value || !selectionListId) {
        return null;
      }

      return api
        .get(apiUrl(ApiEndpoints.selectionentry_list, selectionListId), {
          params: { value: value },
        })
        .then((response) => {
          if (response.data && response.data.length == 1) {
            return response.data[0];
          } else {
            return null;
          }
        });
    },
    [selectionListId],
  );

  const onTemplateValueChange = useCallback(
    (value: any, record: any) => {
      setSelectionListId(record?.selectionlist || null);
      setData("");

      if (record?.checkbox) {
        setChoices([]);
        setFieldType("boolean");
        setData("false");
      } else if (record?.choices) {
        const _choices: string[] = record.choices.split(",");

        if (_choices.length > 0) {
          setChoices(
            _choices.map((choice) => ({
              display_name: choice.trim(),
              value: choice.trim(),
            })),
          );
          setFieldType("choice");
        } else {
          setChoices([]);
          setFieldType("string");
          setData("");
        }
      } else if (record?.selectionlist) {
        setFieldType("related field");
        setData("");
      } else {
        setFieldType("string");
        setData("");
      }
    },
    [setFieldType, setData, setChoices],
  );

  const valueFieldConfig: ApiFormFieldType = useMemo(
    () => ({
      value: data,
      onValueChange: (value: any, record: any) => {
        if (fieldType === "related field" && selectionListId) {
          // For related fields, store the primary key value (not the string representation)
          setData(record?.value ?? value);
        } else {
          setData(value);
        }
      },
      field_type: fieldType,
      choices: fieldType === "choice" ? choices : undefined,
      default: fieldType === "boolean" ? false : undefined,
      pk_field:
        fieldType === "related field" && selectionListId ? "value" : undefined,
      model:
        fieldType === "related field" && selectionListId
          ? ModelType.selectionentry
          : undefined,
      api_url:
        fieldType === "related field" && selectionListId
          ? apiUrl(ApiEndpoints.selectionentry_list, selectionListId)
          : undefined,
      filters: fieldType === "related field" ? { active: true } : undefined,
      adjustValue: (value: any) => {
        let v: string = value.toString().trim();

        if (fieldType === "boolean") {
          if (v.toLowerCase() !== "true") {
            v = "false";
          }
        }

        return v;
      },
      singleFetchFunction: fetchSelectionEntry,
    }),
    [data, fieldType, choices, selectionListId, fetchSelectionEntry],
  );

  return { onTemplateValueChange, valueFieldConfig, reset };
}

export function useParameterFields({
  modelType,
  modelId,
}: {
  modelType: ModelType;
  modelId: number;
}): ApiFormFieldSet {
  const user = useUserState.getState();
  const templateCreateFields = useParameterTemplateFields();

  const resetKey = useMemo(
    () => `${modelType}-${modelId}`,
    [modelType, modelId],
  );
  const { onTemplateValueChange, valueFieldConfig } =
    useDynamicParameterValueField(resetKey);

  return useMemo(() => {
    return {
      model_type: {
        hidden: true,
        value: modelType,
      },
      model_id: {
        hidden: true,
        value: modelId,
      },
      template: {
        filters: {
          for_model: modelType,
          enabled: true,
        },
        onValueChange: onTemplateValueChange,
        addCreateFields: user.isStaff() ? templateCreateFields : undefined,
      },
      data: valueFieldConfig,
      note: {},
    };
  }, [
    modelType,
    modelId,
    onTemplateValueChange,
    valueFieldConfig,
    templateCreateFields,
    user,
  ]);
}

export function selectionListFields(): ApiFormFieldSet {
  return {
    name: {},
    description: {},
    active: { boxed: true },
    source_plugin: {},
    source_string: {},
  };
}

export function selectionEntryFields(): ApiFormFieldSet {
  return {
    value: {},
    label: {},
    description: {},
    active: { boxed: true },
  };
}
