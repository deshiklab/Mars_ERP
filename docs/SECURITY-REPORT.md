# REM ERP — Security Audit & Hardening Report

**Date:** 2026-08-09 · **Applies to:** tag `v2.6` · **Auditor:** Hermes Agent (autonomous)
**Method:** live inspection of site config, whitelist surface, payment code,
auth flow; live exploit-path testing (guest endpoints, CSRF, CORS, 2FA,
brute-force); browser-probe regression.

---

## 1. Findings & fixes applied (all verified live)

| ID | Severity | Finding | Fix (verified) |
|---|---|---|---|
| C1 | 🔴 CRITICAL | `sandbox_mode=1` + guest `demo_confirm` allowed **free invoice settlement**; `payment_callback` trusted caller-supplied `invoice`/`amount` (pay A → settle B) | sandbox_mode=0 · `demo_confirm` now session-required (guest → 403) · `pay_invoice` mints a server-side `mars_pay_bind_{id}` binding (2h TTL) · callback/settle resolve invoice ONLY from binding; caller values ignored (guest callback with fake id → "Unknown payment session") |
| C2 | 🔴 CRITICAL | Demo password `Bismillah@123` **embedded in the shipped PWA** (API tester quick-login); all 5 accounts shared it | Passwords rotated to 16-char random per account · embedded creds stripped (0 occurrences) · tester no longer pre-fills a password |
| C3 | 🔴 CRITICAL | `ignore_csrf=1` site-wide — desk (cookie-authed) was CSRF-vulnerable | `ignore_csrf=0` · verified guest login + sid-authed GET/POST still work (sid-param path is CSRF-immune by design) |
| H1 | 🔴 HIGH | `developer_mode=1` in the live site (tracebacks, debug endpoints) | `developer_mode=0` · local asset no-cache patch made unconditional so PWA deploys still show instantly |
| H2 | 🔴 HIGH | `allow_cors="*"` — any origin could call the API | Restricted to `null` (file://), localhost:8000, 127.0.0.1:8000, LAN http/https · verified evil origin gets **0** ACAO headers |
| H3 | 🔴 HIGH | No TLS anywhere — passwords/sids in cleartext on LAN | nginx TLS (1.2/1.3) on **:8443** with self-signed cert, proxies to bench; LAN https verified 200; watchdog + portproxy now manage both 8000 and 8443 |
| H4 | 🔴 HIGH | Stored-XSS surface: server-controlled free text string-built into innerHTML; sid in localStorage → token theft | `esc()` helper + 49 render sites patched (names, notes, descriptions, subjects, remarks, activity text); 0 double-escapes; input `value=` sites verified correct |
| M1 | 🟠 MED | No 2FA · 170h sessions · 10 allowed login failures | 2FA (OTP App) enforced on all non-Administrator users with two-step login flow (stage1 challenge → stage2 OTP) · session 8h · 3 attempts → lockout (lockout verified live) · PWA `syncConnect` prompts for the OTP |

**Bonus fix (found during M1 verification):** the 5-min Windows watchdog was
**killing healthy benches every tick** — its curl health-check false-failed
while its own `setsid nohup bench start` (started from the task-spawned
shell) died with the parent, so each tick killed the running bench and
started another doomed one. Fixed: listener-based health check
(`ss -tlnp :8000`) + fully-detached bench start; regression-tested (watchdog
run against a healthy bench leaves it untouched).

---

## 2. Credentials (rotated — SAVE THESE)

| Account | Password (16-char random) | 2FA secret (TOTP) |
|---|---|---|
| Administrator | `I%kp!DYFXcMVT9gH` | exempt (Frappe default) |
| manager@mars.com | `9jQZCDT@Y8@8jJb@` | `XSBBOHPNHFCP7HLS` |
| agent@mars.com | `rB5X2$3yULWvD8EF` | `EJKVDECJSG4X4KHH` |
| customer@mars.com | `BZSdXzm4Fdqo82Yx` | `OUE6VRXEHQMPYUNR` |
| rubina@mars.com | `x#RLtJ4GFn@s7qVg` | `TJ3544G63YMOKTBH` |

**Set up your authenticator app:** add each account's `otpauth://totp/MARS%20ERP:<user>?secret=<SECRET>&issuer=MARS%20ERP` (e.g. in Google Authenticator / Aegis / 1Password). The PWA will prompt for the 6-digit code at connect.

> ⚠️ These were auto-generated and are stored in this report only. Rotate
> them again before any real deployment, and treat this file as sensitive.

---

## 3. Residual risks (accepted / deferred)

| Item | Risk | Recommendation |
|---|---|---|
| Self-signed TLS | Browser warning on LAN first visit | Use letsencrypt when hosting on a real domain (runbook prepared) |
| H4 coverage | `esc()` applied to free-text sites; legacy/structural interpolations not swept | Full render-function audit before external exposure |
| HTTP :8000 still open | Cleartext fallback remains for loopback/dev | Deprecate after hosted deployment |
| Payment gateway keys | Not configured (sandbox off, gateways disabled) — payments effectively off | Configure bKash/Nagad credentials + webhook signature verification before enabling |
| CORS whitelist is IP-based | LAN IP can change | Hosted deployment replaces with domain-based |
| `_otpsecret` defaults | Stored encrypted in `tabDefaultValue` (parent `__2fa`) — standard Frappe | OK |
| Rate limiting | API endpoints rely on Frappe defaults | Add per-user throttling if exposed publicly |
| Admin password in this report | Sensitive file | Move to password manager; rotate before prod |

---

## 4. Verification evidence (live, 2026-08-09)

- Guest `demo_confirm` → **403** · guest `payment_callback` fake id → **"Unknown payment session"**
- 2FA: stage1 `two_factor_required: true` + tmp_id → stage2 correct OTP → token (56 chars, expiry 08:00) · wrong OTP → **401**
- Brute force: 4th consecutive wrong attempt → **lockout SecurityException** (60s)
- CORS: evil origin → **0** ACAO headers; file:// (null) → ACAO `*` (required for double-click); LAN https origin → allowed
- CSRF on: guest login 200, authed GET/POST with sid 200, desk page 200
- TLS: `https://localhost:8443/login` 200, `https://192.168.68.100:8443` 200
- Escaping: `esc('<b>&"\'</b>')` → `&lt;b&gt;&amp;&quot;&#39;&lt;/b&gt;` (single-escape confirmed)
- Post-hardening browser probe: esc() present, 2FA challenge received by PWA, global sync + 25 mock leads intact, 78 endpoints live
