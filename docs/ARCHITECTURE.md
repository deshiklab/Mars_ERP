# REM ERP — System Architecture (v2.6)

**MARS Constech · Production ERP · 2026-08-09**
This document describes the system as deployed at tag `v2.6` (post-security-hardening).

---

## 1. Topology

```
┌────────────────────────── Windows 10 laptop (host) ─────────────────────────┐
│  Browsers:                                                                    │
│   • file:// double-click of rem-frappe.html (PWA, local demo)                 │
│   • http://localhost:8000  (hosted PWA + ERPNext desk)                        │
│   • https://192.168.68.100:8443 (LAN via nginx TLS + netsh portproxy)         │
└──────────────────────────────────┬────────────────────────────────────────────┘
                                   │  HTTP 8000 (loopback/LAN)
                                   │  HTTPS 8443 (nginx TLS termination)
┌──────────────────────────────────▼────────────────────────────────────────────┐
│  WSL2 Ubuntu-24.04 — Frappe bench                                             │
│                                                                               │
│  nginx :8443 (TLS 1.2/1.3, self-signed for LAN) ──proxy──► bench :8000        │
│  bench start: web (Werkzeug :8000) · socketio (:9000) · worker · schedule     │
│                                                                               │
│  ERPNext v15 (frappe 15.117.0, erpnext 15.119.0)                              │
│  ├─ mars_constech app (custom)                                                │
│  │   ├─ api/__init__.py        80 whitelisted methods (76 auth, 4 guest)      │
│  │   ├─ 30 doctypes (native bridges + REM custom family)                      │
│  │   ├─ 3 desk pages (land kanban, exec dashboard, settings manager)          │
│  │   ├─ payments/gateways.py   bKash/Nagad adapters + settlement              │
│  │   ├─ public/rem/index.html  THE PWA (single-file, v2.6)                    │
│  │   └─ www/customer_portal/   client portal                                  │
│  └─ MariaDB 10.11 (_b74dab38fb7cdb38) · Redis 11000 (queue) / 13000 (cache)   │
└────────────────────────────────────────────────────────────────────────────────┘
```

**Ops layer (Windows Task Scheduler):** Autostart (logon) · Watchdog (5 min,
elevated — revives redis/bench, refreshes netsh portproxies 8000+8443) ·
Backup (02:00 daily, rotation 14). Backups restore-tested.

---

## 2. The PWA (client)

- Single self-contained `index.html` (~2 MB, no build step), served by Frappe
  at `/assets/mars_constech/rem/index.html` OR opened via `file://`.
- All data lives in `localStorage` collections (`DB.init('leads', [...])`,
  mock seed arrays) + `rem_api_token` / `rem_api_user` for auth state.
- Renders via string-built `innerHTML` (module render fns); **H4 hardening**
  added an `esc()` helper applied to server-controlled free-text fields.

### API integration layer (v2.1+, registry-driven)
- `API_EPS` — registry of all 80 endpoints (name, method, guest flag, group,
  sample query/body). Powers the API tester dropdown AND `syncTestAll()`.
- `API.call(name, opts)` — the one request path: 20s AbortController timeout,
  auto sid-param auth (skipped for guest endpoints), `{message:...}` unwrap,
  stale-URL self-heal (HTTP 4xx/5xx + network throws, retry once), 401 →
  clear token + `onDisconnect`.
- `API._req(method, path, body, raw)` — thin compat wrapper for legacy call
  sites. `API.login(email, pass, otp, tmp_id)` supports the 2FA two-step.

### Global sync (v2.6)
- Top-bar 🔄 button → `globalSyncAll(force)` → 21-module `SYNC_MODULES`
  registry, staggered dispatch (max 4 pipeline calls per 450ms tick), 60s
  per-module cooldown (Shift+click forces), silent-window toast suppression
  during the run, one summary toast, button states idle→spinning→✓.

---

## 3. The bridge (server)

All endpoints live in `mars_constech.mars_constech.api` as
`@frappe.whitelist` functions. Pattern per module:

```
x_pipeline()   → read ERPNext → PWA-shaped rows (merge by id client-side)
x_sync(rows)   → upsert into native/custom doctype (dedupe by rem_ref/id)
x_update_*     → targeted status/follow-up mutations
```

Native bridges: Lead (12 custom fields + scoring), Employee, Timesheet,
Item/Stock/PO/Warehouse, Supplier, Asset, Issue, Project/Task, Sales
Invoice, Payment Entry, Journal Entry, Customer. Custom doctypes:
REM Booking(+Installment), Land Acquisition family, REM Attendance/Leave/
Shift, REM Approval, REM BOQ, REM Broker, REM Handover, REM Labor, REM
Investment, REM Loan, REM Variation Order, REM Work Order, REM Lead
Activity, REM Settings, REM Collection, Mars Payment Gateway Settings.

**Guest endpoints (4):** `login` (2FA-capable), `index` (endpoint map),
`payment_callback` (gateway server-to-server callback — binding-gated),
`demo_confirm` (now session-required).

---

## 4. Authentication & authorization

| Layer | Mechanism |
|---|---|
| Session | Frappe-native sid; 8h expiry (M1) |
| Transport | sid query param (`credentials:'omit'` — no cookies from PWA); cookie session for desk |
| 2FA (M1) | OTP App (TOTP), role-based opt-in (Role.two_factor_auth + All role), enforced in `login()`; Administrator exempt (Frappe default) |
| Brute force (M1) | 3 consecutive attempts → lockout |
| CSRF (C3) | `ignore_csrf: 0` (desk protected; PWA path immune — no cookies) |
| CORS (H2) | whitelist: `null` (file://), localhost:8000, 127.0.0.1:8000, LAN http/https |
| Roles | Administrator / MARS Manager / MARS Agent / MARS Customer (+ portal scoping via User Permission) |

---

## 5. Payments (hardened, C1)

- `pay_invoice` (authed, ownership-checked) → creates gateway session AND a
  **server-side binding** `mars_pay_bind_{payment_id}` → {invoice, gateway}
  in Redis (2h TTL).
- `payment_callback` (guest — real gateways call server-to-server) resolves
  invoice **only from the binding**; caller-supplied invoice/amount ignored.
- `verify_and_settle` uses binding invoice + gateway-verified amount; settles
  via Payment Entry (as Administrator, idempotent by reference_no+party).
- `demo_confirm` requires a session (no longer guest). `sandbox_mode = 0`.

---

## 6. Security posture (post-hardening, v2.6)

| Control | State |
|---|---|
| TLS | nginx self-signed on 8443 (LAN); http 8000 retained for loopback/dev |
| CSRF | enabled (site-wide) |
| XSS | `esc()` on server-controlled free-text render sites (49 sites); residual: non-free-text/legacy sites |
| Payment binding | server-side, caller values ignored |
| Sandbox payments | OFF |
| Hardcoded creds | removed from PWA; all passwords rotated (16-char random) |
| developer_mode | OFF (asset cache kept no-cache via local frappe patch) |
| 2FA | OTP App for all non-Administrator users |
| Sessions | 8h · 3 login attempts · lockout |

**Local-only, uncommittable frappe/app.py patches (documented):** asset
no-cache (now unconditional), PNA preflight header, null-origin CORS
special case, JSON-POST query-arg merge for sid auth.

---

## 7. Key flows

1. **Connect (2FA):** Settings › Server Sync → email+password →
   `login()` stage 1 → `two_factor_required` + tmp_id → prompt() for OTP →
   `login()` stage 2 with otp+tmp_id → token stored → `pushAll()`.
2. **Global sync:** 🔄 → staggered pipeline pulls → merge by id → DB.save →
   single render + summary toast.
3. **Payment:** portal Pay Now → `pay_invoice` (binding) → gateway/demo →
   callback → binding-gated settle → invoice Paid.
4. **Desk:** Administrator/manager login (cookie + CSRF token) → pages
   (land kanban, exec dashboard, settings manager).
