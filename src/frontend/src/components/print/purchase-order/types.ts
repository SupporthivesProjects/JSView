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

export interface PurchaseOrderPrintPayload {
  type: string;
  po: PurchaseOrderPrintHeader;
  lines?: PurchaseOrderPrintLine[];
  totals?: PurchaseOrderPrintTotals;
  costcards?: any[];
}
