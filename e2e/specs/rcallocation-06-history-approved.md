# rcallocation 06: History & Approved Requests

## Application Overview

Regression baseline for the allocation History table (/allocation/requests/view/<id>/history and /allocation/approved_requests/view/<id>/history) and the Approved Requests list (/allocation/approved_requests/) of the Allocations dashboard (rcallocation) on http://dashboard-s.rcdev.nectar.org.au:8000, ahead of a refactor that intends no UI change. Observed live on 2026-10-30 as the pt.openrc user (allocation admin, sorrison@gmail.com). Read-only: nothing is submitted.

GLOBAL RULES FOR EXECUTION
- Run seed.spec.ts first. Keep its blocks (challenges.cloudflare.com, ardc.edu.au, survey.rc.nectar.org.au), dialog auto-accept and 15s default timeout. Rerun the seed if the session expires. Stay on dashboard-s. Submit nothing.
- Pass an explicit timeout to every action and wait. For history tables, a same-origin fetch plus DOMParser inside page.evaluate is reliable and fast (used for most live reads here).
- /allocation/approved_requests/ renders 1601 rows in one page and is slow. Load it ONCE per test run with page.goto(url, { timeout: 90000, waitUntil: 'domcontentloaded' }), then page.waitForSelector('table tbody tr', { timeout: 60000 }). Never take a full accessibility snapshot of it; read the DOM with page.evaluate.
- Navigating away from the seed's /allocation/ page raised a beforeunload dialog on the first goto. The tool returned before the navigation finished. If that happens, do not call goto again; wait with page.waitForURL(/approved_requests/, { timeout: 90000 }) and continue.
- The dev data is mostly Faker-generated (random project titles and email addresses). Titles, approvers and dates below are the dev baseline for the IDs named. If the dev database is reseeded, assert the pattern (columns, formats, delta rules) rather than the literal values.
- Allocations 152181 and 152182 were mutated by suite 05 and are in their final states: 152181 = J ('Update declined'), 152182 = E ('Submitted'). Suite 05 scenario 5.16 already records their history tables after the lifecycle; this suite only re-reads them for the bundle versus custom comparison (6.5) and does not repeat the transition checks.
- Console errors (3 to 7 per page) are present on every page and are not investigated. They are the same before and after the refactor.

OBSERVED DISCREPANCIES FROM THE BRIEF (live results are the baseline)
1. Approved list counts are 1576 A, 9 X and 16 J (1601 rows). The brief's earlier counts were 1576 A, 9 X and 15 J; the extra J row is pwtest-valid (152181).
2. The Name cell is NOT a single string. It renders the project_name as the link text, then a line break, then the project_description in a <small class="muted"> element. Cell textContent therefore reads like 'pwtest-validPW validation test' (no separator). Ordering is by project_name only, not by the full cell text.
3. The brief expected the base columns without detail. Actual headers: State, Name, Current Associated Site, National, Approver, Contact, Last Updated, Expiry Date, Actions. The State column shows the status letter (A, X or J) in a <strong> inside <p class="alloc-icon alloc-icon-ok" title="Approved">; the title attribute is the status display name.
4. ~~The approved_requests/edit_request/<id>/ GET for an A record (98355) returns HTTP 500, 'TypeError: NoneType object is not callable' raised in django/views/generic/edit.py get_form from nectar_dashboard.rcallocation.allocation.views.AllocationUpdateView.~~ **Fixed by the allocation status fix (NECTAR-17320); not yet verified live.** It now returns HTTP 400 'Allocation cannot be edited in its current state', as suite 01 records for requests/edit_request.
5. The NameFilter matches the project description as well as the project name (case-insensitive). 'validation' matched pwtest-valid, whose project_name does not contain it.
6. Approved list ordering by project_name cannot be tested for case sensitivity on this data: every project_name is lowercase and no name starts with an upper-case letter, digit or symbol. Ties on equal names (1493 duplicates, for example many names of 'a') are in an undetermined order, so assert order by project_name only.
7. The History table has a heading 'History' (h1), no per-row actions and no filter. The history of a non-existent ID (999999999) returns HTTP 200 with 'No items to display.' rather than a 404.
8. Bundle column shows '-' for every Faker allocation (no bundle). Suite 05's allocations are the only live bundle examples (152181 'Standard'); 152182 shows '-' in the Bundle column although suite 05 calls it a Custom bundle, so no bundle row is named 'Custom'.

TEST DATA (live)
- 135408 (status X, 'Automated composite intranet'): 8 history rows listed in 6.2.
- 146946 (A, 'Assimilated responsive archive'): 1 history row (itself). It is a history record of 135408.
- 98355 (A, 'Enhanced mission-critical synergy', first row of the Approved list): 8 history rows.
- 145002 (A): 2 history rows. 130198 (A): 6 history rows.
- 152181 (J, pwtest-valid, bundle Standard): 6 history rows. 152182 (E): 5 history rows.

## Test Scenarios

### 1. History & Approved Requests

**Seed:** `seed.spec.ts`

#### 1.1. 6.1 History table structure and header list

**File:** `tests/rcallocation/06-history-approved/history-structure.spec.ts`

**Steps:**
  1. [verified live] Run seed.spec.ts, then goto /allocation/requests/view/135408/history (fetch or goto, 15s timeout).
    - expect: HTTP 200; document title 'Allocation Requests - Nectar Dashboard'; h1 'History'
    - expect: Breadcrumb 'Allocations / Pending Requests / History'
    - expect: Exactly one table with the 10 headers, in order: Project name, Approver, Bundle, SUs, Cores, RAM, Object Storage, Volume Storage, Status, Modification time
    - expect: Table footer reads 'Displaying 8 items'
    - expect: No row actions column and no filter input
  2. [verified live] Read the first column of each row.
    - expect: The link text is the project_description of that row's own record (it differs row to row on Faker data, for example 'Automated composite intranet', 'Assimilated responsive archive')
    - expect: Each link href is /allocation/requests/view/<that row's id>/ (first row /allocation/requests/view/135408/, second /allocation/requests/view/146946/)
  3. [verified live] Goto /allocation/requests/view/146946/history (history of a single record with no children).
    - expect: One row: 'Assimilated responsive archive | gillirene@harding.net | - | 25000 | 120 | - | - | 1000 | Approved | March 15, 2024, 2:15 a.m.'
    - expect: Footer 'Displaying 1 item' (singular)

#### 1.2. 6.2 History of an X allocation: delta and mixed-status cell rules (135408)

**File:** `tests/rcallocation/06-history-approved/history-x-allocation.spec.ts`

**Steps:**
  1. [verified live] Goto /allocation/requests/view/135408/history and read all rows in rendered order.
    - expect: Row 1 (135408, X): 'Automated composite intranet | martinstephen@brown.com | - | -13000 | 80 | 0 | 0 | 100 | Update requested | May 28, 2024, 11:04 a.m.'
    - expect: Row 2 (146946, A): 'Assimilated responsive archive | gillirene@harding.net | - | 25000 | 120 | - | - | 1000 | Approved | March 15, 2024, 2:15 a.m.'
    - expect: Row 3 (138447, X): 'Triple-buffered actuating utilization | kieran08@singh-johnson.org | - | 0 | 0 | 0 | 0 | 1000 | Update requested | Feb. 28, 2024, 4:51 a.m.'
    - expect: Row 4 (137049, A): 'Extended clear-thinking moderator | kpatterson@walker-jackson.net | - | 25000 | 120 | - | - | - | Approved | Feb. 25, 2024, 10:56 p.m.'
    - expect: Row 5 (135915, X): 'Assimilated composite help-desk | jamesarcher@gibson-oliver.com | - | 22500 | 100 | 0 | 0 | 0 | Update requested | Feb. 23, 2024, 4:31 a.m.'
    - expect: Row 6 (135885, A): 'Synchronized empowering hub | ellisanthony@ward.com | - | 2500 | 20 | - | - | - | Approved | Feb. 19, 2024, 6:55 a.m.'
    - expect: Row 7 (135543, Submitted): 'Secured fault-tolerant data-warehouse | antonymorgan@chapman-oconnor.com | - | 2500 | 20 | - | - | - | Submitted | Feb. 15, 2024, 10:41 p.m.'
    - expect: Row 8 (135411, Submitted): 'Enhanced zero tolerance workforce | whittakerlisa@french.biz | - | 2500 | 20 | - | - | - | Submitted | Feb. 15, 2024, 10:41 p.m.'
  2. [verified live] Check the formats and rules across rows.
    - expect: X rows ('Update requested') show requested minus current as a signed integer string: row 1 SUs '-13000' (negative delta is shown with a leading hyphen-minus), cores '80', RAM/object '0', volume '100'
    - expect: A rows show the current value or a single '-' when the value is 0 or absent (rows 2, 4, 6)
    - expect: Submitted rows (status 'E' per code) show the requested value or '-' (rows 7 and 8: 2500 / 20, others '-')
    - expect: Numbers have no unit suffix and no thousands separator (25000, not 25,000)
    - expect: Approver is the approver_email, or an empty cell when none (see 6.5)
    - expect: Modification time format is Django 'N j, Y, P' style: 'March 15, 2024, 2:15 a.m.', 'Feb. 25, 2024, 10:56 p.m.', 'May 28, 2024, 11:04 a.m.'. Month abbreviations follow Django: 'Feb.', 'Sept.', 'Oct.', 'Nov.', 'Jan.', 'April', 'March', 'May'
    - expect: Status column shows the display name: 'Update requested' for X, 'Approved' for A, 'Submitted' for E
  3. [verified live] Record the ordering.
    - expect: Rows are rendered newest Modification time first (descending by modified_time) in this data, although the code has no explicit order_by on the query (parent_request=pk OR pk=pk). The two Submitted rows 135543 and 135411 share the same minute (10:41 p.m.) and their relative order is 135543 then 135411
    - expect: Treat order as a baseline observation; assert descending Modification time and flag any other order

#### 1.3. 6.3 History of A allocations: 98355, 145002, 130198

**File:** `tests/rcallocation/06-history-approved/history-a-allocations.spec.ts`

**Steps:**
  1. [verified live] Goto /allocation/requests/view/98355/history.
    - expect: Footer 'Displaying 8 items'; row 1 is the allocation itself: 'Enhanced mission-critical synergy | brownlouis@carter.biz | - | - | 16 | -1 | - | 500 | Approved | Sept. 4, 2024, 1:20 a.m.' (link /allocation/requests/view/98355/)
    - expect: Row 2 (151311) 'Sharable interactive flexibility | tbarton@moss.co.uk | - | 0 | 0 | 0 | 0 | 0 | Update requested | Sept. 4, 2024, 1:15 a.m.'
    - expect: Row 3 (151305) Approved 'Oct. 3, 2023, 6:20 a.m.'; row 4 (129763) Update requested 'Oct. 3, 2023, 6:15 a.m.'; row 5 (129706) Approved 'Oct. 31, 2022, 5:50 a.m.'; row 6 (113777) Update requested 'Oct. 31, 2022, 5:45 a.m.'; row 7 (113747) Approved 'Nov. 26, 2021, 1:05 a.m.'; row 8 (98358) Submitted 'Nov. 26, 2021, 1 a.m.'
    - expect: A rows show RAM '-1' (a stored quota of -1 is shown as is, not as '-')
    - expect: Time of exactly on the hour drops minutes: 'Nov. 26, 2021, 1 a.m.' (Django 'P' format)
  2. [verified live] Goto /allocation/requests/view/145002/history.
    - expect: Footer 'Displaying 2 items'
    - expect: Row 1 (145002, Approved): 'Triple-buffered leadingedge moderator | whittakerlisa@french.biz | - | - | 2 | 8 | - | - | Approved | April 10, 2024, 3:31 a.m.'
    - expect: Row 2 (145005, Submitted): 'Assimilated empowering alliance | wporter@ball.com | - | - | 2 | 8 | - | - | Submitted | April 10, 2024, 3:27 a.m.'
  3. [verified live] Goto /allocation/requests/view/130198/history.
    - expect: Footer 'Displaying 6 items'
    - expect: Row 1 (130198, Approved): 'Team-oriented content-based ability | hollandbeth@davidson-hill.net | - | 6000 | 20 | - | 16000 | 10 | Approved | Jan. 22, 2024, 12:20 a.m.'
    - expect: Row 2 (134112) Update requested, all zeros, 'Jan. 19, 2024, 12:54 a.m.'; row 3 (134055) Approved '6000 | 20 | - | 16000 | 10' 'Nov. 15, 2023, 4:35 a.m.'
    - expect: Row 4 (131731) Update requested '3000 | 12 | 0 | 0 | 10' 'Nov. 15, 2023, 4:31 a.m.'; row 5 (131725) Approved '3000 | 8 | - | 16000 | -' 'Oct. 16, 2023, 1:05 a.m.'; row 6 (130240) Submitted 'Oct. 13, 2023, 5:15 a.m.'
    - expect: '12:20 a.m.' is used for 20 minutes past midnight (not '0:20')

#### 1.4. 6.4 History of a history record (146946) and approved_requests history route parity

**File:** `tests/rcallocation/06-history-approved/history-route-parity.spec.ts`

**Steps:**
  1. [verified live] Goto /allocation/requests/view/146946/ (a history record of 135408) and read the history link.
    - expect: Title 'View allocation request - Nectar Dashboard', h1 'View Allocation Request'
    - expect: The 'View History' link has href /allocation/requests/view/146946/history
    - expect: /allocation/approved_requests/view/146946/ renders the same page and the same History link href (/allocation/requests/view/146946/history, not an approved_requests path)
  2. [verified live] Goto /allocation/requests/view/146946/history.
    - expect: Renders one row only (the history record itself, because it has no children): 'Assimilated responsive archive | gillirene@harding.net | - | 25000 | 120 | - | - | 1000 | Approved | March 15, 2024, 2:15 a.m.'
    - expect: Footer 'Displaying 1 item'. It does NOT show the parent's 8-row chain
    - expect: The row link is /allocation/requests/view/146946/
  3. [verified live] Goto /allocation/approved_requests/view/135408/history and compare with /allocation/requests/view/135408/history.
    - expect: HTTP 200, title 'Allocation Requests - Nectar Dashboard', h1 'History'
    - expect: Breadcrumb differs only in the middle item: 'Allocations / Approved Requests / History' (the 'Approved Requests' crumb links to /allocation/approved_requests/)
    - expect: The 10 headers, the 8 rows, cell values, ordering and footer 'Displaying 8 items' are identical to 6.2
    - expect: Row links still point to /allocation/requests/view/<id>/ (not approved_requests paths)
    - expect: /allocation/approved_requests/view/146946/history renders the same single row and 'Displaying 1 item'
  4. [verified live] Goto /allocation/requests/view/999999999/history.
    - expect: HTTP 200 (not 404); h1 'History'; breadcrumb 'Allocations / Pending Requests / History'
    - expect: Table body shows 'No items to display.' and no footer item count

#### 1.5. 6.5 History cell formats: bundle versus no bundle, blank approver (152181, 152182)

**File:** `tests/rcallocation/06-history-approved/history-bundle-vs-custom.spec.ts`

**Steps:**
  1. [verified live] Goto /allocation/requests/view/152181/history (Standard bundle, J). Suite 05 scenario 5.16 holds the transition checks; here only cell formats are asserted.
    - expect: Footer 'Displaying 6 items'; row links include /allocation/requests/view/152181/ (row 1) and /allocation/requests/view/152191/ (row 2)
    - expect: Row 1: 'PW validation test | sorrison@gmail.com | Standard | 0 | 0 | 0 | 0 | 0 | Update declined | Oct. 30, 2026, 4:22 a.m.' (J shows delta 0 in all five quota columns, including volume '0')
    - expect: Row 2 (152191): same but status 'Update requested', 4:22 a.m. Row 3 (152190, Approved): 'Standard | 4000 | 64 | 128 | 500 | - | Approved | Oct. 30, 2026, 4:21 a.m.'
    - expect: Row 4 (152189) Update requested zeros 4:20 a.m.; row 5 (152188) Approved 4:19 a.m.; row 6 (152187) Submitted with a blank Approver cell, 'Oct. 30, 2026, 2:42 a.m.'
    - expect: Bundle column shows the bundle name 'Standard'; bundle quotas (4000 SUs, 64 cores, 128 RAM, 500 object) appear in the quota columns with no unit and no separator; volume is '-' when 0 on an A or E row
  2. [verified live] Goto /allocation/requests/view/152182/history (E, no bundle name; custom quotas).
    - expect: Footer 'Displaying 5 items'; Bundle column '-' on every row; quota cells '16000 | 256 | 640 | 6000 | -' on Submitted and Declined rows (E and R show the requested value)
    - expect: Row order: 4:02 a.m. Submitted (current, approver sorrison@gmail.com), 4:01 a.m. Declined (sorrison@gmail.com), 3:49 a.m. Submitted (blank approver), 3:33 a.m. Submitted (blank approver), 2:45 a.m. Submitted (blank approver)
    - expect: Declined status displays as 'Declined' (R)
  3. [derived from code] Review get_quota_by_resource in tables.py for the cases no live record covered.
    - expect: Bundle quota (bundle.get_quota('<service>.<resource>')) is added to the sum of Quota.requested_quota (want) and Quota.quota (have) of the allocation, so a bundle plus custom quota shows the sum
    - expect: Statuses other than X, J, A, E, R (for example N, M, D) render 'Requested <want>, currently have <have>'. No live row with such a status was found in the sampled histories; if a tester finds one, record it

#### 1.6. 6.6 Approved Requests page structure and load performance

**File:** `tests/rcallocation/06-history-approved/approved-structure.spec.ts`

**Steps:**
  1. [verified live] From the seed page, goto /allocation/approved_requests/ with { timeout: 90000, waitUntil: 'domcontentloaded' } (once) and wait for 'table tbody tr' (60s).
    - expect: Load time observed 2026-10-30: DOMContentLoaded about 28.4 s and load event about 29.2 s after navigation start (a 10s timeout will fail)
    - expect: URL stays /allocation/approved_requests/; document title 'Allocation Requests - Nectar Dashboard'; h1 'Approved Requests'
    - expect: Breadcrumb starts 'Allocations / Approved Requests'
    - expect: Sidebar Allocations group contains 'Approved Requests' linking to /allocation/approved_requests/
  2. [verified live] Read the header row and footer.
    - expect: Exactly 9 headers in order: State, Name, Current Associated Site, National, Approver, Contact, Last Updated, Expiry Date, Actions
    - expect: Footer reads 'Displaying 1601 items'
    - expect: 1601 rows in tbody; there is no pagination control (no .pagination, page-link or marker links) and no 'next' link: all rows load on one page
  3. [verified live] Count the State column letters.
    - expect: A = 1576, X = 9, J = 16 (total 1601)
    - expect: pwtest-valid (152181, J) is present: the row has a link /allocation/requests/view/152181/
    - expect: The J list also contains for example 'cumCross-platform systemic synergy' and 'placeatEnhanced mission-critical synergy' (cell text is project_name followed by description)

#### 1.7. 6.7 Approved Requests row cell formats, links and actions

**File:** `tests/rcallocation/06-history-approved/approved-row-cells.spec.ts`

**Steps:**
  1. [verified live] On the loaded approved list, read row 1 (the first row, allocation 98355).
    - expect: State: 'A' inside <p class="alloc-icon alloc-icon-ok" title="Approved"><strong>A</strong></p>
    - expect: Name: link text 'a' (the project_name) href /allocation/requests/view/98355/, then <br> and <small class="muted">Enhanced mission-critical synergy</small> (the project_description). Combined textContent 'aEnhanced mission-critical synergy'
    - expect: Current Associated Site 'University of Melbourne'; National 'False'; Approver 'brownlouis@carter.biz'; Contact 'conwaystewart@example.net'
    - expect: Last Updated 'Sept. 4, 2024' (date only, format 'N j, Y', no time); Expiry Date 'Sept. 4, 2025'
    - expect: Actions cell contains only the link 'View history' with href /allocation/requests/view/98355/history (no Edit request action, no dropdown)
  2. [verified live] Read the last row (allocation 147375).
    - expect: State 'A'; Name link 'voluptatem' href /allocation/requests/view/147375/ with description 'Public-key leadingedge concept'
    - expect: Associated site 'QCIF'; National 'True'; Approver 'kieranbartlett@kay-stevens.info'; Contact 'umarsh@example.com'; Last Updated 'June 12, 2024'; Expiry Date 'June 12, 2025'
    - expect: Action 'View history' href /allocation/requests/view/147375/history
  3. [verified live] Read the pwtest-valid row (152181, J).
    - expect: State 'J'; Name 'pwtest-valid' (link /allocation/requests/view/152181/) with description 'PW validation test'
    - expect: Site 'QCIF'; National 'False'; Approver 'sorrison@gmail.com'; Contact 'sorrison@gmail.com'; Last Updated 'Oct. 30, 2026'; Expiry Date '-' (an empty end_date shows '-')
    - expect: Row index 1145 (0-based) in the list at observation time (position depends on the other project names)
  4. [verified live] Click 'View history' on the first row (98355), or goto its href.
    - expect: URL /allocation/requests/view/98355/history (the Pending Requests path, not approved_requests/view)
    - expect: Page renders the 8-row history from 6.3 with breadcrumb 'Allocations / Pending Requests / History'
  5. [verified live] Click the Name link of the first row, or goto its href.
    - expect: URL /allocation/requests/view/98355/ (admin detail page)

#### 1.8. 6.8 Approved Requests ordering by project_name

**File:** `tests/rcallocation/06-history-approved/approved-ordering.spec.ts`

**Steps:**
  1. [verified live] Read the link text (project_name) of every row via page.evaluate and compare with a sorted copy.
    - expect: First 5 names are 'a', 'a', 'a', 'a', 'a' with allocation IDs 98355, 145002, 130198, 131488, 58545 (in that rendered order)
    - expect: Last 5 names are all 'voluptatem' with IDs 6472, 41837, 125569, 117929, 147375 (in that rendered order)
    - expect: The list equals both a binary sort and a case-insensitive sort of project_name (no mismatch index)
    - expect: There are 1493 repeated names (1601 rows, 108 distinct names), so rows with equal names have no guaranteed order. Assert order by project_name only, not by ID
  2. [verified live] Check case handling.
    - expect: No project_name contains an upper-case letter and none starts with a digit or symbol, so case sensitivity of the ordering cannot be shown on this data. If a tester adds an allocation named with an upper-case initial, record where it sorts (database collation decides)
  3. [derived from code] Confirm the query in allocation_approved/views.py.
    - expect: Top-level allocations (no parent_request) with status in A, X, J, ordered by project_name. History records (children) are not listed; for example 146946 and 138447 do not appear as rows in the approved list

#### 1.9. 6.9 Approved Requests NameFilter (client-side)

**File:** `tests/rcallocation/06-history-approved/approved-filter.spec.ts`

**Steps:**
  1. [verified live] On the loaded approved list, locate input[name='DataTableOptions__filter__q'] (class 'form-control', placeholder 'Filter'). Fill '' then pressSequentially('pwtest', { delay: 30, timeout: 10000 }) and wait 1.5 s.
    - expect: Only one row stays visible: 'pwtest-valid' / 'PW validation test' (152181). Footer 'Displaying 1 item'
    - expect: No network request is made (client-side filter; the URL stays /allocation/approved_requests/)
  2. [verified live] Replace the text with 'PWTEST' (upper case).
    - expect: Same single row: the filter is case-insensitive
  3. [verified live] Replace the text with 'validation' (a word that is in the description only).
    - expect: Same single row (pwtest-valid): the filter matches the description text in the Name cell as well as the project_name
  4. [verified live] Replace the text with 'zzzznomatch'.
    - expect: A single row 'No items to display.' is visible; the footer text is empty; all 1601 data rows are hidden
  5. [verified live] Clear the filter input.
    - expect: All 1601 rows are visible again in the original order; footer 'Displaying 1601 items'; first visible name 'aEnhanced mission-critical synergy'

#### 1.10. 6.10 approved_requests/edit_request GET for an A record (400)

**File:** `tests/rcallocation/06-history-approved/approved-edit-request.spec.ts`

**Steps:**
  1. [verified live] Do not submit anything. GET /allocation/approved_requests/edit_request/98355/ with fetch (credentials same-origin, 20 s abort).
    - expect: HTTP 400; plain-text body 'Allocation cannot be edited in its current state' (plus a trailing HTML comment token)
    - expect: Before NECTAR-17320 this was HTTP 500, 'TypeError: 'NoneType' object is not callable' from AllocationUpdateView.get_form. The approved list does not offer an Edit action, so no UI link leads here
