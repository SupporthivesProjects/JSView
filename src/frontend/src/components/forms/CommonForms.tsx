import { Table, TextInput } from "@mantine/core";
import { randomId } from "@mantine/hooks";
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
import { StandaloneField } from "./StandaloneField";
import {
  TableFieldQuantityInput,
  type TableFieldRowProps,
} from "./fields/TableField";
import RemoveRowButton from "../ui/buttons/RemoveRowButton";

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
      api_url: apiUrl(ApiEndpoints.metal_type_list),
      filters: { active: true },
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
      api_url: apiUrl(ApiEndpoints.metal_type_list),
      filters: { active: true },
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
      api_url: apiUrl(ApiEndpoints.finding_type),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    name: {},
    // type: {},
    weight: {},
    metal: {
      api_url: apiUrl(ApiEndpoints.metal_purity_list),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
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
      api_url: apiUrl(ApiEndpoints.metal_type_list),
      filters: { active: true },
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

export const PURCHASE_REQUEST_FORM_GRID_COLUMNS = { base: 1, sm: 2, lg: 3 };

/** Width of the purchase request modal, sized to hold three columns. */
export const PURCHASE_REQUEST_MODAL_SIZE = "72rem";

/* A purchase order is laid out exactly like a purchase request */
export const PURCHASE_ORDER_FORM_GRID_COLUMNS =
  PURCHASE_REQUEST_FORM_GRID_COLUMNS;
export const PURCHASE_ORDER_MODAL_SIZE = PURCHASE_REQUEST_MODAL_SIZE;

/** Categories which can be assigned to a purchase request */
export const PO_CATEGORY_CHOICES: ApiFormFieldChoice[] = [
  { value: "Extra", display_name: "Extra" },
  { value: "Master Sample", display_name: "Master Sample" },
  { value: "Production", display_name: "Production" },
  { value: "Sample", display_name: "Sample" },
  { value: "Spl Order", display_name: "Spl Order" },
  { value: "Casting", display_name: "Casting" },
  { value: "CZ Sample", display_name: "CZ Sample" },
  { value: "CZ Host Sample", display_name: "CZ Host Sample" },
  { value: "Photo Sample", display_name: "Photo Sample" },
];

/** Split a comma separated list ("7, 8, 9") into its trimmed, non-blank entries */
function splitCommaList(value: any): string[] {
  return String(value ?? "")
    .split(",")
    .map((entry) => entry.trim())
    .filter((entry) => entry !== "");
}

/** Total quantity for a line - the sum of its Size Pcs entries */
function sumSizePcs(spcs: any): number {
  return splitCommaList(spcs).reduce((total, entry) => {
    const pcs = Number(entry);
    return Number.isFinite(pcs) ? total + pcs : total;
  }, 0);
}

/**
 * A single (as yet unsaved) line item row in the purchase request form.
 * Each row maps to one entry of the `items` payload.
 */
function PurchaseRequestLineRow({
  props,
}: Readonly<{ props: TableFieldRowProps }>) {
  const { item, rowId, rowErrors, changeFn, removeFn } = props;

  const costCardField: ApiFormFieldType = useMemo(() => {
    return {
      field_type: "related field",
      api_url: apiUrl(ApiEndpoints.cost_card),
      filters: { active: true },
      required: false,
      value: item.costcardid,
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.cost_card_no ?? "";
      },
      onValueChange: (value: any, instance: any) => {
        changeFn(rowId, "costcardid", value);

        // Carry the style numbers and vendor across from the selected cost card
        if (instance) {
          changeFn(rowId, "styleno", instance.our_style_no ?? "");
          changeFn(rowId, "vstyleno", instance.vendor_style_no ?? "");
          changeFn(rowId, "vendorid", instance.vendor ?? null);
        }
      },
    };
  }, [item.costcardid, rowId, changeFn]);

  // Vendor for this specific line, carried over from the selected cost card.
  // Only the pk is stored on the row, so look up the name for display.
  const api = useApi();
  const vendorQuery = useQuery({
    queryKey: ["purchase-request-line-vendor", item.vendorid],
    queryFn: () =>
      api
        .get(apiUrl(ApiEndpoints.master_vendor_customer, item.vendorid))
        .then((response) => response.data),
    enabled: !!item.vendorid,
    staleTime: 5 * 60 * 1000,
  });

  const vendorName = item.vendorid
    ? (vendorQuery.data?.name ?? vendorQuery.data?.code ?? "")
    : "";

  return (
    <Table.Tr key={`table-row-${rowId}`}>
      <Table.Td>
        <StandaloneField
          fieldName="costcardid"
          fieldDefinition={costCardField}
          error={rowErrors?.costcardid?.message}
          hideLabels
        />
      </Table.Td>
      <Table.Td>
        <TextInput
          aria-label="text-field-styleno"
          value={item.styleno ?? ""}
          disabled
          onChange={(event) =>
            changeFn(rowId, "styleno", event.currentTarget.value)
          }
          error={rowErrors?.styleno?.message}
        />
      </Table.Td>
      <Table.Td>
        {/* Carried over from the selected cost card, never typed by hand */}
        <TextInput
          aria-label="text-field-vstyleno"
          disabled
          value={item.vstyleno ?? ""}
          error={rowErrors?.vstyleno?.message}
        />
      </Table.Td>
      <Table.Td>
        {/* Carried over from the selected cost card, never typed by hand */}
        <TextInput
          aria-label="text-field-vendorid"
          disabled
          value={vendorName}
          error={rowErrors?.vendorid?.message}
        />
      </Table.Td>
      <Table.Td>
        {/* Locked - the handler is kept so it can be reopened for editing
            by dropping `disabled`, without rewiring the row */}
        <TableFieldQuantityInput
          min={0}
          disabled
          value={item.qty ?? 0}
          onChange={(value) => changeFn(rowId, "qty", value === "" ? 0 : value)}
          error={rowErrors?.qty?.message}
        />
      </Table.Td>
      <Table.Td>
        <TextInput
          aria-label="text-field-size"
          placeholder="7,8,9"
          value={item.size ?? ""}
          onChange={(event) =>
            changeFn(rowId, "size", event.currentTarget.value)
          }
          error={rowErrors?.size?.message}
        />
      </Table.Td>
      <Table.Td>
        <TextInput
          aria-label="text-field-spcs"
          placeholder="1,2,3"
          value={item.spcs ?? ""}
          onChange={(event) => {
            const spcs = event.currentTarget.value;
            changeFn(rowId, "spcs", spcs);
            // Quantity is always the total of the Size Pcs entries
            changeFn(rowId, "qty", sumSizePcs(spcs));
          }}
          error={rowErrors?.spcs?.message}
        />
      </Table.Td>
      <Table.Td>
        <RemoveRowButton onClick={() => removeFn(rowId)} />
      </Table.Td>
    </Table.Tr>
  );
}

function newPurchaseRequestLineItem() {
  return {
    uuid: randomId(),
    costcardid: null,
    styleno: "",
    vstyleno: "",
    vendorid: null,
    qty: 0,
    size: "",
    spcs: "",
  };
}

/** The two kinds of record held by the purchase order endpoint */
export type POType = "REQUEST" | "ORDER";

/**
 * Header fields shared by the purchase request and purchase order forms.
 *
 * A request and an order are the same record with a different `potype`; an
 * order additionally names the vendor it is placed with, and the customer's
 * own reference number for it.
 */
function purchaseHeaderFields(potype: POType): ApiFormFieldSet {
  const isOrder = potype === "ORDER";

  return {
    pocategory: {
      label: "Category",
      field_type: "choice",
      default: "Production",
      choices: PO_CATEGORY_CHOICES,
    },
    potype: {
      value: potype,
      hidden: true,
    },
    // Row 1 - the record's own particulars
    podate: {
      label: isOrder ? "P.O. Date" : "P.R. Date",
      default: new Date().toISOString().split("T")[0],
    },
    ddate: {
      label: "Delivery Date",
    },

    ...(isOrder
      ? {
          vcsdate: {
            label: "Vendor Confirmed Ship Date",
          },
        }
      : {}),

    // Row 2 - who the record is for, and on what terms
    customerid: {
      label: "Customer",
      api_url: apiUrl(ApiEndpoints.master_vendor_customer),
      filters: {
        active: true,
        is_customer: true,
      },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.code ?? instance?.name ?? "";
      },
    },
    acexeid: {
      label: "Executive",
      api_url: apiUrl(ApiEndpoints.master_executive),
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? "";
      },
    },
    termsid: {
      label: "Terms",
      api_url: apiUrl(ApiEndpoints.master_terms),
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? "";
      },
    },
    stampid: {
      label: "Stamp",
      api_url: apiUrl(ApiEndpoints.master_stamp),
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? "";
      },
    },
    rem: {
      label: "Remarks",
    },
    ...(isOrder
      ? {
          note: {
            label: "Add note",
            multiline: true,
            gridSpan: "full",
          },
        }
      : {}),
  };
}

/** The editable grid of line items, shared by the create and edit forms */
function purchaseRequestLineTable(potype: POType): ApiFormFieldType {
  return {
    label: "Line Items",
    description:
      potype === "ORDER"
        ? "Styles ordered against this purchase order"
        : "Styles requested against this purchase request",
    field_type: "table",
    required: false,
    gridSpan: "full",
    headers: [
      { title: "Cost Card", style: { minWidth: "180px" } },
      { title: "Style No", style: { minWidth: "120px" } },
      { title: "Vendor Style No", style: { minWidth: "120px" } },
      { title: "Vendor", style: { minWidth: "160px" } },
      { title: "Quantity", style: { minWidth: "90px" } },
      { title: "Size", style: { minWidth: "100px" } },
      { title: "Size Pcs", style: { minWidth: "100px" } },
      { title: "", style: { width: "50px" } },
    ],
    modelRenderer: (row: TableFieldRowProps) => (
      <PurchaseRequestLineRow key={row.rowId} props={row} />
    ),
    addRow: newPurchaseRequestLineItem,
  };
}

function purchaseFields(potype: POType, editing: boolean): ApiFormFieldSet {
  return {
    ...purchaseHeaderFields(potype),
    ...(editing
      ? {
          lines: {
            ...purchaseRequestLineTable(potype),
            exclude: true,
            disabled: false,
            default: [],
          },
        }
      : {
          items: {
            ...purchaseRequestLineTable(potype),
            value: [],
          },
        }),
  };
}

export function purchaseRequestHeaderFields(): ApiFormFieldSet {
  return purchaseHeaderFields("REQUEST");
}

export function purchaseOrderHeaderFields(): ApiFormFieldSet {
  return purchaseHeaderFields("ORDER");
}

export function purchaseRequestFields(editing = false): ApiFormFieldSet {
  return purchaseFields("REQUEST", editing);
}

export function purchaseOrderFields(editing = false): ApiFormFieldSet {
  return purchaseFields("ORDER", editing);
}

function purchaseRequestLinePayload(row: any) {
  return {
    costcardid: row.costcardid ?? null,
    styleno: row.styleno ?? "",
    vstyleno: row.vstyleno ?? "",
    vendorid: row.vendorid ?? null,
    qty: row.qty ?? 0,
    size: row.size ?? "",
    spcs: row.spcs ?? "",
  };
}

/** A row with nothing entered in any of its editable columns */
function isEmptyPurchaseRequestLine(row: any): boolean {
  return (
    !row?.costcardid &&
    !String(row?.styleno ?? "").trim() &&
    !String(row?.vstyleno ?? "").trim() &&
    !row?.vendorid &&
    splitCommaList(row?.size).length === 0 &&
    splitCommaList(row?.spcs).length === 0
  );
}

/**
 * Validate the line items of a purchase request before it is submitted.
 * Errors are attached to the offending rows, and false cancels the submit.
 *
 * @param fieldName : The table field holding the rows ("items" or "lines")
 * @param requireRow : Reject the submit when the table holds no rows at all
 */
export function validatePurchaseRequestLines(
  fieldName: string,
  requireRow = false,
) {
  return (data: any, form: any): boolean => {
    let valid = true;
    const rows = data?.[fieldName] ?? [];

    if (requireRow && rows.length === 0) {
      form.setError(fieldName, {
        message: "At least one line item is required",
      });
      return false;
    }

    rows.forEach((row: any, idx: number) => {
      const path = `${fieldName}.${idx}`;

      if (isEmptyPurchaseRequestLine(row)) {
        form.setError(`${path}.non_field_errors`, {
          message: "Empty row cannot be saved - fill it in or remove it",
        });
        valid = false;
        return;
      }

      if (!row.costcardid) {
        form.setError(`${path}.costcardid`, {
          message: "Cost card is required",
        });
        valid = false;
      }

      const sizes = splitCommaList(row.size);
      const pcs = splitCommaList(row.spcs);

      if (pcs.some((entry) => !Number.isFinite(Number(entry)))) {
        form.setError(`${path}.spcs`, {
          message: "Size Pcs must be comma separated numbers",
        });
        valid = false;
      }

      if (sizes.length !== pcs.length) {
        const message = `Size has ${sizes.length} value(s) but Size Pcs has ${pcs.length}`;
        form.setError(`${path}.size`, { message });
        form.setError(`${path}.spcs`, { message });
        valid = false;
      }
    });

    return valid;
  };
}

/** Strip the client-side row keys from the line items before submission */
export function processPurchaseRequestData(data: any) {
  return {
    ...data,
    items: (data.items ?? []).map(purchaseRequestLinePayload),
  };
}

export async function savePurchaseRequestLines({
  api,
  poPk,
  originalLines,
  rows,
}: {
  api: any;
  poPk: number;
  originalLines: any[];
  rows: any[];
}) {
  const url = apiUrl(ApiEndpoints.purchase_api_line);
  const keptPks = new Set(
    (rows ?? []).map((row: any) => row.pk).filter((pk: any) => !!pk),
  );

  const requests: Promise<any>[] = [];

  // Rows the user removed from the grid. A row that something else already
  // deleted is treated as done rather than as a failure.
  for (const line of originalLines ?? []) {
    if (line.pk && !keptPks.has(line.pk)) {
      requests.push(
        api.delete(`${url}${line.pk}/`).catch((error: any) => {
          if (error?.response?.status !== 404) {
            throw error;
          }
        }),
      );
    }
  }

  for (const row of rows ?? []) {
    const payload = purchaseRequestLinePayload(row);

    if (row.pk) {
      requests.push(api.patch(`${url}${row.pk}/`, payload));
    } else {
      requests.push(api.post(url, { ...payload, poid: poPk }));
    }
  }

  await Promise.all(requests);
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

/**
 * Build an adjustValue function which drops every character not matched by
 * `allowed` as the user types. Letters are upper-cased first, so a typed "x"
 * is kept as "X".
 */
function allowOnlyChars(allowed: RegExp) {
  return (value: any) => {
    if (typeof value !== "string") {
      return value;
    }

    return value
      .toUpperCase()
      .split("")
      .filter((char) => allowed.test(char))
      .join("");
  };
}

// Stone size (Diamond / Color Stone properties): numbers, M and X
const STONE_MM_SIZE_FIELD = {
  adjustValue: allowOnlyChars(/[0-9.MX]/),
  showAdjustedValue: true,
};

// Stone sieve size: numbers, +, -, M and X
const STONE_SIEVE_SIZE_FIELD = {
  adjustValue: allowOnlyChars(/[0-9.+\-MX]/),
  showAdjustedValue: true,
};

export function colorStoneSizeFields(): ApiFormFieldSet {
  return {
    name: {},
    mm_size: { ...STONE_MM_SIZE_FIELD },
    sieve_size: { ...STONE_SIEVE_SIZE_FIELD },
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
      api_url: apiUrl(ApiEndpoints.color_stone_shape_list),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    mm_size: {
      api_url: apiUrl(ApiEndpoints.color_stone_size_list),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    stone: {
      api_url: apiUrl(ApiEndpoints.color_stone_type_list),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    color: {
      api_url: apiUrl(ApiEndpoints.color_stone_color_list),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    cut: {
      api_url: apiUrl(ApiEndpoints.color_stone_cut_list),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    quality: {
      api_url: apiUrl(ApiEndpoints.color_stone_quality_list),
      filters: { active: true },
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

export const COST_CARD_FORM_GRID_COLUMNS = { base: 1, sm: 2, lg: 3 };

/** Width of a cost card line modal, sized to hold three columns of fields. */
export const COST_CARD_LINE_MODAL_SIZE = "72rem";

export function useCostCardGeneralFields(): ApiFormFieldSet {
  const [metalGrams, setMetalGrams] = useState<any>(undefined);
  const [karat, setKarat] = useState<any>(undefined);
  const [findingItemId, setFindingItemId] = useState<any>(undefined);
  const [findingPrice, setFindingPrice] = useState<any>(undefined);

  return useMemo(() => {
    return costCardGeneralFieldSet(
      metalGrams,
      setMetalGrams,
      karat,
      setKarat,
      findingPrice,
      setFindingPrice,
      findingItemId,
      setFindingItemId,
    );
  }, [metalGrams, karat, findingPrice, findingItemId]);
}

function costCardGeneralFieldSet(
  metalGrams: any,
  setMetalGrams: (value: any) => void,
  karat: any,
  setKarat: (value: any) => void,
  findingPrice: any,
  setFindingPrice: (value: any) => void,
  fingingItemId: any,
  setFindingItemId: (value: any) => void,
): ApiFormFieldSet {
  return {
    cost_card_no: { read_only: true },
    our_style_no: {},
    vendor_style_no: {},
    vendor: {
      api_url: apiUrl(ApiEndpoints.master_vendor_customer),
      filters: { active: true, is_supplier: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.code ?? (instance?.code ? `#${instance.code}` : "");
      },
    },
    customer: {
      api_url: apiUrl(ApiEndpoints.master_vendor_customer),
      filters: { active: true, is_customer: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.code ?? (instance?.code ? `#${instance.code}` : "");
      },
    },
    category: {
      api_url: apiUrl(ApiEndpoints.jewellery_category),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    sub_category: {
      api_url: apiUrl(ApiEndpoints.jewellery_sub_category),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    metal_purity: {
      api_url: apiUrl(ApiEndpoints.metal_purity_list),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
      onValueChange: (_value: any, instance?: any) => {
        setKarat(instance?.karat ?? null);
        setFindingItemId(instance?.pk ?? null);
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
      api_url: apiUrl(ApiEndpoints.finding_item),
      filters: { active: true, metal: fingingItemId },
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
    pc: {},
    default_rate: { boxed: true },
    rate: {},
    cts: {},
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
    active: { boxed: true, default: true, hidden: true },
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
  /** The rate table the line's Rate is looked up in. */
  rate: ApiEndpoints;
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
  rate: ApiEndpoints.color_stone_rate_list,
};

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

  // D.R. 'yes' takes the Rate from the rate table; 'no' (the model default,
  // so an untouched selector counts as 'no') leaves it for the user to enter.
  const [defaultRate, setDefaultRate] = useState<any>(undefined);
  const usesDefaultRate = defaultRate === "yes";

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
  // are picked with D.R. set to 'yes', the line's Rate is that row's rate -
  // the field is read-only and can only come from here. A combination with no
  // row priced for it leaves the Rate blank rather than keeping a rate from
  // another combination. With D.R. 'no' the Rate is entered by hand instead.
  const rateLookupKeys = useMemo(
    () =>
      stonePk && shapePk && mmSizePk
        ? { stone: stonePk, shape: shapePk, mm_size: mmSizePk }
        : null,
    [stonePk, shapePk, mmSizePk],
  );

  const rateQuery = useQuery({
    queryKey: ["cost-card-stone-line-rate", endpoints.rate, rateLookupKeys],
    enabled: !!rateLookupKeys,
    queryFn: async () => {
      const response = await api.get(apiUrl(endpoints.rate), {
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
    // A hand-entered rate is left alone - switching D.R. to 'no' keeps
    // whatever rate was showing as the starting point for the user's own.
    if (!usesDefaultRate) return;

    // Push the blank back as "" rather than null - ApiForm only treats a
    // non-null field value as caller-controlled.
    if (!rateLookupKeys) {
      // Clearing any of the three keys clears the rate they produced.
      setRate("");
      return;
    }

    if (lookedUpRate === undefined) return;

    setRate(lookedUpRate ?? "");
  }, [usesDefaultRate, rateLookupKeys, lookedUpRate]);

  const onStoneChange = useCallback(
    (value: any) => setStonePk(value ?? null),
    [],
  );
  const onShapeChange = useCallback(
    (value: any) => setShapePk(value ?? null),
    [],
  );

  const reset = useCallback(() => {
    setPcs(undefined);
    setRate(undefined);
    setLabourRate(undefined);
    setPc(undefined);
    setDefaultRate(undefined);
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
      rate: {
        value: rate,
        read_only: usesDefaultRate,
        disabled: usesDefaultRate,
        // Also seeds the stored rate of the line being edited. A cleared rate
        // is kept as "" so ApiForm does not restore the fetched one over it.
        onValueChange: (value: any) => setRate(value ?? ""),
      },
      amount: { value: amount, read_only: true, disabled: true },
      labour_rate: { onValueChange: (value: any) => setLabourRate(value) },
      labour_amount: {
        value: labourAmount,
        read_only: true,
        disabled: true,
      },
      default_rate: {
        ...baseFields.default_rate,
        onValueChange: (value: any) => setDefaultRate(value),
      },
    };
  }, [
    costCardId,
    endpoints,
    pcs,
    rate,
    usesDefaultRate,
    labourRate,
    pc,
    mmSize,
    sieveSize,
    sieveChoices,
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
      api_url: apiUrl(ApiEndpoints.finish_type),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? "";
      },
    },
    rate: {},
    active: { boxed: true, default: true, hidden: true },
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
    mm_size: { ...STONE_MM_SIZE_FIELD },
    sieve_size: { ...STONE_SIEVE_SIZE_FIELD },
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
      api_url: apiUrl(ApiEndpoints.diamond_shape_list),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    mm_size: {
      api_url: apiUrl(ApiEndpoints.diamond_size_list),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    stone: {
      api_url: apiUrl(ApiEndpoints.diamond_stone_list),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    color: {
      api_url: apiUrl(ApiEndpoints.diamond_color_list),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    cut: {
      api_url: apiUrl(ApiEndpoints.diamond_cut_list),
      filters: { active: true },
      modelRenderer: (arg: any) => {
        const instance = arg?.instance ?? arg;
        return instance?.name ?? (instance?.name ? `#${instance.name}` : "");
      },
    },
    quality: {
      api_url: apiUrl(ApiEndpoints.diamond_quality_list),
      filters: { active: true },
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
