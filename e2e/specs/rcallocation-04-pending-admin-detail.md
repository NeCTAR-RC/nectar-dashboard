# rcallocation 04: Pending Requests and admin detail

## Application Overview

Regression baseline for the Pending Requests list (/allocation/requests/) and the admin detail page (/allocation/requests/view/<id>/) of the Allocations dashboard (rcallocation) on http://dashboard-s.rcdev.nectar.org.au:8000, ahead of a refactor that intends no UI change. Observed live on 2026-10-30 as the pt.openrc user (allocation admin). All scenarios are read-only: GET pages only, nothing is submitted. Suite 05 covers approve, decline, edit and notes submissions. This suite does not repeat suite 01 basics (column set, URL access); it goes deeper on row content, ordering, urgency, filtering, detail sections and buttons.

GLOBAL RULES FOR EXECUTION
- Never navigate to, click or open any URL outside http://dashboard-s.rcdev.nectar.org.au:8000. 'Related tickets' (Freshdesk) and 'Project usage' (Grafana) are checked by reading href and target only. Do NOT click them: on dev they render as relative hrefs starting with 'None' (see discrepancy 1), so a click would navigate to a bogus dashboard-s path.
- Do not click 'Review & Approve', 'Decline with Reason', 'Approve changes', 'Decline changes' or 'Add/edit admin notes' and then submit anything. Reading hrefs is fine.
- Keep the seed's blocks (challenges.cloudflare.com, ardc.edu.au, survey.rc.nectar.org.au), dialog auto-accept and 15s default timeout. If the session expires, rerun the seed.
- The seed leaves /allocation/ open. Navigating away raises a beforeunload dialog. The seed auto-accepts it, but the first page.goto may time out while it is handled. Retry the navigation once.
- In scripts pass { timeout: 10000 } to every action and wait. Use page.evaluate for DOM reads. Use pressSequentially (with a timeout) for the filter box, because locator.fill alone does not trigger filtering.
- Do not load /allocation/approved_requests/ with a short timeout. It lists about 1600 rows and its page.goto timed out at 10s during exploration. To test the 'Back to Approved Requests' button, set the Referer header on the detail request instead (see 4.20).
- A survey modal may overlay pages. Dismiss it with 'Not right now'.

TEST DATA (dev data drifts; re-check if a step fails)
- Pending list on 2026-10-30: 33 rows (24 E, 9 X; no N). Brief expected 31 plus the two pwtest rows. Confirmed.
- E records: 137133 'qui' / 'Assimilated composite help-desk' (contact rhysdawson@example.com, previous approver graemejohnson@nicholls-akhtar.org, Last Updated March 1, 2024); 137145; 145086; 144561; pwtest rows 152181 ('pwtest-valid' / 'PW validation test') and 152182 ('pwtest-202610301345-b' / 'PW warnings flow test'), both contact sorrison@gmail.com, Last Updated Oct. 30, 2026, no previous approver.
- X records: 135408 ('eum' / 'Automated composite intranet', site Intersect, National True, approver martinstephen@brown.com), 58677, 62718, 84989, 38655, 145272, 123439, 135339, 129250 ('labore' / 'Universal asynchronous strategy', site TPAC, National False, Expiry Sept. 26, 2024).
- Admin notes set on X records: 135408, 58677, 84989, 38655, 145272, 135339. No E record has notes (they render 'None').
- Pending order (by submit_date), all 33 IDs: 137133, 137145, 145086, 144561, 145986, 135408, 58677, 147462, 62718, 146607, 149088, 150183, 150633, 84989, 38655, 145272, 151164, 151473, 123439, 151521, 151599, 151632, 151638, 151713, 151878, 151884, 135339, 151554, 152142, 152145, 129250, 152181, 152182.
- A record: 152179 (own allocation, 'gdfgdfgdf' / 'fsdgfdsgdsfg', site QCIF, no project_id).
- History record: 146946 (status A, history of 135408, 'Assimilated responsive archive'). History table of 135408 has 8 rows.
- No Pending record has Special approval set (all 33 scanned). No N or J record is reachable from the Pending list.

OBSERVED DISCREPANCIES FROM THE BRIEF (live results are the baseline)
1. HORIZON_CONFIG.FRESHDESK_SEARCH_URL and GRAFANA_PROJECT_USAGE_URL are unset on dev. 'Related tickets' renders href 'None&q[]=tags%3A%5B%22allocation-<primary_id>%22%5D' and 'Project usage' renders 'None&var-project_id=<project_id>'. Both have target='_blank'. On a configured deployment the href will start with the real Freshdesk or Grafana base URL. Compare only the suffix on dev.
2. The Pending list shows 33 rows, not 31 (the two pwtest rows are the difference). The pwtest rows show urgency '(New)', a value not seen in suite 01 (which saw only '(Overdue)' and '(Danger)').
3. The admin detail on a history record keeps the 'Allocation admin notes' text and the NOTE block; only the 'Add/edit admin notes' button is absent.
4. On a history record, 'Related tickets' uses the PARENT's id (146946 shows allocation-135408), because the tag uses primary_id.
5. The NOTE block says 'See Related Tickets' but the button label is 'Related tickets'.
6. Duplicate DOM ids on the detail page: id='allocation_reject_view' is on both 'Add/edit admin notes' and 'Decline changes' / 'Decline with Reason'; id='allocation_accept_view' is on both 'Approve changes' and 'Review & Approve' (only one of each pair appears per state, but the notes button shares the reject id). Selectors by id are ambiguous. Use text or href.
7. Code bug (derived): get_highlight_attribute lists urgency.OVERDUE in the pending_warn_level_3 branch, so the later 'elif data == OVERDUE' branch (pending_warn_level_1) is unreachable. Only visible for unparenthesised cells, which were never observed.
8. Back to History on a history record links to that record's own history (/allocation/requests/view/146946/history), not the parent's history it was reached from (/allocation/requests/view/135408/history).
9. The Approved Requests list (about 1600 rows) timed out at 10s on page.goto. It is slow, not broken. Not retried beyond once.

## Test Scenarios

### 1. Pending Requests and admin detail

**Seed:** `/home/sam/projects/nectar/nectar-dashboard/seed.spec.ts`

#### 1.1. 4.1 Pending list contains 33 rows including the pwtest requests

**File:** `tests/rcallocation/04-pending-admin-detail/pending-row-count.spec.ts`

**Steps:**
  1. [verified live] Run seed.spec.ts, then navigate to /allocation/requests/ (retry once if the beforeunload dialog interrupts).
    - expect: URL is /allocation/requests/; title 'Allocation Requests - Nectar Dashboard'
    - expect: Table #datatableoptions has 33 body rows; footer reads 'Displaying 33 items'
    - expect: 24 rows have State E and 9 have State X; no N, A or J rows
  2. Find the rows whose Name link is /allocation/requests/view/152181/ and /allocation/requests/view/152182/.
    - expect: Both rows exist, State E, and are the LAST two rows in the table
    - expect: 152181 Name cell: 'pwtest-valid' with subtitle 'PW validation test'; 152182: 'pwtest-202610301345-b' with subtitle 'PW warnings flow test'
    - expect: Both: Current Associated Site '-', National 'False', Previous Approver empty, Contact 'sorrison@gmail.com', Last Updated 'Oct. 30, 2026', Expiry Date '-', Urgency '(New)'

#### 1.2. 4.2 Pending list is ordered by submit date (first and last rows)

**File:** `tests/rcallocation/04-pending-admin-detail/pending-order.spec.ts`

**Steps:**
  1. [verified live] On /allocation/requests/ without touching any column header, read the Name link ID of every row in DOM order.
    - expect: First four: 137133, 137145, 145086, 144561 (Last Updated March 1, 2024; March 1, 2024; April 10, 2024; May 6, 2024)
    - expect: Fifth to eighth: 145986, 135408, 58677, 147462
    - expect: Last four: 152145 (E, Sept. 30, 2024), 129250 (X, Sept. 30, 2024), 152181, 152182
    - expect: Full order is 137133, 137145, 145086, 144561, 145986, 135408, 58677, 147462, 62718, 146607, 149088, 150183, 150633, 84989, 38655, 145272, 151164, 151473, 123439, 151521, 151599, 151632, 151638, 151713, 151878, 151884, 135339, 151554, 152142, 152145, 129250, 152181, 152182
    - expect: E and X rows are interleaved (X is not grouped); the view orders by submit_date, while the Last Updated column shows modified_time, so Last Updated is not strictly monotonic

#### 1.3. 4.3 Pending list cell content for sample E and X rows

**File:** `tests/rcallocation/04-pending-admin-detail/pending-row-cells.spec.ts`

**Steps:**
  1. [verified live] Read the ten cells of rows 137133, 135408 and 129250.
    - expect: 137133: 'E' | 'qui Assimilated composite help-desk' | '-' | 'False' | 'graemejohnson@nicholls-akhtar.org' | 'rhysdawson@example.com' | 'March 1, 2024' | '-' | '(Overdue)' | 'Edit request'
    - expect: 135408: 'X' | 'eum Automated composite intranet' | 'Intersect' | 'True' | 'martinstephen@brown.com' | contact | date | expiry | '(Danger)' | 'Edit request'
    - expect: 129250: 'X' | 'labore Universal asynchronous strategy' | 'TPAC' | 'False' | 'keith28@kaur-adams.com' | 'collinslawrence@example.net' | 'Sept. 30, 2024' | 'Sept. 26, 2024' | '(Danger)' | 'Edit request'
    - expect: Dates render in Django short format ('March 1, 2024', 'Aug. 11, 2024', 'Sept. 30, 2024'); an empty site or expiry date renders '-'
    - expect: Header classes: State has 'text-center'; Actions has 'actions_column' and 'sorter-false'; all other headers are 'sortable normal_column'

#### 1.4. 4.4 Urgency value distribution on the Pending list

**File:** `tests/rcallocation/04-pending-admin-detail/pending-urgency-distribution.spec.ts`

**Steps:**
  1. [verified live] Count Urgency cell text grouped by State.
    - expect: E '(Overdue)': 22 rows (every E row last modified more than 21 days ago)
    - expect: E '(New)': 2 rows (152181 and 152182, modified today)
    - expect: X '(Danger)': 9 rows
    - expect: Every one of the 33 cells is wrapped in parentheses, so none carries a pending_warn_level_N class
    - expect: No '(Warning)', '(Attention)', '(Expired)', '(Stopped)', '(Archived)', '(Unknown)' or unparenthesised value is present
  2. Click the 'Urgency' header once, read the first two rows, click again and read the first two rows.
    - expect: First click (ascending): first two rows are 135408 and 58677, both '(Danger)'
    - expect: Second click (descending): first two rows are 137133 and 137145, both '(Overdue)'
    - expect: Sort is client-side (URL unchanged, footer still 'Displaying 33 items')

#### 1.5. 4.5 urgency.py mapping rules

**File:** `tests/rcallocation/04-pending-admin-detail/urgency-mapping.spec.ts`

**Steps:**
  1. [derived from code; urgency.py, only (Overdue), (Danger) and (New) confirmed live] Review the get_urgency rules, ideally as a unit test over get_urgency(allocation) with controlled modified_time and end_date.
    - expect: Wait time from modified_time: more than 21 days ago is 'Overdue'; more than 14 days is 'Warning'; more than 7 days is 'Attention'; otherwise 'New'
    - expect: Expiry state applies only when end_date is set and before today. Then the clock-stop amendment is the first UPDATE_PENDING record after the last approved child. No amendment found gives 'Unknown'. Clock stop more than 150 days (30*5) ago gives 'Danger'; after end_date + 28 days gives 'Archived'; after end_date + 14 days gives 'Stopped'; after end_date gives 'Expired'; otherwise expiry is 'None'
    - expect: get_urgency returns the expiry state when it is not 'None', otherwise the wait-time state (expiry takes precedence)
    - expect: Live cross-check: X rows with past end dates and an old amendment show 'Danger'; E rows older than 21 days show 'Overdue'; today's rows show 'New'
    - expect: Parentheses: the UrgencyColumn wraps the value in '(...)' unless the approver's interested sites intersect the approver sites (previous approver site, contact organisation site, or the ARDC site as fallback). For pt.openrc no row intersects, so all 33 are parenthesised

#### 1.6. 4.6 Urgency cell CSS class mapping

**File:** `tests/rcallocation/04-pending-admin-detail/urgency-css.spec.ts`

**Steps:**
  1. [derived from code; allocation/tables.py get_highlight_attribute] Review the class rules. Unparenthesised cells need an approver whose site matches a pending request; not reproduced live.
    - expect: Value starting with '(' gets no class (attribute dict empty). Live: all cells have only the classes 'sortable' and 'normal_column', in either order (Horizon builds cell classes from a set, so the order varies between server processes)
    - expect: 'Danger' maps to pending_warn_level_4
    - expect: 'Stopped', 'Archived', 'Expired', 'Overdue', 'Unknown' map to pending_warn_level_3
    - expect: 'Warning' maps to pending_warn_level_2
    - expect: 'Attention' and 'New' map to pending_warn_level_0
    - expect: pending_warn_level_1 is unreachable (the Overdue test in the level_3 branch wins). Treat as existing behaviour; do not 'fix' in the refactor without a decision

#### 1.7. 4.7 Pending row actions and Name links

**File:** `tests/rcallocation/04-pending-admin-detail/pending-row-actions.spec.ts`

**Steps:**
  1. [verified live] For rows 137133, 135408, 152182 read the Name link and the Actions cell links.
    - expect: Name link: /allocation/requests/view/<id>/ (137133, 135408, 152182)
    - expect: Primary action 'Edit request': /allocation/requests/edit_request/<id>/
    - expect: Dropdown toggle link href '#' (empty text); dropdown item 'View history': /allocation/requests/view/<id>/history
    - expect: All 33 rows have exactly this set (Edit request, then View history); no row lacks Edit request, including X rows
    - expect: The table has no table-level action buttons other than the filter (no 'Request a new allocation' button on this list)

#### 1.8. 4.8 Pending filter is client-side and matches any column

**File:** `tests/rcallocation/04-pending-admin-detail/pending-filter.spec.ts`

**Steps:**
  1. [verified live] Focus input[name='DataTableOptions__filter__q'] (placeholder 'Filter'). For each term, clear it (fill '' then Backspace), then pressSequentially the term with a 30ms delay and wait 400ms.
    - expect: 'pwtest' leaves 2 visible rows (152181, 152182)
    - expect: '(New)' leaves the same 2 rows (the Urgency text is searchable)
    - expect: '(Danger)' leaves 9 rows (all X)
    - expect: 'Overdue' leaves 22 rows (all E, excluding the pwtest rows)
    - expect: 'Intersect' leaves 3 rows (135408 and two other X rows; matches the Site column)
    - expect: 'TPAC' leaves 1 row (129250)
    - expect: 'zzzzno' leaves no data rows; the body shows a single row 'No items to display.'
    - expect: The URL stays /allocation/requests/ throughout and the footer text remains 'Displaying 33 items'
  2. Clear the field and press Backspace.
    - expect: All 33 rows are visible again

#### 1.9. 4.9 Pending list has no pagination

**File:** `tests/rcallocation/04-pending-admin-detail/pending-no-pagination.spec.ts`

**Steps:**
  1. [verified live] On /allocation/requests/ search the DOM for .pagination, a[rel=next] and any 'Next' or 'Prev' controls.
    - expect: None exist (0 matches); all 33 rows render on one page
    - expect: Footer reads 'Displaying 33 items' with no page links

#### 1.10. 4.10 Admin detail for submitted record 152182 (E)

**File:** `tests/rcallocation/04-pending-admin-detail/detail-submitted-152182.spec.ts`

**Steps:**
  1. [verified live] Navigate to /allocation/requests/view/152182/ and read the headings.
    - expect: HTTP 200; title 'View allocation request - Nectar Dashboard'; h1 'View Allocation Request'; h2 'PW warnings flow test'
    - expect: h3 sections in order: Requested Resources, Approved Resources (at the time of this record), Use Case, Usage Patterns, Additional Location Requirements, Usage Types, Usage Information, Fields of Research (FOR), Supported Organisations, Chief Investigator, Research Grant Information, Publication/Output and Impact, Allocation admin notes
    - expect: No 'Reviewer Comment' and no 'Special approval reasons' heading
    - expect: h4 includes 'Estimated number of users who will directly access the instances', 'Estimated number of research services or platforms to be hosted using this allocation', 'Estimated total number of unique active users of these services', 'Data Sensitivity Information', and the ARDC and NCRIS support headings; no 'Benefits of Nectar' or 'Research Impact' (new request, cannot have publications)
  2. Read the header tables.
    - expect: Left table: Contact email sorrison@gmail.com; Submit date 'Oct. 30, 2026, 3:49 a.m.'; Last updated same; Start date 'None'; End date 'None'; Estimated project duration '12 month(s)'; Convert trial? 'No'
    - expect: Right table: State 'Submitted' (row class 'danger'); no Approver row; Project Identifier 'pwtest-202610301345-b'; Project ID '(Project not linked)'; Associated Site 'None'; National funded 'no'; Provisioned 'no'
  3. Read the Requested Resources table.
    - expect: 18 rows in this order: 'Bundle Details' = 'Custom'; Compute Service Limits Virtual Cores NeCTAR 256 VCPUs; Compute Service Limits RAM NeCTAR 640 GB; Compute Service Limits Instances NeCTAR 160 Servers; Compute Service Limits Huge RAM Flavors NeCTAR Enabled; Database Service Database RAM NeCTAR 64 GB; Database Service Storage NeCTAR 1000 GB; Reservation Service Reservations NeCTAR 8 Reservations; Reservation Service Duration NeCTAR 400 Days; Reservation Service GPU Flavors NeCTAR Enabled; Reservation Service Huge RAM Flavors NeCTAR Enabled; Advanced Networking Routers NeCTAR 8 Routers; Advanced Networking Floating IPs NeCTAR 16 Floating IPs; Advanced Networking Load Balancers NeCTAR 16 Load Balancers; Advanced Networking Security Groups NeCTAR 90 Security Groups; Object Store Storage NeCTAR 3000 GB; Service Units Budget NeCTAR 16000 SUs; Object Store Storage Pawsey (WA) 3000 GB
    - expect: Boolean resources show 'Enabled' (no unit); other rows show '<requested_quota> <unit>'; the zone shows as a label after the resource name
    - expect: Right column heading is 'Approved Resources (at the time of this record)' with a single row 'No allocation.' (no prior approval)
    - expect: Data Sensitivity subheading is 'Current Values:' (no approved record), single column

#### 1.11. 4.11 Admin detail for update-requested record 135408 (X) with prior approval context

**File:** `tests/rcallocation/04-pending-admin-detail/detail-update-135408.spec.ts`

**Steps:**
  1. [verified live] Navigate to /allocation/requests/view/135408/.
    - expect: Title 'View allocation request - Nectar Dashboard'; h1 'View Allocation Request'; h2 'Automated composite intranet'
    - expect: h3 in order: Requested Resources, Current Resources, Use Case, Usage Patterns, Additional Location Requirements, Usage Types, Usage Information, Fields of Research (FOR), Supported Organisations, Chief Investigator, Research Grant Information, Publication/Output and Impact, Reviewer Comment, Allocation admin notes
    - expect: Reviewer Comment block text 'dolorem'
    - expect: h4 includes 'Estimated Number of Users', 'Benefits of Nectar', 'Research Impact' (publications allowed); no 'Special approval reasons'
  2. Read the header tables.
    - expect: Left: Contact email xwoodward@example.net; Submit date 'May 28, 2024, 11:04 a.m.'; Last updated same; Start date 'March 15, 2024'; End date 'June 15, 2024'; Estimated project duration '3 month(s)'; Convert trial? 'No'
    - expect: Right: State 'Update requested'; Approver 'martinstephen@brown.com'; Project Identifier 'eum'; Project ID '14813f18dc364a4c965aa7399a08614c'; Associated Site 'Intersect'; National funded 'yes'; Provisioned 'no'
  3. Compare the Requested Resources (left) and Current Resources (right) tables.
    - expect: Requested (9 rows): Bundle Custom; Volume Service Storage Monash (VIC) 1000 GB; Compute Service Limits Virtual Cores NeCTAR 200 VCPUs; Compute Service Limits Instances NeCTAR 2 Servers; Reservation Service Reservations NeCTAR 3 Reservations; Reservation Service Duration NeCTAR 14 Days; Reservation Service GPU Flavors NeCTAR Enabled; Service Units Budget NeCTAR 12000 SUs; Volume Service Storage QRIScloud 100 GB
    - expect: Current (8 rows, heading 'Current Resources' because the last approved record is the current approval): Bundle Custom; Volume Monash (VIC) 1000 GB; Virtual Cores NeCTAR 120 VCPUs; Instances NeCTAR 10 Servers; Reservations 3; Duration 14 Days; GPU Flavors Enabled; Service Units Budget NeCTAR 25000 SUs
    - expect: Differences visible: VCPUs 200 vs 120, Instances 2 vs 10, SUs 12000 vs 25000, and Volume QRIScloud 100 GB only in Requested
    - expect: Current Resources equals the Approved Resources of history record 146946 (see 4.19)
    - expect: Data Sensitivity subheading is 'Requested Changes:' (an approved record exists and the record is not active); only one column shows because sensitive-data fields match the approved record

#### 1.12. 4.12 Admin detail for approved record 152179 (A)

**File:** `tests/rcallocation/04-pending-admin-detail/detail-approved-152179.spec.ts`

**Steps:**
  1. [verified live] Navigate to /allocation/requests/view/152179/.
    - expect: Title 'View allocation request - Nectar Dashboard'; h1 'View Allocation Request'; h2 'fsdgfdsgdsfg'
    - expect: h3 in order: Current Resources, Use Case, Usage Patterns, Additional Location Requirements, Usage Types, Usage Information, Fields of Research (FOR), Supported Organisations, Chief Investigator, Research Grant Information, Publication/Output and Impact, Allocation admin notes
    - expect: NO 'Requested Resources' section (rendered only for non-active records); no 'Reviewer Comment'; no 'Special approval reasons'
    - expect: Current Resources table: Bundle Details 'Powerful'; Object Store Storage NeCTAR 3000 GB; Object Store Storage Pawsey (WA) 3000 GB
    - expect: Right table: State 'Approved' (row class 'success'); Approver 'sorrison@gmail.com'; Project Identifier 'gdfgdfgdf'; Project ID '(Project not linked)'; Associated Site 'QCIF'; National funded 'yes'; Provisioned 'no'
    - expect: Left table: Contact email sorrison@gmail.com; Submit date 'April 30, 2026, 6 a.m.'; Last updated 'April 30, 2026, 6:01 a.m.'; Start date 'None'; End date 'None'; Estimated project duration '12 month(s)'; Convert trial? 'No'
    - expect: Usage Information shows the three 'directly access / services / unique active users' h4s plus the three 'past year' h4s and 'Are the above figures measured or estimated?' (can_have_publications is true); Benefits of Nectar and Research Impact are present

#### 1.13. 4.13 Action buttons by state across all Pending records

**File:** `tests/rcallocation/04-pending-admin-detail/detail-buttons-by-state.spec.ts`

**Steps:**
  1. [verified live] For each of the 33 Pending IDs, GET /allocation/requests/view/<id>/ (same-origin fetch is fine) and read the text of every a.btn inside .allocation.
    - expect: 24 E records (including 137133, 152181, 152182): 'Add/edit admin notes' | 'Review & Approve' | 'Decline with Reason' | 'View History' | 'Related tickets'; no 'Project usage' (no project_id); right-hand headings Requested Resources / Approved Resources (at the time of this record)
    - expect: 9 X records (135408, 58677, 62718, 84989, 38655, 145272, 123439, 135339, 129250): 'Add/edit admin notes' | 'Approve changes' | 'Decline changes' | 'View History' | 'Related tickets' | 'Project usage'; headings Requested Resources / Current Resources
    - expect: E record hrefs (152182): approve /allocation/requests/approve_request/152182/ (btn btn-success btn-lg, id allocation_accept_view); decline /allocation/requests/reject_request/152182/ (btn btn-danger btn-lg, id allocation_reject_view)
    - expect: X record hrefs (135408): /allocation/requests/approve_change_request/135408/ (btn-success btn-lg) and /allocation/requests/reject_request/135408/ (btn-danger btn-lg)
    - expect: Always: 'View History' /allocation/requests/view/<id>/history (btn btn-default btn-lg); 'Add/edit admin notes' /allocation/requests/edit_notes/<id>/ (btn btn-default, not btn-lg)
    - expect: Button order inside the actions row is: Approve changes, Decline changes, Review & Approve, Decline with Reason, View History, Related tickets, Project usage (only applicable ones render)

#### 1.14. 4.14 Related tickets and Project usage links (href and target only)

**File:** `tests/rcallocation/04-pending-admin-detail/detail-external-links.spec.ts`

**Steps:**
  1. [verified live] On /allocation/requests/view/135408/ read href and target of #allocation_tickets and #allocation_project_usage with getAttribute. DO NOT CLICK.
    - expect: Related tickets: id 'allocation_tickets', target '_blank', href (dev) 'None&q[]=tags%3A%5B%22allocation-135408%22%5D'
    - expect: Project usage: id 'allocation_project_usage', target '_blank', href (dev) 'None&var-project_id=14813f18dc364a4c965aa7399a08614c'
    - expect: On a configured deployment the href is '<FRESHDESK_SEARCH_URL>&q[]=tags%3A%5B%22allocation-<primary_id>%22%5D' and '<GRAFANA_PROJECT_USAGE_URL>&var-project_id=<project_id>'; assert only the suffix here
  2. Repeat for 152182 (E) and 152179 (A).
    - expect: 152182: Related tickets suffix 'allocation-152182'; NO Project usage button (Project ID '(Project not linked)')
    - expect: 152179: Related tickets suffix 'allocation-152179'; NO Project usage button (no project_id)

#### 1.15. 4.15 Allocation admin notes block and edit button

**File:** `tests/rcallocation/04-pending-admin-detail/detail-admin-notes.spec.ts`

**Steps:**
  1. [verified live] Open /allocation/requests/view/135408/ and read the 'Allocation admin notes' block.
    - expect: h3 'Allocation admin notes' followed by a paragraph 'pending approval from UNSW, 20->120 vCPU'
    - expect: Link 'Add/edit admin notes' (class 'btn btn-default', id 'allocation_reject_view') with href /allocation/requests/edit_notes/135408/, shown below the text
  2. Open /allocation/requests/view/152182/ and /allocation/requests/view/152179/.
    - expect: The paragraph shows the literal text 'None' (empty notes render as None)
    - expect: 'Add/edit admin notes' is present with href /allocation/requests/edit_notes/<id>/
  3. Open the other X records with notes: 58677, 84989, 38655, 145272, 135339 (all read-only).
    - expect: 58677: 'waiting for uts approval'
    - expect: 84989: 'Asked Simon Forsayeth to review as asking for volume storage at Swinburne and astronomy project. Does meet national merit criteria.'
    - expect: 38655: multi-line, starts 'JR (24.06.2022) Contacted TM, asked why vCPU was reduced...' and ends '...so Intersect needs to approve this please'
    - expect: 145272: 'Sergio approved 1TB of volume storage - 2004-04-19'
    - expect: 135339: 'changed volume quota from Melbourne Uni to Intersect'
    - expect: Do not click 'Add/edit admin notes' and submit; GET of the edit_notes page is optional and covered by suite 01 (1.13)

#### 1.16. 4.16 Special approval reasons block (shown only when set)

**File:** `tests/rcallocation/04-pending-admin-detail/detail-special-approval.spec.ts`

**Steps:**
  1. [verified live: absent on all 33 Pending records and on 152179, 146946] Confirm no h3 'Special approval reasons' on 152182, 135408, 152179.
    - expect: No 'Special approval reasons' heading and no extra row above 'Allocation admin notes' on those pages
  2. [derived from code; no record with special_approval was found in the Pending list, so this is NOT verified live] If a record with special_approval set is found (for example via a seeded or approved record), open its detail page. Do not create one in this suite.
    - expect: A row with h3 'Special approval reasons' and a paragraph containing the special_approval text appears BEFORE 'Allocation admin notes' (extra_details block, first row, col-md-12)
    - expect: With special_approval empty the whole row is omitted

#### 1.17. 4.17 Freshdesk NOTE text on the admin detail

**File:** `tests/rcallocation/04-pending-admin-detail/detail-freshdesk-note.spec.ts`

**Steps:**
  1. [verified live] On /allocation/requests/view/152182/, 135408 and 152179 read the block containing the span.label.label-info 'NOTE'.
    - expect: Text: 'NOTE To start a conversation with the user about their allocation request, first click "See Related Tickets" to see Freshdesk tickets tagged with this allocation. Next choose one from the list, change its status to "Open", change its group to "Allocations" and assign it to yourself. When you finish the conversation, please remember to "Resolve" the ticket in the normal way.'
    - expect: Second paragraph: 'If the "See Related Tickets" page gets stuck with a "spinner", try refreshing the page. (We think it is a Freshdesk bug.)'
    - expect: The text says 'See Related Tickets' but the button label is 'Related tickets' (existing mismatch)
    - expect: The block is in a col-md-6 below the notes row and appears on E, X, A and history records alike

#### 1.18. 4.18 Prior approval context rules (which approved record is shown)

**File:** `tests/rcallocation/04-pending-admin-detail/detail-prior-approval-context.spec.ts`

**Steps:**
  1. [verified live for 152182, 135408, 152179, 146946; remaining branches derived from code, views.py AllocationDetailView.get_context_data] Review the right-hand resources heading and table per record type.
    - expect: Active record (A) that is not history, e.g. 152179: shows itself, heading 'Current Resources'
    - expect: Active history record (A with a parent), e.g. 146946: shows itself, heading 'Approved Resources (at the time of this record)'
    - expect: Non-approved record with no approved children, e.g. 152182: heading 'Approved Resources (at the time of this record)', single row 'No allocation.'
    - expect: Non-approved record with approved children, e.g. 135408: shows the latest approved child whose modified_time is earlier than the record's own; heading 'Current Resources' only when that approved record is the first (newest) approved child, otherwise 'Approved Resources (at the time of this record)'. Live 135408 shows 'Current Resources' with 120 VCPUs / 10 Servers / 25000 SUs
    - expect: Requested Resources (left) appears only when the record is not active (E, X, N, J, R, D); the right column uses the approved record's quota, the left uses requested_quota

#### 1.19. 4.19 History record detail (146946) differs from the current record

**File:** `tests/rcallocation/04-pending-admin-detail/detail-history-146946.spec.ts`

**Steps:**
  1. [verified live] Open /allocation/requests/view/146946/ and compare with 135408.
    - expect: HTTP 200; title 'View allocation request - Nectar Dashboard'; h2 'Assimilated responsive archive'
    - expect: NO 'Add/edit admin notes' button; the notes block is still present with text 'pending approval from UNSW, 20->120 vCPU'
    - expect: Buttons present: 'View History' (/allocation/requests/view/146946/history), 'Related tickets' (suffix allocation-135408, the PARENT id), 'Project usage' (project_id 14813f18dc364a4c965aa7399a08614c). No approve or decline buttons
    - expect: h3: Approved Resources (at the time of this record), Use Case, Usage Patterns, Additional Location Requirements, Usage Types, Usage Information, Fields of Research (FOR), Supported Organisations, Chief Investigator, Research Grant Information, Publication/Output and Impact, Reviewer Comment, Allocation admin notes. No 'Requested Resources'
    - expect: Reviewer Comment 'officiis'; left table: Contact email jamespauline@example.org; Submit date 'Feb. 28, 2024, 4:51 a.m.'; Last updated 'March 15, 2024, 2:15 a.m.'; Start 'March 15, 2024'; End 'June 15, 2024'; 3 month(s); Convert trial? No
    - expect: Right table: State 'Approved' (row class success); Approver 'gillirene@harding.net'; Project Identifier 'dolore'; Associated Site 'Intersect'; National funded 'yes'; Provisioned 'yes'
    - expect: Approved Resources: Bundle Custom; Volume Monash (VIC) 1000 GB; Virtual Cores NeCTAR 120 VCPUs; Instances 10 Servers; Reservations 3; Duration 14 Days; GPU Flavors Enabled; Service Units Budget NeCTAR 25000 SUs
    - expect: Data Sensitivity subheading 'Current Values:'

#### 1.20. 4.20 Back button depends on the Referer

**File:** `tests/rcallocation/04-pending-admin-detail/detail-back-button.spec.ts`

**Steps:**
  1. [verified live] Open /allocation/requests/view/135408/history, then click the project name link to /allocation/requests/view/146946/.
    - expect: A '.btn-back' link 'Back to History' appears above the h2 with href /allocation/requests/view/146946/history (the viewed record's own history, not 135408's)
  2. [verified live] Load /allocation/requests/view/137133/ with the request Referer header set to http://dashboard-s.rcdev.nectar.org.au:8000/allocation/approved_requests/ (page.goto with the referer option; do not load the slow list), then with .../allocation/user_requests/, then with .../allocation/requests/.
    - expect: Approved referer: 'Back to Approved Requests' -> /allocation/approved_requests/
    - expect: user_requests referer: 'Back to My Requests' -> /allocation/user_requests/
    - expect: Pending list referer (/allocation/requests/) and direct navigation: no back button (0 matches)

#### 1.21. 4.21 Buttons for N and J records (not reachable from Pending data)

**File:** `tests/rcallocation/04-pending-admin-detail/detail-buttons-n-j.spec.ts`

**Steps:**
  1. [derived from code, not verified live; no N record exists and J records (132752, 22462, 1516) were not opened in this run] Open /allocation/requests/view/132752/ (J) when ready. For N, a new record would be needed; do not create one in this suite.
    - expect: N follows E: 'Review & Approve' and 'Decline with Reason' (can_be_approved, can_be_rejected)
    - expect: J shows no approve or decline buttons, the same as R (since NECTAR-17320, can_approve_change and can_reject_change are true only for X; before it J showed the X buttons)
    - expect: The exact gating comes from AllocationRequest.can_be_approved, can_be_rejected, can_approve_change and can_reject_change in models.py; confirm the J result on the first run and record it. 'View History' and 'Related tickets' always appear

#### 1.22. 4.22 Missing id on admin detail returns 404 and nothing is submitted

**File:** `tests/rcallocation/04-pending-admin-detail/detail-read-only-guard.spec.ts`

**Steps:**
  1. [verified live in suite 01 1.17; not repeated] Document only: /allocation/requests/view/99999999/ returns the Django debug 404. The suite 04 specs must contain no click on submit buttons and no POST requests; assert with a request listener that every recorded request to dashboard-s uses method GET.
    - expect: No POST, PUT or DELETE is issued during the suite
    - expect: No request leaves http://dashboard-s.rcdev.nectar.org.au:8000
