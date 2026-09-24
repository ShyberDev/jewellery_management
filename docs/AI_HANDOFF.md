# AI Agent Handoff — jewellery_management (Frappe/ERPNext)

Created: 2026-09-24. Author: outgoing coding agent. Purpose: let a different AI
agent continue this project without access to the prior conversation.

Rules for this document: facts below were verified with the commands noted.
Anything not verified is explicitly marked NOT VERIFIED or as an assumption.

---

## 1. PROJECT CURRENT STATE

- **App location:** `~/frappe-bench/apps/jewellery_management`
  (absolute: `/home/shyam/frappe-bench/apps/jewellery_management`)
- **Site:** `library.local` (`http://library.local:8000/`), bench root `/home/shyam/frappe-bench`
- **Company:** Sri Sai Krishna Jewellery (shop display name; full legal name NOT VERIFIED — owner was asked, see §12)
- **Frappe:** `17.x.x-develop` (commit `8a43de0`), branch `develop`
- **ERPNext:** `17.x.x-develop` (commit `8c24c5b`), branch `develop`
- **jewellery_management:** version `0.0.1` (from `jewellery_management/__init__.py`), branch `develop`
- **Current Git commit (HEAD):** `df135a2` — "fix: dashboard refresh on return + working cash/bank"
- **Remote:** `https://github.com/ShyberDev/jewellery_management.git` (fetch + push)
- **Push status:** NOT VERIFIED whether remote contains these commits. No push was
  performed during this session (explicit owner instruction: never push; GitHub is backup only).
- **Working tree:** CLEAN at handoff creation (verified `git status --short` → empty;
  the only new file after that check is this `docs/AI_HANDOFF.md` itself, intentionally uncommitted).
- **Installed apps on site:** `['frappe', 'erpnext', 'jewellery_management']`
  (`library_management` exists in `apps/` but is NOT installed on this site).
- **DB:** MariaDB (credentials encountered during work — [SECRET/ CREDENTIAL OMITTED]).
- **Developer mode:** ON (`developer_mode: 1` in `common_site_config.json`).
- **Module ownership anomaly (important):** all 24 custom DocTypes have
  `module = "Jewellery"` whose Module Def `app_name` is `"frappe"`, NOT the app's
  `"Jewellery Management"` module (which owns 0 DocTypes). Verified via
  `tabDocType` query. Consequence: packaging relies on `hooks.fixtures`
  DocType export (which is in place and current), not on module ownership.
  Do not "fix" ownership without a migration plan — DocType JSON fixtures are the source of truth.

---

## 2. WHAT YOU WERE ASKED TO DO

**Original objective (session start):** read-only inspection of the bench, then an
architecture/migration proposal. Constraints at that time: change nothing.

**Evolved objective (explicit owner decisions during work):** build a complete,
production-usable Jewellery ERP on Frappe/ERPNext, V1 simplicity first, with the
custom jewellery workflow as primary. Owner later granted: proceed autonomously
without per-step permission, create test data freely (backup exists), break/rebuild
custom artifacts as needed — with hard limits: never touch Frappe/ERPNext core,
never push to GitHub.

**Key scope decisions made with the owner (all explicit):**
1. Priority 1+2 first: net-weight stock fix, Worker field cleanup. Then full ERP build.
2. Custom architecture is primary; do NOT replace it with standard ERPNext
   Item/Stock-Ledger/GL/BOM flows unless explicitly requested. ERPNext GL/BOM
   migration is a stated long-term direction, NOT V1 scope.
3. Order status flow frozen: `Advance Received → Ordered to Worker →
   Worker Finished → Received → Delivered`. No renames, no new statuses, submit only when Delivered.
4. Previous client scripts are REFERENCE ONLY — rewrite/replace freely.
5. All prior DB DocTypes/scripts/reports are reference; may break/reinstall/modify/delete.
6. Shop name for UI: Sri Sai Krishna Jewellery.
7. GST must include a 0% mode; rates configurable per invoice, never hardcoded.
8. Build order approved: Settlement → GST → Old Gold → HUID → Dashboard/Reports →
   Repairs(minimal)/Returns/Ledgers → Counter hardening.
9. Home screen must show a Sri Sai Krishna app tile opening a full dashboard.
10. Sample/test data is explicitly wanted, must be recognizable (`_sample_data`).

---

## 3. EVERYTHING ACTUALLY CHANGED

Git history this session (oldest → newest, branch `develop`; `76c35a2` and
`e1917ff` predate the session):

1. `30d2d98` — Order Transfer IN/OUT switched from `delivered_gross_weight` to
   `delivered_net_weight` (strict, throw-and-block, no fallback).
   File: `jewellery_management/jewellery_management/stock_hooks.py`. Tested: PASS (§7).
2. `adc1325` — P2 worker cleanup + first fixtures export.
   - `Jewellery Order.worker` (Link→Worker, parent, non-mandatory) ADDED.
   - `Jewellery Order Item.worker` (accidental duplicate) REMOVED after verifying 0 non-empty rows.
   - `worker_received_date` label renamed to `Received Date`.
   - `worker_other_charge_details` Table ADDED on Order Item (later relocated, see 4).
   - `update_worker_dates()` removed from `Client Script: Jewellery Order calculation`.
   - Retail transfer dialog label → "Delivered Net Weight".
   - `hooks.fixtures` + first `fixtures/*.json` export. Tested: PASS.
3. `f80c33e` — charge table relocated to Order parent + `order_item_idx` ref;
   parent-grouped rollup rewrite of calculation script. (Superseded by 4.)
4. `3c5530c` — **Two-world model**: deleted `create_order_stock_out_on_submit`
   (125 lines) + its `on_submit` hook. Transfer creates IN only; Stock Sale creates
   OUT; Order Sale never touches stock. Tested end-to-end: PASS.
5. `f259101` — NEW `Worker Settlement` DocType + `settlement.py` + hooks.
   Gold/cash separate ledger, 8 event types, balances API. Tested: PASS.
6. `c658f73` — GST: `gst_rate`/`gst_amount`(`gst`) fields, calc updates, NEW
   `GST Summary` report. Tested (math + SQL): PASS; browser totals NOT VERIFIED by agent.
7. `c33df8a` — Old Gold Receipt/Melt (+`old_gold.py`), sales exchange-credit fields,
   HUID fields + `HUID Register`, `Jewellery` workspace, `Worker Balances` +
   `Customer Outstanding` reports, `Jewellery Repair` (+`workshop.py`),
   `Jewellery Settings` single, Metal Rate `rate_time`, RSI `barcode`,
   additive counter roles, print worker-field removal. Tested: PASS (server-side).
8. `a4fb72d` — Apps-screen tile + `jewellery-dashboard` Page + `dashboard.py`.
9. `eccc543` — Page module fix (`Jewellery` → `Jewellery Management`; without this
   the dashboard served empty — root cause verified).
10. `9bd75c3` — Metal Rate naming-series fix + Silver 999 purity master (fixtures).
11. `f65a9c5` + `df135a2` — dashboard reload-on-return fix + cash/bank query fix.

**Files created (in app):** `.../jewellery_management/{settlement,old_gold,workshop,dashboard}.py`,
`.../page/jewellery_dashboard/{__init__.py,.js,.json}`,
`.../public/images/logo.svg`, `fixtures/workspace.json` (+ 7 other fixture files on first export).
**Files modified:** `hooks.py`, `stock_hooks.py`, `fixtures/{doctype,client_script,report,print_format,workflow,kanban_board}.json`.
**Files deleted:** none (only code deletion inside `stock_hooks.py`).
**`kanban_board.json` churn:** card-position runtime state deliberately reverted out of
commits twice; committed copy holds board structure only.
**Server scripts:** none (all server logic is committable `.py` files, intentional).
**DB DocType changes (24 total, module `Jewellery`, all `custom=1`):** see fixture list in §9;
field-level detail verified in `fixtures/doctype.json` (committed, current).
**Migrations run:** yes, several `bench --site library.local migrate` (schema sync only).
**No Frappe/ERPNext core file was modified** (verified: `git -C apps/frappe status`,
`git -C apps/erpnext status` were clean at inspection; re-verify on start).

---

## 4. FILES INSPECTED

### Core application files
- `jewellery_management/hooks.py` — full hook map (current content verified in §1 context); fixtures list; apps-screen tile.
- `jewellery_management/__init__.py` — version only.
- `modules.txt` (`Jewellery Management`), `patches.txt` (empty skeleton — NO patches used).

### Python (`jewellery_management/jewellery_management/`)
- `stock_hooks.py` — purchase/sale/opening/transfer IN creators, sales validator,
  candidate/transfer whitelisted APIs, kanban-delete cleanup. No OUT creator (deleted by design).
- `settlement.py` — settlement validation + `get_worker_balances` (tested).
- `old_gold.py` — receipt/melt validation + melt expected/variance math (tested).
- `workshop.py` — repair balance guard (tested).
- `dashboard.py` — read-only dashboard aggregator (tested via API).
- `page/jewellery_dashboard/jewellery_dashboard.js` — dashboard UI (syntax-checked only).

### JavaScript
- `public/js/jewellery_kanban.js` (1295 lines, global via `app_include_js`) — compact
  cards/tooltip/expand; inspected, NOT rewritten; known perf/fragility issues (§10).
- 7 DB Client Scripts (inspected + edited): Order calculation / Retail Stock /
  Submission Control / Opening / Sales / Purchase / RSI Smart Fields.

### Reports (DB, fixture-exported)
Retail Stock Balance (pre-existing), GST Summary, HUID Register, Worker Balances,
Customer Outstanding. All query SQL executed at least once: PASS.

### Hooks / Configuration
- `pyproject.toml` (read once; untouched), `site_config.json` (installed apps only),
  `common_site_config.json` (dev mode, ports).
- Print Formats `Jewellery Order Receipt` / `Jewellery Purchase Invoice Receipt`:
  inspected; worker column removed from Order Receipt (verified 0 refs).

### Templates/UI
- `templates/`, `www/` — EMPTY (no portal pages). No Jinja work done.
- Workspace `Jewellery` (DB + `fixtures/workspace.json`) — HTML-nav workspace.

### Tests
- No Frappe `tests/` directory exists. All verification was ad-hoc `bench execute`
  scripts in `/tmp/opencode/` (ephemeral, NOT committed) plus `node --check` and
  `py_compile`. See §7.

---

## 5. COMMANDS AND TOOLS USED

Conventions: [MODIFYING] changed system/DB/files; [READ-ONLY] did not.

- `bench --site library.local execute "exec(open('/tmp/opencode/*.py').read())"` — [MODIFYING]
  (all DB writes) and bare-expression form for reads — [READ-ONLY].
- `bench --site library.local migrate` — [MODIFYING] (schema sync; NOTE: also
  reimports fixtures, which twice reverted unexported DB work — see §10).
- `bench --site library.local export-fixtures --app jewellery_management` — [MODIFYING]
  (writes fixture JSON in app dir; does not touch DB).
- `bench --site library.local clear-cache` — [MODIFYING] (cache only).
- `bench list-apps`, `bench --site library.local list-apps` — [READ-ONLY].
- `bench build --app jewellery_management` — [MODIFYING] (built assets incl. logo).
- `git -C apps/<app> {status,log,diff,add,commit,checkout,branch,remote}` — commits are
  [MODIFYING] (local repo only; never pushed).
- `node --check <file>` — [READ-ONLY]. `python3 -m py_compile` — [READ-ONLY].
- `ps`, `curl` (login page 200; whitelisted-method probe → 403 as expected) — [READ-ONLY].
- `mariadb`/`mysql` clients directly: NOT USED (all DB access via bench).
- `sed -i` (2 uses: fixture label fix, naming probe cleanup) — [MODIFYING] (own temp/app files).
- `websearch` (exactly 2 calls: one cancelled, one commodity jewellery-ERP feature
  survey: Nexao/JSoft/ERIONT/SourceForge/APPIT/SthirApp/GehnaERP) — [READ-ONLY].
  Used only for the competitor feature map; no code taken from anywhere.
- No MCP servers, no npm/pnpm direct installs, no pip installs, no linter/formatter runs.

---

## 6. DATABASE

- Type: MariaDB. Name/user: known to agent at runtime — [SECRET/ CREDENTIAL OMITTED].
- Tables inspected (read-only SQL unless noted): `tabDocType`, `tabDocField`,
  `tabJewellery Order [Item]`, `tabJewellery Stock Transaction`, `tabRetail Stock Item`,
  `tabWorker Settlement`, `tabMetal Purity`, `tabMetal Rate`, `tabGL Entry`,
  `tabAccount`, `tabPayment Entry` (via API), `tabClient Script` (via API).
- Schema changes (all via DocType API + `migrate`): parent `worker`,
  `worker_other_charge_details` (parent), `total_worker_cost`, `Received Date` label,
  removed item `worker`, GST fields, old-gold credit fields, HUID fields, barcode,
  rate_time, all §3 DocTypes/fields, role permission rows (additive).
- Physical orphan: `tabJewellery Order Item.worker` column remains (Frappe never drops
  columns); unused since DocField removal. Harmless.
- Data created: ~10 rates/purities masters; 10 RSI samples; 10 submitted purchases;
  10 submitted sales; 10 orders (8 draft, 2 submitted); 1 worker + 3 settlements;
  2 receipts + 1 melt; 2 repairs; 2 ERPNext parties; 2 COA accounts; 10 Payment Entries;
  6 earlier draft sample bills. All test rows documented in §7/§8; full cleanup was
  performed for volatile tests (`REMAIN=0` verified), seed data intentionally left.
- Data deleted: test-only rows I created (cancel → delete), plus DocField deletions
  above (after 0-usage verification). No real/user data deleted (all data is test data).
- Fixtures: `fixtures/*.json` exported 4+ times; final export verified field-by-field
  before each commit. Fixture files ARE the reinstall path (fresh-install proof NOT done).
- Assumption (clearly marked): remote Git state NOT VERIFIED (no fetch/push performed).

---

## 7. TESTING AND VERIFICATION

Ad-hoc scripts only; no committed test suite. Frappe `tests/` does not exist.

| Test | Command/action | Expected | Actual | Result |
|---|---|---|---|---|
| Net-weight block | new order, `delivered_net_weight=0` → `get_order_stock_candidates` | throw "Delivered Net Weight is required", no "Gross" | exact | PASS |
| Net-weight pass | same order net=9.5 → candidates | `delivered_net_weight: 9.5`, no gross key | exact | PASS |
| Transfer IN | `send_items_to_retail_stock` | IN 9.8, available 9.8 | exact | PASS |
| No OUT on submit | Delivered + submit | txns stay `[In 9.8]` | exact | PASS |
| Stock-sale OUT | submit Sales Invoice 9.8 | OUT 9.8, available 0.0 | exact | PASS |
| Cleanup | cancel+delete all cycle docs | `REMAIN=0`, ref history intact | exact | PASS |
| Settlement math | earning +9.8, gold-given 10g@75%, advance +20000, convert −10000/−1g | gold 2.3→1.3, cash 10000 | exact | PASS |
| Settlement guards | gold on cash event; empty entry | throws | throws | PASS |
| Old-gold math | 25−1.5g @82%/80% @10000; melt actual 18.5 | net 23.5, est 19.27, assay 18.8, var −0.3 | exact | PASS |
| Repair math/guard | 2000−500; advance>estimate | 1500; throw | exact | PASS |
| GST SQL | `GST Summary` query 2020–2030 | 5 submitted bills listed | 5 rows | PASS |
| HUID SQL | `HUID Register` Full View | 6 RSI, all unhallmarked | exact | PASS |
| Dashboard API | `get_data` Sep + all-time | KPIs incl. cash 65k/bank −20k | exact | PASS |
| Parent charge table | 2 items + 3 tagged charges save/load | rows persist with tags | exact | PASS |
| Page serving | `desk_page.get('jewellery-dashboard')` | script len>0 + onload | 6708 chars | PASS |
| Apps tile hook | `get_hooks('add_to_apps_screen')` | tile entry | exact dict | PASS |
| HTTP smoke | `curl /login`; unauth API probe | 200; 403 (found, blocked) | exact | PASS |
| JS syntax | `node --check` on 3 edited scripts | pass | pass | PASS |
| py_compile | all new/edited `.py` | pass | pass | PASS |

NOT performed: browser/manual UI testing by agent (no browser tool); login-as-counter-role
permission test; fresh-site reinstall proof; load/perf tests; GSTR-1 format validation;
e-invoice/TCS; returns flow; any Frappe/ERPNext upgrade regression.

---

## 8. BUSINESS LOGIC (owner-established)

Legend: IMPLEMENTED = live + tested server-side. Others as labeled.

- Ordered weight is an ESTIMATE; delivered net weight rules everything. IMPLEMENTED
  (`delivered_net_weight` strict; submit blocks when 0; gross never used for order stock).
- Worker uses OWN resources; shop never issues stock to worker. IMPLEMENTED (no such code path exists by design).
- Worker payable = actual delivered net × (purity% + item wastage%) × fine (biscuit) rate.
  Wastage-%-first; cash making derives from it. IMPLEMENTED (client calc; server mirror DEFERRED).
- Customer final = delivered-based quoted + delivery weight/amount adjustments; payments
  mixed cash/UPI/etc.; balance floors at 0. IMPLEMENTED (client calc).
- Customer book vs worker book are SEPARATE; meet only in analysis; prints NEVER carry
  worker fields. IMPLEMENTED (print scrub verified).
- Visit lumps (bus fare) are tagged to item sets or whole order, NEVER split.
  IMPLEMENTED (`applicable_items` "1,2,3"/blank; order total counts once).
- Three costs: customer order-date, worker order-date reference, actual settlement
  (rate moved → variance). First two IMPLEMENTED; settlement-date realized P&L PLANNED
  (needs FIFO auto-allocation).
- Order Sale (no stock touch) vs Stock Sale (stock OUT) are separate worlds; unclaimed
  items enter stock ONLY via explicit Transfer to Stock (IN with net weight).
  IMPLEMENTED + cycle-tested.
- Purchase/Sales/Opening create IN/OUT on submit with duplicate guard
  (`exists(reference…)`) — IMPLEMENTED, but atomicity/race hardening DEFERRED (§10).
- Worker running balance (gold grams and cash SEPARATE; bulk/advance/either-direction;
  cash never auto-converts). Ledger + balances IMPLEMENTED; FIFO auto-allocation PLANNED.
- Old gold: intake estimate vs assay kept separate; melt expected-vs-actual variance;
  outs = exchange-credit at sale OR sale-to-worker. IMPLEMENTED.
- GST per-invoice configurable incl. 0%; subtotal×rate (2dp); total includes GST.
  IMPLEMENTED client-side; server mirror + GSTR-1 filing format DEFERRED.
- HUID lifecycle per piece (Not→Sent→Hallmarked + HUID + date); registry shows
  sold/unsold. IMPLEMENTED (registry live; all stock currently unhallmarked — matches owner).
- Rates: daily default + intraday reprice (`rate_time`); bill uses rate at bill time.
  Schema IMPLEMENTED; auto-feed UNKNOWN (manual entry today).
- Order statuses frozen (5); kanban 5 columns; compact cards/tooltip preserved. IMPLEMENTED.
- Roles: System Manager full + additive Sales/Purchase/Stock/Accounts reads/writes.
  IMPLEMENTED but login-as-role NOT VERIFIED.
- Repairs rare → token + balance only. IMPLEMENTED.
- UNKNOWN/owner-open: full legal company name; 18K rate value; village-wise analytics;
  scheme/chit (explicit V2); diamonds/4Cs, multi-branch, RFID, PMLA (explicit out).

---

## 9. CURRENT ARCHITECTURE

**Standard ERPNext used:** Customer link (orders), Warehouse links, `Customer`/`Supplier`/
`Payment Entry`/`GL Entry`/`Account` (sample money flow → dashboard cash/bank),
`Metal Rate`-adjacent masters are custom; `Kanban Board`, `Workflow` (exists, INACTIVE),
`Print Format`, `Report`, `Workspace`, `Page`, `Client Script` frameworks.

**Deliberately custom (owner directive):** Item/Sales/Purchase/Opening/Order/Stock-ledger
(`Jewellery Stock Transaction` grouped by retail_stock_item+purity),
payments-as-child-tables, worker costing/settlement, old-gold, HUID, GST math,
dashboard. NO ERPNext Stock Ledger/GL posting/BOM/Work Order/Subcontracting in V1.

**Custom DocTypes (24, all module `Jewellery`, `custom=1`):** Jewellery Order (+Item,
+Payment children), Purchase Invoice (+Item, +Payment), Sales Invoice (+Item, +Payment),
Opening Stock (+Item), Stock Transaction, Retail Stock Item, Jewellery Item Type,
Metal Purity, Metal Rate, Worker, Worker Other Charge (child), Worker Settlement,
Old Gold Receipt, Old Gold Melt (+Item child), Jewellery Repair, Jewellery Settings (single).

**Server logic:** `stock_hooks.py`, `settlement.py`, `old_gold.py`, `workshop.py`,
`dashboard.py` (+ page JS). No Server Scripts in DB (intentional).

---

## 10. KNOWN ISSUES (do not hide)

1. **Stock transactions post as DRAFT (`docstatus=0`)** — `insert()` without `submit()`
   everywhere. Dashboard/validators count non-cancelled rows to match. Fix = submit-on-source-submit + backfill; NOT DONE.
2. **No cancel/amend reversal** for stock/invoice flows. Cancelling orphans ledger rows.
3. **Idempotency is check-then-insert** (race-prone); no DB unique index, no locks.
4. **`bench migrate` reimports fixtures** — wiped unexported DB work twice this session.
   Standing rule: DB change → verify → export → commit; never migrate mid-flow.
5. **Kanban JS (1295 lines, global)** — MutationObserver + per-card requests; works but
   heavy/fragile; scoped rewrite DEFERRED.
6. **Totals math is client-side only** (orders/invoices); API/import bypasses it.
7. **Permissions added but never login-tested** as counter roles.
8. **6 early draft sample bills use realistic names WITHOUT `_sample_data`** and their
   `remarks` were silently dropped (verified: Sales Invoice has NO remarks column —
   verify before relying on remarks anywhere; Purchase Invoice remarks NOT VERIFIED).
   Identifiable only by names/dates (JSI-2026-09-24-02…07).
9. **Settings singles row empty** (`shop_name` reads blank until first UI save).
10. **Workflow `Jewellery Order Workflow` inactive** + orphan `workflow_state` field.
11. **Silver Metal Rate 240/g entered; 18K rate missing** (owner to provide; ~11700 est. NOT entered).
12. **Sample Bank reads −₹20,000** (samples overpaid — data artifact, math correct).
13. **No returns flow, no e-invoice/TCS, no FIFO auto, no fresh-install proof.**
14. **Frappe/ERPNext on `develop` (17.0.0-dev)** — upstream churn risk; pin before go-live.

---

## 11. THINGS THAT MUST NOT BE CHANGED (owner constraints)

- Never modify Frappe/ERPNext core files. Never push to GitHub (backup-only remote).
- Do not replace custom jewellery logic with standard ERPNext stock/GL/BOM without
  explicit owner request (long-term direction, not license).
- Order statuses frozen; submit-only-when-Delivered; no per-item delivery status in V1.
- Delivered NET weight is the only stock/settlement weight; never fall back to gross.
- Customer and worker books stay separate; worker data never on customer prints.
- Visit lumps never split across items. Cash never auto-converts to gold.
- History rows are never rewritten (rates, assays, estimates, settlements append-only).
- Do not delete data to simplify implementation; test data deletes only when owner-approved.
- Preserve working kanban tooltip/status behavior; V1 simplicity over completeness.
- Verify DB state after every mutating step; never trust a success message alone.

---

## 12. DEFERRED WORK

**Priority 1:** FIFO auto-allocation (+ realized vs provisional profit); server-side mirrors
of order/invoice totals; stock-transaction submit flow + backfill; cancel/amend reversals.
**Priority 2:** Sales/purchase returns; e-invoice + TCS; GSTR-1 filing format; barcode
scan-to-bill; rate-lock at bill start; login-as-role permission proof; Settings defaults
save; 18K rate entry (owner); legal-name confirmation (owner).
**Later:** Dashboard charts polish; low-stock thresholds per item; kanban rewrite;
fresh-install proof (needs DB-root coordination); intra-day rate feed.
**Deferred (explicit):** savings schemes/chit (V2); diamonds/4Cs; multi-branch; RFID;
PMLA automation; manufacturing BOM; Tally sync.
**Not decided:** which account heads for making/hallmark income; UPI mode-of-payment
master additions (used Cash for UPI/Card entries — "Wire Transfer"/"Credit Card" used
for bank legs); village-wise analytics.

---

## 13. NEXT AGENT INSTRUCTIONS

1. Read this file fully, then `git -C apps/jewellery_management status` and
   `git log --oneline -5` — expect clean tree at `df135a2`.
2. Change nothing until you reproduce: `bench --site library.local execute`
   dashboard `get_data` smoke test (§7) and confirm fixtures match DB for anything
   you plan to touch.
3. Inspect first: `jewellery_management/hooks.py`,
   `.../jewellery_management/{stock_hooks,settlement,old_gold,dashboard}.py`,
   `fixtures/doctype.json` (source of truth for schema), open `Page: jewellery-dashboard`.
4. Never run `migrate` with unexported DB changes (§10.4). Never push.
5. Continue from §12 Priority 1 unless the owner redirects.

---

## 14. GIT STATE

- Current branch: `develop`
- Current commit: `df135a2` ("fix: dashboard refresh on return + working cash/bank")
- Remote: `https://github.com/ShyberDev/jewellery_management.git` (push NOT performed; remote state NOT VERIFIED)
- Working tree: CLEAN except this untracked file:
- Untracked files: `docs/AI_HANDOFF.md` (app-relative; this file — DO NOT COMMIT unless owner asks)
- Modified files: none. Staged files: none. Stash: empty (verified `stash list` → no output).

---

## 15. RESOURCE USAGE / EXTERNAL RESOURCES

- **Agent model:** per session instructions, "Muse Spark 1.3 Free" via provider
  `opencode` — stated as given; underlying infrastructure NOT VERIFIED by agent.
- **Subagents:** requested 3× `explore` subagents at session start; all failed
  (provider free-tier restriction); all inspection done directly. No other agents/MCP used.
- **Websites consulted:** one commodity websearch survey of jewellery-ERP vendors
  (Nexao, JSoft ERP, ERIONT, SourceForge jewellery vertical, APPIT/FlowSense,
  SthirApp, GehnaERP) for the competitor feature map only. No code, docs, or repos
  consumed. Frappe/ERPNext official docs: NOT consulted (all framework behavior
  verified from local source under `apps/frappe`, `apps/erpnext`).
- **GitHub repos consulted:** none (remote is the project's own backup repo; never fetched).
- **External libraries/packages/APIs:** none installed; `node --check` (system node
  v24.18.0) and `curl` used read-only. No database GUI tools (bench CLI only).

---

## 16. FINAL HANDOFF SUMMARY

## CURRENT PROJECT STATE
Working single-shop Jewellery ERP: orders→workers→settlement, purchases/sales with
GST incl. 0%, custom weight-based stock ledger, old-gold two-leg flow, HUID registry,
repairs, rates, roles, workspace, home tile + live dashboard. 24 custom DocTypes,
5 reports, all fixture-versioned on `develop` @ `df135a2`, tree clean, sample data
in place, ERP core untouched, nothing pushed.

## LAST COMPLETED TASK
Home tile + dashboard (with module fix, refresh-on-return fix, cash/bank fix),
today's rates (24K 15600 / 22K 14500 / Silver 240 + Silver 999 master), 10+10+10+10
sample bills/orders/items/stock plus worker/old-gold/repair samples and 10 ERPNext
Payment Entries lighting up Cash ₹65k / Bank −₹20k.

## CURRENT UNFINISHED TASK
Nothing in-flight; all committed except this handoff file. Verification debt (§7 table
"NOT performed") and §12 Priority 1 (FIFO auto, server mirrors, submit flow, reversals).

## NEXT ACTION
Pick the top of §12 Priority 1 (recommend: FIFO auto-allocation + realized-profit,
it unlocks the settlement loop the owner asked for first) after reproducing the
dashboard smoke test.

## IMPORTANT WARNINGS
- `bench migrate` reimports fixtures and SILENTLY reverts unexported DB work.
- Stock/purchase/sale DocTypes live under module `Jewellery` (Frappe-owned), NOT the
  app's module — do not "fix" without a plan; fixtures are the truth.
- 6 early draft bills lack `_sample_data` markers (remarks column doesn't exist).
- Never push; never touch `apps/frappe`, `apps/erpnext`, `apps/library_management`.
