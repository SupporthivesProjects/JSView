/** Response types for the stone requisition report (`requisition/stone/`) */

export type StoneViewType = "details" | "summary";
export type StoneType = "DIAMOND" | "COLOURSTONE";

/** A single stone line of a style, within a P.O. block */
export interface StoneDetailLine {
  setting: string | null;
  stone: string | null;
  shape: string | null;
  cut: string | null;
  colour: string | null;
  quality: string | null;
  mm_size: string | null;
  sieve_size: string | null;
  pointer: number | string | null;
  pcs: number | null;
  cts: number | string | null;
  total_pcs: number | null;
  total_cts: number | string | null;
  // Only present when the report is run with Show Rate = Yes
  rate?: number | string | null;
  amount?: number | string | null;
}

/** One style of a P.O., with the stone lines it is made up of */
export interface StoneDetailStyle {
  sr_no: number;
  style_no: string | null;
  front_view: string | null;
  category: string | null;
  po_qty: number | null;
  lines: StoneDetailLine[];
}

/** Footer totals of a P.O. block */
export interface StoneDetailTotals {
  qty: number | null;
  pcs: number | null;
  cts: number | string | null;
  total_pcs: number | null;
  total_cts: number | string | null;
}

/** One P.O. block of the details view: order header plus its styles */
export interface StoneDetailPo {
  po_id: number;
  po_no: string | null;
  po_date: string | null;
  due_date: string | null;
  customer: string | null;
  stone_ship_date: string | null;
  vendor: string | null;
  prepared: string | null;
  ac_exe: string | null;
  category: string | null;
  remarks: string | null;
  styles: StoneDetailStyle[];
  totals: StoneDetailTotals;
}

/** A stone of the summary view, totalled across every selected P.O. */
export interface StoneSummaryRow {
  sr_no: number;
  stone: string | null;
  shape: string | null;
  cut: string | null;
  colour: string | null;
  quality: string | null;
  mm_size: string | null;
  sieve_size: string | null;
  pointer: number | string | null;
  total_pcs: number | null;
  total_cts: number | string | null;
}

export interface StoneTotals {
  pcs: number | null;
  cts: number | string | null;
}

export type StoneRequisitionResponse =
  | {
      view_type: "details";
      po_ids: number[];
      data: StoneDetailPo[];
    }
  | {
      view_type: "summary";
      po_ids: number[];
      data: StoneSummaryRow[];
      totals: StoneTotals;
    };

/** Response types for the metal requisition report (`requisition/metal/`) */

type MetalNumber = number | string | null;

/** A single style line of a P.O. block */
export interface MetalLine {
  sr_no: number;
  style_no: string | null;
  qty: number | null;
  // Weight of one piece
  net_weight: MetalNumber;
  // Weight of one piece x qty
  total_weight: MetalNumber;
  kt: MetalNumber;
  gold: MetalNumber;
  silver: MetalNumber;
  platinum: MetalNumber;
}

export interface MetalTotals {
  qty: number | null;
  total_weight: MetalNumber;
  gold: MetalNumber;
  silver: MetalNumber;
  platinum: MetalNumber;
}

/** One P.O. block: order header plus its style lines */
export interface MetalPo {
  po_id: number;
  po_no: string | null;
  vendor: string | null;
  lines: MetalLine[];
  totals: MetalTotals;
}

export interface MetalRequisitionResponse {
  po_ids: number[];
  data: MetalPo[];
  grand_totals: MetalTotals;
}
