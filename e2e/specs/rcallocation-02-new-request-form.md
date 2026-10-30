# rcallocation 02: New Request form regression baseline

## Application Overview

Regression baseline for the Allocations "New Request" form (rcallocation app) on the Nectar Horizon dashboard, captured before a refactor that intends no UI change. Base URL: http://dashboard-s.rcdev.nectar.org.au:8000 (dev; notifications go to a dev system). Every scenario starts from the seed /home/sam/projects/nectar/nectar-dashboard/seed.spec.ts (blocks challenges.cloudflare.com, logs in via websso, opens /allocation/). Never remove the Turnstile block. The pt.openrc user is an allocation admin whose only My Requests row at the start is allocation 152179 (identifier gdfgdfgdf, status A).

Tags: "verified live" means observed in the browser on 2026-10-30. "derived from code" means read from source and not exercised live.

GENERAL NOTES FOR TEST AUTHORS (all verified live)
- The form is at /allocation/ (route horizon:allocation:request:request, form id new-allocation, POST to /allocation/). /allocation/request/ returns 404. Page title is "Allocation Request - Nectar Dashboard".
- The form has novalidate. All validation is server side; a failed submit re-renders /allocation/ with the alert "Please fix the errors highlighted below and resubmit." There is NO confirmation modal on Submit (see Discrepancies below). The heading "Are you ready to submit this allocation request?" is static text beside the Submit button.
- Leaving the page raises a beforeunload dialog (handler is unbound when a .submit-form-button is clicked). Accept it, or run $(window).unbind('beforeunload') before navigating.
- Use pressSequentially for JS-driven inputs (select2 searches, project identifier DNS preview, char counters). fill() does not trigger them.
- A "Tell us about your Nectar Cloud experience" survey dialog (with a Dismiss button and a Close button) can appear over the page and block clicks. Close it before interacting. Real clicks on Submit hung the tool twice in the exploration run; clicking via page.evaluate(() => setTimeout(() => submit.click(), 50)) was reliable.
- The page makes one in-page XHR to https://ardc.edu.au/wp-json/ardc-web-components/v1/forms?id=75 (footer newsletter form). Do not navigate there.
- Accordion panel ids: panelOne to panelEight for Details; panelBundle, panelExtras, panelJustification, panelSubmit for Resources. A hidden panel for Publication/Output and Impact ("Step 8 out of 9") exists in the DOM with class "hidden" for new requests.
- Errors render as Bootstrap "form-group has-error" blocks inside the owning accordion panel, except FOR errors (control-group error, help-inline, shown below the Estimated project duration row) and quota errors (rendered inside the Custom Bundle modal, which does not auto-open).

DISCREPANCIES FROM THE BRIEFED FACTS (verified live)
1. Organisation select2 calls /allocation/fetch_organisations/ (query q, page, page_limit, filter=anz), not /allocation/request/fetch_organisations/. The models.py ajax_url matches the live path; request/urls.py registers fetch_organisations/ under the request include.
2. No confirmation modal appears on Submit. "Are you ready to submit this allocation request?" is a static H4 next to the Submit button. Submit posts directly.
3. The "Allocation Classification" panel is not rendered on the new request page. It exists in allocationrequest_base.html (admin edit templates).
4. Project Identifier carries the autofocus attribute but document.activeElement was BODY after load.
5. The textarea char counter stayed "0 / 4096" after pressSequentially typing in one probe.
6. The empty submit does not show estimate-required errors, because the FOR error aborts clean() first. Estimate errors only appear when the FOR rules pass.
7. When quota errors exist, the duplicate-identifier error was not shown alongside it.

ALLOCATIONS CREATED DURING EXPLORATION (dev environment, status E / Submitted, owner sorrison@gmail.com)
- 152181, identifier "pwtest-valid", title "PW validation test", default Standard bundle. Created UNINTENTIONALLY by a validation probe whose flavor checkbox did not trigger a warning under the Standard bundle. It does not follow the pwtest-<yyyymmddhhmm> convention. It counts as one of the two approved submits.
- 152182, identifier "pwtest-202610301345-b", title "PW warnings flow test", Custom quotas, created via "Submit ignoring warnings". Second approved submit.
Both need cleanup by a dev admin (hard_delete_allocation management command or Decline). No further submits were made.

DATA SAFETY: validation scenarios are designed to fail. Any scenario that could succeed MUST use a unique identifier pwtest-<yyyymmddhhmm> (add -b for a second). Only two successful submits were approved for the whole suite and both are now used. The identifier "pwtest-valid" now exists, so reusing it in a failing scenario is a safe guard against accidental success.

TEST DATA (real values seen)
- Bundles (id:name): 3 Standard (4000 SU / year, Popular badge, default), 6 Powerful (8000 SU / year), 9 Extreme (16000 SU / year), plus Custom card (select value empty).
- Organisations (id:label): 5 "Monash University (AU)", 23 "University of Melbourne (AU)", 278639 "University of Sydney - USYD (AU)", 15353 "Auckland City Hospital (NZ)", 4334 "Auckland University of Technology - AUT (NZ)", 314402 "All Organisations - all (AU)", 28610 "Monash Health (AU)", 20276 "Monash Medical Centre - MMC (AU)".
- FOR codes (id: label): "4601 Applied computing", "3101 Biochemistry and cell biology", "46 INFORMATION AND COMPUTING SCIENCES", "31 BIOLOGICAL SCIENCES", "460101 Applications in arts and humanities". FOR select2 uses 2203 local options (no XHR), series ANZSRC_2020.
- Existing identifier for the duplicate test: gdfgdfgdf (allocation 152179, status A).
- Valid baseline payload (field name = value): project_description "PW validation test"; use_case "Playwright validation baseline"; direct_access_user_estimate 1; estimated_service_count 1; estimated_service_active_users 1; has_sensitive_data no_sensitive; data_classification_level green; field_of_research_1 4601 with for_percentage_1 100; supported_organisations 5; investigators-0 title Dr, given_name Pw, surname Tester, email pw@example.edu.au, primary_organisation 5; grants-0 grant_type inst, grant_subtype unspecified, funding_body_scheme "Uni fund", total_funding 1000; first usage_types checkbox ticked; usage_patterns "x"; project_name varied per scenario.
- Option values: has_sensitive_data = no_sensitive / sensitive / unknown; data_classification_level = green / yellow / orange / red / not_sure; institutional_data_review = yes / not_yet; multiple_allocations_check = False / True; grant_type = arc, nhmrc, mrff, rdc, comp, govt, state, industry, ext, inst, nz.

## Test Scenarios

### 1. New Request form

**Seed:** `/home/sam/projects/nectar/nectar-dashboard/seed.spec.ts`

#### 1.1. R1 Page chrome, headings, intro text and ORCID banner

**File:** `tests/rcallocation/new-request/rendering-chrome.spec.ts`

**Steps:**
  1. Run seed.spec.ts, then read the page at /allocation/.
    - expect: Tag: verified live. URL is http://dashboard-s.rcdev.nectar.org.au:8000/allocation/ and the title is 'Allocation Request - Nectar Dashboard'.
    - expect: Left nav 'Allocations' group lists: New Request (/allocation/), Pending Requests (/allocation/requests/), Approved Requests (/allocation/approved_requests/), My Requests (/allocation/user_requests/).
    - expect: Breadcrumb reads 'Allocations' then '/ None'.
    - expect: H3 'New Allocation Request: About the Project' with a link 'All My Requests' (/allocation/user_requests/).
    - expect: Intro paragraph begins 'This form allows you to request a project allocation on the Nectar Research Cloud. Allocation requests can take up to 3 weeks to process.' with links 'eligibility criteria' (https://support.ehelp.edu.au/support/solutions/articles/6000226889) and 'create a support ticket' (https://support.ehelp.edu.au/support/tickets/new). Record hrefs only, do not click.
    - expect: Second paragraph begins 'NOTE If you would like to request an extension or amendment of an existing allocation, please use the Amend/Extend allocation action on the existing allocation request on the My Requests page.'
    - expect: Blockquote H4 'ORCID Connected' with the ORCID record link (sandbox.orcid.org/0009-0006-2369-9936) and 'Is this ORCID incorrect? Sign out at orcid.org and then go to the My Details page to disconnect.' (My Details = /settings/my-details/).
    - expect: Blockquote 'INFO: Required fields are marked with an * sign.'
    - expect: Info panel H4 'Before you begin...' then 'Before requesting an allocation, please ensure that you:' with 7 bullets: check your eligibility ... using the Eligibility Assessment Tool (https://eligibility.rc.nectar.org.au/); understand and follow Nectar's Sensitive Data Guidelines (https://support.ehelp.edu.au/support/solutions/articles/6000277743); have an ORCID and it is connected to your Nectar account; have the Project Information ready; know the Chief Investigator name and contact details; can provide the Research Grant information; know the FoR code to describe the research. No 8th bullet about publications on a new request.
    - expect: Step tabs 'STEP 1: About the project' (#form-step1, active) and 'STEP 2: Cloud resources' (#form-step2).
    - expect: Bottom of the form shows H4 'Are you ready to submit this allocation request?' and a primary 'Submit' button. No 'Submit ignoring warnings' button on a fresh load.
    - expect: The nav also shows 'Select Project' with the pt-44 project switcher, which is not part of the form.

#### 1.2. R2 Details accordion: section order, headings and required-asterisk markers

**File:** `tests/rcallocation/new-request/rendering-details-sections.spec.ts`

**Steps:**
  1. Run seed. Read the headings in the Step 1 accordion.
    - expect: Tag: verified live. Eight section links in order: '1. Project Details' (#panelOne, open by default), '2. Usage Information', '3. Fields of Research (FOR)', '4. Supported Institutions', '5. Investigator', '6. Project Support', '7. Research Grant Information', '8. Continue'.
    - expect: No 'Publication/Output and Impact' section is visible; a hidden panel for it exists in the DOM (class panel-default hidden, 'Step 8 out of 9').
    - expect: Collapsed headers show required-marker icons: panel 2 has six, panel 4 has one, panel 5 has five, panel 7 has five.
    - expect: Step counters read 'Step N out of 8' for panels 1 to 8. Panel 8 reads 'Step 8 out of 8' with 'Continue to select cloud resources.' and buttons 'Previous' and 'Continue'.
    - expect: Panel 1 has 'Next' only; panels 4 and 5 have 'Previous' and 'Next'.

#### 1.3. R3 Project Details defaults and help text

**File:** `tests/rcallocation/new-request/rendering-project-details.spec.ts`

**Steps:**
  1. Run seed. Inspect panel 1 (#panelOne).
    - expect: Tag: verified live. Labels in order: 'Project allocation title *' (empty), 'Contact e-mail' (prefilled with the logged-in username, here sorrison@gmail.com), 'Project Identifier *' (empty) with help text 'Project identifier cannot be changed after allocation is approved.', 'Generated project DNS zone name' (disabled input), 'Estimated project duration *', 'Convert trial project?'.
    - expect: Estimated project duration options: 1-month, 3-months, 6-months, 12-months; 12-months selected (value 12).
    - expect: Convert trial project? options: 'No, start with a blank project.' (selected, value False) and 'Yes, move resources from my pt- project to this new project.'.
    - expect: The project_name input carries the HTML autofocus attribute, but document.activeElement is BODY after load. Assert the attribute and record actual focus separately.
    - expect: Type 'Abc-Test9' into Project Identifier with pressSequentially: the disabled DNS zone field becomes 'abc-test9.cloud.edu.au'.

#### 1.4. R4 Usage Information panel rendering

**File:** `tests/rcallocation/new-request/rendering-usage-info.spec.ts`

**Steps:**
  1. Open '2. Usage Information'.
    - expect: Tag: verified live. NOTE 'Estimate the number of users and services that will be supported by the allocation over the next year. Please distinguish between users who will have direct access to the VM instances and those who will use any services that are hosted on the instances.'
    - expect: Select 'Does the research project have more than one allocation on the Nectar Cloud where the number of users has already been provided in a separate allocation?' with options 'No, this is the only allocation for this project.' (default, False) and 'Yes, usage numbers have already been provided.' (True).
    - expect: Three empty number inputs: 'Estimated number of users who will directly access the instances', 'Estimated number of research services or platforms to be hosted using this allocation', 'Estimated total number of unique active users of these services'.
    - expect: Textarea 'Research project description *' with counter '0 / 4096' (class char-counter). The counter stayed 0 / 4096 after pressSequentially('hello') in one probe; record actual behaviour.
    - expect: Select 'Does your project contain sensitive data? *' options: 'Please select...', 'No, the project does not involve sensitive data.', 'Yes, the project involves sensitive data.', 'I am unsure if my project contains sensitive data.'.
    - expect: Select 'How would data used in the project be classified according to The Data Classification Framework? *' options: Please select..., Green, Yellow, Orange, Red, Not Sure. A hidden input id_data_classification_level_hidden exists.
    - expect: Select 'I have discussed the use of sensitive data on the Nectar Research Cloud with my institution.' options: Please select..., Yes, Not yet.
    - expect: Changing the sensitive-data select or the multiple-allocations select does not auto-set, disable or hide any other field.

#### 1.5. R5 Fields of Research panel rendering

**File:** `tests/rcallocation/new-request/rendering-for.spec.ts`

**Steps:**
  1. Open '3. Fields of Research (FOR)'.
    - expect: Tag: verified live. NOTE 'Please enter at least 1 and up to 3 ANZSRC 2020 Field of Research (FoR) codes for the area(s) of research supported by this allocation request, and set percentages adding up to a total of 100%. Please see How to use FoR codes in the Nectar Allocation request form for more details. Please provide FoR codes for your research areas, not your research methodologies.'
    - expect: Three select2 pairs: 'First Field Of Research' / 'Percentage for First Field Of Research', then Second, then Third. Placeholder 'Enter a 2, 4 or 6 digit ANZSRC_2020 FoR code'.
    - expect: Percentage selects offer 0% to 100% in 10% steps. Defaults: first 100%, second 0%, third 0%.
    - expect: Select2 is local data (2203 options, e.g. '30 AGRICULTURAL, VETERINARY AND FOOD SCIENCES', '4601 Applied computing'); no XHR is made when searching. Note: typing a code such as '0803' returned 'No matches found' (not in the ANZSRC 2020 list).

#### 1.6. R6 Supported Institutions: organisation select2 and its XHR path

**File:** `tests/rcallocation/new-request/rendering-supported-orgs.spec.ts`

**Steps:**
  1. Open '4. Supported Institutions'. Capture requests, run page.evaluate(() => $('#id_supported_organisations').select2('open')) then page.keyboard.type('Monash').
    - expect: Tag: verified live. NOTE 'Specify the Universities and other Research Organisations that will be supported by the allocation. Alternatively you can select 'All Organisations'.'
    - expect: Field label 'Supported organisations' (required), multi-select select2 with placeholder 'Enter one or more organisation...'.
    - expect: Checkbox 'Show only Australia and New Zealand organisations' checked by default (name anz).
    - expect: Help text 'If the Organisation you are trying to enter is not listed, you can propose it for addition to our database.' with a 'Propose an Organisation' button opening the 'Propose a new Organisation' modal (Full name, Short name, Country default Australia, Website URL, button 'Propose'; submits to /rest_api/organisations/). Do not submit it.
    - expect: The XHR is GET /allocation/fetch_organisations/?q=Monash&page=1&page_limit=10&filter=anz (not /allocation/request/fetch_organisations/).
    - expect: Result labels follow 'Full Name - Short (cc)': 'Monash Alfred Psychiatry Research centre - MAPrc (AU)', 'Monash Children’s Hospital (AU)', 'Monash Health (AU)', 'Monash Institute of Medical Research - MIMR (AU)', 'Monash IVF (AU)', 'Monash Medical Centre - MMC (AU)', 'Monash University (AU)'. When no short name exists, ' - Short' is omitted. JSON is {total, more, results:[{id, text}]}; Monash University is id 5.
    - expect: No match shows 'No matches found'.
    - expect: Panel buttons: 'Previous' and 'Next', 'Step 4 out of 8'.
    - expect: Caution: if a previous select2 dropdown is still open, typed text accumulates (e.g. 'MonashMonash'). Clear with Control+A, Backspace.

#### 1.7. R7 Investigator panel: one empty Chief Investigator form

**File:** `tests/rcallocation/new-request/rendering-investigator.spec.ts`

**Steps:**
  1. Open '5. Investigator'.
    - expect: Tag: verified live. Heading 'Chief Investigator' and NOTE 'For research projects specify the first investigator. For higher degree research projects specify the primary supervisor. For other activities specify the academic sponsor or head of the managing organisation unit.'
    - expect: Management form: investigators-TOTAL_FORMS 1, INITIAL_FORMS 0, MIN_NUM_FORMS 0, MAX_NUM_FORMS 1000 (one empty form).
    - expect: Fields: Title, Given name, Surname, Institutional email address (type email), Primary organisation (select2, placeholder 'Enter an organisation name or acronym...', anz checkbox checked, 'Propose an Organisation' button), textarea 'Please list all other primary investigators, partner investigators and other research collaborators' with counter '0 / 1000'.
    - expect: No add or remove investigator control is visible.

#### 1.8. R8 Project Support panel (ARDC and NCRIS)

**File:** `tests/rcallocation/new-request/rendering-project-support.spec.ts`

**Steps:**
  1. Open '6. Project Support'.
    - expect: Tag: verified live. Lead text 'If your project is supported by an ARDC program or an NCRIS facility, please enter the information here.'
    - expect: Multi-select 'ARDC program or project supporting this request' (placeholder 'Enter an ARDC project or progr...'). Option values include ACCS, AEDAPT, AgReFed, AHDAP; labels like 'ACCS - The Australian Characterisation Commons at Scale'. Text input 'ARDC Support details'.
    - expect: Multi-select 'NCRIS Facilities supporting this request' (placeholder 'Enter an NCRIS Facility name'). Option values: AAL, ALA, AuScope, ACDP, ANFF, APPN, AURIN, BPA, HIA, IMOS, MA, NCI, NDF, NIF, NSF, Pawsey, PA, PHRN, TERN, TIA, Pilot ('Pilot - NCRIS Pilot project'), Other ('Other - Other NCRIS support'), ACCESS. Text input 'NCRIS Support details'.
    - expect: All four fields are optional.

#### 1.9. R9 Research Grant Information: default grant form and 'I don't have any grants'

**File:** `tests/rcallocation/new-request/rendering-grants.spec.ts`

**Steps:**
  1. Open '7. Research Grant Information'. Read the text, click 'I don't have any grants', then click 'Add Grant'.
    - expect: Tag: verified live. NOTE starts 'Research grant information aids in the assessment of research allocations and indicates the scale of the research supported. You must put at least one grant, or specify you have no grants for the project', then the National project allocation criteria list with links (national competitive research grant to docs.education.gov.au; NCRIS to education.gov.au; RC-NAS Policy to support.ehelp.edu.au).
    - expect: Management form: grants-TOTAL_FORMS 1, MIN_NUM_FORMS 1, MAX_NUM_FORMS 1000 (one grant form).
    - expect: Grant form fields: Grant Type, Grant Subtype, Other funding source details, Grant ID, First year funded (default 2026), Last year funded (default 2027), Total funding (AUD).
    - expect: Grant Type options: Select a grant type, Australian Research Council, NHMRC, Medical Research Future Fund (MRFF), Rural Research and Development Corporations (RDCs), Other Australian Federal Govt competitive grant, Australian Federal Govt non-competitive funding, Australian State / Territory Govt funding, Industry funding, Other external funding, Institutional research funding, New Zealand research funding. Grant Subtype list begins 'Select a grant subtype', 'ARC Discovery project' and ends 'unspecified'; the retired nhmrc-mrff choice is absent.
    - expect: Buttons: 'I don't have any grants' (id delete-grant) and 'Add Grant' (id add_another).
    - expect: After 'I don't have any grants': grants-TOTAL_FORMS becomes 0, grant fields are removed and only 'Add Grant' remains.
    - expect: After 'Add Grant': a grant form returns with buttons 'Delete' and 'Add Grant'.
    - expect: Not tested: whether a zero-grant form posts successfully (derived from code: NO_VALID_GRANTS is an advisory checker).

#### 1.10. R10 Continue panel replaces Publication/Output and Impact

**File:** `tests/rcallocation/new-request/rendering-continue.spec.ts`

**Steps:**
  1. Open '8. Continue' and then use the 'STEP 2: Cloud resources' tab.
    - expect: Tag: verified live for panel text and tab navigation; derived from code for the 'Continue' button click itself. Panel text 'Step 8 out of 8 Continue to select cloud resources.' with 'Previous' and 'Continue'.
    - expect: The STEP 2 tab sets #form-step1 display none, shows #form-step2, makes the tab active and appends '#!#form-step2' to the URL.
    - expect: Publications formset has TOTAL_FORMS 0; no 'Add publication' control visible.
    - expect: The DOI checker modal (modal-doi-checker) exists but is hidden. Do not exercise it: it calls api.crossref.org from the browser.

#### 1.11. R11 Resources: bundle cards and Custom card

**File:** `tests/rcallocation/new-request/rendering-bundles.spec.ts`

**Steps:**
  1. Switch to STEP 2 and read '1. Resource Bundles' (#panelBundle, open by default).
    - expect: Tag: verified live. Heading 'Resource Bundle' and 'Select the most suitable Resource Bundle for your project needs...'.
    - expect: Card 1: badge 'Popular', 'Standard', '4000 SU / year', 'A standard resource bundle suitable for researchers wanting extra compute power, similar to a personal computer, to host a simple web application or run basic computations.', 'Runs 16 VCPUs continuously (max 64 VCPUs at one time)', 'Up to 40 instances', '500 GB Object Storage', '2 x reservations for GPUs', 'Volume Storage requested separately *', 'More details' link, button 'Select Standard' / 'Selected'. Active with 'Selected' shown by default; hidden select id_bundle value 3.
    - expect: Card 2: 'Powerful', '8000 SU / year', 'Runs 32 VCPUs continuously (max 128 VCPUs at one time)', 'Up to 80 instances', '1500 GB Object Storage' (value 6).
    - expect: Card 3: 'Extreme', '16000 SU / year', 'Runs 64 VCPUs continuously (max 256 VCPUs at one time)', 'Up to 160 instances', '3000 GB Object Storage' (value 9).
    - expect: Card 4: 'Custom', 'For advanced cloud users with a specific set of resource requirements. Users must be able to estimate their requested SU budget.', 'User defined resource limits', 'Volume Storage requested separately *', 'More details', button 'Select Custom' / 'Customise'.
    - expect: id_bundle options: '---------' (empty), 3 Standard, 6 Powerful, 9 Extreme.
    - expect: Panel shows 'Step 1 out of 4'. Support link hrefs (record only): Resource Bundle https://support.ehelp.edu.au/support/solutions/articles/6000271205, Resource Bundle Table https://support.ehelp.edu.au/support/solutions/articles/6000271206.
  2. Click the 'Select Powerful' button with a real mouse click (a synthetic .click() on the card container did not change the selection).
    - expect: Tag: derived from code (form-nav.js around line 246). id_bundle becomes 6, the Powerful card gets class 'active' and shows 'Selected'. Verify live and record; this was not confirmed.

#### 1.12. R12 Custom Bundle modal

**File:** `tests/rcallocation/new-request/rendering-custom-bundle.spec.ts`

**Steps:**
  1. On Step 2 click 'Select Custom' / 'Customise' (data-target #modal-custom-bundle).
    - expect: Tag: verified live. id_bundle becomes empty and the Custom card is the active card.
    - expect: Modal 'Custom Bundle' with subtitle 'Request custom resource limits for your allocation' and '(Fields are prefilled with the same limits as the Extreme Bundle to assist customisation).'
    - expect: Sections 'Service Units' (NOTE 'Unsure how to estimate a usage budget? Checkout this guide.' opens usage_budget_modal 'Service Unit Budget Guide'), 'Budget' / 'SUs' ('Specify a usage budget in service units. Service units are only used for compute resources.'), 'Compute Service Limits'.
    - expect: Prefilled values: Budget 16000, Virtual Cores 256, RAM 640, Instances 160, Routers 8, Floating IPs 16, Load Balancers 16, Security Groups 90, Object Storage (nectar) 3000, Object Storage (pawsey) 3000, Database RAM 64, Database Storage 1000, Reservations 8, Duration 400. Flavor toggles On/Off for Huge RAM Flavors (compute), GPU Flavors and Huge RAM Flavors (reservation) are all Off.
    - expect: Modal has a close 'x' and a 'Done' button. 'Done' hides the modal (display none) and keeps id_bundle empty.

#### 1.13. R13 Location Specific Resources grouped by zone

**File:** `tests/rcallocation/new-request/rendering-location-resources.spec.ts`

**Steps:**
  1. Read '2. Location Specific Resources' (#panelExtras).
    - expect: Tag: verified live. Heading 'Location Specific Cloud Resources', 'The following additional resources can be requested for specific locations.' and 'Not sure if you need additional resources? For more information read the Location Specific Resources support article.'
    - expect: Block 'Volume Service' with On/Off toggle (default Off) and a long description beginning 'A persistent volume looks and acts like a hard drive...'. NOTE 'University of Melbourne Performance is only available to UoM researchers'. 'Zones' group of 15 number inputs, all default 0, in this order: Auckland (NZ) Storage, Auckland (NZ) encrypted Storage, Intersect (NSW) Storage, Intersect (NSW) encrypted Storage, Melbourne University Storage, Melbourne University encrypted Storage, Melbourne University performance Storage, Monash (VIC) Storage, Monash (VIC) encrypted Storage, QRIScloud Storage, QRIScloud encrypted Storage, Swinburne (VIC) Storage, Swinburne (VIC) encrypted Storage, Tasmania Storage, Tasmania encrypted Storage. Field names quota-volume.gigabytes__<zone>.
    - expect: Block 'Shared File System Service' with On/Off toggle (default Off) and two zone groups (auckland, monash-02-cephfs), each with Shares, Storage, Snapshots, Snapshot storage, all default 0.
    - expect: Compute-style quotas are prefilled from the Extreme values (e.g. quota-compute.cores__nectar 256), volume and share quotas default to 0.
    - expect: Panel shows 'Step 2 out of 4' with Previous and Next.

#### 1.14. R14 Resource Justification, Submit Checklist, Submit button, absent Allocation Classification panel

**File:** `tests/rcallocation/new-request/rendering-justification-submit.spec.ts`

**Steps:**
  1. Read '3. Resource Justification' and '4. Submit Checklist'.
    - expect: Tag: verified live. Heading 'Resource Justification' and 'Provide some information about the project to justify your selected resources.'
    - expect: Textarea 'Justification and details of your Proposed Cloud Usage' with counter '0 / 1024'; textarea 'Special location requirements' with counter '0 / 1024'.
    - expect: Checkbox group 'Usage types' (required; error 'Please check one or more of the above'): Hosting services to support research, Collaboration platform, Hosting a website, Hosting a database, Hosting and sharing data, Collaborating with other institutions, Collaborating internationally, Machine learning, Data analysis, Modelling and simulation, Other.
    - expect: Checklist: 'Before submitting this allocation request, please review the following checklist:' then 'I have provided all required project information.', 'I have provided the data sensitivity and classification details for this project.', 'I have provided the Chief Investigator details and contact information.', 'I have provided Research Grant information.', 'I have provided the FoR code to describe the research for this project.'
    - expect: Counters 'Step 3 out of 4' and 'Step 4 out of 4'.
    - expect: Submit section shows 'Are you ready to submit this allocation request?' and a single 'Submit' button (class submit-form-button).
    - expect: The 'Allocation Classification' panel is NOT present. Its markup lives in allocationrequest_base.html (admin edit views).

#### 1.15. R15 beforeunload prompt on leaving the form

**File:** `tests/rcallocation/new-request/leave-warning.spec.ts`

**Steps:**
  1. Load /allocation/, then navigate to /allocation/user_requests/ without submitting.
    - expect: Tag: verified live. A beforeunload dialog with an empty message appears; accepting it completes navigation.
    - expect: Clicking any .submit-form-button (Submit or 'Propose an Organisation') unbinds the handler (form-nav.js lines 263 to 266).

#### 1.16. V1 Empty form submit: error inventory and placement

**File:** `tests/rcallocation/new-request/validation-empty.spec.ts`

**Steps:**
  1. Load /allocation/ and click Submit without changing anything (JS-driven click; see overview).
    - expect: Tag: verified live. The page re-renders at /allocation/ with the alert 'Please fix the errors highlighted below and resubmit.' above the Before-you-begin panel. Panel 1 stays the only open accordion panel; no scrolling or section jumps.
    - expect: Panel 1: 'Project allocation title' and 'Project Identifier' show 'This field is required.'.
    - expect: Panel 2: 'Research project description' 'This field is required.'; sensitive-data select errors; classification 'This field is required.'. No estimate errors (clean() is aborted by the FOR error).
    - expect: Panel 3: 'Percentage set for unspecified Field Of Research' in the FOR error area.
    - expect: Panel 4: Supported organisations error. Panel 5: Title, Given name, Surname, Institutional email address each 'This field is required.'; Primary organisation error. Panel 7: Grant Type, Grant Subtype errors and 'Total funding (AUD)' 'This field is required.'. Resource Justification: Usage types error.
    - expect: Exact wording of the sensitive-data select, supported-organisations and grant type or subtype required errors was not captured verbatim; record it when authoring.

#### 1.17. V2 Project Identifier: regex, length, pt- prefix, duplicate

**File:** `tests/rcallocation/new-request/validation-project-identifier.spec.ts`

**Steps:**
  1. Fill the baseline payload with project_name 'ab' and submit.
    - expect: Tag: verified live. Panel 1 Project Identifier shows 'Between 5 and 32 characters required.' (the clean() 'at least 5 characters' message does not show).
  2. Repeat with '1abcdef'.
    - expect: 'Letters, numbers, underscore and hyphens only. Must start with a letter.'
  3. Repeat with 'abc def!'.
    - expect: 'Letters, numbers, underscore and hyphens only. Must start with a letter.'
  4. Repeat with 'pt-abcdef'.
    - expect: 'Must not start with "pt-" or similar.'
  5. Repeat with a 33 character name.
    - expect: 'Between 5 and 32 characters required.'
  6. Repeat with 'gdfgdfgdf' (existing allocation 152179).
    - expect: 'That project identifier already exists. If your allocation has been approved already, please go here to amend it. Otherwise, choose a different identifier.' where 'here' links to /allocation/user_requests/ (horizon:allocation:user_requests:index).

#### 1.18. V3 Fields of Research percentage rules

**File:** `tests/rcallocation/new-request/validation-for.spec.ts`

**Steps:**
  1. Baseline with field_of_research_1 4601 and for_percentage_1 0.
    - expect: Tag: verified live. FOR error area shows "Percentage for Field Of Research '4601' cannot be 0".
  2. Baseline with field_of_research_1 empty and for_percentage_1 50.
    - expect: 'Percentage set for unspecified Field Of Research'.
  3. Baseline with 4601 at 60 and field_of_research_2 3101 at 60.
    - expect: 'Sum of Field Of Research percentages greater than 100'. All three render in the separate FOR error area, not beside a field.

#### 1.19. V4 Sensitive data and classification rules

**File:** `tests/rcallocation/new-request/validation-sensitive.spec.ts`

**Steps:**
  1. Baseline with has_sensitive_data no_sensitive, classification red.
    - expect: Tag: verified live. Classification field: 'Data classification must be Green when project has no sensitive data'.
  2. has_sensitive_data unknown, classification green.
    - expect: 'Data classification must be Not Sure when unsure about sensitive data'.
  3. has_sensitive_data sensitive, classification green, review empty.
    - expect: Classification: 'Data classification cannot be Green when project has sensitive data'; review field: 'This field is required when the project involves sensitive data'.
  4. has_sensitive_data sensitive, classification red, review empty.
    - expect: Only 'This field is required when the project involves sensitive data' on 'I have discussed the use of sensitive data on the Nectar Research Cloud with my institution.' All render in panel 2.

#### 1.20. V5 Usage estimates required unless multiple allocations is Yes

**File:** `tests/rcallocation/new-request/validation-estimates.spec.ts`

**Steps:**
  1. Baseline with the three estimate fields empty and multiple_allocations_check False.
    - expect: Tag: verified live. Each of the three estimate fields shows 'This field is required' (no full stop) in panel 2.
  2. Same with multiple_allocations_check True, using a failing guard identifier (for example pwtest-valid).
    - expect: Tag: derived from code. No estimate errors; values stored as null. Not submitted live to avoid creating an allocation.

#### 1.21. V6 ARDC and NCRIS support rules

**File:** `tests/rcallocation/new-request/validation-support.spec.ts`

**Steps:**
  1. Baseline with ardc_explanation 'Some detail' and no ARDC selection.
    - expect: Tag: verified live. 'ARDC Support details': 'No ARDC projects or programs have been selected: choose one or more, or remove the explanation text.'
  2. Baseline with ncris_explanation 'Some detail' and no facilities.
    - expect: Tag: verified live. 'NCRIS Support details': 'No NCRIS Facilities have been selected: choose one or more, or remove the explanation text.'
  3. Baseline with ncris_facilities Pilot and no explanation.
    - expect: Tag: verified live. 'NCRIS Support details': "More details are required when you include 'Pilot' or 'Other' above."
  4. Select an ARDC program flagged explain=True with no explanation.
    - expect: Tag: derived from code. 'Add details for the ARDC support that you are claiming for your request.' (the explain flag was not identified live). All errors render in panel 6.

#### 1.22. V7 Supported organisations and Chief Investigator organisation rules

**File:** `tests/rcallocation/new-request/validation-organisations.spec.ts`

**Steps:**
  1. Baseline with supported_organisations '314402,5'.
    - expect: Tag: verified live. Panel 4: "'All Organisations' should not be used with any other organisation".
  2. Baseline with investigators-0-primary_organisation 314402.
    - expect: Tag: verified live. Panel 5: "'All Organisations' is not meaningful in this context".
  3. Baseline with investigators-0-primary_organisation empty.
    - expect: Tag: verified live. Panel 5: 'This field is required.'
  4. Select a disabled organisation as primary organisation (none located live).
    - expect: Tag: derived from code. 'This organisation is not (or no longer) valid: select an alternate one.'

#### 1.23. V8 Grant rules

**File:** `tests/rcallocation/new-request/validation-grants.spec.ts`

**Steps:**
  1. Baseline with grant type arc and subtype empty.
    - expect: Tag: verified live. Grant Subtype 'This field is required.' and Grant ID 'Enter the ARC grant id for this grant'. (A posted subtype value 'arc-discovery-project' behaved as empty in the probe because the real option value differs; copy values from the live select.)
  2. Grant type nhmrc, subtype empty.
    - expect: Subtype 'This field is required.'; Grant ID 'Enter the NHMRC grant id for this grant'.
  3. Grant type mrff, subtype empty.
    - expect: Subtype 'This field is required.'; Grant ID 'Enter the MRFF grant id for this grant'.
  4. Grant type rdc, subtype empty, scheme and id empty.
    - expect: Subtype 'This field is required.'; 'Other funding source details': 'Provide details for this grant or a grant id (below!)'.
  5. Grant type state, subtype unspecified.
    - expect: Grant Subtype: 'Select the State for this grant'.
  6. Grant type inst, subtype nsw.
    - expect: Grant Subtype: 'Inappropriate subtype for this grant'.
  7. Grant type inst, subtype unspecified, 'Other funding source details' empty.
    - expect: 'Other funding source details': 'Provide details for this grant'.
  8. Post a non-blank subtype from the wrong family (for example arc with an nhmrc subtype value).
    - expect: Tag: derived from code. 'Select an ARC grant subtype for this grant' (and the NHMRC, MRFF, RDC equivalents).

#### 1.24. V9 Quota bounds in the Custom Bundle modal

**File:** `tests/rcallocation/new-request/validation-quotas.spec.ts`

**Steps:**
  1. Baseline with bundle empty (Custom) and quota-compute.cores__nectar -1; submit.
    - expect: Tag: verified live. The page re-renders with Step 2 shown. The Custom Bundle modal does not open automatically but contains under 'Virtual Cores': 'Ensure this value is greater than or equal to 0.'
  2. Same with 2147483648.
    - expect: 'Ensure this value is less than or equal to 2147483647.' under 'Virtual Cores' inside the modal. In both probes the duplicate-identifier error did not appear alongside the quota error.

#### 1.25. W1 Quota warning FLAVORS_NOT_JUSTIFIED with ignore and resubmit (creates an allocation)

**File:** `tests/rcallocation/new-request/warnings-flavors.spec.ts`

**Steps:**
  1. Fill the baseline with project_name pwtest-<yyyymmddhhmm>-b, bundle empty (Custom), usage_patterns empty, and tick 'Huge RAM Flavors' (quota-compute.flavor:hugeram-v3__nectar). Submit.
    - expect: Tag: verified live. The page re-renders at /allocation/ with no field errors and no 'Please fix the errors' alert.
    - expect: An alert-warning block reads: 'Warnings Please review the following warnings. Then either modify the form and "Submit" it again, or "Submit ignoring warnings". Requests for access to special flavors must be explained in the "Justification ..." field. More information'.
    - expect: The submit section shows two buttons: 'Submit' and 'Submit ignoring warnings'. Hidden id_ignore_warnings is still empty.
  2. Click 'Submit ignoring warnings'.
    - expect: Tag: verified live. submit_ignore() sets id_ignore_warnings to 1, disables the .submit-form-button buttons and submits natively.
    - expect: Redirect to /allocation/user_requests/ with title 'Allocation Requests - Nectar Dashboard'; new row shows status E, identifier pwtest-202610301345-b, title 'PW warnings flow test', associated site '-', National False, Expiry '-', action 'Edit request' (/allocation/user_requests/edit_request/152182/). Created allocation 152182.
    - expect: The same checkbox under the default Standard bundle did not trigger the warning (the flavor toggle only counts in Custom), and that path submitted straight through (allocation 152181). Both approved submits are used, so do not rerun without fresh approval.

#### 1.26. S1 Successful submit, redirect, My Requests row, detail page and Pending Requests (creates an allocation)

**File:** `tests/rcallocation/new-request/submit-success.spec.ts`

**Steps:**
  1. Fill the valid baseline with a unique identifier pwtest-<yyyymmddhhmm>, keep the default Standard bundle, and submit.
    - expect: Tag: verified live (allocation 152181, pwtest-valid). No confirmation modal appears. The page redirects to /allocation/user_requests/ with title 'Allocation Requests - Nectar Dashboard'; no success message was captured.
    - expect: My Requests columns: State, Name, Current Associated Site, National, Contact, Last Updated, Expiry Date, Actions.
    - expect: New row text: 'E pwtest-valid PW validation test - False sorrison@gmail.com Oct. 30, 2026 -'. Name link /allocation/user_requests/view/152181/; site '-'; National False; Expiry '-'. State E is bold (Submitted).
    - expect: Row actions: only 'Edit request' (/allocation/user_requests/edit_request/152181/). The existing row 152179 shows 'Amend/Extend allocation' instead.
  2. Open /allocation/user_requests/view/152181/.
    - expect: Tag: verified live. Title 'View allocation request - Nectar Dashboard'; H3 'PW validation test'; 'State Submitted'; 'Project Identifier pwtest-valid'; 'Project ID (Project not linked)'.
    - expect: Section headings: Requested Resources, Approved Resources (at the time of this record), Use Case, Usage Patterns, Additional Location Requirements, Usage Types, Usage Information, Data Sensitivity Information, Fields of Research (FOR), Supported Organisations, Chief Investigator, Research Grant Information, 'ARDC (or ANDS, Nectar, or RDS) funded projects supporting this request:', 'NCRIS Facilities supporting this request:', Publication/Output and Impact.
    - expect: The only action button is 'Edit request' (/allocation/user_requests/edit_request/152181/).
  3. Open Pending Requests (/allocation/requests/).
    - expect: Tag: verified live. Columns: State, Name, Current Associated Site, National, Previous Approver, Contact, Last Updated, Expiry Date, Urgency, Actions.
    - expect: The new row reads 'E pwtest-valid PW validation test - False sorrison@gmail.com Oct. 30, 2026 - (New)' with links to /allocation/requests/view/152181/, 'Edit request' (/allocation/requests/edit_request/152181/) and 'View history' (/allocation/requests/view/152181/history). Urgency cell shows '(New)'. The table footer read 'Displaying 32 items' at the time.

#### 1.27. X1 Client-side form-nav behaviour

**File:** `tests/rcallocation/new-request/client-side-nav.spec.ts`

**Steps:**
  1. Click 'Next' in panel 1, then the 'STEP 2: Cloud resources' tab.
    - expect: Tag: verified live. 'Next' opens panel 2 (panelBundle also remains open in the hidden Step 2 section).
    - expect: The STEP 2 tab hides #form-step1, shows #form-step2 and sets URL hash '#!#form-step2'.
    - expect: No client-side check blocks Step 2 or Submit; the form has novalidate and all validation is server side.
    - expect: Server-rendered errors do not open or move panels beyond panel 1; for quota errors Step 2 is shown but the Custom Bundle modal stays closed.

#### 1.28. X2 Sensitive-data client behaviour is absent

**File:** `tests/rcallocation/new-request/client-side-sensitive.spec.ts`

**Steps:**
  1. Change 'Does your project contain sensitive data?' through each option.
    - expect: Tag: verified live. The classification select stays unset and enabled in all three cases, and the review select visibility does not change. Recorded so any new auto-select or show/hide behaviour introduced by the refactor is detected.
