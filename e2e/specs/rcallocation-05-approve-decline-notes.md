# rcallocation 05: Approve / Decline / Admin notes lifecycle

## Application Overview

Regression baseline for the Approve / Decline / Admin notes lifecycle of the Allocations dashboard (rcallocation) on http://dashboard-s.rcdev.nectar.org.au:8000, ahead of a refactor that intends no UI change. Observed live on 2026-10-30 as the pt.openrc user (allocation admin, sorrison@gmail.com). Unlike suites 01 to 04 this suite SUBMITS forms. The user approved submissions on the dev system, restricted to allocations 152181 (pwtest-valid) and 152182 (pwtest-202610301345-b). Both started in status E.

GLOBAL RULES FOR EXECUTION
- Run seed.spec.ts first. Keep its blocks (challenges.cloudflare.com, ardc.edu.au, survey.rc.nectar.org.au), dialog auto-accept and 15s default timeout. Rerun the seed if the session expires.
- Only the two pwtest allocations may be submitted. Never touch another allocation. Read-only GETs elsewhere are fine. Stay on dashboard-s. Do not open the Freshdesk or Grafana links (their dev hrefs start with 'None').
- The scenarios MUTATE state and are NOT independently re-runnable on the same IDs. 152181 and 152182 were left in J and E respectively. To re-run, create two fresh E allocations (suite 02 form) and substitute their IDs. The history IDs below are the live results for the first run only, so assert the pattern (one new history row per transition) rather than the exact IDs on later runs.
- Run scenarios in order: 5.1 to 5.2 (notes), 5.3 to 5.6 (decline and resubmit, on 152182), 5.7 to 5.11 (approve, on 152181), 5.12 to 5.15 (amend, approve changes, decline changes, on 152181), 5.16 (history, read-only).
- The seed leaves /allocation/ open. The first page.goto away can raise a beforeunload dialog that the seed auto-accepts. Retry the navigation once.
- Collapsed accordion panels hide fields. Expand the panel first, or set values with page.evaluate and dispatch input and change events. Pass { timeout: 10000 } to every action and wait. Submit buttons are input[type=submit]. The ignore-warnings buttons are input[type=button] with the values 'Submit ignoring warnings' (user edit forms) and 'Approve ignoring warnings' (approve form).
- Do not goto /allocation/approved_requests/ (about 1600 rows, times out). Use detail and history URLs directly. For lists, same-origin fetch plus DOMParser is reliable.
- Selectors by duplicate DOM id are ambiguous (see suite 04 discrepancy 6). Use link text or href.

LIVE TRANSITION LOG (first run, 2026-10-30)
| Step | Allocation | Before | After | New history record IDs |
| Admin notes save | 152181 | E | E (unchanged) | none |
| Decline | 152182 | E | R | 152185 (Submitted, 3:49 a.m.) |
| Resubmit | 152182 | R | E | 152186 (Declined, 4:01 a.m.) |
| Approve | 152181 | E | A | 152187 (Submitted, 2:42 a.m.) |
| Amend | 152181 | A | X | 152188 (Approved, 4:19 a.m.) |
| Approve changes | 152181 | X | A | 152189 (Update requested, 4:20 a.m.) |
| Amend again | 152181 | A | X | 152190 (Approved, 4:21 a.m.) |
| Decline changes | 152181 | X | J | 152191 (Update requested, 4:22 a.m.) |
Final state: 152181 = J ('Update declined'), 152182 = E ('Submitted').
Pre-existing history of 152182 before this suite: 152184 (3:33 a.m.) and 152183 (2:45 a.m.), both Submitted, plus the current record 152182 (3:49 a.m. at baseline). The decline then added 152185.

OBSERVED DISCREPANCIES FROM THE BRIEF (live results are the baseline)
1. The Edit Notes document title is 'Edit allocation Admin notes - Nectar Dashboard', not 'Edit Allocation Admin Notes'. The page has an empty h1 and no visible heading. The textarea label is 'Private notes for admins', with no help text. Breadcrumb: 'Allocations / Pending Requests / None'.
2. Decline and approve pages also have an empty h1. The brief's titles ('Decline or Request Amendment from User', 'Approve Request') are the document titles, not visible headings. The decline form's section h4 is 'Allocation Classification' even though it holds only the read-only fields and the reason.
3. Decline form labels: 'Project identifier' (project_name), 'Project allocation title' (project_description), 'Reason' (status_explanation), button 'Decline Request'. The brief called the textarea status_explanation 'Comment'; on the decline form it is labelled 'Reason'. On the approve form it is labelled 'Comment' with popover help 'Reviewer Comment'.
4. Approve form labels differ in case and wording from the brief: 'Associated site' (not 'Associated Site'), 'National funding' (not 'National'), 'Special RC-NAS approval reasons' (not 'Special approval'). Help text is not inline: it is the data-content attribute of an img.help-popover in each label (see 5.7).
5. The approve form shows NO compute quota fields (no SU, cores, RAM, instances). Only per-zone Volume Service Storage inputs and Shared File System inputs render, all empty. The Bundle select (prefilled 'Standard' for 152181) drives the allocation values. Prefilled quota inputs: none.
6. Approver warning on approval was 'Problem with approver registration: contact Core Services', not APPROVER_NOT_AUTHORIZED or NO_VALID_GRANTS. The pt.openrc user triggers it on every approval. The grants and authorisation warnings were not reproduced live (see 5.17).
7. Approve changes: the page at approve_change_request/152181/ posts to action '/allocation/requests/approve_request/152181/'. The warning re-render therefore appears at the approve_request URL, not approve_change_request. After 'Approve ignoring warnings' the redirect is to /allocation/requests/.
8. The amend form (edit_change_request) submitted with NO required-field errors and NO warnings on 152181, so the 'fill required past-year usage and grant fields' step was not needed. The 'Attention Required' modal does auto-open. Submitting while the modal is closed redirects straight to /allocation/user_requests/.
9. After an amendment (X) the history row shows deltas of 0 in all five numeric columns, because nothing changed in the request.
10. A J record (Update declined) still shows 'Approve changes' and 'Decline changes' on the admin detail page, but is not listed on the Pending list. GET approve_change_request/152181/ on the J record returned HTTP 200 (a form), with no guard.
11. After resubmit (R to E), 152182 keeps the previous approver sorrison@gmail.com in the Approver column and the user detail still renders a 'Reviewer Comment' heading (see 5.6).
12. The My Requests row for an R record still offers 'Edit request', as expected.
13. A user-edit submit that returns warnings does NOT change the URL (POST re-render at the same URL) and creates no history row. Only the 'ignoring warnings' submit saves.

TEST DATA
- 152181: project_name 'pwtest-valid', description 'PW validation test', contact sorrison@gmail.com, bundle Standard (4000 SUs, 64 cores, 128 GB RAM, 500 GB object storage), start status E, submitted Oct. 30, 2026, 2:42 a.m.
- 152182: project_name 'pwtest-202610301345-b', description 'PW warnings flow test', contact sorrison@gmail.com, Custom bundle (16000 SUs, 256 cores, 640 GB RAM, 6000 GB object storage), start status E.
- Admin notes text used: 'PW regression note A1'. Decline reason: 'PW decline reason B1'. Decline-changes reason: 'PW decline changes reason G1'.
- Console errors (3 to 7 per page) were present on every page and were not investigated. They are the same before and after the refactor.

## Test Scenarios

### 1. Approve / Decline / Admin notes lifecycle

**Seed:** `/home/sam/projects/nectar/nectar-dashboard/seed.spec.ts`

#### 1.1. 5.1 Edit admin notes form structure

**File:** `tests/rcallocation/05-approve-decline-notes/notes-form.spec.ts`

**Steps:**
  1. [verified live] Run seed.spec.ts, then goto /allocation/requests/view/152181/ and click 'Add/edit admin notes' (href /allocation/requests/edit_notes/152181/).
    - expect: URL is /allocation/requests/edit_notes/152181/; document title 'Edit allocation Admin notes - Nectar Dashboard'
    - expect: h1 is empty; no other heading; breadcrumb 'Allocations / Pending Requests / None' ('Pending Requests' links to /allocation/requests/)
    - expect: Form action /allocation/requests/edit_notes/152181/, method POST
    - expect: Exactly one visible field: textarea name 'notes', id 'id_notes', label 'Private notes for admins', not required, empty at baseline, no help text
    - expect: Exactly one submit: input[type=submit] value 'Submit'; no Cancel link

#### 1.2. 5.2 Save admin notes: redirect, display, no timestamp change, no history

**File:** `tests/rcallocation/05-approve-decline-notes/notes-save.spec.ts`

**Steps:**
  1. [verified live] Before saving, read Last updated on /allocation/requests/view/152181/ ('Oct. 30, 2026, 2:42 a.m.') and the history table (1 row).
    - expect: Allocation admin notes paragraph reads 'None'
    - expect: History shows one row: Submitted, Oct. 30, 2026, 2:42 a.m.
  2. Fill #id_notes with 'PW regression note A1' and click input[type=submit].
    - expect: Redirect to /allocation/requests/view/152181/ (the admin detail page), title 'View allocation request - Nectar Dashboard'
    - expect: No flash message or alert is shown
  3. Read the detail page and history.
    - expect: Allocation admin notes paragraph reads 'PW regression note A1'; 'Add/edit admin notes' still present
    - expect: Submit date and Last updated both still 'Oct. 30, 2026, 2:42 a.m.' (save_without_updating_timestamps)
    - expect: State still 'Submitted'; 152181 still listed on /allocation/requests/
    - expect: History table still has exactly 1 row (152181, Submitted, 2:42 a.m.); NO new history record
    - expect: The notes persist after later transitions (still shown after approval, see 5.10)

#### 1.3. 5.3 Decline form structure for a new request (152182)

**File:** `tests/rcallocation/05-approve-decline-notes/decline-form.spec.ts`

**Steps:**
  1. [verified live] goto /allocation/requests/view/152182/ and click 'Decline with Reason' (href /allocation/requests/reject_request/152182/).
    - expect: URL /allocation/requests/reject_request/152182/; title 'Decline or Request Amendment from User - Nectar Dashboard'; h1 empty; only h4 is 'Allocation Classification'
    - expect: Breadcrumb 'Allocations / Pending Requests / None'
    - expect: Fields: project_name (label 'Project identifier', value 'pwtest-202610301345-b', readonly), project_description (label 'Project allocation title', value 'PW warnings flow test', readonly), status_explanation (textarea, label 'Reason', not required, empty), hidden csrfmiddlewaretoken
    - expect: No help text on any field; one submit input value 'Decline Request'
    - expect: Form action /allocation/requests/reject_request/152182/

#### 1.4. 5.4 Decline a new request: E to R

**File:** `tests/rcallocation/05-approve-decline-notes/decline-submit.spec.ts`

**Steps:**
  1. [verified live] Fill #id_status_explanation with 'PW decline reason B1' and click input[type=submit].
    - expect: Redirect to /allocation/requests/ (Pending Requests); no flash message
    - expect: 152182 is no longer in the Pending list
    - expect: History of 152182 (/allocation/requests/view/152182/history): 4 rows in order Declined (Oct. 30, 2026, 4:01 a.m., Approver sorrison@gmail.com), 152185 Submitted (3:49 a.m., Approver empty), 152184 Submitted (3:33 a.m.), 152183 Submitted (2:45 a.m.). Values for R and E rows: SUs 16000, Cores 256, RAM 640, Object Storage 6000, Volume Storage '-', Bundle '-'. One new history record: 152185
  2. Read /allocation/user_requests/ (My Requests) for 152182.
    - expect: Row: State 'R', Name 'pwtest-202610301345-b' plus 'PW warnings flow test', Current Associated Site '-', National 'False', Contact sorrison@gmail.com, Last Updated 'Oct. 30, 2026', Expiry '-'
    - expect: Actions: primary link 'Edit request' (/allocation/user_requests/edit_request/152182/); can_user_edit includes R
  3. Open /allocation/user_requests/view/152182/.
    - expect: State 'Declined'
    - expect: h3 sections include 'Requested Resources', 'Approved Resources (at the time of this record)' and, last, 'Reviewer Comment'
    - expect: Reviewer Comment text 'PW decline reason B1'
    - expect: Only button besides the project switcher: 'Edit request' (/allocation/user_requests/edit_request/152182/)

#### 1.5. 5.5 Decline guard returns 400 for an already declined allocation

**File:** `tests/rcallocation/05-approve-decline-notes/decline-guard.spec.ts`

**Steps:**
  1. [verified live] With 152182 in status R, GET /allocation/requests/reject_request/152182/.
    - expect: HTTP 400; body 'Allocation already declined' (plain text, no template)

#### 1.6. 5.6 Resubmit a declined request: R to E (warnings flow)

**File:** `tests/rcallocation/05-approve-decline-notes/resubmit-after-decline.spec.ts`

**Steps:**
  1. [verified live] goto /allocation/user_requests/edit_request/152182/ (title 'Edit Allocation Request - Nectar Dashboard') and click the visible input[type=submit] 'Submit' without changing anything.
    - expect: URL does not change (POST re-render at the same edit URL); no new history row
    - expect: A warning panel appears: 'Warnings: Please review the following warnings. Then either modify the form and "Submit" it again, or "Submit ignoring warnings".' followed by 'Requests for access to special flavors must be explained in the "Justification ..." field. More information'
    - expect: A visible button input[type=button] value 'Submit ignoring warnings' appears; hidden input name 'ignore_warnings' (empty)
  2. Click 'Submit ignoring warnings'.
    - expect: Redirect to /allocation/user_requests/ (My Requests)
    - expect: My Requests row for 152182: State 'E', Last Updated 'Oct. 30, 2026', Actions 'Edit request'
    - expect: History of 152182 has 5 rows: current 152182 Submitted (4:02 a.m., Approver sorrison@gmail.com), 152186 Declined (4:01 a.m.), 152185, 152184, 152183 (Submitted). One new history record: 152186
    - expect: Admin detail /allocation/requests/view/152182/ shows State 'Submitted' and again offers 'Review & Approve' and 'Decline with Reason'; the heading 'Reviewer Comment' is still present (the previous decline reason is retained)

#### 1.7. 5.7 Approve form structure (152181)

**File:** `tests/rcallocation/05-approve-decline-notes/approve-form.spec.ts`

**Steps:**
  1. [verified live] goto /allocation/requests/view/152181/ and click 'Review & Approve' (href /allocation/requests/approve_request/152181/).
    - expect: Title 'Approve Request - Nectar Dashboard'; h1 empty; h2 'Cloud Resources'; h3 'Availability Zone Resources'; final h4 'Allocation Classification'
    - expect: project_name: label 'Project identifier', value 'pwtest-valid', disabled and readonly; popover help 'A short name used to identify your project.<br>Must contain only letters and numbers.<br>16 characters max.'
    - expect: project_description: label 'Project allocation title', value 'PW validation test', disabled and readonly
    - expect: estimated_project_duration: select (1-month, 3-months, 6-months, 12-months), selected '12-months'
    - expect: bundle: select, required (asterisk), options '---------', Standard, Powerful, Extreme; Standard preselected; hint text near it 'Is this a suitable bundle? Review the Resource Bundle Table before approving.'
    - expect: Quota inputs (all type number, all EMPTY, none required): Volume Service 'Storage' per zone for Auckland (NZ), Auckland (NZ) encrypted, Intersect (NSW), Intersect (NSW) encrypted, Melbourne University, Melbourne University encrypted, Melbourne University performance, Monash (VIC), Monash (VIC) encrypted, QRIScloud, QRIScloud encrypted, Swinburne (VIC), Swinburne (VIC) encrypted, Tasmania, Tasmania encrypted (names quota-volume.gigabytes__<zone>); Shared File System for Auckland (NZ) and Monash (VIC): Shares, Storage, Snapshots, Snapshot storage (quota-share.*). No compute, SU, RAM or object storage input
    - expect: associated_site: select, required, label 'Associated site', options '---------', Auckland, Intersect, Monash, QCIF, Swinburne, TPAC, University of Melbourne, ARDC; popover help (data-content) 'The Approver will normally set the Associated Site to their own node.'
    - expect: national: checkbox, label 'National funding', unchecked; popover help "The Approver should check 'National funding' for all allocations that meet the Nectar national funding criteria."
    - expect: special_approval: text, maxlength 1024, label 'Special RC-NAS approval reasons', empty; popover help 'Use this field to record reasons the allocation is approved as National despite not meeting the primary criteria; i.e. a current competitive, NCRIS support or ARDC support. See the RC-NAS policy for the possible reasons. This is only visible to allocation admins'
    - expect: status_explanation: textarea, label 'Comment', popover help 'Reviewer Comment', empty (initial forced to '')
    - expect: Hidden: csrfmiddlewaretoken, ignore_warnings (empty). One submit input value 'Approve Request'. Form action /allocation/requests/approve_request/152181/

#### 1.8. 5.8 Approve: Associated site required validation

**File:** `tests/rcallocation/05-approve-decline-notes/approve-required-site.spec.ts`

**Steps:**
  1. [verified live] On the approve form leave Associated site at '---------'. Read select.validationMessage.
    - expect: Client-side: the select is invalid, validationMessage 'Please select an item in the list.' and the browser blocks submit
  2. Remove the required attribute from #id_associated_site with page.evaluate, then click input[type=submit].
    - expect: Stays on /allocation/requests/approve_request/152181/; no redirect, status unchanged (E)
    - expect: Alert div 'alert alert-danger': 'Please fix the errors highlighted below and resubmit.'
    - expect: #id_associated_site-group has class 'has-error' with help-block 'This field is required.'
    - expect: Other values are retained (Bundle still Standard)

#### 1.9. 5.9 Approve: approver registration warning and ignore

**File:** `tests/rcallocation/05-approve-decline-notes/approve-warning-ignore.spec.ts`

**Steps:**
  1. [verified live] Select Associated site 'QCIF', leave National unchecked and Comment empty, click 'Approve Request'.
    - expect: No redirect; page re-renders at /allocation/requests/approve_request/152181/ with 'alert alert-warning': 'Warnings Please review the following warnings. Then either modify the form and "Submit" it again, or "Submit ignoring warnings". Problem with approver registration: contact Core Services More information'
    - expect: 'More information' link: https://support.ehelp.edu.au/support/solutions/articles/6000220088#APPROVER_PROBLEM, target _blank (do not click)
    - expect: Buttons now: 'Approve Request' (submit) and 'Approve ignoring warnings' (input[type=button])
    - expect: Form values retained: Associated site QCIF, Bundle Standard, National unchecked
    - expect: No history row created yet (history of 152181 still 1 row)
  2. Click 'Approve ignoring warnings'.
    - expect: Redirect to /allocation/requests/ (Pending Requests); no flash message
    - expect: 152181 no longer appears in the Pending list

#### 1.10. 5.10 State and actions after approval: E to A

**File:** `tests/rcallocation/05-approve-decline-notes/approve-outcome.spec.ts`

**Steps:**
  1. [verified live] Read /allocation/requests/view/152181/ after approval.
    - expect: Right table: State 'Approved', Approver 'sorrison@gmail.com', Project Identifier 'pwtest-valid', Project ID '(Project not linked)', Associated Site 'QCIF', National funded 'no', Provisioned 'no'
    - expect: Left table: Submit date 'Oct. 30, 2026, 2:42 a.m.'; Last updated 'Oct. 30, 2026, 4:19 a.m.' (modified time did change)
    - expect: h3 order starts 'Current Resources' (no 'Requested Resources'); ends 'Allocation admin notes'; NO 'Reviewer Comment' (comment was empty)
    - expect: Notes paragraph still 'PW regression note A1'
    - expect: Buttons: 'Add/edit admin notes', 'View History', 'Related tickets' only; NO 'Review & Approve', 'Decline with Reason', 'Approve changes' or 'Decline changes'
  2. Read My Requests and the user detail page for 152181.
    - expect: My Requests row: State 'A', Current Associated Site 'QCIF', National 'False', Actions primary link 'Amend/Extend allocation' (/allocation/user_requests/edit_change_request/152181/)
    - expect: /allocation/user_requests/view/152181/ shows a button 'Request amendment' (same href) and no 'Edit request'
  3. Read the history table.
    - expect: 2 rows: 152181 Approved (4:19 a.m., Approver sorrison@gmail.com, Bundle Standard, SUs 4000, Cores 64, RAM 128, Object Storage 500, Volume '-') and 152187 Submitted (2:42 a.m., Approver empty, same values). One new history record: 152187

#### 1.11. 5.11 Approve guard returns 400 for an already approved allocation

**File:** `tests/rcallocation/05-approve-decline-notes/approve-guard.spec.ts`

**Steps:**
  1. [verified live] With 152181 in status A, GET /allocation/requests/approve_request/152181/.
    - expect: HTTP 400; body 'Allocation already approved'

#### 1.12. 5.12 Amend an approved allocation: A to X

**File:** `tests/rcallocation/05-approve-decline-notes/amend-request.spec.ts`

**Steps:**
  1. [verified live] goto /allocation/user_requests/edit_change_request/152181/ and wait 2.5s.
    - expect: Title 'Request Allocation Extension - Nectar Dashboard'; h3 'Edit Allocation Request: About the Project'
    - expect: Modal #modal-nags (class 'modal in') is visible: '× Attention Required The following items require your attention before you submit this amendment. These may be a result of changes that we have made to this form since your last submission. Please provide an impact and benefit statement for your project. Also include any publications which have occurred since your last renewal. Providing this information supports the ongoing sustainability of the ARDC Nectar Research Cloud. Close'
    - expect: Modal buttons: '×' and 'Close', both data-dismiss
  2. Click 'Close' in #modal-nags, then click the visible input[type=submit] 'Submit'.
    - expect: No validation errors and no warning panel; redirect to /allocation/user_requests/ (My Requests)
    - expect: My Requests row for 152181: State 'X', Actions primary link 'Edit amend/extend request' (/allocation/user_requests/edit_change_request/152181/)
    - expect: /allocation/user_requests/view/152181/ buttons: 'Back to My Requests', 'Edit change request' (same href)
    - expect: Admin detail: State 'Update requested'; Last updated 'Oct. 30, 2026, 4:20 a.m.'; h3 begins 'Requested Resources', 'Current Resources'; buttons 'Add/edit admin notes', 'Approve changes' (/allocation/requests/approve_change_request/152181/), 'Decline changes' (/allocation/requests/reject_request/152181/), 'View History', 'Related tickets'
    - expect: 152181 is back on the Pending list
    - expect: History: 3 rows. 152181 Update requested (4:20 a.m., Approver sorrison@gmail.com, SUs 0, Cores 0, RAM 0, Object 0, Volume 0 as deltas), 152188 Approved (4:19 a.m., current values 4000/64/128/500/-), 152187 Submitted. One new history record: 152188

#### 1.13. 5.13 Approve changes: X to A

**File:** `tests/rcallocation/05-approve-decline-notes/approve-changes.spec.ts`

**Steps:**
  1. [verified live] On /allocation/requests/view/152181/ (X) click 'Approve changes'.
    - expect: URL /allocation/requests/approve_change_request/152181/; title 'Approve Request - Nectar Dashboard'
    - expect: Same fields as 5.7 but Associated site prefilled 'QCIF', Bundle 'Standard', Comment empty; submit 'Approve Request'
    - expect: Form action is /allocation/requests/approve_request/152181/ (NOT approve_change_request)
  2. Click 'Approve Request'.
    - expect: No redirect; the warning panel (same text as 5.9, 'Problem with approver registration: contact Core Services') re-renders at URL /allocation/requests/approve_request/152181/, and the admin detail is still State 'Update requested'
    - expect: Click 'Approve ignoring warnings': redirect to /allocation/requests/
    - expect: Admin detail: State 'Approved'; Last updated 'Oct. 30, 2026, 4:21 a.m.'; buttons back to 'Add/edit admin notes', 'View History', 'Related tickets'
    - expect: My Requests row: State 'A', Actions 'Amend/Extend allocation'
    - expect: History top 2 rows: 152181 Approved (4:21 a.m., 4000/64/128/500/-), 152189 Update requested (4:20 a.m., 0/0/0/0/0). One new history record: 152189

#### 1.14. 5.14 Amend again then decline changes: A to X to J

**File:** `tests/rcallocation/05-approve-decline-notes/decline-changes.spec.ts`

**Steps:**
  1. [verified live] Repeat the 5.12 amend flow on 152181 (close #modal-nags, Submit).
    - expect: Redirect to /allocation/user_requests/; status X ('Update requested'); admin detail again shows 'Approve changes' and 'Decline changes'
    - expect: One new history record: 152190 (Approved, 4:21 a.m., 4000/64/128/500/-); current row Update requested 4:22 a.m. with 0/0/0/0/0
  2. On the admin detail click 'Decline changes' (href /allocation/requests/reject_request/152181/).
    - expect: Same form as 5.3 (title 'Decline or Request Amendment from User - Nectar Dashboard'; read-only 'Project identifier' 'pwtest-valid' and 'Project allocation title' 'PW validation test'; 'Reason' textarea; submit 'Decline Request')
  3. Fill 'Reason' with 'PW decline changes reason G1' and click 'Decline Request'.
    - expect: Redirect to /allocation/requests/; 152181 not on the Pending list
    - expect: Admin detail: State 'Update declined' (letter J); Approver sorrison@gmail.com; Last updated 'Oct. 30, 2026, 4:22 a.m.'; h3 includes 'Requested Resources', 'Current Resources', 'Reviewer Comment' (text 'PW decline changes reason G1'), 'Allocation admin notes'
    - expect: Admin detail buttons: 'Add/edit admin notes', 'Approve changes', 'Decline changes', 'View History', 'Related tickets' (the J record still offers both change buttons)
    - expect: My Requests row: State 'J', Actions primary link 'Edit amend/extend request' (/allocation/user_requests/edit_change_request/152181/)
    - expect: User detail: State 'Update declined', Reviewer Comment 'PW decline changes reason G1', button 'Edit change request' (same href), no 'Request amendment'
    - expect: One new history record: 152191 (Update requested, 4:22 a.m., 0/0/0/0/0)

#### 1.15. 5.15 Decline guard on a J record, and approve_change GET on J

**File:** `tests/rcallocation/05-approve-decline-notes/j-state-guards.spec.ts`

**Steps:**
  1. [verified live] With 152181 in status J, GET /allocation/requests/reject_request/152181/.
    - expect: HTTP 400; body 'Allocation already declined'
  2. [verified live] With 152181 in status J, GET /allocation/requests/approve_change_request/152181/ (read-only GET, do not submit).
    - expect: HTTP 200 with the approve form (no 400 guard). Record as existing behaviour; do not submit it

#### 1.16. 5.16 Final history tables for 152181 and 152182

**File:** `tests/rcallocation/05-approve-decline-notes/history-tables.spec.ts`

**Steps:**
  1. [verified live] goto /allocation/requests/view/152181/history and read the table.
    - expect: Title 'Allocation Requests - Nectar Dashboard'; h2 'History'
    - expect: Columns in order: Project name, Approver, Bundle, SUs, Cores, RAM, Object Storage, Volume Storage, Status, Modification time. Rows are ordered newest first and the Project name cell links to /allocation/requests/view/<id>/
    - expect: 6 rows in order. 152181: 'Update declined' | Oct. 30, 2026, 4:22 a.m. | Approver sorrison@gmail.com | Standard | 0 | 0 | 0 | 0 | 0 (deltas). 152191: 'Update requested' | 4:22 a.m. | sorrison@gmail.com | Standard | 0 | 0 | 0 | 0 | 0. 152190: 'Approved' | 4:21 a.m. | sorrison@gmail.com | Standard | 4000 | 64 | 128 | 500 | '-'. 152189: 'Update requested' | 4:20 a.m. | sorrison@gmail.com | Standard | 0 | 0 | 0 | 0 | 0. 152188: 'Approved' | 4:19 a.m. | sorrison@gmail.com | Standard | 4000 | 64 | 128 | 500 | '-'. 152187: 'Submitted' | 2:42 a.m. | Approver empty | Standard | 4000 | 64 | 128 | 500 | '-'
    - expect: Project name cell for every row is 'PW validation test'; Volume Storage is '-' for A, E rows and '0' for X, J rows (delta)
  2. [verified live] goto /allocation/requests/view/152182/history and read the table.
    - expect: 5 rows. 152182: 'Submitted' | 4:02 a.m. | sorrison@gmail.com | '-' | 16000 | 256 | 640 | 6000 | '-'. 152186: 'Declined' | 4:01 a.m. | sorrison@gmail.com | same values. 152185: 'Submitted' | 3:49 a.m. | Approver empty | same values. 152184: 'Submitted' | 3:33 a.m. | empty | same values. 152183: 'Submitted' | 2:45 a.m. | empty | same values
    - expect: Bundle column '-' (Custom bundle); project name cell 'PW warnings flow test'. R and E rows show requested values, A shows current values, X and J show deltas

#### 1.17. 5.17 Approver warning codes not reproduced live (derived from code)

**File:** `tests/rcallocation/05-approve-decline-notes/approver-warnings-derived.spec.ts`

**Steps:**
  1. [derived from code; checkers.py, NOT verified live] Use a controlled unit or integration test over the approver checks with a non-admin-site approver and a National approval without grants.
    - expect: APPROVER_NOT_AUTHORIZED: 'Quota should be authorized by the other site before...' (suffix per checkers.py; confirm the full text in code before asserting)
    - expect: NO_VALID_GRANTS: 'There are no current competitive grants for this request. Either approve it as Local, or add a Special approval reason.' (from the brief; not seen live because 152181 has Local approval and the approver check fired first)
    - expect: Each warning renders in alert-warning with a 'More information' link to a support article anchor equal to the code, and reveals the 'Approve ignoring warnings' button
    - expect: Live equivalent: approver problem uses anchor #APPROVER_PROBLEM (see 5.9)

#### 1.18. 5.18 Decline flow status letters by prior status (derived from code)

**File:** `tests/rcallocation/05-approve-decline-notes/reject-status-mapping-derived.spec.ts`

**Steps:**
  1. [derived from code; allocation/forms.py and views.py, partly verified live] Review the reject form's save logic.
    - expect: Current status E (or N) goes to R (live: 152182 E to R)
    - expect: Current status X goes to J (live: 152181 X to J)
    - expect: Rejecting an already R or J record returns HTTP 400 'Allocation already declined' (live in 5.5 and 5.15)
    - expect: Approving an A record returns 400 'Allocation already approved' (live in 5.11)
    - expect: N and an approve of N were not exercised (no N record available; do not create one in this suite)
