import { t } from "@lingui/core/macro";

import { text } from "../../print/purchase-order/format";
import "./metalRequisition.css";
import type { MetalPo, MetalTotals } from "./types";

type Value = number | string | null | undefined;

/** Line figures are shown as they come, e.g. 19.7 */
function plain(value: Value) {
  if (value === null || value === undefined || value === "") {
    return "";
  }

  const numeric = Number(value);

  return Number.isNaN(numeric) ? String(value) : String(numeric);
}

/** Totals are shown to three decimals, e.g. 82.200 */
function weight(value: Value) {
  if (value === null || value === undefined || value === "") {
    return "";
  }

  const numeric = Number(value);

  return Number.isNaN(numeric) ? String(value) : numeric.toFixed(3);
}

function PoBlock({
  po,
  poLabel,
}: Readonly<{ po: MetalPo; poLabel?: string }>) {
  const totals = po.totals;

  return (
    <div className="mr-po-block">
      <div className="mr-info">
        <div>
          <span className="mr-label">{t`PO NO:`}</span>
          {text(po.po_no ?? poLabel)}
        </div>
        <div>
          <span className="mr-label">{t`Vendor:`}</span>
          {text(po.vendor)}
        </div>
      </div>
      <table className="mr-table">
        <thead>
          <tr>
            <th>{t`Sr. No`}</th>
            <th className="mr-style">{t`Style No.`}</th>
            <th>{t`Qty`}</th>
            <th>{t`Net. Weight`}</th>
            <th>{t`KT`}</th>
            <th>{t`Gold(24KT)`}</th>
            <th>{t`Silver`}</th>
            <th>{t`Platinum`}</th>
          </tr>
        </thead>
        <tbody>
          {po.lines.length ? (
            po.lines.map((line) => (
              <tr key={line.sr_no}>
                <td>{text(line.sr_no)}</td>
                <td className="mr-style">{text(line.style_no)}</td>
                <td>{text(line.qty)}</td>
                <td>{plain(line.total_weight)}</td>
                <td>{plain(line.kt)}</td>
                <td>{plain(line.gold)}</td>
                <td>{plain(line.silver)}</td>
                <td>{plain(line.platinum)}</td>
              </tr>
            ))
          ) : (
            // A P.O. without lines still shows one empty ruled row
            <tr>
              <td>1</td>
              <td className="mr-style" />
              <td />
              <td />
              <td />
              <td />
              <td />
              <td />
            </tr>
          )}
        </tbody>
        <tfoot>
          <tr>
            <th className="mr-total-label" colSpan={2}>{t`Total :`}</th>
            <td>{text(totals.qty)}</td>
            <td>{po.lines.length ? weight(totals.total_weight) : ""}</td>
            <td />
            <td>{weight(totals.gold)}</td>
            <td>{weight(totals.silver)}</td>
            <td>{weight(totals.platinum)}</td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

function GrandTotal({ totals }: Readonly<{ totals: MetalTotals }>) {
  return (
    <table className="mr-table mr-grand">
      <tbody>
        <tr>
          <th className="mr-grand-label" rowSpan={2}>{t`Total`}</th>
          <th>{t`Qty`}</th>
          <th>{t`Net. Weight`}</th>
          <th>{t`Gold(24KT)`}</th>
          <th>{t`Silver`}</th>
          <th>{t`Platinum`}</th>
        </tr>
        <tr>
          <td>{text(totals.qty)}</td>
          <td>{weight(totals.total_weight)}</td>
          <td>{weight(totals.gold)}</td>
          <td>{weight(totals.silver)}</td>
          <td>{weight(totals.platinum)}</td>
        </tr>
      </tbody>
    </table>
  );
}

/**
 * Metal order requisition sheet: one ruled block per purchase order,
 * followed by the grand total across every selected P.O.
 *
 * `poLabels` maps a P.O. id to its number, used as the header of a P.O.
 * the API returns without lines (and so without a number).
 */
export default function MetalRequisitionTable({
  data,
  grandTotals,
  poLabels = {},
}: Readonly<{
  data: MetalPo[];
  grandTotals: MetalTotals;
  poLabels?: Record<string, string>;
}>) {
  return (
    <div className="mr-sheet">
      {data.map((po) => (
        <PoBlock
          key={po.po_id}
          po={po}
          poLabel={poLabels[String(po.po_id)]}
        />
      ))}
      <GrandTotal totals={grandTotals} />
    </div>
  );
}
