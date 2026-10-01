import { t } from "@lingui/core/macro";

import { generateUrl } from "@helpers/urls";
import { formatPrintDate, text } from "../../print/purchase-order/format";
import "./stoneRequisition.css";
import type { StoneDetailPo } from "./types";

/** Columns between the Qty and Pcs columns, spanned by the second "Total :" */
const STONE_COLUMN_SPAN = 9;

function decimal(value: number | string | null | undefined, places = 2) {
  if (value === null || value === undefined || value === "") {
    return "";
  }

  const numeric = Number(value);

  return Number.isNaN(numeric) ? String(value) : numeric.toFixed(places);
}

function PoHeader({ po }: Readonly<{ po: StoneDetailPo }>) {
  return (
    <table className="sr-info">
      <tbody>
        <tr>
          <td className="sr-label">{t`PO NO`}</td>
          <td>{text(po.po_no)}</td>
          <td className="sr-label">{t`Customer`}</td>
          <td>{text(po.customer)}</td>
          <td className="sr-label">{t`Vendor`}</td>
          <td>{text(po.vendor)}</td>
          <td className="sr-label">{t`A/c Exe`}</td>
          <td>{text(po.ac_exe)}</td>
        </tr>
        <tr>
          <td className="sr-label">{t`PO Date`}</td>
          <td>{formatPrintDate(po.po_date)}</td>
          <td className="sr-label">{t`Stone Ship Date`}</td>
          <td>{formatPrintDate(po.stone_ship_date)}</td>
          <td className="sr-label">{t`Prepared`}</td>
          <td>{text(po.prepared)}</td>
          <td className="sr-label">{t`Category`}</td>
          <td>{text(po.category)}</td>
        </tr>
        <tr>
          <td className="sr-label">{t`Due Date`}</td>
          <td>{formatPrintDate(po.due_date)}</td>
          <td className="sr-label">{t`Remarks`}</td>
          <td className="sr-remarks" colSpan={5}>
            {text(po.remarks)}
          </td>
        </tr>
      </tbody>
    </table>
  );
}

function PoBlock({
  po,
  showRate,
}: Readonly<{ po: StoneDetailPo; showRate: boolean }>) {
  const totals = po.totals;

  return (
    <div className="sr-po-block">
      <PoHeader po={po} />
      <table className="sr-table">
        <thead>
          <tr>
            <th>{t`Sr. No`}</th>
            <th>{t`Style NO.`}</th>
            <th>{t`Category`}</th>
            <th>{t`Qty`}</th>
            <th>{t`Setting`}</th>
            <th>{t`Stone`}</th>
            <th>{t`Shape`}</th>
            <th>{t`Cut`}</th>
            <th>{t`Colour`}</th>
            <th>{t`Quality`}</th>
            <th>{t`MM Size`}</th>
            <th>{t`Sieve Size`}</th>
            <th>{t`Ptr`}</th>
            <th>{t`Pcs`}</th>
            <th>{t`cts`}</th>
            <th>{t`Total Pcs`}</th>
            <th>{t`Total cts`}</th>
            {showRate && <th>{t`Rate`}</th>}
            {showRate && <th>{t`Amount`}</th>}
          </tr>
        </thead>
        <tbody>
          {po.styles.map((style) =>
            style.lines.map((line, index) => (
              <tr key={`${style.sr_no}-${index}`}>
                {index === 0 && (
                  <>
                    <td rowSpan={style.lines.length}>{text(style.sr_no)}</td>
                    <td className="sr-style" rowSpan={style.lines.length}>
                      {text(style.style_no)}
                      {style.front_view && (
                        <img
                          src={generateUrl(style.front_view)}
                          alt={text(style.style_no)}
                        />
                      )}
                    </td>
                    <td rowSpan={style.lines.length}>{text(style.category)}</td>
                    <td rowSpan={style.lines.length}>{text(style.po_qty)}</td>
                  </>
                )}
                <td>{text(line.setting)}</td>
                <td>{text(line.stone)}</td>
                <td>{text(line.shape)}</td>
                <td>{text(line.cut)}</td>
                <td>{text(line.colour)}</td>
                <td>{text(line.quality)}</td>
                <td>{text(line.mm_size)}</td>
                <td>{text(line.sieve_size)}</td>
                <td>{text(line.pointer)}</td>
                <td>{text(line.pcs)}</td>
                <td>{text(line.cts)}</td>
                <td>{text(line.total_pcs)}</td>
                <td>{text(line.total_cts)}</td>
                {showRate && <td>{decimal(line.rate)}</td>}
                {showRate && <td>{decimal(line.amount)}</td>}
              </tr>
            )),
          )}
        </tbody>
        <tfoot>
          <tr>
            <th colSpan={3}>{t`Total :`}</th>
            <th>{text(totals.qty)}</th>
            <th colSpan={STONE_COLUMN_SPAN}>{t`Total :`}</th>
            <th>{text(totals.pcs)}</th>
            <th>{decimal(totals.cts)}</th>
            <th>{text(totals.total_pcs)}</th>
            <th>{decimal(totals.total_cts)}</th>
            {showRate && <th />}
            {showRate && <th />}
          </tr>
        </tfoot>
      </table>
    </div>
  );
}

/**
 * Details view of the stone order list: one ruled block per purchase order,
 * with the stone lines of each style merged under its style row.
 */
export default function StoneRequisitionDetailsTable({
  data,
  showRate,
}: Readonly<{ data: StoneDetailPo[]; showRate: boolean }>) {
  return (
    <div className="sr-sheet">
      {data.map((po) => (
        <PoBlock key={po.po_id} po={po} showRate={showRate} />
      ))}
    </div>
  );
}
