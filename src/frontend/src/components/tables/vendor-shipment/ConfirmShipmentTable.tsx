import { t } from "@lingui/core/macro";
import { Button, Checkbox } from "@mantine/core";
import { Fragment, useEffect, useMemo, useState } from "react";

import "./confirmShipment.css";

type Value = number | string | null | undefined;

/** A shipment line as returned by the confirm data endpoint */
export interface ConfirmShipmentLine {
  tableid: number;
  vendorshipid: number;
  pono: string | null;
  styleno: string | null;
  pcs: Value;
  triounce: Value;
  metalwt: Value;
  diawt: Value;
  colwt: Value;
  labour: Value;
  finding: Value;
  confrm: boolean | null;
  purchaseno: string | null;
  coststyle: string | null;
  qty: Value;
  touncep: Value;
  metalgms: Value;
  diacts: Value;
  colcts: Value;
  costlabour: Value;
  costfinding: Value;
}

/**
 * Two row columns: the shipped figure sits in the upper cell, the matching
 * cost card figure in the lower cell
 */
type FigureKey =
  | "triounce"
  | "touncep"
  | "metalwt"
  | "metalgms"
  | "diawt"
  | "diacts"
  | "colwt"
  | "colcts"
  | "labour"
  | "costlabour"
  | "finding"
  | "costfinding";

function splitColumns(): {
  title: string;
  upper: FigureKey;
  lower: FigureKey;
}[] {
  return [
    { title: t`Tri Ounce`, upper: "triounce", lower: "touncep" },
    { title: t`Metal Wt`, upper: "metalwt", lower: "metalgms" },
    { title: t`Dia. Wt`, upper: "diawt", lower: "diacts" },
    { title: t`Col. Wt`, upper: "colwt", lower: "colcts" },
    { title: t`Labour`, upper: "labour", lower: "costlabour" },
    { title: t`Finding`, upper: "finding", lower: "costfinding" },
  ];
}

function isBlank(value: Value) {
  return value === null || value === undefined || value === "";
}

/** Lower (cost card) figures are shown as they come, e.g. 11.8 */
function plain(value: Value) {
  if (isBlank(value)) {
    return "";
  }

  const numeric = Number(value);

  return Number.isNaN(numeric) ? String(value) : String(numeric);
}

/** Upper (shipped) figures are left empty until a value is entered */
function shipped(value: Value) {
  return Number(value) ? plain(value) : "";
}

/** A shipped figure is flagged when it is entered and differs from the cost */
function isMismatch(upper: Value, lower: Value) {
  return !!Number(upper) && Number(upper) !== Number(lower ?? 0);
}

export default function ConfirmShipmentTable({
  lines,
}: Readonly<{ lines: ConfirmShipmentLine[] }>) {
  const columns = useMemo(() => splitColumns(), []);

  // Line ids ticked for confirmation, seeded from the saved state
  const [checked, setChecked] = useState<Set<number>>(new Set());

  useEffect(() => {
    setChecked(
      new Set(lines.filter((line) => !!line.confrm).map((l) => l.tableid)),
    );
  }, [lines]);

  const allChecked = lines.length > 0 && checked.size === lines.length;
  const someChecked = checked.size > 0 && !allChecked;

  const toggleAll = () => {
    setChecked(
      allChecked ? new Set() : new Set(lines.map((line) => line.tableid)),
    );
  };

  const toggleLine = (id: number) => {
    setChecked((previous) => {
      const next = new Set(previous);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  const handleUpdate = () => {
    // TODO: send the confirmation for the checked lines
  };

  return (
    <div className="cs-sheet">
      <table className="cs-table">
        <thead>
          <tr>
            <th>#</th>
            <th>{t`P.O. No`}</th>
            <th className="cs-style">{t`Style No.`}</th>
            <th>{t`Pcs`}</th>
            {columns.map((column) => (
              <th key={column.upper}>{column.title}</th>
            ))}
            <th className="cs-check">
              <Checkbox
                aria-label={t`Select all`}
                checked={allChecked}
                indeterminate={someChecked}
                onChange={toggleAll}
                style={{ display: "inline-block" }}
              />
            </th>
          </tr>
        </thead>
        <tbody>
          {lines.map((line, index) => (
            <Fragment key={line.tableid}>
              <tr>
                <td rowSpan={2}>{index + 1}</td>
                <td rowSpan={2}>{line.pono ?? ""}</td>
                <td rowSpan={2} className="cs-style">
                  {line.styleno ?? ""}
                </td>
                <td rowSpan={2}>{plain(line.pcs)}</td>
                {columns.map((column) => (
                  <td
                    key={column.upper}
                    className={
                      isMismatch(line[column.upper], line[column.lower])
                        ? "cs-upper cs-mismatch"
                        : "cs-upper"
                    }
                  >
                    {shipped(line[column.upper])}
                  </td>
                ))}
                <td rowSpan={2} className="cs-check">
                  <Checkbox
                    aria-label={t`Confirm line`}
                    checked={checked.has(line.tableid)}
                    onChange={() => toggleLine(line.tableid)}
                    style={{ display: "inline-block" }}
                  />
                </td>
              </tr>
              <tr>
                {columns.map((column) => (
                  <td key={column.lower} className="cs-lower">
                    {plain(line[column.lower])}
                  </td>
                ))}
              </tr>
            </Fragment>
          ))}
        </tbody>
        <tfoot>
          <tr>
            <td colSpan={5 + columns.length}>
              <Button onClick={handleUpdate} disabled={checked.size === 0}>
                {t`Update Confirmation`}
              </Button>
            </td>
          </tr>
        </tfoot>
      </table>
    </div>
  );
}
