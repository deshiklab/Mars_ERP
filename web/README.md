# REM ERP — Vue 3 PWA (web/)

The Vue 3 + TypeScript + Tailwind v4 + Vite rebuild of the REM ERP PWA,
feature-complete against the vanilla `rem-frappe.html` app and talking to the
same 78-endpoint Frappe bridge (`mars_constech.mars_constech.api`).

## Stack

- **Vue 3** (`<script setup>`) · **TypeScript** · **Vite 6** · **vite-plugin-pwa** (generateSW)
- Design system mirrors the HTML PWA: LIGHT theme, 72px white sidebar
  (#2F80ED accents, collapses to a 46px icon rail under 768px), 44px top bar,
  9–12px Inter, 720px `drawer-sheet` drawers, dark-mode class on `<html>`.

## Layout

```
src/
  main.ts            bootstrap + router + PWA registration
  App.vue            shell: sidebar, topbar, footer, global drawers
  router/index.ts    95 routes (SPA history mode)
  shell/groups.ts    11 sidebar groups → module ids
  views/             91 view components (one per module)
  components/        21 shared components (DataTable, drawers, panels…)
  stores/data.ts     Pinia store: 13 collections + loaders
  stores/auth.ts     session / 2FA restore
  api/client.ts      typed bridge client (38 methods, dot-form endpoints)
  api/types.ts       36 PWA contracts (Lead, Booking, Due, …)
  i18n.ts            EN / বাংলা dictionary
  toast.ts           global toast state
```

## DataTable — the smart table toolkit

Every module table is a `DataTable` instance with:

- **Sortable headers, column visibility, live search, tabs, pagination, CSV, Print**
- **Smart cell clicks** (contextual, no conflicts with row-click or inline edit):
  - phone → `tel:` call link · email → `mailto:`
  - invoice number → opens the invoice record
  - property name → routes to Flats & Units
  - status → inline dropdown (options aligned to the server funnels;
    `@status-change` persists via the bridge with revert-on-failure)
  - money cells → click to copy
- **Name-link cells** — blue, clickable; **✎ inline edit** (Enter commits, Esc cancels)
- **Row click** → opens the record's detail drawer (7 dedicated drawers +
  a universal `GenericDetailDrawer` used by ~70 views with prev/next,
  copy-on-click, status pill, Esc/overlay close, print)

## Build

```bash
export PATH="$HOME/node20/bin:$PATH"   # Node ≥ 20 (terser needs it)
npm run build                          # vue-tsc + vite + generateSW → dist/
npm run dev -- --host 0.0.0.0 --port 5173
npm run preview                        # serves dist/ for production checks
```

Dev-mode service worker is disabled (`devOptions.enabled: false`) — a stale
dev SW caused blank-screen reports after restarts. PWA install/offline is
verified against production builds.

## API access

- Authed via `localStorage.rem_api_token` (the bridge `login` → 2FA token).
- `apiBaseUrl` falls back to same-origin (`/api/method/...`) — works
  file:// (with the token seeded) and hosted.
- Guest-whitelisted endpoints (login, signup, index health) stay guest;
  everything else requires the sid.

## Verification workflow

- Route sweep: every path returns 200 (SPA fallback).
- iframe seeds + headless Edge screenshots: real DOM clicks (⋯ → View Details,
  status dropdown, dashboard widget rows, money copy) with a debug-log overlay.
- `--print-to-pdf` for the print stylesheet; fresh `--user-data-dir` profiles
  to rule out stale SW/cache.

## Deployment

See `REM-ERP-Vue3-PWA-Deployment-Runbook.docx` (two options: static
`public/rem-vue` mount or replacing the vanilla PWA with rollback), SPA
fallback rules, and the post-deploy checklist.
