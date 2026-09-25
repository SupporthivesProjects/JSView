import type { PurchaseOrderPrintPayload } from './types';

/**
 * Temporary hand-off store for PO print payloads.
 *
 * The print view is opened in a new browser tab, which is a fresh JS context,
 * so the fetched payload is parked in localStorage under a one-shot key and
 * read (and removed) by the print page. The print page falls back to fetching
 * the payload itself if the key has already expired or was never written.
 */

const STORAGE_PREFIX = 'po-print-payload:';

/** Stale payloads are dropped after this long */
const PAYLOAD_TTL = 5 * 60 * 1000;

interface StoredPayload {
  created: number;
  payload: PurchaseOrderPrintPayload;
}

function newKey(): string {
  if (typeof crypto?.randomUUID === 'function') {
    return crypto.randomUUID();
  }

  return `${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

/** Drop any payloads left behind by tabs which were never opened */
function pruneExpired() {
  const now = Date.now();

  for (let idx = localStorage.length - 1; idx >= 0; idx--) {
    const key = localStorage.key(idx);

    if (!key?.startsWith(STORAGE_PREFIX)) {
      continue;
    }

    try {
      const stored: StoredPayload = JSON.parse(localStorage.getItem(key) ?? '');

      if (now - stored.created < PAYLOAD_TTL) {
        continue;
      }
    } catch (_error) {
      // Unreadable entry - remove it too
    }

    localStorage.removeItem(key);
  }
}

/**
 * Store a print payload, returning the key required to read it back.
 * Returns null if the payload could not be stored (e.g. storage disabled).
 */
export function stashPrintPayload(
  payload: PurchaseOrderPrintPayload
): string | null {
  const key = newKey();

  try {
    pruneExpired();

    localStorage.setItem(
      `${STORAGE_PREFIX}${key}`,
      JSON.stringify({ created: Date.now(), payload })
    );
  } catch (_error) {
    return null;
  }

  return key;
}

/**
 * Read back (and consume) a stored print payload.
 */
export function takePrintPayload(
  key: string | null
): PurchaseOrderPrintPayload | null {
  if (!key) {
    return null;
  }

  const storageKey = `${STORAGE_PREFIX}${key}`;

  try {
    const raw = localStorage.getItem(storageKey);

    if (!raw) {
      return null;
    }

    localStorage.removeItem(storageKey);

    const stored: StoredPayload = JSON.parse(raw);

    if (Date.now() - stored.created > PAYLOAD_TTL) {
      return null;
    }

    return stored.payload;
  } catch (_error) {
    return null;
  }
}
