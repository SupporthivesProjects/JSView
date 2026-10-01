import { t } from "@lingui/core/macro";

import { text } from "../../print/purchase-order/format";
import "./stoneRequisition.css";
import type { StoneSummaryRow, StoneTotals } from "./types";

/** Columns preceding the Pcs total, spanned by the "Total" label */
const TOTAL_LABEL_SPAN = 9;

function decimal(value: number | string | null | undefined, places = 2) {
  if (value === null || value === undefined || value === "") {
    return "";
  }

  const numeric = Number(value);

  return Number.isNaN(numeric) ? String(value) : numeric.toFixed(places);
}

/**
 * Summary view of the stone order list: every stone of the selected purchase
 * orders, grouped and totalled across the orders.
 */
export default function StoneRequisitionSummaryTable({
  rows,
  totals,
  poNumbers,
}: Readonly<{
  rows: StoneSummaryRow[];
  totals: StoneTotals;
  poNumbers: string[];
}>) {
  return (
    <div className="sr-sheet">
      <table className="sr-table sr-summary">
        <thead>
          <tr>
            <th className="sr-po-list" colSpan={11}>
              {t`P.O#:`} {poNumbers.join(", ")}
            </th>
          </tr>
          <tr>
            <th>#</th>
            <th>{t`Stone`}</th>
            <th>{t`Shape`}</th>
            <th>{t`Cut`}</th>
            <th>{t`Color`}</th>
            <th>{t`Quality`}</th>
            <th>{t`MM Size`}</th>
            <th>{t`Sieve Size`}</th>
            <th>{t`Pointer`}</th>
            <th>{t`Pcs`}</th>
            <th>{t`Cts.`}</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((row) => (
            <tr key={row.sr_no}>
              <td>{row.sr_no}</td>
              <td>{text(row.stone)}</td>
              <td>{text(row.shape)}</td>
              <td>{text(row.cut)}</td>
              <td>{text(row.colour)}</td>
              <td>{text(row.quality)}</td>
              <td>{text(row.mm_size)}</td>
              <td>{text(row.sieve_size)}</td>
              <td>{decimal(row.pointer, 4)}</td>
              <td>{text(row.total_pcs)}</td>
              <td>{text(row.total_cts)}</td>
            </tr>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <th className="sr-total-label" colSpan={TOTAL_LABEL_SPAN}>
              {t`Total`}
            </th>
            <th>{text(totals.pcs)}</th>
            <th>{decimal(totals.cts)}</th>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
