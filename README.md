# Mars_ERP — REM ERP on ERPNext (Frappe)

Custom ERP for **MARS Constech** — a real-estate development company. Built as a
custom Frappe app (`mars_constech`) on top of **ERPNext v15**, running in
**WSL2 Ubuntu 24.04** on the developer laptop. The REM ERP V10 PWA prototype is
hosted inside Frappe and syncs with the backend through a Flask-style API bridge.

> The V10 PWA (`design-prototype-v10.html`) is the UI/UX spec. Its built-in
> server-sync layer (`API` object: login/bootstrap/sync) — originally written for
> a Flask backend — is reused unchanged by implementing the same contract on the
> Frappe side.

---

## Quick start (dev environment)

### Requirements

- Windows 10+ with **WSL2** (Ubuntu 24.04)
- **8 GB RAM** allocated to WSL (see `%USERPROFILE%\.wslconfig`)
- ~20 GB free disk

### Bring the stack up

```bash
# From Windows:
C:\Users\deshik\autostart-rem-erp.bat
```

Or manually inside WSL:

```bash
echo Bismillah | sudo -S service mariadb start
redis-server ~/frappe-bench/config/redis_queue.conf --daemonize yes   # port 11000
redis-server ~/frappe-bench/config/redis_cache.conf --daemonize yes   # port 13000
cd ~/frappe-bench && nohup bench start &>/tmp/bench-start.log &
# wait ~40s
curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/login   # → 200
```

A **Task Scheduler job ("REM ERP Autostart")** runs this automatically at logon.

### Access

| What | URL | Credentials |
|---|---|---|
| ERPNext desk | http://localhost:8000 | `Administrator` / `admin` |
| REM V10 PWA (hosted) | http://localhost:8000/assets/mars_constech/rem/index.html | via Server Sync (below) |
| Site name | `mars.local` (also reachable as `localhost` via sites symlink) | — |

### Connect the PWA to the backend

In the PWA: **Settings (gear) → Server Sync** →

- Server URL: `http://localhost:8000/api/method/mars_constech.mars_constech.api`
- Email: `Administrator`
- Password: `admin`

It then pushes local demo collections to ERPNext (`REM Collection` doctype) and
pulls them back on demand.

---

## Architecture

```
REM V10 PWA (single-file HTML, served by Frappe)
        │  <base>/login  <base>/bootstrap  <base>/sync  <base>/logout
        ▼
mars_constech.mars_constech.api  (whitelisted Frappe methods, api/__init__.py)
        │
        ├── REM Collection doctype  → JSON-blob storage for PWA collections
        └── Core doctypes           → structured ERP records
             ├── Land Acquisition     (6-stage pipeline + scorecard + legal + audit)
             ├── Project Lifecycle    (7 stages + transition audit trail)
             └── Booking              (payment plans + installment schedule)
```

Key design decisions:

- **Do not fork ERPNext.** `mars_constech` is a custom app on top — upstream
  updates come free.
- **~80% of REM's spec already exists in ERPNext** (accounting, CRM, projects,
  assets, HR) — the custom app covers only the real-estate differentiators.
- **The PWA's sync contract was already built** (originally for Flask). The
  Frappe side implements the exact same contract, so the frontend needed only a
  5-line patch (default URL + dotted paths).

---

## Doctypes (module: Mars Constech)

| Doctype | Purpose |
|---|---|
| **Land Acquisition** | 6-stage pipeline: Lead → Survey → Negotiation → Agreement → Registration → Handover |
| — Scorecard Item (child) | Feasibility criteria with weight + rating; auto-computes `feasibility_score` (%) |
| — Legal Check (child) | Legal vetting checklist (Pending / Cleared / Issues Found) |
| — Stage Log (child) | Read-only audit trail; every stage change appends user + timestamp |
| **Project Lifecycle** | 7 stages: Planning → Land Acquisition → Design & Approval → Construction → Marketing & Sales → Handover → Closed; progress %, audit trail |
| — Stage Log (child) | Transition audit rows |
| **Booking** | Customer, project, property/unit, total price, payment plan, installment schedule; auto-computes Total Paid / Total Due / Days Overdue |
| — Installment (child) | Installment rows (amount, paid, status) |
| **REM Collection** | JSON-blob store mirroring the PWA's localStorage keys (sync bridge) |

### Business logic in controllers

- `LandAcquisition.validate()` → weighted feasibility score:
  `Σ(score/5 × weight) / Σ(weight) × 100`
- `LandAcquisition.validate()` / `ProjectLifecycle.validate()` → appends audit
  row when `current_stage` changes (idempotent; compares against DB value)
- `Booking.validate()` → payment summary ripple: `total_paid` = Σ installments
  paid, `total_due` = price − paid, `days_overdue` from oldest unpaid past-due
  installment

---

## API bridge (PWA ⇄ Frappe)

Whitelisted methods in `mars_constech/mars_constech/api/__init__.py`:

| Method | Path (dotted) | Purpose |
|---|---|---|
| `login` (allow_guest) | `<base>.login` | Authenticate → `{token: sid, full_name, user}` |
| `bootstrap` | `<base>.bootstrap` | Pull all stored collections → `{collections, meta}` |
| `sync` | `<base>.sync` | Upsert JSON collections → `{rows, collections}` |
| `logout` | `<base>.logout` | End session → `{ok: true}` |

Where `<base>` = `http://localhost:8000/api/method/mars_constech.mars_constech.api`.

**Critical gotchas** (both cost debugging time):

1. **Dots, not slashes** — Frappe's `/api/method/` handler truncates at the
   first `/`. Use `...api.login`, never `...api/login`.
2. **Functions must live directly in `api/__init__.py`** — a submodule
   (`api/rem_api.py`) breaks Frappe's `rsplit(".", 1)` resolution.

---

## Development workflow

### Scaffolding a new doctype

1. Author `mars-doctypes/<dt_name>/<dt_name>.json` (module = `"Mars Constech"`).
2. Copy into the app + migrate:
   ```bash
   APP=~/frappe-bench/apps/mars_constech/mars_constech/mars_constech
   mkdir -p $APP/doctype/<dt_name>
   cp mars-doctypes/<dt_name>/<dt_name>.json $APP/doctype/<dt_name>/
   cd ~/frappe-bench && bench --site mars.local migrate
   ```
3. Write the controller `.py`, syntax-check (`ast.parse`), then **restart bench
   with a full kill** (see pitfalls).
4. Verify via REST API.

### Restarting bench after code changes (nuclear restart)

```bash
pkill -9 -f "bench"; pkill -9 -f gunicorn; pkill -9 -f honcho; sleep 4
ss -tlnp | grep 8000          # must be EMPTY — a stale listener serves old code
find ~/frappe-bench/apps/mars_constech -name __pycache__ -type d -exec rm -rf {} +
nohup bench start &> /tmp/bench-start.log &
```

### Git

```bash
cd ~/frappe-bench/apps/mars_constech
git add -A && git commit -m "..." && git push
```

Pushes go to `github.com/deshiklab/Mars_ERP` (branch `main`) via a **deploy key**
(scoped to this repo only). On a fresh WSL if the first push hangs, accept the
host key first:
`GIT_SSH_COMMAND="ssh -o StrictHostKeyChecking=accept-new" git push`

---

## Troubleshooting / pitfalls (all hit in the field)

1. **Stale bench owns port 8000** — `pkill -f "bench start"` does NOT kill
   gunicorn (different cmdline). Result: old code keeps serving, bizarre errors
   ("no attribute", "not whitelisted") that don't reproduce in `bench console`.
   → Nuclear restart (above), then confirm a NEW pid on port 8000.
2. **MariaDB root auth** — Ubuntu 24.04 root uses `unix_socket`; bench connects
   via TCP and gets `(1698) Access denied`. Fix once:
   `ALTER USER 'root'@'localhost' IDENTIFIED VIA mysql_native_password USING PASSWORD('root');`
3. **localhost 404 on Frappe v15** — the site is resolved purely from the Host
   header; there is no `serve_default_site` fallback. Fix: symlink
   `~/frappe-bench/sites/localhost -> mars.local`.
4. **Child-table audit logs** — never `db_set` a Table field (SQL error 1064).
   Append rows in `validate()` comparing against `frappe.db.get_value(...)`,
   guard duplicates via the last row's value.
5. **WSL has no systemd** — services don't auto-start; use the autostart task.
6. **`bench new-app` is interactive** — pipe all fields in order (title,
   description, publisher, valid email, lowercase license e.g. `mit`, y/N).
7. **`bench --site` must run from the bench dir** — `cd ~/frappe-bench` first.
8. **Host terminal blocks `sudo -S`** — put sudo inside a script file and run it
   via `wsl bash <script>`; don't pipe passwords in the raw terminal command.
9. **Windows `python3` is the MS Store stub** — run Python via WSL.

---

## Verification checklist

- `curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/login` → 200
- Login: `POST <base>.login` `{"email":"Administrator","password":"admin"}` → token
- Sync: `POST <base>.sync` `{"collections":{"<key>":[...]}}` → `{"rows":N}`
- Bootstrap: `POST <base>.bootstrap` → collections echo back
- PWA: `http://localhost:8000/assets/mars_constech/rem/index.html` → 200, title
  "REM ERP v10 — PWA Edition"

---

## Roadmap / next steps

- [ ] Port PWA collections into real doctypes (map `bookings` → `Booking`,
      `customers` → `Customer`, `invoices` → `Sales Invoice`, etc.)
- [ ] bKash / Nagad payment adapters (ripple logic from REM's old Flask backend)
- [ ] Customer portal on Frappe's portal framework (mobile-friendly, payment
      gateway hooks)
- [ ] Land Acquisition dashboard + kanban matching the V10 design
- [ ] Production deploy: 4 GB+ VPS with HTTPS, backups, monitoring
- [ ] Roles & permissions (Super Admin / Manager / Agent / Customer)

---

## License

MIT (see `license.txt`). ERPNext itself is GPLv3 — internal use for MARS
Constech is fine; check obligations if ever productized as multi-tenant SaaS.
