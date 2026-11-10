# rcallocation 01: Navigation and permissions

## Application Overview

Regression baseline for the Allocations dashboard (`rcallocation`) on http://dashboard-s.rcdev.nectar.org.au:8000 ahead of a refactor that intends no UI change. All scenarios are read-only (GET only, no form submissions). Observed live as the pt.openrc user, who is confirmed to be an allocation admin (Pending Requests, Approved Requests and admin-only URLs all return 200). Scenarios for regular users and TenantManagers are derived from code and not verified live.

GLOBAL RULES FOR EXECUTION
- Never navigate to, click or open any URL outside http://dashboard-s.rcdev.nectar.org.au:8000. Links to support.ehelp.edu.au, sandbox.orcid.org, surveymonkey, doi.org, Freshdesk, Grafana and similar are recorded by href only.
- The seed blocks challenges.cloudflare.com. Never remove or bypass that block. If the session expires, rerun the seed.
- If a page shows a challenge, CAPTCHA, a non-Horizon login page, or does not settle in about 30 seconds, abandon the step and note it.
- The seed leaves the form page /allocation/ open. Navigating away from it raises a "beforeunload" dialog; accept it (leave page) before continuing.
- Use short waits. Do not wait for networkidle. A survey modal ("Tell us about your Nectar Cloud experience") may overlay pages; dismiss it with "Not right now".
- Page titles all end with " - Nectar Dashboard".

TEST DATA FOUND ON dashboard-s (read-only; dev data may change, re-check if a step fails)
- Own allocation (contact sorrison@gmail.com, project pt-44 context): 152179, status A (Approved), name "gdfgdfgdf", description "fsdgfdsgdsfg", site QCIF, National True, last updated April 30, 2026. This is the only row in My Requests.
- Status E (Submitted), Pending list: 137133 ("qui", "Assimilated composite help-desk"), 137145, 145086, 144561, 145986, 147462, 146607 (22 of 31 Pending rows are E).
- Status X (Update requested): 135408 ("eum", "Automated composite intranet", site Intersect, National True); also 58677, 62718, 84989, 38655, 145272, 123439, 135339, 129250. All X rows also appear in Approved Requests (9 X there).
- Status A (Approved): 152179, 98355 (first Approved row, "a", "Enhanced mission-critical synergy"), 145002, 130198. Approved Requests shows 1576 A rows.
- Status J (Update declined), top-level, in Approved Requests: 132752, 22462, 1516 (15 J rows in total).
- Status R (Declined) history record: 63117 (appears in a history table; it is a history record, not a list row).
- Status N (New) and D (Deleted): none found in any list. No ID available; scenarios needing them are not covered.
- History record IDs (have a parent_request) from the history of 135408: 146946 (Approved), 138447 (Update requested), 137049, 135915, 135885, 135543, 135411. The first row in that history table is the current record itself (135408).
- Non-existent ID for 404 checks: 99999999.
- Counts at time of exploration: Pending 31 rows (22 E, 9 X; no N); Approved 1600 rows (1576 A, 9 X, 15 J).

OBSERVED DISCREPANCIES FROM THE BRIEF (live results are the baseline)
1. Page title for Pending Requests, Approved Requests and My Requests is "Allocation Requests - Nectar Dashboard" (not "Approved Requests" / "My Requests"). The h1 differs: Pending "Allocation Requests", Approved "Approved Requests", My Requests "My Requests".
2. Pending Requests columns are State, Name, Current Associated Site, National, Previous Approver, Contact, Last Updated, Expiry Date, Urgency, Actions. There is no "Approver" column.
3. Approved Requests columns include "Approver". Name links go to /allocation/requests/view/<id>/ (not approved_requests/view/<id>/).
4. My Requests columns are State, Name, Current Associated Site, National, Contact, Last Updated, Expiry Date, Actions (no Approver, no Previous Approver, no Urgency). It has no filter box. The row action is "Amend/Extend allocation" (to user_requests/edit_change_request/<id>/). The table action "Request a new allocation" links to /allocation/, not /allocation/request/.
5. /allocation/request/ returns 404. The New Request panel is served at /allocation/ and the sidebar link is /allocation/.
6. Urgency values are the words "(Overdue)" and "(Danger)", all in parentheses, with no pending_warn_level cell class. All 31 pending rows were parenthesised. pending_warn_level_0 to 4 were not observed.
7. The Pending "Edit request" row action appears on both E and X rows. No row lacked it.
8. ~~requests/edit_request/<id>/ for an Approved record (152179, 146946) returns HTTP 500 (TypeError "'NoneType' object is not callable").~~ **Fixed by the allocation status fix (NECTAR-17320); not yet verified live.** It now returns HTTP 400 'Allocation cannot be edited in its current state'. It returns 200 for E record 137133. Scenario 1.15 is updated.
9. ~~user_requests/edit_request/146946/ and edit_change_request/146946/ return 200 for a history record, although user_requests/view/146946/ returns 403.~~ **Fixed, deployed to dashboard-s and verified live on 2026-10-30.** Cause: `BaseAllocationView` listed `UpdateView` before `UserPassesTestMixin`, so `test_func()` never ran for any of its subclasses. The fix puts the mixin first (see `releasenotes/notes/allocation-view-access-checks-*.yaml`). Expected after the fix: these URLs return 403 for history records for every user, and 403 for any allocation where the user is not the contact, a TenantManager of its project or an allocation admin. Scenarios 1.16, 1.20 and 1.21 are updated accordingly.
10. ~~reject_request on an Approved record (152179) returns 200 (only R/J are guarded).~~ **Fixed by the allocation status fix (NECTAR-17320); not yet verified live.** It now returns HTTP 400 'Allocation is not awaiting approval'. approve_request and approve_change_request on Approved record 152179 return 400 "Allocation already approved".
11. The Pending name filter is client-side (typing filters rows in place, no reload) and matches text in any column (for example "Intersect" matches the site column).
12. The reject page title is "Decline or Request Amendment from User", while the code page_title says "Decline or Request Changes from User".

## Test Scenarios

### 1. Navigation & permissions

**Seed:** `/home/sam/projects/nectar/nectar-dashboard/seed.spec.ts`

#### 1.1. Allocations sidebar group lists four panels in order

**File:** `tests/rcallocation/01-navigation-permissions/sidebar-panels.spec.ts`

**Steps:**
  1. [verified live] Run seed.spec.ts. Page opens at /allocation/. Expand the Allocations sidebar group if collapsed.
    - expect: URL is http://dashboard-s.rcdev.nectar.org.au:8000/allocation/
    - expect: Page title is 'Allocation Request - Nectar Dashboard'
    - expect: Breadcrumb reads 'Allocations' then 'None' (observed live)
    - expect: Sidebar group 'Allocations' has links in this order: 'New Request' (/allocation/), 'Pending Requests' (/allocation/requests/), 'Approved Requests' (/allocation/approved_requests/), 'My Requests' (/allocation/user_requests/)
  2. Confirm the pt.openrc user is an allocation admin by checking that both admin panels are listed.
    - expect: 'Pending Requests' and 'Approved Requests' are visible, so the user holds openstack.roles.allocationadmin

#### 1.2. New Request panel renders at /allocation/ as the default panel

**File:** `tests/rcallocation/01-navigation-permissions/new-request-panel.spec.ts`

**Steps:**
  1. [verified live] Start from seed (URL /allocation/). Inspect the heading, links and form steps.
    - expect: h3 'New Allocation Request: About the Project' is visible
    - expect: Link 'All My Requests' has href /allocation/user_requests/
    - expect: Paragraph contains link 'My Requests' with href /allocation/user_requests/
    - expect: Step links: 'STEP 1: About the project' (#form-step1), 'STEP 2: Cloud resources' (#form-step2)
    - expect: Accordion headings in order: '1. Project Details', '2. Usage Information', '3. Fields of Research (FOR)', '4. Supported Institutions', '5. Investigator', '6. Project Support', '7. Research Grant Information', '8. Continue'
    - expect: Project Details has 'Project allocation title *', 'Contact e-mail' (prefilled sorrison@gmail.com), 'Project Identifier *', 'Generated project DNS zone name' (disabled), 'Estimated project duration *' (1-month, 3-months, 6-months, 12-months selected), 'Convert trial project?'
    - expect: A 'Submit' button exists under 'Are you ready to submit this allocation request?'. DO NOT click it.

#### 1.3. /allocation/request/ is not a valid URL (404)

**File:** `tests/rcallocation/01-navigation-permissions/request-url-404.spec.ts`

**Steps:**
  1. [verified live] Navigate to /allocation/request/.
    - expect: HTTP 404; title 'Page not found at /allocation/request/'; heading 'Page not found (404)'
  2. Click sidebar 'New Request'.
    - expect: Navigates to /allocation/ (not /allocation/request/)

#### 1.4. Pending Requests table layout and headings

**File:** `tests/rcallocation/01-navigation-permissions/pending-layout.spec.ts`

**Steps:**
  1. [verified live] Click sidebar 'Pending Requests' (/allocation/requests/). Accept the beforeunload dialog if shown.
    - expect: URL /allocation/requests/; title 'Allocation Requests - Nectar Dashboard'
    - expect: Single h1 'Allocation Requests'; breadcrumb 'Allocations' / 'Allocation Requests'
    - expect: Table id 'datatableoptions' with headers exactly: State, Name, Current Associated Site, National, Previous Approver, Contact, Last Updated, Expiry Date, Urgency, Actions
    - expect: No 'Approver' column
    - expect: Footer 'Displaying 31 items' (count may drift)
    - expect: Only statuses E and X appear (no N in current data). Rows sorted by Last Updated ascending (first row 'qui Assimilated composite help-desk', 137133, March 1, 2024)
    - expect: Dates render as 'March 1, 2024', 'Aug. 11, 2024', 'Sept. 2, 2024'; empty site and expiry render '-'

#### 1.5. Pending Requests State column and CSS classes

**File:** `tests/rcallocation/01-navigation-permissions/pending-state-column.spec.ts`

**Steps:**
  1. [verified live] On /allocation/requests/, inspect the State cell of rows 137133 and 135408.
    - expect: 137133: <p class='alloc-icon alloc-icon-wip' title='Submitted'><strong>E</strong></p>
    - expect: 135408: text 'X', title 'Update requested', class 'alloc-icon alloc-icon-wip'
    - expect: State cell has class 'text-center'
    - expect: No row has alloc-icon-ok (A is not listed here)

#### 1.6. Pending Requests Urgency column values

**File:** `tests/rcallocation/01-navigation-permissions/pending-urgency.spec.ts`

**Steps:**
  1. [verified live] Read the Urgency cell of every row.
    - expect: All E rows show '(Overdue)'; all X rows show '(Danger)' (31 of 31 parenthesised)
    - expect: Cells have no pending_warn_level_N class (class attribute holds only 'sortable' and 'normal_column', in either order: Horizon builds cell classes from a set, so the order varies between server processes)
    - expect: pending_warn_level_0 to 4 and unparenthesised values were NOT observed; covering them needs a record relevant to the approver's site (none found)

#### 1.7. Pending Requests name filter is client-side and matches any column

**File:** `tests/rcallocation/01-navigation-permissions/pending-filter.spec.ts`

**Steps:**
  1. [verified live] Focus input name='DataTableOptions__filter__q' (placeholder 'Filter'). Type 'Intersect' key by key (locator.fill alone does not trigger filtering; use pressSequentially).
    - expect: 3 rows remain visible (135408, 58677, 135339). URL does not change.
  2. Clear and type 'zzzzno'.
    - expect: Table body shows 'No items to display.'
  3. Clear and type 'automated composite', then '135408'.
    - expect: 1 row visible each time (135408)
  4. Clear the field and press Backspace.
    - expect: All 31 rows visible again

#### 1.8. Pending Requests row actions and links

**File:** `tests/rcallocation/01-navigation-permissions/pending-row-actions.spec.ts`

**Steps:**
  1. [verified live] Inspect links in row 137133.
    - expect: Name link: /allocation/requests/view/137133/
    - expect: 'Edit request' primary action: /allocation/requests/edit_request/137133/
    - expect: Dropdown action 'View history': /allocation/requests/view/137133/history
    - expect: Same pattern for X row 135408. All 31 rows show both actions.

#### 1.9. Approved Requests table layout

**File:** `tests/rcallocation/01-navigation-permissions/approved-layout.spec.ts`

**Steps:**
  1. [verified live] Click sidebar 'Approved Requests' (/allocation/approved_requests/).
    - expect: URL /allocation/approved_requests/; title 'Allocation Requests - Nectar Dashboard'; h1 'Approved Requests'; breadcrumb 'Allocations' / 'Approved Requests'
    - expect: Columns exactly: State, Name, Current Associated Site, National, Approver, Contact, Last Updated, Expiry Date, Actions
    - expect: Footer 'Displaying 1600 items' (no pagination control). Statuses present: A (1576), X (9), J (15)
    - expect: Rows sorted by project name ascending (first names start 'a', e.g. 98355, then 'accusantium...')
    - expect: Name links go to /allocation/requests/view/<id>/ e.g. 98355. Only action is 'View history'; no 'Edit request'.

#### 1.10. Approved Requests State column per status

**File:** `tests/rcallocation/01-navigation-permissions/approved-state-column.spec.ts`

**Steps:**
  1. [verified live] Inspect State cells for 98355 (A), 145272 (X), 132752 (J).
    - expect: A: 'alloc-icon alloc-icon-ok', title 'Approved'
    - expect: X: 'alloc-icon alloc-icon-wip', title 'Update requested'
    - expect: J: 'alloc-icon alloc-icon-wip', title 'Update declined'

#### 1.11. Approved Requests name filter

**File:** `tests/rcallocation/01-navigation-permissions/approved-filter.spec.ts`

**Steps:**
  1. [derived from code; the filter input DataTableOptions__filter__q was seen live but filtering was not exercised on this table] Type 'Intersect' or a project name such as 'accusantium' into the filter box (use pressSequentially).
    - expect: Rows filter client-side without reload; clearing restores 1600 rows. Capture exact counts on first run.

#### 1.12. My Requests table for an allocation admin

**File:** `tests/rcallocation/01-navigation-permissions/my-requests.spec.ts`

**Steps:**
  1. [verified live] Click sidebar 'My Requests' (/allocation/user_requests/).
    - expect: URL /allocation/user_requests/; title 'Allocation Requests - Nectar Dashboard'; h1 'My Requests'; breadcrumb 'Allocations' / 'My Requests'
    - expect: Columns: State, Name, Current Associated Site, National, Contact, Last Updated, Expiry Date, Actions
    - expect: One row: State A, Name 'gdfgdfgdf' with subtitle 'fsdgfdsgdsfg', site QCIF, National True, contact sorrison@gmail.com, Last Updated 'April 30, 2026', Expiry '-'
    - expect: Name link /allocation/user_requests/view/152179/; row action 'Amend/Extend allocation' -> /allocation/user_requests/edit_change_request/152179/
    - expect: Table action 'Request a new allocation' -> /allocation/
    - expect: No filter box. Footer 'Displaying 1 item'. An admin sees only own or managed allocations here.

#### 1.13. Admin detail and history views

**File:** `tests/rcallocation/01-navigation-permissions/admin-detail-views.spec.ts`

**Steps:**
  1. [verified live] Open /allocation/requests/view/152179/, /allocation/approved_requests/view/152179/ and /allocation/user_requests/view/152179/.
    - expect: Each returns 200, title 'View allocation request - Nectar Dashboard', headings 'View Allocation Request', 'fsdgfdsgdsfg', 'Current Resources'
  2. Open /allocation/requests/view/135408/history and /allocation/approved_requests/view/152179/history.
    - expect: 200; title 'Allocation Requests - Nectar Dashboard'; heading 'History'
    - expect: Columns: Project name, Approver, Bundle, SUs, Cores, RAM, Object Storage, Volume Storage, Status, Modification time
    - expect: 135408 history has 8 rows; the first is 135408 itself; statuses include 'Update requested' and 'Approved'; Project name links go to /allocation/requests/view/<id>/
  3. GET /allocation/requests/edit_notes/152179/ and /allocation/requests/reject_request/137133/ (do not submit).
    - expect: edit_notes: 200, title 'Edit allocation Admin notes - Nectar Dashboard'
    - expect: reject_request: 200, title 'Decline or Request Amendment from User - Nectar Dashboard'
    - note: This step used reject_request/152179/ (Approved) until NECTAR-17320, which returns 400 for it (see 1.14 step 4)
  4. GET /allocation/requests/approve_request/137133/ and /allocation/requests/approve_change_request/135408/ (E and X records).
    - expect: 200, title 'Approve Request - Nectar Dashboard'
  5. GET /allocation/requests/edit_request/137133/ (E record).
    - expect: 200, title 'Edit Allocation Request - Nectar Dashboard'

#### 1.14. Guarded pages return 400 with plain-text message

**File:** `tests/rcallocation/01-navigation-permissions/guarded-400.spec.ts`

**Steps:**
  1. [verified live] GET /allocation/requests/approve_request/152179/ (Approved record).
    - expect: HTTP 400; body is plain text 'Allocation already approved' (plus a trailing HTML comment token); no Horizon chrome, empty title
  2. GET /allocation/requests/approve_change_request/152179/.
    - expect: HTTP 400, 'Allocation already approved'
  3. GET /allocation/requests/reject_request/132752/ (status J) and /allocation/requests/reject_request/63117/ (status R history record).
    - expect: HTTP 400, body 'Allocation already declined'
  4. GET /allocation/requests/reject_request/152179/ (Approved record).
    - expect: HTTP 400, body 'Allocation is not awaiting approval' (guarded since NECTAR-17320; before it, HTTP 200 with the decline form)

#### 1.15. Admin edit_request on an Approved record returns 400

**File:** `tests/rcallocation/01-navigation-permissions/admin-edit-approved-500.spec.ts`

**Steps:**
  1. [verified live] GET /allocation/requests/edit_request/152179/ and /allocation/requests/edit_request/146946/.
    - expect: HTTP 400; body 'Allocation cannot be edited in its current state'. Before NECTAR-17320 this was HTTP 500 (TypeError "'NoneType' object is not callable"). The 'Edit request' row action is not offered for Approved rows.

#### 1.16. User view denied for a history record (403 look)

**File:** `tests/rcallocation/01-navigation-permissions/history-record-denied.spec.ts`

**Steps:**
  1. [verified live] As the admin, open /allocation/user_requests/view/146946/ (history record of 135408).
    - expect: HTTP 403, no redirect (URL unchanged)
    - expect: Title '- Forbidden - Nectar Dashboard'; heading 'Forbidden'
    - expect: Body text: 'You do not have the required privileges to access this content. If you believe this message to be in error, please contact your project manager.'
  2. Open /allocation/requests/view/146946/ (admin view) for comparison.
    - expect: 200, 'View Allocation Request', 'Assimilated responsive archive'. The admin view does not deny history records.
  3. Open /allocation/user_requests/edit_request/146946/ and /allocation/user_requests/edit_change_request/146946/.
    - expect: [verified live after permission fix] HTTP 403 with the same 'Forbidden' page as step 1 (title '- Forbidden - Nectar Dashboard'), for both URLs, even as an allocation admin
    - note: Before the fix, both returned 200 ('Edit Allocation Request - Nectar Dashboard' and 'Request Allocation Extension - Nectar Dashboard'), verified live on 2026-10-30.

#### 1.17. Missing allocation id returns 404

**File:** `tests/rcallocation/01-navigation-permissions/missing-id-404.spec.ts`

**Steps:**
  1. [verified live] GET /allocation/requests/view/99999999/.
    - expect: HTTP 404, title 'Page not found at /allocation/requests/view/99999999/', heading 'Page not found (404)' (Django debug page; dev environment)

#### 1.18. External links on allocation pages (record only, never follow)

**File:** `tests/rcallocation/01-navigation-permissions/external-links.spec.ts`

**Steps:**
  1. [verified live] On /allocation/, read hrefs only with getAttribute. Do not click.
    - expect: https://support.ehelp.edu.au/support/solutions/articles/6000171494-project-allocation-expiry-and-renewal#pt (sidebar 'Learn more about project trials')
    - expect: https://support.ehelp.edu.au/support/solutions/articles/6000226889 ('eligibility criteria')
    - expect: https://support.ehelp.edu.au/support/tickets/new ('create a support ticket')
    - expect: https://sandbox.orcid.org/0009-0006-2369-9936 ('View ORCID record') and https://sandbox.orcid.org ('orcid.org')
    - expect: https://eligibility.rc.nectar.org.au/ ('Eligibility Assessment Tool')
    - expect: https://support.ehelp.edu.au/support/solutions/articles/6000277743 ('Sensitive Data Guidelines')
    - expect: https://www.surveymonkey.com/r/YGWYNMB (survey 'Start survey')
    - expect: Footer links to dashboard.rc.nectar.org.au, status.rc.nectar.org.au, tutorials.rc.nectar.org.au, ardc.edu.au
    - expect: Freshdesk 'Related tickets' and Grafana 'Project usage' links on detail pages were NOT inspected (abandoned to stay in bounds)

#### 1.19. Regular user sees only New Request and My Requests

**File:** `tests/rcallocation/01-navigation-permissions/nonadmin-sidebar.spec.ts`

**Steps:**
  1. [derived from code, not verified live] Log in as a user without openstack.roles.allocationadmin. Open /allocation/.
    - expect: Sidebar Allocations group shows 'New Request' and 'My Requests' only; 'Pending Requests' and 'Approved Requests' are hidden (panel permissions = ('openstack.roles.allocationadmin',))

#### 1.20. Regular user is denied admin URLs

**File:** `tests/rcallocation/01-navigation-permissions/nonadmin-admin-urls.spec.ts`

**Steps:**
  1. [derived from code, not verified live] As a non-admin GET /allocation/requests/, /allocation/approved_requests/, requests/view/<id>/, requests/view/<id>/history, requests/edit_request/<id>/, approve_request/<id>/, reject_request/<id>/, approve_change_request/<id>/, edit_notes/<id>/.
    - expect: Panel list URLs are blocked by Horizon panel permissions (redirect or 403; exact form not verified). Detail and edit views use UserPassesTestMixin with user_is_allocation_admin, so expect 403 with the same 'Forbidden' page as the history denial above. Capture exact status and text on first run with a non-admin account.
    - note: Before the permission fix, the edit, approve, approve-change and reject views relied only on the Horizon panel permission (their test_func never ran). After the fix they also deny non-admins in the view itself; the visible result for a non-admin should be the same.

#### 1.21. Regular user My Requests and user views

**File:** `tests/rcallocation/01-navigation-permissions/nonadmin-user-views.spec.ts`

**Steps:**
  1. [derived from code, not verified live] As a non-admin open /allocation/user_requests/.
    - expect: 200 (test_func returns True). Lists top-level allocations where contact_email equals the username or project_id is in the user's TenantManager projects, ordered by status
  2. [derived from code] Open user_requests/view/<id>/ for own allocation, another user's allocation, and a history record.
    - expect: Own (contact) allocation: 200 'View allocation request'
    - expect: Other user's allocation where user is not TenantManager: 403 Forbidden
    - expect: History record: 403 Forbidden
  3. [after permission fix, derived from code and unit tests; not yet verified live] GET user_requests/edit_request/<id>/ and edit_change_request/<id>/ for another user's allocation (user is not contact or TenantManager), then POST a valid form to each.
    - expect: GET returns 403 'Forbidden'; POST returns 403 and creates no history record
    - expect: For the user's own (contact) Submitted allocation, edit_request returns 200 and edit_change_request returns HTTP 400 'Allocation cannot be amended in its current state' (the amend view only opens for A, X and J since NECTAR-17320; before it, 200)
    - note: Before the fix, any logged-in user got 200 on GET and could save via POST (unit test confirmed a history record was created).

#### 1.22. TenantManager access

**File:** `tests/rcallocation/01-navigation-permissions/tenantmanager-access.spec.ts`

**Steps:**
  1. [derived from code, not verified live] As a TenantManager of a project whose allocation has a different contact, open My Requests, then user_requests/view/<id>/, edit_request/<id>/ and edit_change_request/<id>/.
    - expect: Allocation appears in My Requests; view and edit_request return 200 (check_tm_or_alloc_admin uses manuka users.projects(user.id, 'TenantManager')). Admin-only requests/* URLs remain denied.
    - expect: edit_change_request returns HTTP 400 'Allocation cannot be amended in its current state' for this Submitted allocation (since NECTAR-17320; before it, 200)
