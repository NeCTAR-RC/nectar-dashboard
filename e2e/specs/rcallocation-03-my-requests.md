# rcallocation 03: My Requests list and detail, user edit and amend forms

## Application Overview

Regression baseline for the My Requests area of the Allocations dashboard (rcallocation) on http://dashboard-s.rcdev.nectar.org.au:8000, captured before a refactor that intends no UI change. Covers the My Requests list (/allocation/user_requests/), the user detail page, the user edit form (edit_request) and the user amend form (edit_change_request). Observed live on 2026-10-30 as the pt.openrc user (an allocation admin, contact sorrison@gmail.com). Notifications go to a dev system.

Tags: "verified live" means observed in the browser. "derived from code" means read from source and not exercised live.

GLOBAL RULES FOR EXECUTION
- Never navigate to, click or open any URL outside http://dashboard-s.rcdev.nectar.org.au:8000. Record external hrefs only. Do not run the DOI checker.
- Never remove or bypass the seed (it blocks challenges.cloudflare.com, ardc.edu.au and survey.rc.nectar.org.au, auto-accepts dialogs, sets a 15s default timeout, logs in via websso and opens /allocation/). If the session expires, rerun the seed.
- Page titles all end with " - Nectar Dashboard".
- SUBMISSIONS: only 152181 and 152182 may be submitted successfully. On 152179 (status A, the admin's own approved allocation) only submit when failure is certain (a required field cleared). Never click "Submit ignoring warnings" on 152179.

TEST DATA (real IDs on dashboard-s)
- 152179: identifier gdfgdfgdf, description "fsdgfdsgdsfg", status A, site QCIF, National True, last updated April 30, 2026 (list), Powerful bundle. History: 152179 itself plus 152180 (Submitted).
- 152181: identifier pwtest-valid, description "PW validation test", status E, Standard bundle, last updated Oct. 30, 2026. History: only itself.
- 152182: identifier pwtest-202610301345-b, description "PW warnings flow test", status E, Custom bundle (16000 SUs, 256 VCPUs, 640 GB RAM, special flavors enabled). The edit scenario (3.5) changes this record, so later scenarios must treat use case text and history length as relative to the state found.
- History (parent_request) records of other allocations: 146946, 138447, 137049. History records of 152182: 152183, 152184 (152184 was created by the edit in scenario 3.5).
- Non-existent id: 99999999.
- Statuses R, N, X and J have no row in this user's My Requests; scenarios for them are derived from code.

PRIOR STATE OF 152182 (found before this run's edit)
/allocation/requests/view/152182/history showed 2 rows: current 152182 (Submitted, modified Oct. 30, 2026, 3:33 a.m.) and history record 152183 (Submitted, 2:45 a.m.). Use case was "Playwright warnings flow test" (unchanged text), so the earlier interrupted runs had already produced at least one edit. After the scenario 3.5 edit the history has 3 rows (152182 at 3:49 a.m., 152184 at 3:33 a.m., 152183 at 2:45 a.m.).

CHANGES MADE TO ALLOCATIONS DURING EXPLORATION
- 152182: one successful edit via "Submit ignoring warnings" (appended " [regression edit 03]" to use case). Status E before, E after. Last updated and submit date moved from Oct. 30, 2026, 3:33 a.m. to 3:49 a.m. New history record 152184.
- No other allocation changed. 152179 and 152181 were not submitted. Three invalid submits (two on 152182, one on 152179) were rejected by validation and changed nothing.

OBSERVED DISCREPANCIES AND ODDITIES (live results are the baseline)
1. The page title of the amend form is "Request Allocation Extension" but its visible h3 is "Edit Allocation Request: About the Project" (same h3 as the edit form). The amend breadcrumb ends in "None".
2. ~~user_requests/edit_request/<history id>/ and edit_change_request/<history id>/ return 200 while user_requests/view/<history id>/ returns 403.~~ **Fixed, deployed to dashboard-s and verified live on 2026-10-30:** the views' access check now runs, so both URLs return 403 for history records. See scenario 1.20 and suite 01 discrepancy 9.
3. ~~user_requests/edit_request/152179/ (status A) returns 200, and edit_change_request/152182/ and 152181/ (status E) return 200. The view does not guard by status, even though the list only offers the matching action.~~ **Fixed by the allocation status fix (NECTAR-17320); not yet verified live.** edit_request opens only for N, E and R; edit_change_request only for A, X and J. Other statuses return HTTP 400 ('Allocation request cannot be edited in its current state' or 'Allocation cannot be amended in its current state'). Scenario 5.2 and the non-admin edit test in `nonadmin.spec.ts` are updated.
4. The amend form (152179) shows "Grant Type", "Grant Subtype" and "Total funding (AUD)" required errors in panel 7 on any invalid submit, because the grant row has years prefilled (2026, 2027) but no type or amount.
5. Time zone rendering is inconsistent within the session: the 152182 history showed "3:49 a.m." on one run and "2:49 p.m." on a later load of the same record (about an 11 hour offset), and the detail page showed 6:01 a.m. for 152179 where history showed 4:01 p.m. Assert dates only, or compare times within a single page.
6. The detail page for 152182 shows no success message after an edit. The redirect target list has an empty hidden "messages" container.
7. The edit form of 152182 includes the text "Usage Types", usage_patterns and geographic_requirements in the Resources step panel panelJustification (not in panel 2).

NOTES FOR TEST GENERATION (accordion panels, hangs)
- Forms are Bootstrap accordions. Details step panel ids: panelOne to panelEight (edit) and panelOne to panelNine (amend, because it has an extra 8. Publication/Output and Impact panel). Resources step (hidden until "Continue"/STEP 2): panelBundle, panelExtras, panelJustification, panelSubmit. Only panelOne and panelBundle are open on load.
- Expand a panel before interacting: click its heading link (for example getByRole('link', { name: '2. Usage Information' })) or the Next link, then expect the field to be visible. Never fill, click, check or select a hidden field.
- Every action and wait must carry an explicit timeout, for example page.fill(sel, v, { timeout: 10000 }), locator.click({ timeout: 10000 }), page.waitForURL(re, { timeout: 15000 }).
- To read form structure use page.evaluate (no visibility wait). To set a value on a hidden field set el.value and dispatch input and change events through page.evaluate.
- The Submit control is input[type=submit].submit-form-button (value "Submit"), NOT a button element. A script looking for button elements finds nothing. "Submit ignoring warnings" is input[type=button] with onclick submit_ignore() and only exists after a warnings response. Click it via page.evaluate(() => setTimeout(() => el.click(), 50)) as real clicks have hung the tool, and wrap the navigation in page.waitForNavigation({ timeout: 15000 }).
- Before leaving a form page run $(window).unbind('beforeunload') in page.evaluate to avoid the beforeunload dialog (the seed also auto-accepts dialogs).
- The amend form auto-opens the "Attention Required" modal (#modal-nags, class "modal in", display block) on a fresh GET. Close it ($('#modal-nags').modal('hide') or its Close button) before clicking anything else. It is absent from the DOM after an invalid POST re-render.
- Validation is server side (form has novalidate). A failed submit re-renders the same URL with the alert "Please fix the errors highlighted below and resubmit." and the panel holding the first error opens (other panels collapse).
- A survey modal may overlay pages; dismiss it with "Not right now" if present (the survey host is blocked by the seed).

## Test Scenarios

### 1. My Requests list & detail

**Seed:** `seed.spec.ts`

#### 1.1. 1.1 My Requests page chrome and table layout

**File:** `tests/rcallocation/03-my-requests/list-layout.spec.ts`

**Steps:**
  1. Run seed.spec.ts, then navigate to /allocation/user_requests/ (use the sidebar link 'My Requests'). Data: 152179, 152181, 152182. [verified live]
    - expect: URL is http://dashboard-s.rcdev.nectar.org.au:8000/allocation/user_requests/
    - expect: Page title is 'Allocation Requests - Nectar Dashboard'
    - expect: Single h1 'My Requests'; breadcrumb reads 'Allocations' then 'My Requests'
    - expect: Table headers exactly: State, Name, Current Associated Site, National, Contact, Last Updated, Expiry Date, Actions
    - expect: Footer reads 'Displaying 3 items' (count depends on dev data)
    - expect: No filter or search input exists on the page (zero input[type=search] and zero input[name*=filter])
    - expect: Table action 'Request a new allocation' has href /allocation/

#### 1.2. 1.2 Approved row 152179 cell content

**File:** `tests/rcallocation/03-my-requests/list-row-approved.spec.ts`

**Steps:**
  1. On /allocation/user_requests/ read row id DataTableOptions__row__152179. Data: 152179. [verified live]
    - expect: State cell has class 'text-center' and contains <p title='Approved' class='alloc-icon alloc-icon-ok'><strong>A</strong></p>
    - expect: Name cell contains link 'gdfgdfgdf' with href /allocation/user_requests/view/152179/, then <br>, then <small class='muted'>fsdgfdsgdsfg</small>
    - expect: Current Associated Site 'QCIF'; National 'True'; Contact 'sorrison@gmail.com'
    - expect: Last Updated 'April 30, 2026' (date only, no time); Expiry Date '-'
    - expect: Actions cell has exactly one link, 'Amend/Extend allocation', id DataTableOptions__row_152179__action_amend, classes 'btn data-table-action btn-default btn-associate', href /allocation/user_requests/edit_change_request/152179/

#### 1.3. 1.3 Submitted rows 152181 and 152182 cell content and ordering

**File:** `tests/rcallocation/03-my-requests/list-rows-submitted.spec.ts`

**Steps:**
  1. On /allocation/user_requests/ read rows 152181 and 152182 and the row order. Data: 152181, 152182. [verified live]
    - expect: Row order top to bottom is 152179 (A), 152181 (E), 152182 (E): rows sort by status
    - expect: 152181: State <p title='Submitted' class='alloc-icon alloc-icon-wip'><strong>E</strong></p>; Name link 'pwtest-valid' to /allocation/user_requests/view/152181/ with <small class='muted'>PW validation test</small>; Site '-'; National 'False'; Contact sorrison@gmail.com; Last Updated 'Oct. 30, 2026'; Expiry '-'
    - expect: 152182: State title 'Submitted' class alloc-icon-wip, letter E; Name link 'pwtest-202610301345-b' to /allocation/user_requests/view/152182/ with <small class='muted'>PW warnings flow test</small>; Site '-'; National 'False'; Last Updated 'Oct. 30, 2026'; Expiry '-'
    - expect: The alloc-icon-ok class appears only on the A row; E rows use alloc-icon-wip
    - expect: Dates use Django style (April 30, 2026 / Oct. 30, 2026); empty site and expiry render '-'

#### 1.4. 1.4 Row actions for A and E statuses

**File:** `tests/rcallocation/03-my-requests/list-row-actions.spec.ts`

**Steps:**
  1. Read the Actions cell of each row. Data: 152179, 152181, 152182. [verified live]
    - expect: 152179 (A): single action 'Amend/Extend allocation' to /allocation/user_requests/edit_change_request/152179/
    - expect: 152181 (E): single action 'Edit request' (id DataTableOptions__row_152181__action_user_edit) to /allocation/user_requests/edit_request/152181/
    - expect: 152182 (E): single action 'Edit request' to /allocation/user_requests/edit_request/152182/
    - expect: No dropdown menu or 'View history' action exists in this table
    - expect: Neither E row offers 'Amend/Extend allocation'; the A row does not offer 'Edit request'

#### 1.5. 1.5 Row actions for R, N, X and J statuses

**File:** `tests/rcallocation/03-my-requests/list-row-actions-other-statuses.spec.ts`

**Steps:**
  1. [derived from code, not verified live: user_allocations/tables.py] No R, N, X or J allocation exists for the pt.openrc user. If one is created or found, read its Actions cell. Data: none available.
    - expect: R (Declined), N (New) and E show 'Edit request' (user_edit, href user_requests/edit_request/<id>/)
    - expect: X (Update requested) and J (Update declined) show 'Edit amend/extend request' (href user_requests/edit_change_request/<id>/)
    - expect: A shows 'Amend/Extend allocation'
    - expect: State cell: class alloc-icon-ok only for A; alloc-icon-wip for every other status, with a title tooltip carrying the status label

#### 1.6. 1.6 List scope: contact or TenantManager, top-level only

**File:** `tests/rcallocation/03-my-requests/list-scope.spec.ts`

**Steps:**
  1. [derived from code, not verified live: user_allocations/views.py] As a non-admin user who is the contact of one allocation and a TenantManager of another project, open /allocation/user_requests/. Compare with history records of 152182 (152183, 152184).
    - expect: Rows are top-level allocations (no parent_request) where contact_email equals the username or project_id is a TenantManager project of the user
    - expect: History records never appear as rows: for the pt.openrc user 152183 and 152184 are absent from the list (verified live) and only 152179, 152181, 152182 appear
    - expect: Rows are ordered by status
    - expect: An allocation admin sees only own or managed allocations here, not all allocations (verified live: 3 rows)

#### 1.7. 1.7 Name link and table action navigation

**File:** `tests/rcallocation/03-my-requests/list-navigation.spec.ts`

**Steps:**
  1. Click the Name link 'gdfgdfgdf' on /allocation/user_requests/. Data: 152179. [verified live]
    - expect: Navigates to /allocation/user_requests/view/152179/ with title 'View allocation request - Nectar Dashboard'
  2. Navigate back, click the table action 'Request a new allocation'.
    - expect: Navigates to /allocation/ with title 'Allocation Request - Nectar Dashboard' and h3 'New Allocation Request: About the Project'. Run $(window).unbind('beforeunload') or accept the dialog when leaving that page
  3. On /allocation/ click 'All My Requests'.
    - expect: Returns to /allocation/user_requests/ (h1 'My Requests')

#### 1.8. 2.1 User detail page for Approved allocation 152179

**File:** `tests/rcallocation/03-my-requests/detail-approved.spec.ts`

**Steps:**
  1. Navigate to /allocation/user_requests/view/152179/. Data: 152179 (status A). [verified live]
    - expect: HTTP 200; title 'View allocation request - Nectar Dashboard'; breadcrumb 'Allocations', 'My Requests', 'View Allocation Request'
    - expect: h1 'View Allocation Request'; h2 'fsdgfdsgdsfg'
    - expect: Summary rows: Contact email sorrison@gmail.com; Submit date April 30, 2026, 6 a.m.; Last updated April 30, 2026, 6:01 a.m.; Start date None; End date None; Estimated project duration '12 month(s)'; Convert trial? No; State Approved; Approver sorrison@gmail.com; Project Identifier gdfgdfgdf; Project ID '(Project not linked)'; Associated Site QCIF; National funded yes; Provisioned no (time of day may vary by time zone)
    - expect: Headings in order: h3 'Current Resources' (Bundle Details Powerful; Object Store Storage NeCTAR 3000 GB; Object Store Storage Pawsey (WA) 3000 GB), 'Use Case' (text 'ggdfgdf'), 'Usage Patterns' (No Submission), 'Additional Location Requirements' (No Submission), 'Usage Types' (Collaborating with other institutions), 'Usage Information', 'Data Sensitivity Information', 'Fields of Research (FOR)', 'Supported Organisations', 'Chief Investigator', 'Research Grant Information', 'Publication/Output and Impact'
    - expect: Usage Information h4s: 'Estimated number of users who will directly access the instances' (44), 'Estimated number of research services or platforms to be hosted using this allocation' (55), 'Estimated total number of unique active users of these services' (55), 'Number of users directly accessing instances over the past year' (None), 'Number of active research services or platforms hosted using this allocation' (None), 'Total number of unique active users of these services over the past year' (None), 'Are the above figures measured or estimated?' (Measured)
    - expect: Data Sensitivity: h5 'Current Values:'; 'Contains sensitive data?' = 'No, the project does not involve sensitive data.'; 'Data classification Level Framework details' = Green; 'Discussed the use of sensitive data ...' = None; 'Data misuse would have little to no impact.'
    - expect: FOR 1 '30 AGRICULTURAL, VETERINARY AND FOOD SCIENCES (100%)'; Organisations 'AARNet (Australia)'; Chief Investigator Name 'fdgdgf fdggfd gfdgfd', Email fdgfd@ggg.cpo, Primary Organisation 'Aboriginal Health and Medical Research Council of New South Wales'
    - expect: Research Grant Information, 'ARDC (or ANDS, Nectar, or RDS) funded projects supporting this request:', 'NCRIS Facilities supporting this request:', Publication/Output and Impact, 'Benefits of Nectar' and 'Research Impact' each show 'No Submission'
    - expect: Exactly one action button in the page body: 'Request amendment' with href /allocation/user_requests/edit_change_request/152179/
    - expect: No admin notes, approve, decline or 'Edit request' controls are present

#### 1.9. 2.2 User detail page for Submitted allocation 152182

**File:** `tests/rcallocation/03-my-requests/detail-submitted.spec.ts`

**Steps:**
  1. Navigate to /allocation/user_requests/view/152182/. Data: 152182 (status E). [verified live]
    - expect: HTTP 200; title 'View allocation request - Nectar Dashboard'; h1 'View Allocation Request'; h2 'PW warnings flow test'
    - expect: State Submitted; Project Identifier pwtest-202610301345-b; Project ID '(Project not linked)'; Associated Site None; National funded no; Provisioned no; Estimated project duration '12 month(s)'; Convert trial? No; no Approver row
    - expect: h3 'Requested Resources' lists Bundle Details Custom, Compute Service Limits Virtual Cores NeCTAR 256 VCPUs, RAM NeCTAR 640 GB, Instances NeCTAR 160 Servers, Huge RAM Flavors NeCTAR Enabled, Database RAM 64 GB, Database Storage 1000 GB, Reservations 8, Reservation Duration 400 Days, GPU Flavors Enabled, Huge RAM Flavors Enabled, Routers 8, Floating IPs 16, Load Balancers 16, Security Groups 90, Object Store Storage NeCTAR 3000 GB, Service Units Budget NeCTAR 16000 SUs, Object Store Storage Pawsey (WA) 3000 GB
    - expect: h3 'Approved Resources (at the time of this record)' shows 'No allocation.'
    - expect: Use Case reads 'Playwright warnings flow test' followed by any text appended by scenario 3.5 (' [regression edit 03]' once 3.5 has run); Usage Types 'Hosting services to support research'
    - expect: Usage Information shows only the three 'Estimated ...' values (1, 1, 1); the past-year h4s are absent (they appear only for A records)
    - expect: FOR 1 '4601 Applied computing (100%)'; Organisations Monash University; Chief Investigator 'Dr Pw Tester', pw@example.edu.au, Monash University; Grant Type 'Institutional research funding', Subtype unspecified, Other funding source details 'Uni fund', First year funded 2026, Last year funded 2027, Total funding (AUD) 1000.0
    - expect: Publication/Output and Impact reads 'No Submission. (None expected for new requests.)'
    - expect: Exactly one action button: 'Edit request' with href /allocation/user_requests/edit_request/152182/; no 'Request amendment', admin notes, approve or decline buttons
  2. Navigate to /allocation/user_requests/view/152181/. Data: 152181. [verified live]
    - expect: State Submitted; Bundle Details Standard under 'Requested Resources'; single button 'Edit request' to /allocation/user_requests/edit_request/152181/

#### 1.10. 2.3 Detail page button precedence and external links

**File:** `tests/rcallocation/03-my-requests/detail-buttons-logic.spec.ts`

**Steps:**
  1. [derived from code, not verified live: allocationrequest_user_detail.html and models.py can_user_edit, can_user_edit_amendment, can_be_amended] Review which button shows by status. Data: A 152179 and E 152182 verified live; X and J need data not available.
    - expect: Only one button renders: 'Edit request' when can_user_edit, else 'Edit change request' when can_user_edit_amendment, else 'Request amendment' when can_be_amended
    - expect: E shows 'Edit request' (verified); A shows 'Request amendment' (verified)
    - expect: X and J (not verified live) should show 'Edit change request'
    - expect: No admin controls render for any status in the user view
  2. Read external hrefs on the detail page without clicking. [verified live]
    - expect: Page chrome links: http://support.nectar.org.au/, https://desktop.rc.nectar.org.au/, https://jupyterhub.rc.nectar.org.au/, https://binderhub.rc.nectar.org.au/, https://tutorials.rc.nectar.org.au/, https://support.ehelp.edu.au/support/solutions/articles/6000171494-project-allocation-expiry-and-renewal#pt, https://dashboard.rc.nectar.org.au/terms, https://status.rc.nectar.org.au/, https://ardc.edu.au/ and sub pages. Freshdesk and Grafana links were not seen on the user detail page

#### 1.11. 3.1 User edit form render for 152182

**File:** `tests/rcallocation/03-my-requests/edit-render.spec.ts`

**Steps:**
  1. Navigate to /allocation/user_requests/edit_request/152182/ (use the row action 'Edit request'). Data: 152182. [verified live]
    - expect: HTTP 200; title 'Edit Allocation Request - Nectar Dashboard'; breadcrumb 'Allocations', 'My Requests', 'None'
    - expect: h3 'Edit Allocation Request: About the Project'; h4 'ORCID Connected'; info panel 'Before you begin...'; no 'Attention' alert (no nags) and no Warnings block on fresh load
    - expect: Form id new-allocation, method post, action /allocation/user_requests/edit_request/152182/, novalidate
    - expect: Step tabs 'STEP 1: About the project' (#form-step1) and 'STEP 2: Cloud resources' (#form-step2)
    - expect: Panel headings in order: '1. Project Details', '2. Usage Information', '3. Fields of Research (FOR)', '4. Supported Institutions', '5. Investigator', '6. Project Support', '7. Research Grant Information', '8. Continue'; a hidden panel '8. Publication/Output and Impact' exists with class hidden. Only panelOne is open
    - expect: Step counters read 'Step N out of 8'
    - expect: Panel 1 (panelOne): 'Project allocation title' = PW warnings flow test; 'Contact e-mail' = sorrison@gmail.com (readonly); 'Project Identifier' = pwtest-202610301345-b (editable); 'Generated project DNS zone name' = pwtest-202610301345-b.cloud.edu.au; 'Estimated project duration' = 12-months; 'Convert trial project?' = 'No, start with a blank project.'
    - expect: Panel 2 (panelTwo) labels: 'Does the research project have more than one allocation ...' (No, this is the only allocation for this project.); 'Estimated number of users who will directly access the instances' = 1; 'Estimated number of research services or platforms to be hosted using this allocation' = 1; 'Estimated total number of unique active users of these services' = 1; 'Research project description' (use_case textarea); 'Does your project contain sensitive data?' = 'No, the project does not involve sensitive data.'; 'How would data used in the project be classified ...' = Green (disabled); 'I have discussed the use of sensitive data ...' select = 'Please select...'
    - expect: Panel 3: three FOR selects with percentages 100%, 0%, 0%. Panel 4: 'Supported organisations' with 'Show only Australia and New Zealand organisations' checked and a 'Propose an Organisation' button. Panel 5: Title Dr, Given name Pw, Surname Tester, email pw@example.edu.au, Primary organisation, additional researchers empty. Panel 6: ARDC and NCRIS support fields empty. Panel 7: Grant Type 'Institutional research funding', Subtype unspecified, 'Other funding source details' Uni fund, First year funded 2026, Last year funded 2027, Total funding 1000.0. Panel 8 reads 'Continue to select cloud resources.' with 'Previous' and 'Continue'
    - expect: Resources step panels: '1. Resource Bundles' (cards Standard 4000 SU / year, Powerful 8000 SU / year, Extreme 16000 SU / year, Custom), '2. Location Specific Resources', '3. Resource Justification' (usage_patterns, geographic_requirements, usage_types checkboxes), '4. Submit Checklist'
    - expect: Bottom section 'Are you ready to submit this allocation request?' has a primary 'Submit' button and no 'Submit ignoring warnings' button on fresh load

#### 1.12. 3.2 Invalid edit submit with error in the open panel

**File:** `tests/rcallocation/03-my-requests/edit-invalid-panel1.spec.ts`

**Steps:**
  1. Load /allocation/user_requests/edit_request/152182/. Via page.evaluate set project_description (label 'Project allocation title') to '' and dispatch change; unbind beforeunload; click input[type=submit].submit-form-button via evaluate with a navigation wait. Data: 152182. [verified live]
    - expect: URL stays /allocation/user_requests/edit_request/152182/; title 'Edit Allocation Request - Nectar Dashboard'
    - expect: Alert alert-danger 'Please fix the errors highlighted below and resubmit.'
    - expect: Error is in panelOne: form-group has-error on 'Project allocation title' with help-block 'This field is required.'
    - expect: panelOne is open; panelTwo to panelEight are closed. The field value remains empty after re-render
    - expect: No record is created or changed (history length unchanged)

#### 1.13. 3.3 Invalid edit submit with error in a collapsed panel auto-expands it

**File:** `tests/rcallocation/03-my-requests/edit-invalid-panel2.spec.ts`

**Steps:**
  1. Load the edit form for 152182, set direct_access_user_estimate to '' via evaluate (panelTwo field), submit as in 3.2. Data: 152182. [verified live]
    - expect: Alert alert-danger 'Please fix the errors highlighted below and resubmit.'
    - expect: Error is in panelTwo: has-error on 'Estimated number of users who will directly access the instances' with help-block 'This field is required'
    - expect: panelTwo is open and panelOne is now closed (the panel with the error auto-expands; others collapse)

#### 1.14. 3.4 Unchanged edit submit shows the Warnings block

**File:** `tests/rcallocation/03-my-requests/edit-warnings.spec.ts`

**Steps:**
  1. Load the edit form for 152182, append ' [regression edit 03]' to use_case via evaluate (or leave unchanged), unbind beforeunload and click Submit. Data: 152182 (Custom bundle with special flavors). [verified live]
    - expect: Same URL re-rendered, title 'Edit Allocation Request - Nectar Dashboard', no error alert
    - expect: Visible alert alert-warning with h4 'Warnings', text 'Please review the following warnings. Then either modify the form and "Submit" it again, or "Submit ignoring warnings".', a rule, and one list item: 'Requests for access to special flavors must be explained in the "Justification ..." field.' with a 'More information' link (target _blank) to https://support.ehelp.edu.au/support/solutions/articles/6000220088#FLAVORS_NOT_JUSTIFIED (do not click)
    - expect: Buttons at the bottom: 'Submit' and 'Submit ignoring warnings'
    - expect: The posted use_case value persists in the re-rendered form
    - expect: A 'DOI lookup failure' alert (alert-danger) is in the DOM but hidden (belongs to the DOI checker modal); do not run the DOI checker
    - expect: No record is created at this step

#### 1.15. 3.5 Successful edit of 152182 via Submit ignoring warnings

**File:** `tests/rcallocation/03-my-requests/edit-success.spec.ts`

**Steps:**
  1. Continue from 3.4 (warnings shown). Unbind beforeunload, click 'Submit ignoring warnings' via evaluate wrapped in waitForNavigation({ timeout: 20000 }). Data: 152182, status E before. This is an approved submit; do NOT repeat on 152179. [verified live]
    - expect: Redirects to http://dashboard-s.rcdev.nectar.org.au:8000/allocation/user_requests/ (My Requests), title 'Allocation Requests - Nectar Dashboard', h1 'My Requests'
    - expect: No visible success message (the messages container is empty and hidden)
    - expect: Row 152182 still shows State E (title 'Submitted', alloc-icon-wip), Name 'pwtest-202610301345-b' with description 'PW warnings flow test', Last Updated 'Oct. 30, 2026', action 'Edit request'
    - expect: Rows 152179 (A) and 152181 (E) are unchanged; the table still shows 3 rows

#### 1.16. 3.6 History and detail after the 152182 edit

**File:** `tests/rcallocation/03-my-requests/edit-verify-history.spec.ts`

**Steps:**
  1. After 3.5 open /allocation/requests/view/152182/history. Data: 152182, history 152183 existed beforehand. [verified live]
    - expect: Title 'Allocation Requests - Nectar Dashboard'; 'Displaying 3 items' (was 2 before 3.5)
    - expect: Columns: Project name, Approver, Bundle, SUs, Cores, RAM, Object Storage, Volume Storage, Status, Modification time
    - expect: Rows newest first: 152182 (current), 152184 (new history record), 152183; all 'PW warnings flow test', Bundle '-', 16000 SUs, 256 cores, 640 RAM, 6000 object storage, status Submitted
    - expect: Project name links are /allocation/requests/view/152182/, /allocation/requests/view/152184/, /allocation/requests/view/152183/. The newest row's modification time is later than the previous newest (3:33 a.m. became 3:49 a.m. in the observed run)
  2. Open /allocation/user_requests/view/152182/. [verified live]
    - expect: State Submitted; Submit date and Last updated both equal the new edit time (Oct. 30, 2026, 3:49 a.m. observed); Use Case 'Playwright warnings flow test [regression edit 03]'; button 'Edit request' still shown

#### 1.17. 4.1 User amend form render for 152179

**File:** `tests/rcallocation/03-my-requests/amend-render.spec.ts`

**Steps:**
  1. From My Requests click 'Amend/Extend allocation' on 152179 (or open /allocation/user_requests/edit_change_request/152179/). Close the auto-opened 'Attention Required' modal. Data: 152179 (status A). [verified live]
    - expect: HTTP 200; title 'Request Allocation Extension - Nectar Dashboard'; breadcrumb 'Allocations', 'My Requests', 'None'
    - expect: Visible h3 is 'Edit Allocation Request: About the Project' (differs from title)
    - expect: Form id new-allocation, method post, action /allocation/user_requests/edit_change_request/152179/
    - expect: Panels: '1. Project Details', '2. Usage Information', '3. Fields of Research (FOR)', '4. Supported Institutions', '5. Investigator', '6. Project Support', '7. Research Grant Information', '8. Publication/Output and Impact', '9. Continue' (panelNine). Resources step: panelBundle (Powerful selected), panelExtras, panelJustification, panelSubmit
    - expect: panelOne: 'Project allocation title' = fsdgfdsgdsfg (readonly), 'Contact e-mail' = sorrison@gmail.com (readonly), 'Project identifier' = gdfgdfgdf (readonly), 'Generated project DNS zone name', and label 'Estimated extension duration' (select estimated_project_duration = 12-months)
    - expect: panelTwo contains: multiple_allocations_check; direct_access_user_past_year (label 'Number of users directly accessing instances over the past year') = 44; active_service_count (label 'Number of active research services or platforms hosted using this allocation') = 55; service_active_users_past_year (label 'Total number of unique active users of these services over the past year') = 55; users_figure_type (label 'Are the above figures measured or estimated?', options Measured, Estimated) = Measured; use_case = 'ggdfgdf'; has_sensitive_data = 'No, the project does not involve sensitive data.'; data_classification_level = Green (disabled); institutional_data_review = 'Please select...'. The 'Estimated number of users ...' fields from the new request form are absent
    - expect: panelThree FOR percentages 100%, 0%, 0%; panelFour anz checked; panelFive investigator fdgdgf / fdggfd / gfdgfd / fdgfd@ggg.cpo; panelSeven grant row with first year 2026 and last year 2027, no type or amount
    - expect: panelEight (class panel-collapse, heading '8. Publication/Output and Impact', step 'Step 8 out of 9'): note 'List any publications or other research outputs from work on this project that has been supported by use of the Nectar cloud.' with an 'Add publication' button, textarea nectar_benefit_description (label 'Benefits of Nectar', counter '0 / 4096') and textarea nectar_research_impact (label 'Research Impact', counter '0 / 4096'), both empty, with buttons 'Previous' and 'Next'
    - expect: panelJustification: usage_patterns, geographic_requirements empty; usage_types checkboxes with only 'Collaborating with other institutions' checked
    - expect: The page has a 'Submit' button (input type submit) and no 'Submit ignoring warnings' button on fresh load

#### 1.18. 4.2 Attention alert and Attention Required modal content on 152179

**File:** `tests/rcallocation/03-my-requests/amend-attention-blocks.spec.ts`

**Steps:**
  1. Load /allocation/user_requests/edit_change_request/152179/ and read the 'Attention' alert and the modal immediately. Data: 152179. [verified live]
    - expect: Alert (class alert alert-warning, role alert) has h4 'Attention' with a warning icon, paragraph 'There are items that require your attention before you submit this form.' and an input button 'Review Reminders' (onclick show_nags())
    - expect: On load the modal #modal-nags (class 'modal in') is displayed (display block) with title 'Attention Required' and a close (x) button
    - expect: Modal body paragraph: 'The following items require your attention before you submit this amendment. These may be a result of changes that we have made to this form since your last submission.'
    - expect: Modal list has one item: 'Please provide an impact and benefit statement for your project. Also include any publications which have occurred since your last renewal. Providing this information supports the ongoing sustainability of the ARDC Nectar Research Cloud.'
    - expect: Modal footer has one 'Close' button; after closing, display is none. Clicking 'Review Reminders' reopens it (derived from the onclick handler, not exercised)

#### 1.19. 4.3 Invalid amend submit with past-year fields cleared

**File:** `tests/rcallocation/03-my-requests/amend-invalid.spec.ts`

**Steps:**
  1. Load the amend form, close #modal-nags, then via page.evaluate clear direct_access_user_past_year, active_service_count, service_active_users_past_year and set users_figure_type to ''. Unbind beforeunload and click input[type=submit] via evaluate with a navigation wait. Data: 152179. The submit is certain to fail (required fields empty); never use Submit ignoring warnings here. [verified live]
    - expect: URL stays /allocation/user_requests/edit_change_request/152179/; title 'Request Allocation Extension - Nectar Dashboard'; alert alert-danger 'Please fix the errors highlighted below and resubmit.'
    - expect: panelTwo errors (form-group has-error, help-block): 'Number of users directly accessing instances over the past year' 'This field is required'; 'Number of active research services or platforms hosted using this allocation' 'This field is required'; 'Total number of unique active users of these services over the past year' 'This field is required'; 'Are the above figures measured or estimated?' 'This field is required.' (note the trailing full stop on the last one)
    - expect: panelSeven errors: 'Grant Type' 'This field is required.', 'Grant Subtype' 'This field is required.', 'Total funding (AUD)' 'This field is required.' (caused by the prefilled grant years)
    - expect: panelTwo is open; all other details panels (including panelSeven) are closed after re-render
    - expect: The #modal-nags modal is absent from the DOM after the re-render
    - expect: 152179 remains status A, with unchanged history (152179 and 152180)

#### 1.20. 5.1 Edit and amend URLs for history records are denied

**File:** `tests/rcallocation/03-my-requests/history-record-urls.spec.ts`

**Steps:**
  1. GET user_requests/view/<id>/, edit_request/<id>/ and edit_change_request/<id>/ for id in 146946, 138447, 137049. Do not submit. Data: 146946, 138447, 137049.
    - expect: [verified live] view/<id>/ returns 403 with title '- Forbidden - Nectar Dashboard' (also view/152183/ returns 403)
    - expect: [verified live after permission fix] edit_request/<id>/ returns 403 with title '- Forbidden - Nectar Dashboard'
    - expect: [verified live after permission fix] edit_change_request/<id>/ returns 403 with title '- Forbidden - Nectar Dashboard'
    - note: Before the fix (verified live 2026-10-30), edit_request returned 200 ('Edit Allocation Request - Nectar Dashboard') and edit_change_request returned 200 ('Request Allocation Extension - Nectar Dashboard').

#### 1.21. 5.2 Status-guarded edit URLs and missing id

**File:** `tests/rcallocation/03-my-requests/urls.spec.ts`

**Steps:**
  1. GET (no submit) user_requests/edit_request/<E id>/ and edit_change_request/<A id>/. [derived from code and unit tests; not yet verified live]
    - expect: Both return 200 with titles 'Edit Allocation Request - Nectar Dashboard' (edit_request) or 'Request Allocation Extension - Nectar Dashboard' (edit_change_request)
  2. GET (no submit) user_requests/edit_request/<A id>/ and edit_change_request/<E id>/. [derived from code and unit tests; not yet verified live]
    - expect: HTTP 400 with the plain-text body 'Allocation request cannot be edited in its current state' (edit_request) or 'Allocation cannot be amended in its current state' (edit_change_request). Before NECTAR-17320 both returned 200: the views did not enforce the status that the list uses to choose between them
  2. GET /allocation/user_requests/view/99999999/. [verified live]
    - expect: HTTP 404, title 'Page not found at /allocation/user_requests/view/99999999/', heading 'Page not found (404)' (Django debug page on dev)
