# JSIView × InvenTree — PO Print / Report API

> **Purpose:** Reference for the single read-only endpoint that feeds the four print buttons on the
> Purchase Order detail page.
> Written 2026-09-24 against `feature/purchase-order` (HEAD `37664539a`).
> Every field name, type and derived pricing figure below was verified against real output from
> `purchase_order/tests.py::POPrintViewTests`. The `prepby` name, `stamp_image` and `images.*` values
> are shown populated for illustration — the test fixture leaves those empty.
>
> **Golden rules:** read-only endpoint · images are returned as URLs (never base64) · the vendor
> formats must never leak internal amounts.

---

## ⚡ Quick Reference

| Item | Value |
|---|---|
| Endpoint | `GET /api/purchase-order/po/<poid>/print/?type=<type>` |
| Valid `type` values | `vendor` · `self` · `vendor_costcard` · `self_costcard` |
| Auth | Same as every other `/api/purchase-order/` endpoint — InvenTree login; send `Authorization: Token {{token}}` |
| Writes | None. Strictly read-only. |
| Images | Absolute URLs (front/side/back cost-card images, stamp image) |
| View | `purchase_order/views.py::POPrintView` |
| Route name | `api-po-print` |
| URL pattern | `purchase_order/urls.py` → `po/<int:pk>/print/` |
| Helpers | `build_po_header` · `build_simple_lines` · `build_costcards` · `build_costcard_block` |
| Legacy equivalent | Go `PurchaseOrderRoutes` print endpoints (4 formats: Vendor, Self, Vendor Costcard, Self Costcard) |

### The four formats at a glance

| `type` | Sheet | Order value | Cost breakdown | Amounts |
|---|---|---|---|---|
| `vendor` | Simple PO | **hidden** | — | — |
| `self` | Simple PO | **visible** | — | — |
| `vendor_costcard` | Cost breakdown | — | yes | **masked** |
| `self_costcard` | Cost breakdown | — | yes | **visible** |

---

## 1. Request

```
GET /api/purchase-order/po/<poid>/print/?type=<type>
```

| Parameter | In | Type | Required | Notes |
|---|---|---|---|---|
| `poid` | path | int | yes | `PurchaseOrder` primary key |
| `type` | query | string | yes | One of `vendor`, `self`, `vendor_costcard`, `self_costcard` |

### Errors

| Status | When | Body |
|---|---|---|
| `400 Bad Request` | `type` missing or not one of the four valid values | `{"error": "Invalid type. Must be one of: vendor, self, vendor_costcard, self_costcard"}` |
| `404 Not Found` | no `PurchaseOrder` with that `poid` | standard DRF not-found |

Both `400` cases are identical — a missing `type` is **not** treated as a default. There is no
"default format"; the caller must always be explicit.

---

## 2. Shared `po` header object

Every one of the four formats returns the same `po` block, built by `build_po_header()`.

| Field | Type | Source |
|---|---|---|
| `pono` | string | `PurchaseOrder.pono` (auto-generated `{ccode} {year}-{npono:04d} {P\|S}`) |
| `podate` | date | `PurchaseOrder.podate` |
| `ddate` | date \| null | `PurchaseOrder.ddate` |
| `pocategory` | string | `PurchaseOrder.pocategory` (`""` when unset) |
| `customer` | string | `customerid.code`, falling back to `customerid.name` |
| `vendor` | string | `vendorid.name` |
| `vendor_address` | string | `vendorid` primary address string (`""` when the vendor has no address) |
| `prepby` | string | `prepby` full name, falling back to username |
| `acexe` | string | `acexeid.name` |
| `terms` | string | `termsid.name` |
| `stamp` | string | `stampid.name` |
| `stamp_image` | url \| null | `stampid.image` absolute URL |
| `rem` | string | `PurchaseOrder.rem` |

> **Note on `customer`:** it is the short ledger **code** (e.g. `ASC`) because that is what the client
> prints on the sheet — the same value used to build the `pono` prefix. `vendor` is the full name,
> since vendor ledger rows have no code. This mirrors `purchase_order/utils.py::generate_po_number`.

---

## 3. Format `type=vendor` and `type=self`

Both return `po` + `lines` + `totals`. The **only** difference between them is that `self` adds
`totals.order_value`.

### `lines[]`

| Field | Type | Source |
|---|---|---|
| `sr` | int | 1-based row number, in PO line order |
| `style_no` | string | `PurchaseOrderLine.styleno` |
| `v_style_no` | string | `PurchaseOrderLine.vstyleno` |
| `qty` | int | `PurchaseOrderLine.qty` |
| `size` | string | `PurchaseOrderLine.size` (CSV, e.g. `N A`) |
| `size_pcs` | string | `PurchaseOrderLine.spcs` (CSV pieces per size, e.g. `2`) |
| `metal_color_kt` | string | frozen snapshot `metal_purity.name`; falls back to the live `CostCard.metal_purity.name` |

### `totals`

| Field | Type | Source | `vendor` | `self` |
|---|---|---|---|---|
| `total_qty` | int | Σ `line.qty` | shown | shown |
| `metal_value` | decimal(2) | Σ snapshot `metal_amount` | shown | shown |
| `labour_value` | decimal(2) | Σ snapshot `labour_amount` | shown | shown |
| `order_value` | decimal(2) | Σ snapshot `final_amount` | **omitted** | shown |

When a line has no frozen snapshot (e.g. a Purchase **Request**), the live `CostCard` of that line is
used for the three sums instead — the field names are shared by both models.

### Sample — `type=vendor`

```json
{
  "type": "vendor",
  "po": {
    "pono": "ASC 2025-0570 P",
    "podate": "2025-09-16",
    "ddate": "2025-09-27",
    "pocategory": "Master Sample",
    "customer": "ASC",
    "vendor": "Omnia Jewels LLP",
    "vendor_address": "",
    "prepby": "Shekhar",
    "acexe": "SHEKHAR",
    "terms": "Net 30",
    "stamp": "AA LOGO, KT, COO - LGD",
    "stamp_image": "http://server/media/stamps/1/image.jpg",
    "rem": "DIRECT SHIPMENT TO CANADA"
  },
  "lines": [
    {
      "sr": 1,
      "style_no": "AAE075A0664",
      "v_style_no": "OE1801075",
      "qty": 2,
      "size": "N A",
      "size_pcs": "2",
      "metal_color_kt": "STERLING SILVER"
    }
  ],
  "totals": {
    "total_qty": 2,
    "metal_value": 0.0,
    "labour_value": 4.5
  }
}
```

### Sample — `type=self`

Identical, except `totals` gains the order value:

```json
"totals": {
  "total_qty": 2,
  "metal_value": 0.0,
  "labour_value": 4.5,
  "order_value": 72.95
}
```

---

## 4. Format `type=vendor_costcard` and `type=self_costcard`

Both return `po` + `costcards[]`. `vendor_costcard` **masks** amounts; `self_costcard` shows
everything. One entry is emitted per distinct cost card referenced by the PO's lines, in PO line
order; frozen snapshots whose originating cost card has been deleted are appended after those.

### `costcards[]` — identity & classification

| Field | Type | Source |
|---|---|---|
| `cc_no` | string | snapshot `costcardno` (e.g. `00001`) |
| `style_no` | string | snapshot `our_style_no` |
| `v_style_no` | string | snapshot `vendor_style_no` |
| `customer` | string | snapshot customer `code`, falling back to `name` |
| `vendor` | string | snapshot vendor `name` |
| `vendor_address` | string | snapshot vendor primary address (`""` when none) |
| `category` | string | snapshot `category.name` |
| `sub_category` | string | snapshot `sub_category.name` |
| `date` | date | `PurchaseOrder.podate` |
| `modified_by` | string | latest `revision.CostCardVersion.created_by`; falls back to the PO's `prepby` |
| `design_instruction` | string | linked live `CostCard.design_note` (`""` when the card was deleted) |

### `costcards[].images`

| Field | Type | Source |
|---|---|---|
| `front` | url \| null | `CostCard.front_view` absolute URL |
| `side` | url \| null | `CostCard.side_view` absolute URL |
| `back` | url \| null | `CostCard.back_view` absolute URL |

All three are `null` when the originating `CostCard` has been deleted (the snapshot itself does not
store images). Images are always URLs — never base64.

### `costcards[].metal`

| Field | Type | Source |
|---|---|---|
| `type` | string | snapshot `metal_purity.name` (e.g. `STERLING SILVER`) |
| `troy_oz` | decimal | snapshot `troy_ounce_price` |
| `kt` | int \| string | snapshot `karat`, coerced to a number when numeric |
| `net_wt` | decimal | snapshot `net_weight` |
| `loss_pct` | decimal | snapshot `metal_loss_pct` |
| `metal_amount` | decimal(2) | snapshot `metal_amount` |

> `kt` is coerced because `POCostCard.karat` is a free-text field (`"24"`, `"18KT"`), while
> `CostCard.karat` is an integer. Numeric text is returned as a number; anything else passes through
> unchanged.

### `costcards[].stone_lines[]`

Diamond and colour-stone rows, from the frozen `POCostCardLine` rows (`etype` `DIAMOND` /
`COLOURSTONE`). Finish rows are **not** listed here — they feed `labour.finish` only.

| Field | Type | Notes |
|---|---|---|
| `etype` | string | `DIAMOND` or `COLOURSTONE` |
| `shape` | string | |
| `cut` | string | |
| `mm_size` | string | |
| `sieve_size` | string | |
| `stone` | string | |
| `colour` | string | |
| `pointer` | decimal \| null | |
| `pcs` | int | |
| `cts` | decimal | |
| `pc` | string | `P` = per piece, `C` = per carat |
| `rate` | decimal | **always visible, even on `vendor_costcard`** |
| `amount` | decimal \| null | `null` on `vendor_costcard` |
| `setting` | string | |
| `labour_rate` | decimal \| null | `null` on `vendor_costcard` |
| `labour_amount` | decimal \| null | `null` on `vendor_costcard` |

### `costcards[].stone_totals`

| Field | Type | Source | `vendor_costcard` | `self_costcard` |
|---|---|---|---|---|
| `total_pcs` | int | snapshot `stone_pcs` | shown | shown |
| `total_cts` | decimal | snapshot `stone_cts` | shown | shown |
| `total_amount` | decimal \| null | snapshot `stone_amount` | `null` | shown |

### `costcards[].labour`

Always visible on **both** cost-card formats.

| Field | Type | Source |
|---|---|---|
| `finish` | decimal(2) | Σ `amount` over `FINISHTYPE` snapshot lines |
| `diamond` | decimal(2) | Σ `labour_amount` over `DIAMOND` snapshot lines |
| `colorstone` | decimal(2) | Σ `labour_amount` over `COLOURSTONE` snapshot lines |

### `costcards[].summary`

| Field | `vendor_costcard` | `self_costcard` | Source / formula |
|---|---|---|---|
| `metal` | shown | shown | snapshot `metal_amount` |
| `studding` | **omitted** | shown | snapshot `stone_amount` |
| `labour` | shown | shown | snapshot `labour_amount`, falling back to `finish + diamond + colorstone` |
| `none` | shown | shown | always `0.00` — no source field on `POCostCard` |
| `fob` | **omitted** | shown | snapshot `fob`, falling back to `metal + studding + labour + none` |
| `markup_pct` | **omitted** | shown | snapshot `vendor_markup_pct` |
| `with_markup` | **omitted** | shown | `after_markup` when `markup_pct` is non-zero, otherwise `0.00` |
| `duty_pct` | **omitted** | shown | snapshot `duty_pct` |
| `with_duty` | **omitted** | shown | `after_markup × (1 + duty_pct/100)` |
| `margin_pct` | **omitted** | shown | snapshot `margin_pct` |
| `final_price` | **omitted** | shown | `after_markup × (1 + duty_pct/100) × (1 + margin_pct/100)` |

where `after_markup = fob × (1 + markup_pct/100)` when `markup_pct` is non-zero, otherwise `fob`.

> These are the exact formulas implemented in `build_costcard_block()`. They were chosen to
> reproduce the client's legacy sheet, where `fob = 38.70`, `duty_pct = 30`, `margin_pct = 45`
> yields `with_duty = 50.31` and `final_price = 72.95`. Change them here **and** in the view together.

### Sample — `type=self_costcard`

```json
{
  "type": "self_costcard",
  "po": { "...": "same po header as above" },
  "costcards": [
    {
      "cc_no": "00001",
      "style_no": "AAE075A0664",
      "v_style_no": "OE1801075",
      "customer": "ASC",
      "vendor": "Omnia Jewels LLP",
      "vendor_address": "",
      "category": "EARRING",
      "sub_category": "STUDS",
      "date": "2025-09-16",
      "modified_by": "Shekhar",
      "images": {
        "front": "http://server/media/cards/costs/1/front/img.jpg",
        "side": "http://server/media/cards/costs/1/side/img.jpg",
        "back": "http://server/media/cards/costs/1/back/img.jpg"
      },
      "metal": {
        "type": "STERLING SILVER",
        "troy_oz": 0.0,
        "kt": 24,
        "net_wt": 1.0,
        "loss_pct": 10.0,
        "metal_amount": 0.0
      },
      "stone_lines": [
        {
          "etype": "DIAMOND",
          "shape": "ROUND",
          "cut": "",
          "mm_size": "",
          "sieve_size": "",
          "stone": "DIAMOND",
          "colour": "",
          "pointer": 0.38,
          "pcs": 2,
          "cts": 0.76,
          "pc": "C",
          "rate": 45.0,
          "amount": 34.2,
          "setting": "",
          "labour_rate": 0.0,
          "labour_amount": 0.0
        }
      ],
      "stone_totals": {
        "total_pcs": 2,
        "total_cts": 0.76,
        "total_amount": 34.2
      },
      "labour": {
        "finish": 4.5,
        "diamond": 0.0,
        "colorstone": 0.0
      },
      "summary": {
        "metal": 0.0,
        "studding": 34.2,
        "labour": 4.5,
        "none": 0.0,
        "fob": 38.7,
        "markup_pct": 0.0,
        "with_markup": 0.0,
        "duty_pct": 30.0,
        "with_duty": 50.31,
        "margin_pct": 45.0,
        "final_price": 72.95
      },
      "design_instruction": "Set the stones tight"
    }
  ]
}
```

### Sample — `type=vendor_costcard`

Same envelope, with the masked fields. Only the differences are shown:

```json
{
  "type": "vendor_costcard",
  "po": { "...": "same po header" },
  "costcards": [
    {
      "cc_no": "00001",
      "style_no": "AAE075A0664",
      "...": "identity + metal identical to self_costcard",
      "stone_lines": [
        {
          "etype": "DIAMOND",
          "rate": 45.0,
          "amount": null,
          "labour_rate": null,
          "labour_amount": null,
          "...": "shape/cut/size/stone/pointer/pcs/cts/pc/setting unchanged"
        }
      ],
      "stone_totals": {
        "total_pcs": 2,
        "total_cts": 0.76,
        "total_amount": null
      },
      "labour": {
        "finish": 4.5,
        "diamond": 0.0,
        "colorstone": 0.0
      },
      "summary": {
        "metal": 0.0,
        "labour": 4.5,
        "none": 0.0
      }
    }
  ]
}
```

---

## 5. Amount visibility matrix

The single source of truth for what each format may expose.

| Field | `vendor` | `self` | `vendor_costcard` | `self_costcard` |
|---|:--:|:--:|:--:|:--:|
| `po` header (all fields) | ✅ | ✅ | ✅ | ✅ |
| `lines[].metal_color_kt` | ✅ | ✅ | — | — |
| `stone_lines[].rate` | — | — | ✅ | ✅ |
| `stone_lines[].amount` | — | — | ❌ `null` | ✅ |
| `stone_lines[].labour_rate` | — | — | ❌ `null` | ✅ |
| `stone_lines[].labour_amount` | — | — | ❌ `null` | ✅ |
| `stone_totals.total_amount` | — | — | ❌ `null` | ✅ |
| `labour.*` | — | — | ✅ | ✅ |
| `summary.metal` / `.labour` / `.none` | — | — | ✅ | ✅ |
| `summary.studding` | — | — | ❌ omitted | ✅ |
| `summary.fob` / `.markup_pct` / `.with_markup` | — | — | ❌ omitted | ✅ |
| `summary.duty_pct` / `.with_duty` | — | — | ❌ omitted | ✅ |
| `summary.margin_pct` / `.final_price` | — | — | ❌ omitted | ✅ |
| `totals.order_value` | ❌ omitted | ✅ | — | — |

Masked fields are `null`; hidden summary keys are **omitted from the object entirely** (the frontend
should treat "key absent" as "do not render this row"). Per-stone `rate` stays visible on the vendor
sheet — only the computed amounts are masked.

---

## 6. Where the data comes from

```
PurchaseOrder ──┬── PurchaseOrderLine ──┬── POCostCard (frozen snapshot) ── POCostCardLine
                │                       │      preferred source              (DIAMOND /
                │                       │                                     COLOURSTONE /
                │                       └── CostCard (live)                    FINISHTYPE)
                │                              fallback source
                └── Company (customer/vendor) · Stamp · ACExecutive · Terms
```

**Snapshot first, live card second.** When a line is saved on an `ORDER`-type PO with a
`costcardid`, `utils.create_po_costcard_snapshot()` freezes the cost card into
`POCostCard` / `POCostCardLine`. The print API prefers that frozen row, so a reprinted sheet shows
what the piece actually cost at order time even if the cost card is later edited or deleted.

**When there is no snapshot** — a Purchase **Request** never freezes one, nor does a line without a
`costcardid` — the API falls back to the live `CostCard` reachable from the PO line. Both paths are
normalised to the same response shape, so the frontend never needs to know which one was used.

Which fields still need the live `CostCard` even on the snapshot path:

| Field | Why |
|---|---|
| `images.front/side/back` | `POCostCard` does not store images |
| `design_instruction` | `design_note` is not part of the frozen snapshot |
| `modified_by` | comes from `revision.CostCardVersion`, not the snapshot |

If the original `CostCard` has since been deleted (`POCostCard.costcard` is `SET_NULL`), those fields
degrade to `null` / `""` while every frozen number and string survives.

---

## 7. Worked example

```bash
# Simple vendor sheet (order value hidden)
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/purchase-order/po/1/print/?type=vendor"

# Internal sheet with the full cost breakdown
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/purchase-order/po/1/print/?type=self_costcard"

# Vendor cost sheet (amounts masked)
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/purchase-order/po/1/print/?type=vendor_costcard"

# Invalid -> 400
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/purchase-order/po/1/print/?type=pdf"
# {"error": "Invalid type. Must be one of: vendor, self, vendor_costcard, self_costcard"}
```

The frontend selects a format and renders the JSON directly — see the PO detail page print buttons.

---

## 8. Implementation notes

- **Read-only.** `POPrintView` extends `RetrieveAPI` and overrides `get()` only. No model, serializer
  or existing view was modified to add this endpoint.
- **Snapshot prerequisite.** The frozen path only exists if `utils.create_po_costcard_snapshot()` runs
  when an ORDER line is saved. That function translates `CostCardStoneLineMixin.default_rate`
  (`'yes'` / `'no'`) into `POCostCardLine.default_rate` (boolean). If that coercion regresses, saving
  an ORDER line with a cost card raises `ValidationError` and this endpoint silently falls back to the
  live cost card.
- **Rounding.** Computed money values are quantised to 2 decimal places with `ROUND_HALF_UP`
  (`_money()`). Raw line values (`rate`, `cts`, `pointer`) are passed through untouched.
- **Decimals.** Values are returned as Django `Decimal`s, so DRF encodes them as JSON numbers.
- **N+1 care.** Snapshots are loaded with `select_related` / `prefetch_related` up front rather than
  per line, and each cost card is emitted only once even when several PO lines reference it.
- **`summary.none`** is currently hardcoded `0.00` because `POCostCard` has no field backing it. It
  exists so `fob = metal + studding + labour + none` stays a complete identity. If a "finding / other"
  component is ever added to the snapshot, wire it here.

### Extending

To add a fifth format:

1. Append the value to `PO_PRINT_TYPES` in `purchase_order/views.py`.
2. Add the branch in `POPrintView.get()` (or reuse `build_simple_lines` / `build_costcards` with a
   different `include_order_value` / `show_amounts` combination).
3. Add the field-visibility rules to the matrix in §5 **and** a test in `POPrintViewTests`.

---

## 9. Tests

`src/backend/InvenTree/purchase_order/tests.py::POPrintViewTests`

```bash
cd src/backend/InvenTree && ../env/bin/python manage.py test purchase_order.tests.POPrintViewTests
```

| Test | Covers |
|---|---|
| `test_missing_type_is_rejected` | `400` when `type` is absent |
| `test_invalid_type_is_rejected` | `400` when `type` is unknown |
| `test_vendor_format` | header mapping, line mapping, `order_value` absent |
| `test_self_format_reveals_order_value` | `order_value` present |
| `test_vendor_costcard_hides_amounts` | every masked field |
| `test_self_costcard_shows_amounts` | amounts + the full pricing summary / formulas |
| `test_request_prints_from_live_cost_card` | live-card fallback for a Purchase Request |
