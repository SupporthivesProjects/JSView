/** Shared value formatting for the printable purchase order sheets */

const MONTHS = [
  'Jan',
  'Feb',
  'Mar',
  'Apr',
  'May',
  'Jun',
  'Jul',
  'Aug',
  'Sep',
  'Oct',
  'Nov',
  'Dec'
];

/**
 * Format an ISO date (YYYY-MM-DD) as e.g. "13 Aug 2026".
 * Parsed from the string itself, so the printed date never shifts with the
 * browser timezone.
 */
export function formatPrintDate(value: string | null | undefined): string {
  if (!value) {
    return '';
  }

  const [year, month, day] = value.slice(0, 10).split('-');
  const monthName = MONTHS[Number(month) - 1];

  if (!monthName || !day || !year) {
    return value;
  }

  return `${Number(day)} ${monthName} ${year}`;
}

/** Split a comma separated field (e.g. "6,7,8") into its parts */
export function splitList(value: string | null | undefined): string[] {
  if (!value) {
    return [];
  }

  return value
    .split(',')
    .map((entry) => entry.trim())
    .filter((entry) => entry.length > 0);
}

/**
 * Print a raw value, leaving empty cells empty.
 * Counts, weights and percentages are printed exactly as the API returns them.
 */
export function text(value: unknown): string {
  if (value === null || value === undefined) {
    return '';
  }

  return String(value);
}

/**
 * Print a monetary value with two decimals.
 * Values which are hidden by the vendor formats arrive as null and stay blank.
 */
export function money(value: number | string | null | undefined): string {
  if (value === null || value === undefined || value === '') {
    return '';
  }

  const numeric = Number(value);

  return Number.isNaN(numeric) ? String(value) : numeric.toFixed(2);
}
