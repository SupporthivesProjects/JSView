/**
 * Shape of the payload returned by
 * `GET /api/purchase-order/po/<pk>/print/?type=<type>`.
 *
 * Only the `vendor` / `self` ("simple") formats are typed here; the cost card
 * formats carry a `costcards` block instead of `lines` + `totals`.
 */

export interface PurchaseOrderPrintHeader {
  pono: string;
  podate: string | null;
  ddate: string | null;
  pocategory: string;
  customer: string;
  vendor: string;
  vendor_address: string;
  prepby: string;
  acexe: string;
  terms: string;
  stamp: string;
  stamp_image: string | null;
  rem: string;
}

export interface PurchaseOrderPrintLine {
  sr: number;
  style_no: string;
  v_style_no: string;
  qty: number;
  /** Comma separated list of sizes, e.g. "6,7,8" */
  size: string;
  /** Comma separated list of pieces per size, e.g. "11,11,7" */
  size_pcs: string;
  metal_color_kt: string;
}

export interface PurchaseOrderPrintTotals {
  total_qty: number;
  metal_value: string;
  labour_value: string;
  /** Only present for the `self` format */
  order_value?: string;
}

/**
 * A single studding (diamond / colour stone) line of a cost card.
 * The amount / labour fields are null on the `vendor_costcard` format, where
 * the backend strips every value the vendor must not see.
 */
export interface PurchaseOrderCostCardStoneLine {
  etype: string;
  shape: string;
  cut: string;
  mm_size: string;
  sieve_size: string;
  stone: string;
  colour: string;
  pointer: number | string | null;
  pcs: number | string | null;
  cts: number | string | null;
  pc: string;
  rate: number | string | null;
  amount: number | string | null;
  setting: string;
  labour_rate: number | string | null;
  labour_amount: number | string | null;
}

export interface PurchaseOrderCostCardSummary {
  metal: number | string | null;
  /** Only present on `self_costcard` */
  studding?: number | string | null;
  labour: number | string | null;
  none: number | string | null;
  fob?: number | string | null;
  markup_pct?: number | string | null;
  with_markup?: number | string | null;
  duty_pct?: number | string | null;
  with_duty?: number | string | null;
  margin_pct?: number | string | null;
  final_price?: number | string | null;
}

export interface PurchaseOrderCostCard {
  cc_no: string;
  style_no: string;
  v_style_no: string;
  customer: string;
  vendor: string;
  vendor_address: string;
  category: string;
  sub_category: string;
  date: string | null;
  modified_by: string;
  images: {
    front: string | null;
    side: string | null;
    back: string | null;
  };
  metal: {
    type: string;
    troy_oz: number | string | null;
    kt: number | string | null;
    net_wt: number | string | null;
    loss_pct: number | string | null;
    metal_amount: number | string | null;
  };
  stone_lines: PurchaseOrderCostCardStoneLine[];
  stone_totals: {
    total_pcs: number | string | null;
    total_cts: number | string | null;
    total_amount: number | string | null;
  };
  labour: {
    finish: number | string | null;
    diamond: number | string | null;
    colorstone: number | string | null;
  };
  summary: PurchaseOrderCostCardSummary;
  design_instruction: string;
}

export interface PurchaseOrderPrintPayload {
  type: string;
  po: PurchaseOrderPrintHeader;
  lines?: PurchaseOrderPrintLine[];
  totals?: PurchaseOrderPrintTotals;
  costcards?: PurchaseOrderCostCard[];
}
