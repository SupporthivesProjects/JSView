# Frontend Reorg — Proposed Old → New Mapping

**Status: proposal only. Nothing has been moved or deleted yet.** Review this, tell me to proceed
(or adjust), and I'll execute the moves + import-path fixes as a separate step.

Scope: `src/frontend/src/` and `src/frontend/lib/` (~546 files total: 493 in `src/`, 53 in `lib/`).

---

## 0. Decisions already made (per your answers)

1. **`@lib` alias**: kept as-is, pointing at the existing `src/frontend/lib/` (InvenTree's published
   plugin SDK, `@inventreedb/ui`). The new "single shared API client" folder gets a **different**
   alias: **`@app-lib` → `/src/lib`** (avoiding `@core`, since InvenTree already has an unrelated
   `pages/core/` business domain — "Core" objects like Users/Groups — and reusing that word for the
   alias would be confusing).
2. **`actions/`**: created, but only populated with `functions/auth.tsx` → `actions/auth.ts` (the one
   file that already groups real API calls by resource). Nothing else moves there — the rest of the
   app calls its API through generic components (`InvenTreeTable`, `ApiForm`, `useInstance`), not
   per-resource files, and synthesizing new `actions/*.ts` files from that would mean writing new
   code, not relocating existing code.

## 1. A few more calls I made while building this mapping (flagging, not asking)

These are all low-risk / easily-renamed-later, so I didn't want to spend another round of questions
on them — but flagging so nothing is a surprise:

| Item | Decision | Why |
|---|---|---|
| Zustand global stores (`states/`) | New top-level `store/` (not folded into `context/`) | Your template's `context/` is described as "global providers" (React Context). Zustand stores aren't providers — forcing them into `context/` would misdescribe them. |
| Static config/constants (`defaults/`) | New top-level `config/` | Same reasoning — these are constants/config objects (nav links, backend enum mappings, default host list), not "helpers" in the function-utility sense. `formatters.tsx` is the one real utility file in there, so it moves to `helpers/` instead (see §4). |
| App shell bootstrap (`views/`) | Left as its own top-level `views/`, unchanged | `MainView`/`DesktopAppView`/`MobileAppView` choose the mobile-vs-desktop shell and wrap providers — broader than "the route path tree" your `routes/` spec is scoped to, and not reusable page logic either. |
| Route-loading layout components (`Layout.tsx` x2) | New `components/layouts/` | They're route `element`s but wrap *every* child route via `<Outlet/>` — not one route's page logic, so they don't fit `containers/<route>/` either. |
| Vanilla-extract theme files (`theme.ts`, `main.css.ts`) | Consolidated into existing `styles/` folder | `src/styles/overrides.css` already exists; grouping all three styling files together is a small, safe tidy-up. |
| `lib/types/` (model types: `ModelType`, `TableColumn`, `User`, etc.) | **Not moved** — stays in `lib/` | These are part of the published plugin-SDK surface, not app-internal types. Nothing currently qualifies for a new `src/types/` folder — it would just be empty. |
| `src/locales/` (117 Lingui i18n catalog files) | **Not moved** | Build-tool-coupled translation data (Lingui extract/compile config points at this exact path). Doesn't conceptually fit any bucket in your target tree, and moving it risks breaking the i18n pipeline for zero benefit. |

---

## 2. New alias configuration required

**`vite.config.ts`** (existing `resolve.alias` block, `@lib` stays untouched, `@app-lib` added):
```ts
alias: {
  '@lib': '/lib',
  '@app-lib': '/src/lib'
}
```

**`tsconfig.json`** (existing `@lib/*` stays untouched, `@app-lib/*` added):
```json
"paths": {
  "@lib/*": ["./lib/*"],
  "@app-lib/*": ["./src/lib/*"]
}
```

I'd also suggest adding `@containers`, `@components`, `@context`, `@helpers`, `@config`, `@store`,
`@actions`, `@routes` aliases the same way, per your original request — full list at the bottom (§7).

This project uses **Vite**, not Create React App, so the alias limitation you flagged doesn't apply
here — no ejecting/craco needed.

---

## 3. Routes — `router.tsx` → `routes/` + `containers/<route>/index.tsx`

`router.tsx` (238 lines) becomes `routes/router.tsx`. Every page component it currently imports from
`pages/...` moves into a `containers/<route-name>/index.tsx`, and `router.tsx`'s imports get updated
to point there — this is the core of the "no page logic inline in the route file" rule, and it's
already true today (the route file only ever imports+renders page components, never defines its own
JSX/state), so this is a pure relocation + import-path fix, not a rewrite.

| Route path | Old page file | New container |
|---|---|---|
| `*` (catch-all) | `components/errors/NotFound.tsx` | `containers/not-found/index.tsx` |
| `/` (index) & `home/` | `pages/Index/Home.tsx` | `containers/home/index.tsx` |
| `notifications/*` | `pages/Notifications.tsx` | `containers/notifications/index.tsx` |
| `scan/` | `pages/Index/Scan.tsx` | `containers/scan/index.tsx` |
| `settings/admin/*` | `pages/Index/Settings/AdminCenter/Index.tsx` | `containers/settings-admin/index.tsx` |
| `settings/system/*` | `pages/Index/Settings/SystemSettings.tsx` | `containers/settings-system/index.tsx` |
| `settings/user/*` | `pages/Index/Settings/UserSettings.tsx` | `containers/settings-user/index.tsx` |
| `part/category/:id?/*` | `pages/part/CategoryDetail.tsx` | `containers/part-category/index.tsx` |
| `part/:id/*` | `pages/part/PartDetail.tsx` | `containers/part-detail/index.tsx` |
| `stock/location/:id?/*` | `pages/stock/LocationDetail.tsx` | `containers/stock-location/index.tsx` |
| `stock/item/:id/*` | `pages/stock/StockDetail.tsx` | `containers/stock-item/index.tsx` |
| `stock/transfer-order/:id/*` | `pages/stock/TransferOrderDetail.tsx` | `containers/stock-transfer-order/index.tsx` |
| `manufacturing/index/*` | `pages/build/BuildIndex.tsx` | `containers/manufacturing/index.tsx` |
| `manufacturing/build-order/:id/*` | `pages/build/BuildDetail.tsx` | `containers/build-order/index.tsx` |
| `purchasing/index/*` | `pages/purchasing/PurchasingIndex.tsx` | `containers/purchasing/index.tsx` |
| `purchasing/purchase-order/:id/*` | `pages/purchasing/PurchaseOrderDetail.tsx` | `containers/purchase-order/index.tsx` |
| `purchasing/supplier/:id/*` | `pages/company/SupplierDetail.tsx` | `containers/supplier/index.tsx` |
| `purchasing/supplier-part/:id/*` | `pages/company/SupplierPartDetail.tsx` | `containers/supplier-part/index.tsx` |
| `purchasing/manufacturer/:id/*` | `pages/company/ManufacturerDetail.tsx` | `containers/manufacturer/index.tsx` |
| `purchasing/manufacturer-part/:id/*` | `pages/company/ManufacturerPartDetail.tsx` | `containers/manufacturer-part/index.tsx` |
| `company/:id/*` | `pages/company/CompanyDetail.tsx` | `containers/company/index.tsx` |
| `sales/index/*` | `pages/sales/SalesIndex.tsx` | `containers/sales/index.tsx` |
| `sales/sales-order/:id/*` | `pages/sales/SalesOrderDetail.tsx` | `containers/sales-order/index.tsx` |
| `sales/shipment/:id/*` | `pages/sales/SalesOrderShipmentDetail.tsx` | `containers/sales-order-shipment/index.tsx` |
| `sales/return-order/:id/*` | `pages/sales/ReturnOrderDetail.tsx` | `containers/return-order/index.tsx` |
| `sales/customer/:id/*` | `pages/company/CustomerDetail.tsx` | `containers/customer/index.tsx` |
| `core/index/*` | `pages/core/CoreIndex.tsx` | `containers/core/index.tsx` |
| `core/user/:id/*` | `pages/core/UserDetail.tsx` | `containers/core-user/index.tsx` |
| `core/group/:id/*` | `pages/core/GroupDetail.tsx` | `containers/core-group/index.tsx` |
| `/login` | `pages/Auth/Login.tsx` | `containers/login/index.tsx` |
| `/logged-in` | `pages/Auth/LoggedIn.tsx` | `containers/logged-in/index.tsx` |
| `/logout` | `pages/Auth/Logout.tsx` | `containers/logout/index.tsx` |
| `/register` | `pages/Auth/Register.tsx` | `containers/register/index.tsx` |
| `/mfa` | `pages/Auth/MFA.tsx` | `containers/mfa/index.tsx` |
| `/mfa-setup` | `pages/Auth/MFASetup.tsx` | `containers/mfa-setup/index.tsx` |
| `/change-password` | `pages/Auth/ChangePassword.tsx` | `containers/change-password/index.tsx` |
| `/reset-password` | `pages/Auth/Reset.tsx` | `containers/reset-password/index.tsx` |
| `/set-password` | `pages/Auth/ResetPassword.tsx` | `containers/set-password/index.tsx` |
| `/verify-email/:key` | `pages/Auth/VerifyEmail.tsx` | `containers/verify-email/index.tsx` |

**Not a route path → not a container:**
- `pages/ErrorPage.tsx` is used as `errorElement` on every route group (a fallback, not a path-bound
  page) → `components/shared/errors/ErrorPage.tsx`.
- `components/nav/Layout.tsx` (`LayoutComponent`) and `pages/Auth/Layout.tsx`
  (`LoginLayoutComponent`) wrap *all* their child routes via `<Outlet/>` → `components/layouts/AppLayout.tsx`
  and `components/layouts/AuthLayout.tsx` (see §0 table).
- `functions/loading.tsx` (`Loadable`/`EagerLoadable`) and `functions/localeReady.ts`
  (`onLocaleReady`) are used by more than just the router (also by `GlobalImporterDrawer`,
  `AdminCenter`, `LanguageContext`) → `helpers/loading.ts` / `helpers/localeReady.ts`, not `routes/`.

## 4. Container-local sub-components (verified by import-usage, not guessed)

I checked actual import usage for every file that looked page-specific before deciding where it goes.
Two were **not** page-specific and are called out as shared exceptions:

| Old path | New path | Why |
|---|---|---|
| `pages/part/PartAllocationPanel.tsx`, `PartPricingPanel.tsx`, `PartStockHistoryDetail.tsx`, `PartSupplierDetail.tsx` | `containers/part-detail/components/*` | Only imported from within `pages/part/` (PartDetail's own tabs) |
| `pages/part/bom/BomActions.tsx`, `BomCompare.tsx` | `containers/part-detail/components/bom/*` | Only used by PartDetail's BOM tab |
| `pages/part/pricing/*.tsx` (7 files: `BomPricingPanel`, `PriceBreakPanel`, `PricingOverviewPanel`, `PricingPanel`, `PurchaseHistoryPanel`, `SaleHistoryPanel`, `SupplierPricingPanel`, `VariantPricingPanel`) | `containers/part-detail/components/pricing/*` | Only used by PartDetail's pricing tab |
| `pages/Index/Settings/AdminCenter/*.tsx` (9 panel files) | `containers/settings-admin/components/*` | Only used by AdminCenter's own `Index.tsx` |
| `pages/Index/Settings/AccountSettings/AccountDetailPanel.tsx`, `MFASettings.tsx`, `SecurityContent.tsx`, `UserPanel.tsx`, `UserThemePanel.tsx` | `containers/settings-user/components/*` | Only used by `UserSettings.tsx` |
| **`pages/Index/Settings/AccountSettings/QrRegistrationForm.tsx`** | **`components/shared/QrRegistrationForm.tsx`** | ⚠️ Exception: imported by both `UserSettings.tsx` (settings-user container) *and* `pages/Auth/MFASetup.tsx` (mfa-setup container) — used by two different containers, so it can't live inside just one |
| **`pages/Index/Settings/PluginSettingsGroup.tsx`** | **`components/shared/PluginSettingsGroup.tsx`** | ⚠️ Exception: imported by both `UserSettings.tsx` *and* `SystemSettings.tsx` — two different containers |

All 20 files in `src/hooks/` were checked the same way (grep'd every importer): **none are
single-page-only** — every hook (`UseForm`, `UseInstance`, `UseModal`, `UsePlugins`, etc.) is used
from `tables/`, `components/`, and multiple `pages/*` domains simultaneously. So `hooks/` stays a
shared top-level folder unchanged — nothing moves into a `containers/<route>/hooks/`.

## 5. Domain folders (`tables/`, `forms/`) → `components/`

These are used across *multiple* containers each (e.g. `PartTable` is rendered from both the
part-category container and the stock-location container), so per your own template's definition of
`components/shared` ("reused across multiple pages"), they belong under `components/`, not inside
any single container:

| Old path | New path |
|---|---|
| `src/tables/<domain>/*` (12 domains, 88 files: `bom`, `build`, `company`, `general`, `machine`, `notifications`, `part`, `plugin`, `purchasing`, `sales`, `settings`, `stock`) | `components/tables/<domain>/*` (unchanged internal filenames — joins the existing generic table engine files that already live at `components/tables/`, e.g. `InvenTreeTable.tsx`, `ColumnRenderers.tsx`) |
| `src/forms/*.tsx` (12 files: `PartForms`, `BomForms`, `BuildForms`, `CompanyForms`, `PurchaseOrderForms`, `ReturnOrderForms`, `SalesOrderForms`, `StockForms`, `TransferOrderForms`, `ImporterForms`, `CommonFields`, `CommonForms`) | `components/forms/*.tsx` (flat, unchanged filenames — joins the existing generic form engine files already there, e.g. `ApiForm.tsx`) |

## 6. `components/` reorganization into `ui/` / `shared/`

The existing `components/` has 19 subfolders + `SplashScreen.tsx`. I split out the two that are
genuinely base-primitive widget libraries into `ui/`; everything else (already "reused across
multiple pages" by construction — that's why it isn't inside a specific page folder today) becomes
`shared/`, keeping each subfolder's name and internal structure exactly as-is:

| Old path | New path |
|---|---|
| `components/buttons/*` (11 files) | `components/ui/buttons/*` |
| `components/items/*` (22 files) | `components/ui/items/*` — note some of these (`ActionDropdown.tsx`, `RoleTable.tsx`, `MenuLinks.tsx`, `TransferList.tsx`) are more "composite/business" than pure primitives; I left them here rather than guessing a finer split — flag if you want them reclassified into `shared/` individually |
| `components/SplashScreen.tsx` | `components/shared/SplashScreen.tsx` |
| `components/barcodes/*` | `components/shared/barcodes/*` |
| `components/calendar/*` | `components/shared/calendar/*` |
| `components/charts/*` | `components/shared/charts/*` |
| `components/dashboard/*` | `components/shared/dashboard/*` |
| `components/details/*` | `components/shared/details/*` |
| `components/editors/*` | `components/shared/editors/*` |
| `components/errors/{ClientError,GenericErrorPage,NotAuthenticated,PermissionDenied,ServerError}.tsx` | `components/shared/errors/*` (NotFound.tsx excluded — see §3, it's a container) |
| `components/images/*` | `components/shared/images/*` |
| `components/importer/*` | `components/shared/importer/*` |
| `components/modals/*` | `components/shared/modals/*` |
| `components/nav/*` (minus `Layout.tsx`, see §3) | `components/nav/*` (kept as its own top-level grouping — cohesive nav-chrome module, reused everywhere; forcing it under `shared/` or `ui/` wouldn't add clarity) |
| `components/panels/*` | `components/shared/panels/*` |
| `components/plugins/*` | `components/shared/plugins/*` |
| `components/render/*` | `components/shared/render/*` |
| `components/settings/*` | `components/shared/settings/*` |
| `components/wizards/*` | `components/shared/wizards/*` |
| `components/tables/*` (generic engine, +joined by §5's domain subfolders) | `components/tables/*` (unchanged) |
| `components/forms/*` (generic engine, +joined by §5's domain files) | `components/forms/*` (unchanged) |

## 7. Remaining top-level files

| Old path | New path |
|---|---|
| `src/App.tsx` (axios instance, `setApiDefaults`, `QueryClient`, trace-id headers) | `src/lib/api/client.ts` — this file *is* the "single shared API client" your template describes |
| `src/contexts/*` (4 files: `ApiContext`, `LanguageContext`, `ThemeContext`, `colorSchema`) | `src/context/*` (renamed folder, files unchanged) |
| `src/states/*` (10 Zustand stores) | `src/store/*` (renamed folder, files unchanged — see §1) |
| `src/defaults/{actions,backendMappings,defaultHostList,defaults,links,templates}.tsx` | `src/config/*` (renamed folder — see §1) |
| `src/defaults/formatters.tsx` | `src/helpers/formatters.ts` (real utility functions, not config) |
| `src/functions/auth.tsx` | `src/actions/auth.ts` (per your decision in §0) |
| `src/functions/{api,comparison,debug,forms,icons,loading,localeReady,notifications,urls}.tsx` | `src/helpers/*` (unchanged filenames, `.ts`/`.tsx` as appropriate) |
| `src/theme.ts`, `src/main.css.ts` | `src/styles/theme.ts`, `src/styles/main.css.ts` (joins existing `src/styles/overrides.css`) |
| `src/assets/inventree.svg` + `src/components/items/inventree.svg` (duplicate) | `src/assets/images/inventree.svg` (consolidated; the two importers' relative import paths get updated) |
| `src/main.tsx`, `src/views/*`, `src/router.tsx` (→ `src/routes/router.tsx`) | see §3 |
| `src/locales/*` (117 files) | **unchanged** — see §0 |
| `lib/*` (53 files, published plugin SDK) | **unchanged** — see §0 |

## 8. Suggested alias set (Vite + tsconfig, in addition to §2)

```ts
// vite.config.ts resolve.alias
{
  '@lib': '/lib',                 // existing — untouched
  '@app-lib': '/src/lib',
  '@routes': '/src/routes',
  '@actions': '/src/actions',
  '@containers': '/src/containers',
  '@components': '/src/components',
  '@context': '/src/context',
  '@store': '/src/store',
  '@config': '/src/config',
  '@helpers': '/src/helpers',
  '@assets': '/src/assets'
}
```
Mirror the same set under `tsconfig.json` → `compilerOptions.paths` (each as `"@x/*": ["./src/x/*"]`,
except `@lib/*` which stays `["./lib/*"]`).

---

## 9. Reconciling with your Next.js reference tree (`tree.txt`)

You shared a real Next.js App Router project as the target shape. Good news: it's the same family
of convention as §0–§8 above (containers mirror routes 1:1, actions hold API calls, components split
into `ui`/`shared`, `lib` holds the API client + utils, `context`/`helpers`/`types`/`assets` as
named) — so the concrete mapping table doesn't change. But Next.js's `app/` directory relies on
**file-system routing** (folder path = URL path, `page.tsx`/`layout.tsx`/`(group)` are special
filenames Next itself discovers), which Vite + `react-router-dom` (what this project uses) has no
equivalent mechanism for. Translating faithfully rather than copying folder-for-folder:

- **`app/` itself → `routes/router.tsx`, not a folder tree.** Vite doesn't scan folders for routes;
  the tree has to be one explicit file (or a few files) listing every `<Route>`, which is exactly
  `routes/router.tsx` from §3. Creating a `page.tsx` per folder to visually match your reference
  would just be dead code Vite never wires up. *Optional, if you want closer visual/organizational
  parity anyway:* I can split the current 238-line `router.tsx` into per-domain fragment files
  (e.g. `routes/part.routes.tsx`, `routes/stock.routes.tsx`) composed into one root
  `routes/router.tsx` — say the word and I'll add it to the plan. This goes slightly beyond a pure
  "move" (it restructures one file into several), which is why I'm calling it out as optional rather
  than folding it into the default plan.
- **`(auth)` / `(public)` route groups** (parentheses = organizational only, no URL segment) map to
  something this router already does: two separate top-level `<Route path='/'>` blocks, one wrapped
  in `LayoutComponent` (main app shell) and one in `LoginLayoutComponent` (auth flow) — same idea,
  no folder syntax needed. Nothing to change here.
- **Per-folder `layout.tsx` at arbitrary depth** → this app only ever needs 2 layout levels (app
  shell, auth shell) — `components/layouts/AppLayout.tsx` + `AuthLayout.tsx` (§0/§3) already covers
  it. Part/Stock/Settings pages implement their own internal tabs via `PanelGroup`, which is page
  *content*, not a route layout — no deeper nesting needed.
- **`actions/` is fully populated in your reference** (11 files, one per resource) — real evidence
  of the pattern, but it doesn't change my earlier read on this codebase: InvenTree's frontend has no
  `getClients()`/`createDress()`-style functions to relocate. Its equivalent logic is generic and
  inline (`InvenTreeTable`, `ApiForm`, `useInstance` calling `apiUrl(ApiEndpoints.x)` directly).
  Populating `actions/{part,stock,build,...}.ts` the way your reference does would mean **writing**
  ~10 new wrapper-function files that don't exist today — a real refactor, not a relocation, so it
  stays out of scope. `actions/auth.ts` (from `functions/auth.tsx`) remains the one honest fit.
- **`components/ui/`** in your reference is shadcn/ui (Radix-based) primitives. This project uses
  Mantine, not shadcn — its structural equivalent is what §6 already identified:
  `components/buttons/` + `components/items/` → `components/ui/buttons/`, `components/ui/items/`.
  Same role, different underlying library — nothing changes.
- **`public/assets/fonts/` + `public/assets/images/`** — two notes:
  1. This app bundles no custom fonts today (no `@font-face`/`.ttf`/`.woff` anywhere in `src/`), so
     `assets/fonts/` would start empty — not a problem, just nothing to move there yet.
  2. There are actually **three copies of the same logo** already in this codebase:
     `src/frontend/public/inventree.svg` (Vite's existing serve-as-is folder), `src/assets/inventree.svg`,
     and `src/components/items/inventree.svg`. Moving the latter two into a Next-style
     `public/assets/images/` would change *how* they're referenced — from a bundled import
     (`import logo from './inventree.svg'`) to a root-relative URL string — which is a behavior
     change, not a pure move. I'd keep the two component-facing copies under `src/assets/images/`
     (bundled-import style, consistent with §7) and leave the existing `public/inventree.svg`
     exactly where it is.
- **Root config files with no equivalent to create here**: `next.config.ts`, `next-env.d.ts`,
  `components.json` (shadcn CLI config — n/a, no shadcn in this project), `postcss.config.mjs` (n/a
  — this project styles with vanilla-extract, not Tailwind/PostCSS). `proxy.tsx`'s job is already
  done by this project's existing `vite.config.ts` `server.proxy` block (`/media` → backend) — no
  new file needed.
- **`lib/utils.ts`** (one generic-utilities file) has no clean 1:1 source here — this app's utility
  functions are already split by concern (`comparison.tsx`, `debug.tsx`, `urls.tsx`, etc., all going
  to `helpers/` per §7). Merging them into one `lib/utils.ts` would combine file contents — a
  rewrite, not a move — so they stay as individually-named files under `helpers/` instead of a
  manufactured `lib/utils.ts`.

Everything in §0–§8 (the route→container table, container-local sub-components, tables/forms→components,
ui/shared split, remaining top-level files, alias list) is unchanged by this — your reference
confirms the shape rather than altering it.

---

## 10. Before you say "go": scale and risk, plainly

- This touches **~470 files** (everything in `src/` except `locales/`, which is excluded) plus two
  config files. Moving a file is the easy part; **every file that imports a moved file also needs
  its import path fixed** — that's not optional bookkeeping, the build won't compile otherwise. I'd
  do this with a scripted pass (compute old→new path table, then rewrite import specifiers
  file-by-file) rather than hundreds of individual manual edits, to keep it accurate.
- This is a big divergence from upstream InvenTree's own folder conventions. If you ever want to pull
  future upstream InvenTree changes into this fork, or contribute anything back, that becomes much
  harder once the internal layout no longer matches upstream's `tables/`/`forms/`/`pages/`-by-domain
  structure. Worth a deliberate "yes, this is a permanent fork" call, not just a tidy-up.
- I'd want to verify after moving: the app still builds (`yarn build`), the plugin SDK still builds
  separately (`yarn lib`), and the Playwright e2e tests still resolve their imports
  (`src/frontend/tests/`) — none of these run automatically as a side effect of moving files.
- Per this repo's `CLAUDE.md`, no PR should be opened without your manual review either way — this
  would land as local, uncommitted changes for you to review and commit yourself.

**Nothing has been moved. Let me know if you want me to proceed as mapped above, want changes to any
row first (especially §6's ui/shared split, which is the one place I made a judgment call rather than
verifying usage), or want to do this in smaller batches (e.g. routes+containers first, components
reshuffle later) instead of all at once.**
