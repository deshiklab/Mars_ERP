# REM ERP — Technical Specification

**MARS Constech · Production ERP · v3.1.8 · 2026-08-10**
Live data verified against the running system.

---

## 1. System Overview

REM ERP is a production ERP for MARS Constech (Bangladesh real-estate
developer) built as a **PWA (V10 UI spec) running inside ERPNext v15**
via a custom Frappe app (`mars_constech`). The PWA preserves the V10
interface; the data layer is patched to Frappe REST endpoints through a
registry-driven bridge. No React rewrite, no separate Flask backend —
ERPNext is the single source of truth.

**Codebase:** `github.com/deshiklab/Mars_ERP` (branch `main`, deploy key)
**Current release:** v3.1.8 (git `4e414ff`)

---

## 2. Technology Stack

| Layer | Technology | Version |
|---|---|---|
| Host OS | Windows 10 (laptop `deshik`) + WSL2 | — |
| Linux distro | Ubuntu | 24.04 |
| ERP platform | ERPNext | **15.119.0** |
| Frappe framework | Frappe | **15.117.0** |
| Python | CPython | **3.12.3** |
| Node.js (assets/realtime) | Node | **18.19.1** |
| Database | MariaDB | (site DB `_b74dab38fb7cdb38`) |
| Web server (LAN) | nginx (reverse proxy, TLS) | — |
| TLS | Self-signed cert (10y, LAN SAN) | — |
| Frontend | Vanilla JS PWA (single `index.html`, ~2 MB) | V10 UI |
| App | `mars_constech` (custom) | v3.1.8 |

---

## 3. Runtime Topology

```
┌─ Windows 10 ──────────────────────────────────────────────┐
│  Browser (file:// or http://localhost:8000)               │
│    │                                                      │
│  netsh portproxy  8000 → 127.0.0.1 loopback only (dev)    │
│  netsh portproxy  8443 → 0.0.0.0 LAN (TLS only)           │
└──────────┬────────────────────────────────────────────────┘
           │
┌─ WSL2 (Ubuntu 24.04) ─────────────────────────────────────┐
│  nginx :8443 (TLS) ──► bench :8000                        │
│  frappe-bench (honcho)                                    │
│    ├─ web.1   werkzeug :8000  (site mars.local)           │
│    ├─ redis   :9000-ish (realtime, queue)                 │
│    └─ socketio :9000 (realtime websocket)                 │
│  MariaDB (local socket / 127.0.0.1:3306)                  │
│  watchdog: rem-watchdog.sh (listener check every 5 min)   │
└────────────────────────────────────────────────────────────┘
```

- **PWA URL:** `http://localhost:8000/assets/mars_constech/rem/index.html`
- **LAN (TLS):** `https://192.168.68.100:8443/assets/mars_constech/rem/index.html`
- **API base:** `.../api/method/mars_constech.mars_constech.api`
- **Desk:** `/app/rem-executive-dashboard`, `/app/rem-settings-manager`,
  `/app/land-acquisition-pipeline`

---

## 4. API Bridge (78 endpoints)

Registry-driven single path (`API.call`) with:

| Convention | Meaning |
|---|---|
| `*_pipeline` | read (GET, session-required) |
| `*_sync` | upsert (POST) |
| `*_update*` | status mutation |
| `booking_invoice` / `booking_payment` | native Sales Invoice / Payment Entry |

**Endpoint map (78 total):**
- Core/session (7): `index` (guest health; map session-gated), `login`
  (guest, 2FA), `logout`, `bootstrap`, `sync`, `settings_get`,
  `settings_set`
- CRM & Leads (12): `leads_pipeline`, `leads_sync`, `lead_update_status`,
  `lead_activity_add`, `brokers_pipeline`, `brokers_sync`,
  `complaints_pipeline`, `complaints_sync`, `bookings_pipeline`,
  `bookings_sync`, `booking_update_status`, `booking_invoice`
- Land & Legal (5): `land_pipeline`, `land_sync`, `land_legal_checklist`,
  `land_legal_update`, `land_legal_load_standard`
- Dues & Finance (10): `dues_pipeline`, `dues_update`, `finance_pipeline`,
  `journal_sync`, `invoices_pipeline`, `payments_pipeline`,
  `party_ledger_pipeline`, `booking_payment`, `download_invoice`,
  `demo_confirm` (session-required since v2.7)
- HR (7): `employees_pipeline`, `employees_sync`, `attendance_pipeline`,
  `attendance_sync`, `leave_pipeline`, `leave_sync`, `shifts_pipeline`
- Stock & Procurement (5): `inventory_pipeline`, `inventory_sync`,
  `po_pipeline`, `po_sync`, `receipts_pipeline`
- Projects & Construction (13): `projects_pipeline`, `projects_sync`,
  `tasks_pipeline`, `tasks_sync`, `plots_pipeline`, `plots_sync`,
  `plot_update_status`, `contractors_pipeline`, `contractors_sync`,
  `work_orders_pipeline`, `work_orders_sync`, `equipment_pipeline`,
  `equipment_sync`
- Quality & Approvals (5): `qc_pipeline`, `approvals_pipeline`,
  `approvals_sync`, `boq_pipeline`, `boq_sync`
- Sweep-2 modules (14): fixed_assets, tickets, handover, variation_orders,
  labor, investments, loans — each `*_pipeline` + `*_sync`
- Guest endpoints: `signup` (rate-limited 5/5min/IP) added v3.0

---

## 5. Authentication & Authorization

### Login flow (two-step, 2FA enforced)
1. `POST login` {email, password} → 200 challenge
   `{two_factor_required:true, tmp_id, verification:{method:'OTP App'},
   user}` (note: no token in this response)
2. `POST login` {email, password, otp, tmp_id} → `{token (sid), user,
   roles, session_expiry:'08:00'}`
3. All calls append `?sid=<token>`; `credentials:'omit'` (CSRF-immune by
   design; no cookies from the PWA)

### Roles
| ERPNext role | PWA role | Access |
|---|---|---|
| Administrator / MARS Manager | Super Admin | everything |
| MARS Agent | Sales Agent | CRM, bookings, dues, handover, tasks… |
| MARS Customer | Customer | portal-only (portal, bookings, dues, ticketing, handover) |

- Login gate at boot (no session → sign-in card; valid session → dashboard)
- OTP auto-submit on 6th digit; 30s-refresh hint
- Session expiry: 8h; 3 failed attempts → 60s lockout; login rate-limited
  10/60s/IP; sync + 9 hot pipelines 60/60s/user
- Self-registration: guest `signup` creates Customer + User with MARS
  Customer & Customer roles

### Accounts (rotated v2.7, in `docs/SECURITY-REPORT.md`)
- Administrator (exempt from 2FA), manager@mars.com, agent@mars.com,
  customer@mars.com, rubina@mars.com — all with TOTP secrets

---

## 6. Data Model

- **DB:** 49.8 MB, 733 tables, site `mars.local`
- **Custom doctypes:** 28 under module `Mars Constech` (incl. REM Booking,
  REM Lead, REM Settings, REM Broker, REM Collection, REM Attendance,
  REM Leave, REM Shift, REM BOQ, REM Approval, REM Handover, REM Investment,
  REM Labor, REM Loan, REM Variation Order, REM Work Order, Land
  Acquisition, Project Lifecycle, Mars Payment Gateway Settings…)
- **Seed data (live):** 17 REM Bookings · 22 Leads (server-computed scores,
  priorities, follow-ups) · 12 Employees · 32 Items · 6 Brokers ·
  5 Complaints · 84 Attendance rows · 4 Shifts · 10 stock bins ·
  3 Purchase Orders
- PWA merges server data into localStorage collections (100 keys
  whitelisted server-side for `sync`)

---

## 7. Security Posture (hardening v2.7–v3.1.8)

| Control | State |
|---|---|
| Transport | TLS on LAN via nginx :8443; loopback http allowed for dev only; **LAN http :8000 deprecated (v2.8)** |
| 2FA | TOTP required for all non-Administrator accounts |
| Sessions | 8h · 3 failed attempts → lockout · login rate-limited 10/60s/IP |
| CSRF | enabled site-wide (PWA path immune — sid param, no cookies) |
| CORS | whitelisted origins (file:// null, localhost, LAN http/https); evil origin gets 0 ACAO headers |
| Payments | `pay_invoice` mints server-side binding `mars_pay_bind_*`; callbacks settle only bound invoices (kills pay-A-settle-B); sandbox_mode=0 |
| XSS | `esc()` applied at render sites (656-site sweep v2.8; 49 high-risk sites v2.7); 0 double-escapes verified |
| Sync | collection keys whitelisted to 100 real PWA collections; unknown keys rejected + logged |
| Rate limits | login 10/60s/IP; sync + hot pipelines 60/60s/user |
| Enumeration | `index` endpoint map session-gated (guest = health only) |
| Stale-cache | network-only `sw.js` (v3.1.4) replaces stale workers; self-heal on version mismatch (v3.1.7); drawer z-index fix (v3.1.8) |

**Credentials:** all passwords rotated (16-char) v2.7; embedded PWA demo
password removed; TOTP secrets stored in `docs/SECURITY-REPORT.md`.

---

## 8. PWA Architecture

- Single `index.html` (~2 MB) — no build step, no framework
- **API layer:** `const API` with registry `API_EPS` (name → method/guest),
  `call()` = fetch + AbortController timeout (20s default, 8s login),
  stale-URL self-heal, 401 → token clear + disconnect hook, version ping
- **DB layer:** `DB.init('collection', [...])` → localStorage persistence
  (100 collections), merge pulls (idempotent), pushAll → server `sync`
- **RBAC:** `ROLE_MODULES` per PWA role + `canAccess()`/`canEdit()` +
  permission matrix; sidebar filtered per role
- **UX:** login gate (boot), drawer modal system (`openModal`),
  `askFields()` form modals (replaced all 42 prompt() dialogs, v2.9),
  global sync button (staggered 4 calls/450ms, 60s cooldown, silent toasts,
  v2.6), user profile panel (v3.1), toasts, notifications, 7 groups /
  35+ modules
- **Service worker:** network-only (v3.1.4) — exists to replace stale
  workers; `updateViaCache:'none'`

---

## 9. Deployment & Operations

- **Watchdog:** `~/rem-watchdog.sh` — ss-listener health check on :8000,
  `setsid` detached bench start; runs every 5 min via Task Scheduler;
  Windows `rem-watchdog.bat` refreshes portproxies (8000 loopback + 8443 LAN)
- **Restart:** kill ports 8000/9000 → clear `__pycache__` → `bench start`
  (background terminal, watch "web.1 started")
- **Backups:** auto-backup enabled (latest full `20260809_143730`; take a
  fresh one before migrations)
- **Runbook:** `REM-ERP-DEPLOYMENT-RUNBOOK.md` (hosted deployment parked;
  VPS provider TBD)

---

## 10. Version History (releases)

| Tag | Key change |
|---|---|
| v2.0–v2.4 | Module bridging, 78 endpoints |
| v2.5 (`625e0bf`) | CRM & Leads full contract, server scores, activities, brokers |
| v2.6 (`beadda9`) | Global Sync button (staggered, cooldown, silent) |
| v2.7 (`94fb61b`) | Security hardening: C1 payment binding, C2 creds rotated, C3 CSRF, H1 dev off, H2 CORS, H3 TLS, H4 XSS esc, M1 2FA |
| v2.8 (`cb9109a`) | H4 completion (656 sites), M2 index gating, rate limits, LAN http deprecated |
| v2.9 (`1f7accf`) | 42 prompt() → modal forms; sync collection whitelist |
| v2.9.1 (`1b321f2`) | 2FA modal fix (branch checks token not user) |
| v2.9.2 (`35d0701`) | API & Auth (2FA) guide docs |
| v3.0 (`ccaa9ca`) | Login/sign-in system + RBAC + customer signup |
| v3.1 (`eb07082`) | Profile panel replaces demo Switch Role; PWA link on login page |
| v3.1.1–v3.1.3 | 2FA hardening, dashboard redirect, auto-submit, hang fix |
| v3.1.4–v3.1.7 | Stale SW fix, flip-loop fix, false-notice fix, self-heal |
| v3.1.8 (`4e414ff`) | Invisible 2FA modal fix (drawer z-index) |

---

## 11. Known Limitations / Next Steps

- Self-signed TLS cert — replace with a real cert for hosted deployment
- Hosted deployment (Phase 2/3 of runbook) not yet executed — VPS provider
  question outstanding
- HTTP loopback :8000 remains for dev; LAN is TLS-only
- Authenticator secrets are static (documented); rotation policy manual
