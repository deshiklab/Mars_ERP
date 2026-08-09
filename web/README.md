# REM ERP — Vue 3 PWA (web/)

Modern frontend rebuild of the REM ERP PWA: Vue 3 + TypeScript + Tailwind CSS v4 + Vite, installable as a PWA.

## Requirements
- **Node >= 20** (create-vue and the Tailwind v4 oxide native binding both require it).
  On this machine: `/tmp/node-v20.19.0-linux-x64/bin` (export PATH first).

## Install & run

```bash
cd web
export PATH="/tmp/node-v20.19.0-linux-x64/bin:$PATH"
npm install
npm run dev        # http://localhost:5173  (proxies /api -> localhost:8000)
npm run build      # production build -> dist/ (PWA SW + manifest generated)
npm run preview    # serve the production build
```

## Architecture

```
src/
  api/client.ts    Typed API client for the Frappe bridge (sid-param auth,
                   2FA login, bootstrap, leads) — relative base, proxied in dev
  api/types.ts     Bridge response types
  stores/auth.ts   Pinia auth store — two-step 2FA state machine, role mapping
  stores/data.ts   Pinia data store — dashboard stats + CRM leads
  views/LoginView.vue   Secure sign-in + OTP stage
  views/DashboardView.vue
  views/LeadsView.vue   CRM leads table with status updates
  router/index.ts  Auth + role guards
  App.vue          Shell with role-aware nav
```

## Auth flow
1. `login(email, password)` → `two_factor_required` challenge (`tmp_id`)
2. `verifyOtp(email, password, otp, tmp_id)` → `{ token (sid), roles, ... }`
3. All calls append `?sid=<token>` (CSRF-immune; `credentials: 'omit'`)
4. Role mapping: Administrator/MARS Manager → Super Admin · MARS Agent →
   Sales Agent · MARS Customer → Customer (module access via `ROLE_MODULES`)

## PWA
- `vite-plugin-pwa`, `registerType: 'autoUpdate'` (new SW auto-reloads the app)
- Workbox: **NetworkFirst** for `/api/method/mars_constech*` (8s timeout, 1h cache),
  **StaleWhileRevalidate** for static assets (30d cache)
- Manifest: name/short_name/theme `#2f80ed`/icons (192/512/maskable)

## Dev proxy
`vite.config.ts` proxies `/api` → `http://localhost:8000` in dev, so the browser
never hits CORS. In production, serve `dist/` from the Frappe app (same origin).
