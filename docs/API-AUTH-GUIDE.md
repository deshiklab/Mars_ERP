# REM ERP — API & Authentication (2FA) Guide

**MARS Constech · Production ERP · v2.9.1 · 2026-08-09**
Covers: how the PWA talks to ERPNext, every API endpoint, the authentication
flow (including two-factor), credentials & 2FA secrets, and worked examples.

---

## 1. API Base & Conventions

| Item | Value |
|---|---|
| Base URL (local) | `http://localhost:8000/api/method/mars_constech.mars_constech.api` |
| Base URL (LAN, TLS) | `https://192.168.68.100:8443/api/method/mars_constech.mars_constech.api` |
| Endpoint form | append the method name: `...api.<method>` |
| Response wrapper | Frappe standard: `{"message": {...}}` (the PWA auto-unwraps) |
| Auth transport | **sid query param** (`?sid=<token>`), `credentials: 'omit'` — never cookies from the PWA |
| Session expiry | 8 hours |
| Guest endpoints | `index`, `login`, `payment_callback` (binding-gated) — `demo_confirm` requires a session (v2.7+) |
| Rate limits | `login` 10 req/60s per IP · `sync` + 9 hot pipelines 60 req/60s per user |

The PWA (single `index.html`) stores its session in `localStorage`
(`rem_api_token`, `rem_api_user`) and calls every endpoint through one
registry-driven path (`API.call`) with a 20s timeout, stale-URL self-heal,
and 401 handling (token cleared + disconnect hook).

---

## 2. Authentication Flow (with 2FA)

Two-factor authentication (TOTP) is **enabled for all non-Administrator
users**. The login is a two-step flow:

### Stage 1 — password
```
POST .../api.login
Content-Type: application/json

{"email":"manager@mars.com","password":"<PASSWORD>"}
```

**Response** (2FA user):
```json
{
  "message": {
    "two_factor_required": true,
    "tmp_id": "519e17cb",
    "verification": {"method": "OTP App", "setup": true},
    "user": "manager@mars.com"
  }
}
```
Note: this response carries `user` but **no token** — a valid session is only
issued after the OTP is confirmed.

### Stage 2 — OTP
```
POST .../api.login
Content-Type: application/json

{"email":"manager@mars.com","password":"<PASSWORD>","otp":"123456","tmp_id":"519e17cb"}
```

**Response** (success):
```json
{
  "message": {
    "token": "d2843ba93754a6b05d98217c724d6a9061d31195333e4a807af59b72",
    "full_name": "MARS Manager",
    "user": "manager@mars.com",
    "session_expiry": "08:00"
  }
}
```
The `token` is the sid — append it as `?sid=<token>` to every authenticated
call. Wrong OTP → HTTP 401. Three failed password attempts → account lockout
(60s). Rate limit → HTTP 429.

### Curl example (full round-trip)
```bash
BASE=http://localhost:8000/api/method/mars_constech.mars_constech.api

# 1. password -> challenge
R1=$(curl -s -X POST "$BASE.login" -H "Content-Type: application/json" \
  -d '{"email":"manager@mars.com","password":"<PASSWORD>"}')
TMPID=$(echo "$R1" | python3 -c "import sys,json;print(json.load(sys.stdin)['message']['tmp_id'])")

# 2. compute the TOTP from the secret (python: pip install pyotp)
OTP=$(python3 -c "import pyotp;print(pyotp.TOTP('<2FA_SECRET>').now())")

# 3. OTP -> token
TOKEN=$(curl -s -X POST "$BASE.login" -H "Content-Type: application/json" \
  -d "{\"email\":\"manager@mars.com\",\"password\":\"<PASSWORD>\",\"otp\":\"$OTP\",\"tmp_id\":\"$TMPID\"}" \
  | python3 -c "import sys,json;print(json.load(sys.stdin)['message']['token'])")

# 4. use it
curl -s "$BASE.dues_pipeline?sid=$TOKEN"
```

### Non-2FA path (Administrator / desk)
The desk uses the standard cookie + CSRF-token login. Administrator is
exempt from 2FA. Direct API login as Administrator is single-step (returns
token immediately).

---

## 3. Credentials & 2FA Secrets (rotated 2026-08-09, v2.7)

| Account | Password | 2FA secret (TOTP) |
|---|---|---|
| Administrator | `I%kp!DYFXcMVT9gH` | exempt |
| manager@mars.com | `9jQZCDT@Y8@8jJb@` | `XSBBOHPNHFCP7HLS` |
| agent@mars.com | `rB5X2$3yULWvD8EF` | `EJKVDECJSG4X4KHH` |
| customer@mars.com | `BZSdXzm4Fdqo82Yx` | `OUE6VRXEHQMPYUNR` |
| rubina@mars.com | `x#RLtJ4GFn@s7qVg` | `TJ3544G63YMOKTBH` |

**Set up an authenticator app** (Google Authenticator / Microsoft
Authenticator / Aegis / 1Password): add a manual TOTP entry with the secret,
e.g. for manager:

```
otpauth://totp/MARS%20ERP:manager%40mars.com?secret=XSBBOHPNHFCP7HLS&issuer=MARS%20ERP
```

> ⚠️ These are auto-generated and stored in this document. Rotate before any
> real deployment. Treat as sensitive.

---

## 4. Full Endpoint Map (78 total)

### Core / session (7)
`index` (guest health; map behind session) · `login` (guest, 2FA) ·
`logout` · `bootstrap` · `sync` (whitelisted keys) · `settings_get` ·
`settings_set`

### CRM & Leads (12)
`leads_pipeline` · `leads_sync` · `lead_update_status` ·
`lead_activity_add` · `brokers_pipeline` · `brokers_sync` ·
`complaints_pipeline` · `complaints_sync` · `bookings_pipeline` ·
`bookings_sync` · `booking_update_status` · `booking_invoice`

### Land & Legal (5)
`land_pipeline` · `land_sync` · `land_legal_checklist` ·
`land_legal_update` · `land_legal_load_standard`

### Dues & Finance (10)
`dues_pipeline` · `dues_update` · `finance_pipeline` · `journal_sync` ·
`invoices_pipeline` · `payments_pipeline` · `party_ledger_pipeline` ·
`booking_payment` · `download_invoice` · `demo_confirm` (session)

### HR (7)
`employees_pipeline` · `employees_sync` · `attendance_pipeline` ·
`attendance_sync` · `leave_pipeline` · `leave_sync` · `shifts_pipeline`

### Stock & Procurement (5)
`inventory_pipeline` · `inventory_sync` · `po_pipeline` · `po_sync` ·
`receipts_pipeline`

### Projects & Construction (13)
`projects_pipeline` · `projects_sync` · `tasks_pipeline` · `tasks_sync` ·
`plots_pipeline` · `plots_sync` · `plot_update_status` ·
`contractors_pipeline` · `contractors_sync` · `work_orders_pipeline` ·
`work_orders_sync` · `equipment_pipeline` · `equipment_sync`

### Quality & Approvals (5)
`qc_pipeline` · `approvals_pipeline` · `approvals_sync` · `boq_pipeline` ·
`boq_sync`

### Sweep-2 modules (14)
`fixed_assets_pipeline` · `fixed_assets_sync` · `tickets_pipeline` ·
`tickets_sync` · `handover_pipeline` · `handover_sync` ·
`variation_orders_pipeline` · `variation_orders_sync` · `labor_pipeline` ·
`labor_sync` · `investments_pipeline` · `investments_sync` ·
`loans_pipeline` · `loans_sync`

**Naming convention:** `*_pipeline` = read (GET, session) · `*_sync` =
upsert (POST) · `*_update*` = status mutation · `booking_invoice` /
`booking_payment` = native Sales Invoice / Payment Entry creation.

---

## 5. Security posture (applies to API use)

| Control | State |
|---|---|
| Transport | TLS on LAN (`https://…:8443`); loopback http allowed for dev only |
| 2FA | TOTP required for all non-Administrator accounts |
| Sessions | 8h · 3 failed attempts → lockout · login rate-limited 10/60s/IP |
| CSRF | enabled site-wide (PWA path immune — no cookies) |
| CORS | whitelisted origins (file:// null, localhost, LAN http/https) |
| Payments | `pay_invoice` mints a server-side binding; callbacks settle only bound invoices |
| XSS | `esc()` applied at render sites for server-controlled text |
| Sync | collection keys whitelisted to the 100 real PWA collections |

---

## 6. Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `two_factor_required` response with no modal | Old PWA tab — close & reopen (file:// loads JS once) |
| "2FA verification failed" | OTP expired (30s window) — re-enter the current code |
| HTTP 401 on login | Wrong password or wrong OTP |
| HTTP 429 on login | Rate limit (10/min/IP) — wait 60s |
| "Your account has been locked" | 3 failed attempts — wait 60s |
| HTTP 403 on `demo_confirm` | Session required since v2.7 (expected) |
| Unknown collection in `sync` | Key not in whitelist — rejected + logged (expected) |
| LAN connect fails | Use https://192.168.68.100:8443 (http deprecated v2.8) |
