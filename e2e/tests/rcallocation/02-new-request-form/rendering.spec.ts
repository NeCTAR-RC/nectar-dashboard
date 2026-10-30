import { Request } from '@playwright/test';

import { test, expect } from '../../../support/fixtures';
import {
  FORM_TITLE,
  FORM_URL,
  acceptDialogsOnce,
  byId,
  expandPanel,
  normalise,
  openDrop,
  openForm,
  optionTexts,
  optionValues,
} from './helpers';

// Rendering of the New Request form at /allocation/.  These tests only
// read the page and use client-side controls; nothing is submitted.
test.beforeEach(async ({ page }) => {
  acceptDialogsOnce(page);
  await openForm(page);
});

const label = (page: import('@playwright/test').Page, forId: string) =>
  page.locator(`label[for="${forId}"]`);

// Bootstrap-toggle wraps each On/Off checkbox in a div.toggle that carries
// 'off' while unchecked.
const toggleOf = (page: import('@playwright/test').Page, inputId: string) =>
  page.locator('div.toggle').filter({ has: byId(page, inputId) });

test.describe('New Request form: rendering', () => {
  test('R1 Page chrome, headings, intro text and ORCID banner', async ({ page }) => {
    await expect(page).toHaveURL(FORM_URL);
    await expect(page).toHaveTitle(FORM_TITLE);

    const nav = page.locator('#sidebar-accordion-allocation-default a');
    await expect(nav).toHaveText([
      'New Request',
      'Pending Requests',
      'Approved Requests',
      'My Requests',
    ]);
    expect(await nav.evaluateAll((as) => as.map((a) => a.getAttribute('href')))).toEqual([
      '/allocation/',
      '/allocation/requests/',
      '/allocation/approved_requests/',
      '/allocation/user_requests/',
    ]);
    await expect(nav.first()).toHaveClass(/active/);

    await expect(page.locator('ol.breadcrumb li')).toHaveText(['Allocations', 'None']);

    await expect(
      page.getByRole('heading', {
        level: 3,
        name: 'New Allocation Request: About the Project',
      }),
    ).toBeVisible();
    await expect(page.getByRole('link', { name: 'All My Requests' })).toHaveAttribute(
      'href',
      '/allocation/user_requests/',
    );

    const intro = page.locator('.intro p');
    await expect(intro.nth(0)).toHaveText(
      'This form allows you to request a project allocation on the Nectar ' +
        'Research Cloud. Allocation requests can take up to 3 weeks to ' +
        'process. To receive approval, research projects must meet the ' +
        'eligibility criteria and all relevant information about the ' +
        'project must be provided. If you have any questions please create ' +
        'a support ticket.',
    );
    await expect(intro.nth(0).getByRole('link', { name: 'eligibility criteria' })).toHaveAttribute(
      'href',
      'https://support.ehelp.edu.au/support/solutions/articles/6000226889',
    );
    await expect(
      intro.nth(0).getByRole('link', { name: 'create a support ticket' }),
    ).toHaveAttribute('href', 'https://support.ehelp.edu.au/support/tickets/new');
    await expect(intro.nth(1)).toHaveText(
      'NOTE If you would like to request an extension or amendment of an ' +
        'existing allocation, please use the Amend/Extend allocation action ' +
        'on the existing allocation request on the My Requests page.',
    );
    await expect(intro.nth(1).getByRole('link', { name: 'My Requests' })).toHaveAttribute(
      'href',
      '/allocation/user_requests/',
    );

    const orcid = page.locator('blockquote.border-success');
    await expect(orcid.locator('h4')).toHaveText('ORCID Connected');
    await expect(orcid.getByRole('link', { name: 'View ORCID record' })).toHaveAttribute(
      'href',
      'https://sandbox.orcid.org/0009-0006-2369-9936',
    );
    await expect(orcid.locator('small')).toHaveText(
      'Is this ORCID incorrect? Sign out at orcid.org and then go to the ' +
        'My Details page to disconnect.',
    );
    await expect(orcid.getByRole('link', { name: 'My Details' })).toHaveAttribute(
      'href',
      '/settings/my-details/',
    );

    await expect(page.locator('blockquote', { hasText: 'INFO:' })).toHaveText(
      'INFO: Required fields are marked with an sign.',
    );
    await expect(
      page.locator('blockquote', { hasText: 'INFO:' }).locator('.glyphicon-asterisk'),
    ).toHaveCount(1);

    const before = page.locator('.panel-info .panel-body');
    await expect(before.locator('h4')).toHaveText('Before you begin...');
    await expect(before.locator('p')).toHaveText(
      'Before requesting an allocation, please ensure that you:',
    );
    await expect(before.locator('li')).toHaveText([
      'check your eligibility for a national or local allocation using the Eligibility Assessment Tool',
      "understand and follow Nectar's Sensitive Data Guidelines",
      'have an ORCID and it is connected to your Nectar account',
      'have the Project Information ready',
      'know the Chief Investigator name and contact details',
      'can provide the Research Grant information',
      'know the FoR code to describe the research',
    ]);
    await expect(before.getByRole('link', { name: 'Eligibility Assessment Tool' })).toHaveAttribute(
      'href',
      'https://eligibility.rc.nectar.org.au/',
    );
    await expect(before.getByRole('link', { name: 'Sensitive Data Guidelines' })).toHaveAttribute(
      'href',
      'https://support.ehelp.edu.au/support/solutions/articles/6000277743',
    );

    const tabs = page.locator('#allocation_form_nav li');
    await expect(tabs).toHaveText(['STEP 1: About the project', 'STEP 2: Cloud resources']);
    await expect(tabs.nth(0)).toHaveClass(/active/);
    await expect(tabs.nth(1)).not.toHaveClass(/active/);
    expect(
      await tabs.locator('a').evaluateAll((as) => as.map((a) => a.getAttribute('href'))),
    ).toEqual(['#form-step1', '#form-step2']);

    const submitSection = page.locator('#submit-section');
    await expect(submitSection.locator('h4')).toHaveText(
      'Are you ready to submit this allocation request?',
    );
    await expect(submitSection.locator('input')).toHaveCount(1);
    await expect(submitSection.locator('input[type=submit]')).toHaveValue('Submit');
    await expect(submitSection.locator('input[type=submit]')).toHaveClass(/btn-primary/);

    // The project switcher in the nav is not part of the form.
    await expect(page.locator('#project_select h6')).toHaveText('Select Project');
    await expect(page.locator('#project_select .context-project')).toHaveText('pt-44');
  });

  test('R2 Details accordion: section order, headings and required-asterisk markers', async ({
    page,
  }) => {
    const headings = page.locator('#request_accordion > .panel > .panel-heading');
    await expect(headings.filter({ visible: true })).toHaveText([
      '1. Project Details',
      '2. Usage Information',
      '3. Fields of Research (FOR)',
      '4. Supported Institutions',
      '5. Investigator',
      '6. Project Support',
      '7. Research Grant Information',
      '8. Continue',
    ]);
    // Only panel 1 is open on load.
    await expect(page.locator('#request_accordion .request-collapse.in')).toHaveCount(1);
    await expect(page.locator('#panelOne')).toHaveClass(/\bin\b/);

    // The publications panel is in the DOM but hidden on a new request.
    const pubs = page.locator('#request_accordion > .panel', {
      hasText: '8. Publication/Output and Impact',
    });
    await expect(pubs).toHaveCount(1);
    await expect(pubs).toHaveClass(/panel-default/);
    await expect(pubs).toHaveClass(/\bhidden\b/);
    await expect(pubs).toBeHidden();
    await expect(pubs.locator('.step-nav p')).toHaveText('Step 8 out of 9');

    // Required markers inside the (collapsed) panels.
    const asterisks = (panel: string) => page.locator(`#${panel} .glyphicon-asterisk`);
    await expect(asterisks('panelTwo')).toHaveCount(6);
    await expect(asterisks('panelFour')).toHaveCount(1);
    await expect(asterisks('panelFive')).toHaveCount(5);
    await expect(asterisks('panelSeven')).toHaveCount(5);

    const panels = [
      'panelOne',
      'panelTwo',
      'panelThree',
      'panelFour',
      'panelFive',
      'panelSix',
      'panelSeven',
      'panelEight',
    ];
    for (const [i, panel] of panels.entries()) {
      await expect(page.locator(`#${panel} .step-nav p`).first()).toHaveText(
        `Step ${i + 1} out of 8`,
      );
    }
    const buttons = (panel: string) => page.locator(`#${panel} .step-nav a.btn`);
    await expect(buttons('panelOne')).toHaveText(['Next']);
    for (const panel of panels.slice(1, 7)) {
      await expect(buttons(panel)).toHaveText(['Previous', 'Next']);
    }
    await expect(buttons('panelEight')).toHaveText(['Previous', 'Continue']);
    await expect(page.locator('#panelEight h3')).toHaveText('Continue to select cloud resources.');
  });

  test('R3 Project Details defaults and help text', async ({ page }) => {
    const panel = page.locator('#panelOne');
    expect(
      (await panel.locator('label').allTextContents()).map(normalise),
    ).toEqual([
      'Project allocation title',
      'Contact e-mail',
      'Project Identifier',
      'Generated project DNS zone name',
      'Estimated project duration',
      'Convert trial project?',
    ]);
    for (const id of ['id_project_description', 'id_project_name', 'id_estimated_project_duration']) {
      await expect(label(page, id).locator('.glyphicon-asterisk'), id).toHaveCount(1);
    }
    for (const id of ['id_contact_email', 'id_dns_domain', 'id_convert_trial_project']) {
      await expect(label(page, id).locator('.glyphicon-asterisk'), id).toHaveCount(0);
    }

    await expect(byId(page, 'id_project_description')).toHaveValue('');
    // Prefilled with the logged-in username and read-only.
    await expect(byId(page, 'id_contact_email')).toHaveValue('sorrison@gmail.com');
    await expect(byId(page, 'id_contact_email')).toHaveAttribute('readonly', 'readonly');
    await expect(byId(page, 'id_project_name')).toHaveValue('');
    await expect(panel.locator('small')).toHaveText(
      'Project identifier cannot be changed after allocation is approved.',
    );
    await expect(byId(page, 'id_dns_domain')).toBeDisabled();
    await expect(byId(page, 'id_dns_domain')).toHaveValue('');

    const duration = byId(page, 'id_estimated_project_duration');
    expect(await optionTexts(duration)).toEqual(['1-month', '3-months', '6-months', '12-months']);
    await expect(duration).toHaveValue('12');

    const convert = byId(page, 'id_convert_trial_project');
    expect(await optionTexts(convert)).toEqual([
      'No, start with a blank project.',
      'Yes, move resources from my pt- project to this new project.',
    ]);
    expect(await optionValues(convert)).toEqual(['False', 'True']);
    await expect(convert).toHaveValue('False');

    // The identifier carries autofocus, yet nothing has focus after load.
    await expect(byId(page, 'id_project_name')).toHaveAttribute('autofocus', 'autofocus');
    expect(await page.evaluate(() => document.activeElement?.tagName)).toBe('BODY');

    await byId(page, 'id_project_name').pressSequentially('Abc-Test9');
    await expect(byId(page, 'id_dns_domain')).toHaveValue('abc-test9.cloud.edu.au');
  });

  test('R4 Usage Information panel rendering', async ({ page }) => {
    const panel = await expandPanel(page, 'panelTwo');
    await expect(panel).toContainText(
      'NOTE Estimate the number of users and services that will be supported ' +
        'by the allocation over the next year. Please distinguish between ' +
        'users who will have direct access to the VM instances and those who ' +
        'will use any services that are hosted on the instances.',
    );

    const multiple = byId(page, 'id_multiple_allocations_check');
    await expect(label(page, 'id_multiple_allocations_check')).toContainText(
      'Does the research project have more than one allocation on the Nectar ' +
        'Cloud where the number of users has already been provided in a ' +
        'separate allocation?',
    );
    expect(await optionTexts(multiple)).toEqual([
      'No, this is the only allocation for this project.',
      'Yes, usage numbers have already been provided.',
    ]);
    expect(await optionValues(multiple)).toEqual(['False', 'True']);
    await expect(multiple).toHaveValue('False');

    for (const [id, text] of [
      ['id_direct_access_user_estimate', 'Estimated number of users who will directly access the instances'],
      ['id_estimated_service_count', 'Estimated number of research services or platforms to be hosted using this allocation'],
      ['id_estimated_service_active_users', 'Estimated total number of unique active users of these services'],
    ]) {
      await expect(label(page, id)).toContainText(text);
      await expect(byId(page, id)).toHaveAttribute('type', 'number');
      await expect(byId(page, id)).toHaveValue('');
      await expect(byId(page, id)).toBeVisible();
    }

    await expect(label(page, 'id_use_case')).toContainText('Research project description');
    await expect(label(page, 'id_use_case').locator('.glyphicon-asterisk')).toHaveCount(1);
    const counter = page.locator('#id_use_case + .char-counter');
    await expect(counter).toHaveText('0 / 4096');
    await byId(page, 'id_use_case').pressSequentially('hello');
    await expect(counter).toHaveText('5 / 4096');

    const sensitive = byId(page, 'id_has_sensitive_data');
    await expect(label(page, 'id_has_sensitive_data')).toContainText(
      'Does your project contain sensitive data?',
    );
    await expect(label(page, 'id_has_sensitive_data').locator('.glyphicon-asterisk')).toHaveCount(1);
    expect(await optionTexts(sensitive)).toEqual([
      'Please select...',
      'No, the project does not involve sensitive data.',
      'Yes, the project involves sensitive data.',
      'I am unsure if my project contains sensitive data.',
    ]);
    expect(await optionValues(sensitive)).toEqual(['', 'no_sensitive', 'sensitive', 'unknown']);

    const classification = byId(page, 'id_data_classification_level');
    await expect(label(page, 'id_data_classification_level')).toContainText(
      'How would data used in the project be classified according to The ' +
        'Data Classification Framework?',
    );
    expect(await optionTexts(classification)).toEqual([
      'Please select...',
      'Green',
      'Yellow',
      'Orange',
      'Red',
      'Not Sure',
    ]);
    expect(await optionValues(classification)).toEqual([
      '', 'green', 'yellow', 'orange', 'red', 'not_sure',
    ]);
    await expect(byId(page, 'id_data_classification_level_hidden')).toHaveAttribute(
      'name',
      'data_classification_level',
    );

    const review = byId(page, 'id_institutional_data_review');
    await expect(label(page, 'id_institutional_data_review')).toContainText(
      'I have discussed the use of sensitive data on the Nectar Research Cloud with my institution.',
    );
    expect(await optionTexts(review)).toEqual(['Please select...', 'Yes', 'Not yet']);
    expect(await optionValues(review)).toEqual(['', 'yes', 'not_yet']);
  });

  test('R5 Fields of Research panel rendering', async ({ page }) => {
    const panel = await expandPanel(page, 'panelThree');
    // The NOTE says 'ANZSRC 2020'; the select2 placeholder 'ANZSRC_2020'.
    await expect(panel.locator('.col-xs-12').first()).toHaveText(
      'NOTE Please enter at least 1 and up to 3 ANZSRC 2020 Field of Research ' +
        '(FoR) codes for the area(s) of research supported by this allocation ' +
        'request, and set percentages adding up to a total of 100%. Please ' +
        'see How to use FoR codes in the Nectar Allocation request form for ' +
        'more details. Please provide FoR codes for your research areas, not ' +
        'your research methodologies.',
    );
    await expect(
      panel.getByRole('link', { name: 'How to use FoR codes in the Nectar Allocation request form' }),
    ).toHaveAttribute('href', 'https://support.ehelp.edu.au/support/solutions/articles/6000241729');

    const ordinals = ['First', 'Second', 'Third'];
    const percentages = Array.from({ length: 11 }, (_, i) => `${i * 10}%`);
    for (const [i, ordinal] of ordinals.entries()) {
      const n = i + 1;
      await expect(panel.locator('label').filter({ hasText: new RegExp(`^${ordinal} Field Of Research$`) })).toHaveCount(1);
      await expect(label(page, `id_for_percentage_${n}`)).toHaveText(
        `Percentage for ${ordinal} Field Of Research`,
      );
      await expect(byId(page, `id_field_of_research_${n}`)).toHaveAttribute(
        'data-placeholder',
        'Enter a 2, 4 or 6 digit ANZSRC_2020 FoR code',
      );
      await expect(byId(page, `s2id_id_field_of_research_${n}`)).toContainText(
        'Enter a 2, 4 or 6 digit ANZSRC_2020 FoR code',
      );
      const pct = byId(page, `id_for_percentage_${n}`);
      expect(await optionTexts(pct)).toEqual(percentages);
      await expect(pct).toHaveValue(n === 1 ? '100' : '0');
    }

    // The FoR choices are local select2 data.
    const data = await byId(page, 'id_field_of_research_1').evaluate(
      (e) => JSON.parse(e.getAttribute('data-select2-options')!).data as { id: string; text: string }[],
    );
    expect(data).toHaveLength(2203);
    expect(data[0]).toEqual({ id: '30', text: '30 AGRICULTURAL, VETERINARY AND FOOD SCIENCES' });
    expect(data).toContainEqual({ id: '4601', text: '4601 Applied computing' });

    // Searching makes no request.
    const requests: Request[] = [];
    page.on('request', (r) => requests.push(r));
    await byId(page, 's2id_id_field_of_research_1').locator('a.select2-choice').click();
    const search = openDrop(page).locator('input.select2-input');
    await search.pressSequentially('4601');
    const results = openDrop(page).locator('.select2-result-label');
    await expect(results.first()).toHaveText('4601 Applied computing');
    await search.press('Control+a');
    await search.press('Backspace');
    await search.pressSequentially('0803');
    await expect(openDrop(page).locator('.select2-no-results')).toHaveText(
      'No matches found',
    );
    await search.press('Escape');
    expect(
      requests.filter((r) => ['xhr', 'fetch'].includes(r.resourceType())).map((r) => r.url()),
    ).toEqual([]);
  });

  test('R6 Supported Institutions: organisation select2 and its XHR path', async ({ page }) => {
    const panel = await expandPanel(page, 'panelFour');
    await expect(panel.locator('.col-xs-12').first()).toContainText(
      "NOTE Specify the Universities and other Research Organisations that " +
        "will be supported by the allocation. Alternatively you can select " +
        "'All Organisations'.",
    );
    const fieldLabel = panel.locator('label').first();
    await expect(fieldLabel).toHaveText('Supported organisations');
    await expect(fieldLabel.locator('.glyphicon-asterisk')).toHaveCount(1);
    await expect(byId(page, 's2id_id_supported_organisations')).toHaveClass(/select2-container-multi/);
    await expect(byId(page, 'id_supported_organisations')).toHaveAttribute(
      'data-placeholder',
      'Enter one or more organisation names or acronyms...',
    );
    const anz = byId(page, 'id_supported_organisations_anz');
    await expect(anz).toBeChecked();
    await expect(anz).toHaveAttribute('name', 'anz');
    await expect(label(page, 'id_supported_organisations_anz')).toHaveText(
      'Show only Australia and New Zealand organisations',
    );
    await expect(panel.locator('#id_supported_organisations_filter + div p')).toHaveText(
      'If the Organisation you are trying to enter is not listed, you can propose it for addition to our database.',
    );
    await expect(panel.locator('.step-nav p')).toHaveText('Step 4 out of 8');
    await expect(panel.locator('.step-nav a.btn')).toHaveText(['Previous', 'Next']);

    // Search: the XHR goes to /allocation/fetch_organisations/.
    const search = byId(page, 's2id_id_supported_organisations').locator('input.select2-input');
    const fetched = page.waitForResponse((r) => r.url().includes('fetch_organisations'));
    await search.click();
    await search.pressSequentially('Monash');
    const response = await fetched;
    const url = new URL(response.url());
    expect(url.pathname).toBe('/allocation/fetch_organisations/');
    // Plus a jQuery cache-busting '_' timestamp.
    expect(Object.fromEntries(url.searchParams)).toEqual({
      q: 'Monash',
      page: '1',
      page_limit: '10',
      filter: 'anz',
      _: expect.stringMatching(/^\d+$/),
    });
    const body = await response.json();
    expect(Object.keys(body).sort()).toEqual(['more', 'results', 'total']);
    expect(body.results).toContainEqual({ id: 5, text: 'Monash University (AU)' });

    const results = openDrop(page).locator('.select2-result-label');
    await expect(results).toContainText([
      'Monash Alfred Psychiatry Research centre - MAPrc (AU)',
      'Monash Children’s Hospital (AU)',
      'Monash Health (AU)',
      'Monash Institute of Medical Research - MIMR (AU)',
      'Monash IVF (AU)',
      'Monash Medical Centre - MMC (AU)',
      'Monash University (AU)',
    ]);

    await search.press('Control+a');
    await search.press('Backspace');
    await search.pressSequentially('zzqqxxnomatch');
    await expect(openDrop(page).locator('.select2-no-results')).toHaveText(
      'No matches found',
    );
    await search.press('Escape');

    // The propose modal; it is opened but never submitted.
    await panel.locator('input[value="Propose an Organisation"]').click();
    const modal = page.locator('#modal-propose');
    await expect(modal).toBeVisible();
    await expect(modal.locator('.modal-title')).toHaveText('Propose a new Organisation');
    await expect(modal.locator('label')).toHaveText([
      'Full name',
      'Short name',
      'Country',
      'Website URL',
    ]);
    await expect(modal.locator('select[name=country]')).toHaveValue('AU');
    await expect(modal.locator('#propose-organisation')).toHaveValue('Propose');
    await modal.locator('.form-actions button', { hasText: 'Close' }).click();
    await expect(modal).toBeHidden();
  });

  test('R7 Investigator panel: one empty Chief Investigator form', async ({ page }) => {
    const panel = await expandPanel(page, 'panelFive');
    await expect(panel.locator('h2')).toHaveText('Chief Investigator');
    await expect(panel.locator('.investigator')).toContainText(
      'NOTE For research projects specify the first investigator. For higher ' +
        'degree research projects specify the primary supervisor. For other ' +
        'activities specify the academic sponsor or head of the managing ' +
        'organisation unit.',
    );
    for (const [name, value] of [
      ['TOTAL_FORMS', '1'],
      ['INITIAL_FORMS', '0'],
      ['MIN_NUM_FORMS', '0'],
      ['MAX_NUM_FORMS', '1000'],
    ]) {
      await expect(byId(page, `id_investigators-${name}`)).toHaveValue(value);
    }
    await expect(panel.locator('.investigator')).toHaveCount(1);

    for (const [field, text] of [
      ['title', 'Title'],
      ['given_name', 'Given name'],
      ['surname', 'Surname'],
      ['email', 'Institutional email address'],
      ['additional_researchers', 'Please list all other primary investigators, partner investigators and other research collaborators'],
    ]) {
      await expect(label(page, `id_investigators-0-${field}`)).toHaveText(text);
      await expect(byId(page, `id_investigators-0-${field}`)).toHaveValue('');
    }
    await expect(byId(page, 'id_investigators-0-email')).toHaveAttribute('type', 'email');
    await expect(
      panel.locator('label').filter({ hasText: /^\s*Primary organisation\s*$/ }),
    ).toHaveCount(1);
    await expect(byId(page, 'id_investigators-0-primary_organisation')).toHaveAttribute(
      'data-placeholder',
      'Enter an organisation name or acronym...',
    );
    await expect(byId(page, 'id_investigators-0-primary_organisation_anz')).toBeChecked();
    await expect(panel.locator('input[value="Propose an Organisation"]')).toHaveCount(1);
    await expect(
      page.locator('[id="id_investigators-0-additional_researchers"] + .char-counter'),
    ).toHaveText('0 / 1000');

    // No add or remove investigator controls.
    await expect(panel.locator('button')).toHaveCount(0);
    await expect(panel.getByText(/add (another )?investigator|remove/i)).toHaveCount(0);
  });

  test('R8 Project Support panel (ARDC and NCRIS)', async ({ page }) => {
    const panel = await expandPanel(page, 'panelSix');
    await expect(panel.locator('.col-xs-12 > p').first()).toHaveText(
      'If your project is supported by an ARDC program or an NCRIS facility, please enter the information here.',
    );
    // The select2 labels point at select2's own search inputs.
    const labels = panel.locator('label');
    expect((await labels.allTextContents()).map(normalise)).toEqual([
      'ARDC program or project supporting this request',
      'ARDC Support details',
      'NCRIS Facilities supporting this request',
      'NCRIS Support details',
    ]);
    await expect(byId(page, 'id_ardc_support')).toHaveAttribute(
      'data-placeholder',
      'Enter an ARDC project or program name',
    );
    const ardcValues = await optionValues(byId(page, 'id_ardc_support'));
    expect(ardcValues.slice(0, 4)).toEqual(['ACCS', 'AEDAPT', 'AgReFed', 'AHDAP']);
    await expect(byId(page, 'id_ardc_support').locator('option[value="ACCS"]')).toHaveText(
      'ACCS - The Australian Characterisation Commons at Scale',
    );
    await expect(label(page, 'id_ardc_explanation')).toHaveText('ARDC Support details');
    await expect(byId(page, 'id_ardc_explanation')).toHaveAttribute('type', 'text');

    await expect(byId(page, 'id_ncris_facilities')).toHaveAttribute(
      'data-placeholder',
      'Enter an NCRIS Facility name',
    );
    expect(await optionValues(byId(page, 'id_ncris_facilities'))).toEqual([
      'AAL', 'ALA', 'AuScope', 'ACDP', 'ANFF', 'APPN', 'AURIN', 'BPA', 'HIA',
      'IMOS', 'MA', 'NCI', 'NDF', 'NIF', 'NSF', 'Pawsey', 'PA', 'PHRN', 'TERN',
      'TIA', 'Pilot', 'Other', 'ACCESS',
    ]);
    await expect(byId(page, 'id_ncris_facilities').locator('option[value="Pilot"]')).toHaveText(
      'Pilot - NCRIS Pilot project',
    );
    await expect(byId(page, 'id_ncris_facilities').locator('option[value="Other"]')).toHaveText(
      'Other - Other NCRIS support',
    );
    await expect(label(page, 'id_ncris_explanation')).toHaveText('NCRIS Support details');

    // All four fields are optional.
    await expect(panel.locator('.glyphicon-asterisk')).toHaveCount(0);
  });

  test("R9 Research Grant Information: default grant form and 'I don't have any grants'", async ({
    page,
  }) => {
    const panel = await expandPanel(page, 'panelSeven');
    await expect(panel.locator('p').first()).toHaveText(
      'NOTE Research grant information aids in the assessment of research ' +
        'allocations and indicates the scale of the research supported. You ' +
        'must put at least one grant, or specify you have no grants for the project',
    );
    await expect(panel.locator('p').nth(1)).toHaveText(
      'A National project allocation request can only be approved if the project is:',
    );
    await expect(panel.getByRole('link', { name: 'national competitive research grant' })).toHaveAttribute(
      'href',
      'https://docs.education.gov.au/system/files/doc/other/2018_acgr_listing_final.pdf',
    );
    await expect(
      panel.getByRole('link', { name: 'National Collaborative Research Infrastructure Strategy' }),
    ).toHaveAttribute('href', 'https://www.education.gov.au/funded-research-infrastructure-projects');
    await expect(panel.getByRole('link', { name: 'RC-NAS Policy' })).toHaveAttribute(
      'href',
      'https://support.ehelp.edu.au/support/solutions/articles/6000191233-research-cloud-national-allocation-scheme-rc-nas-policy-',
    );

    await expect(byId(page, 'id_grants-TOTAL_FORMS')).toHaveValue('1');
    await expect(byId(page, 'id_grants-MIN_NUM_FORMS')).toHaveValue('1');
    await expect(byId(page, 'id_grants-MAX_NUM_FORMS')).toHaveValue('1000');

    const fields: [string, string][] = [
      ['grant_type', 'Grant Type'],
      ['grant_subtype', 'Grant Subtype'],
      ['funding_body_scheme', 'Other funding source details'],
      ['grant_id', 'Grant ID'],
      ['first_year_funded', 'First year funded'],
      ['last_year_funded', 'Last year funded'],
      ['total_funding', 'Total funding (AUD)'],
    ];
    for (const [field, text] of fields) {
      await expect(label(page, `id_grants-0-${field}`)).toHaveText(text);
    }
    const thisYear = new Date().getFullYear();
    await expect(byId(page, 'id_grants-0-first_year_funded')).toHaveValue(String(thisYear));
    await expect(byId(page, 'id_grants-0-last_year_funded')).toHaveValue(String(thisYear + 1));

    expect(await optionTexts(byId(page, 'id_grants-0-grant_type'))).toEqual([
      'Select a grant type',
      'Australian Research Council',
      'NHMRC',
      'Medical Research Future Fund (MRFF)',
      'Rural Research and Development Corporations (RDCs)',
      'Other Australian Federal Govt competitive grant',
      'Australian Federal Govt non-competitive funding',
      'Australian State / Territory Govt funding',
      'Industry funding',
      'Other external funding',
      'Institutional research funding',
      'New Zealand research funding',
    ]);
    // The subtype field stays hidden until a grant type with subtypes is
    // chosen.
    await expect(byId(page, 'id_grants-0-grant_subtype-group')).toBeHidden();
    await byId(page, 'id_grants-0-grant_type').selectOption('arc');
    await expect(byId(page, 'id_grants-0-grant_subtype-group')).toBeVisible();
    await byId(page, 'id_grants-0-grant_type').selectOption('');
    await expect(byId(page, 'id_grants-0-grant_subtype-group')).toBeHidden();
    const subtypes = await optionTexts(byId(page, 'id_grants-0-grant_subtype'));
    expect(subtypes.slice(0, 2)).toEqual(['Select a grant subtype', 'ARC Discovery project']);
    expect(subtypes[subtypes.length - 1]).toBe('unspecified');
    expect(await optionValues(byId(page, 'id_grants-0-grant_subtype'))).not.toContain('nhmrc-mrff');

    const buttons = panel.locator('.grant_formset button');
    await expect(buttons).toHaveText(["I don't have any grants", 'Add Grant']);
    await expect(panel.locator('#delete-grant')).toHaveText("I don't have any grants");
    await expect(panel.locator('#add_another')).toHaveText('Add Grant');

    await panel.locator('#delete-grant').click();
    await expect(byId(page, 'id_grants-TOTAL_FORMS')).toHaveValue('0');
    await expect(panel.locator('.grant_formset fieldset')).toHaveCount(0);
    await expect(buttons).toHaveText(['Add Grant']);

    await panel.locator('#add_another').click();
    await expect(byId(page, 'id_grants-TOTAL_FORMS')).toHaveValue('1');
    await expect(panel.locator('.grant_formset fieldset')).toHaveCount(1);
    await expect(byId(page, 'id_grants-0-grant_type')).toBeVisible();
    await expect(buttons).toHaveText(['Delete', 'Add Grant']);
  });

  test('R10 Continue panel replaces Publication/Output and Impact', async ({ page }) => {
    const panel = await expandPanel(page, 'panelEight');
    await expect(panel).toHaveText(
      'Step 8 out of 8 Continue to select cloud resources. Previous Continue',
    );
    await expect(byId(page, 'id_publications-TOTAL_FORMS')).toHaveValue('0');
    await expect(page.getByText(/add (a )?publication/i).filter({ visible: true })).toHaveCount(0);
    // The DOI checker modal exists but is never shown (it calls crossref).
    await expect(page.locator('#modal-doi-checker')).toHaveCount(1);
    await expect(page.locator('#modal-doi-checker')).toBeHidden();

    // The 'Continue' button shows step 2 with the bundle panel open.
    await panel.locator('a.continue-button').click();
    await expect(page.locator('section#form-step1')).toBeHidden();
    await expect(page.locator('section#form-step2')).toBeVisible();
    await expect(page.locator('#panelBundle')).toBeVisible();
    await expect(page.locator('#form-step-title')).toHaveText('Cloud Resources');
    await expect(page.locator('#allocation_form_nav li').nth(1)).toHaveClass(/active/);

    // Back to step 1, then the STEP 2 tab.
    await page.locator('#allocation_form_nav a[href="#form-step1"]').click();
    await expect(page.locator('section#form-step1')).toBeVisible();
    await expect(page.locator('section#form-step2')).toBeHidden();
    await page.locator('#allocation_form_nav a[href="#form-step2"]').click();
    await expect(page.locator('section#form-step1')).toBeHidden();
    await expect(page.locator('section#form-step2')).toBeVisible();
    await expect(page.locator('#allocation_form_nav li').nth(1)).toHaveClass(/active/);
    await expect(page.locator('#allocation_form_nav li').nth(0)).not.toHaveClass(/active/);
    await expect(page).toHaveURL(/\/allocation\/#!#form-step2$/);
  });

  test('R11 Resources: bundle cards and Custom card', async ({ page }) => {
    const panel = await expandPanel(page, 'panelBundle');
    await expect(panel.locator('h3').first()).toHaveText('Resource Bundle');
    await expect(panel.locator('h5').first()).toHaveText(
      'Select the most suitable Resource Bundle for your project needs...',
    );
    await expect(panel.locator('h5').getByRole('link', { name: 'Resource Bundle' })).toHaveAttribute(
      'href',
      'https://support.ehelp.edu.au/support/solutions/articles/6000271205',
    );
    await expect(
      panel.getByRole('link', { name: 'Resource Bundle Table support article' }),
    ).toHaveAttribute('href', 'https://support.ehelp.edu.au/support/solutions/articles/6000271206');
    await expect(panel.locator('.step-nav p')).toHaveText('Step 1 out of 4');

    const cards = panel.locator('.bundle');
    await expect(cards.locator('h4')).toHaveText(['Standard', 'Powerful', 'Extreme', 'Custom']);

    const standard = cards.nth(0);
    await expect(standard.locator('.bundle-badge')).toHaveText('Popular');
    await expect(cards.locator('.bundle-badge')).toHaveCount(1);
    await expect(standard.locator('h3')).toHaveText('4000 SU / year');
    await expect(standard.locator('p.mb-auto')).toHaveText(
      'A standard resource bundle suitable for researchers wanting extra ' +
        'compute power, similar to a personal computer, to host a simple web ' +
        'application or run basic computations.',
    );
    await expect(standard.locator('ul.features li')).toHaveText([
      'Runs 16 VCPUs continuously (max 64 VCPUs at one time)',
      'Up to 40 instances',
      '500 GB Object Storage',
      '2 x reservations for GPUs',
    ]);
    for (const card of [0, 1, 2, 3]) {
      await expect(cards.nth(card).locator('ul.not-features li')).toHaveText(
        'Volume Storage requested separately *',
      );
      await expect(cards.nth(card).getByText('More details')).toBeVisible();
    }
    await expect(standard).toHaveClass(/\bactive\b/);
    await expect(standard.locator('.btn .selected')).toBeVisible();
    await expect(standard.locator('.btn .selected')).toHaveText('Selected');
    await expect(standard.locator('.btn .not-selected')).toBeHidden();
    await expect(standard.locator('.btn .not-selected')).toHaveText('Select Standard');

    const powerful = cards.nth(1);
    await expect(powerful.locator('h3')).toHaveText('8000 SU / year');
    await expect(powerful.locator('ul.features li')).toContainText([
      'Runs 32 VCPUs continuously (max 128 VCPUs at one time)',
      'Up to 80 instances',
      '1500 GB Object Storage',
    ]);
    const extreme = cards.nth(2);
    await expect(extreme.locator('h3')).toHaveText('16000 SU / year');
    await expect(extreme.locator('ul.features li')).toContainText([
      'Runs 64 VCPUs continuously (max 256 VCPUs at one time)',
      'Up to 160 instances',
      '3000 GB Object Storage',
    ]);
    expect(
      await cards.evaluateAll((cs) => cs.map((c) => c.getAttribute('data-bundle'))),
    ).toEqual(['3', '6', '9', null]);

    const custom = cards.nth(3);
    await expect(custom.locator('p.mb-auto')).toHaveText(
      'For advanced cloud users with a specific set of resource requirements. ' +
        'Users must be able to estimate their requested SU budget.',
    );
    await expect(custom.locator('ul.features li')).toHaveText(['User defined resource limits']);
    await expect(custom.locator('.btn .not-selected')).toHaveText('Select Custom');
    await expect(custom.locator('.btn .selected')).toHaveText('Customise');
    await expect(custom.locator('.btn')).toHaveAttribute('data-target', '#modal-custom-bundle');

    const bundle = byId(page, 'id_bundle');
    await expect(bundle).toHaveValue('3');
    expect(await optionTexts(bundle)).toEqual(['---------', 'Standard', 'Powerful', 'Extreme']);
    expect(await optionValues(bundle)).toEqual(['', '3', '6', '9']);

    // A real click on 'Select Powerful' moves the selection.
    await powerful.getByText('Select Powerful').click();
    await expect(bundle).toHaveValue('6');
    await expect(powerful).toHaveClass(/\bactive\b/);
    await expect(standard).not.toHaveClass(/\bactive\b/);
    await expect(panel.locator('.bundle.active')).toHaveCount(1);
    await expect(powerful.locator('.btn .selected')).toBeVisible();
  });

  test('R12 Custom Bundle modal', async ({ page }) => {
    const panel = await expandPanel(page, 'panelBundle');
    const custom = panel.locator('.bundle').nth(3);
    await custom.getByText('Select Custom').click();

    const modal = page.locator('#modal-custom-bundle');
    await expect(modal).toBeVisible();
    await expect(byId(page, 'id_bundle')).toHaveValue('');
    await expect(custom).toHaveClass(/\bactive\b/);
    await expect(panel.locator('.bundle.active')).toHaveCount(1);

    await expect(modal.locator('.modal-title')).toHaveText('Custom Bundle');
    await expect(modal.locator('.modal-body h4').first()).toHaveText(
      'Request custom resource limits for your allocation',
    );
    await expect(modal.locator('.modal-body p').first()).toHaveText(
      '(Fields are prefilled with the same limits as the Extreme Bundle to assist customisation).',
    );
    await expect(modal.locator('legend')).toHaveText([
      'Service Units',
      'Compute Service Limits',
      'Advanced Networking',
      'Object Store',
      'Database Service',
      'Reservation Service',
    ]);
    const su = modal.locator('fieldset').first();
    await expect(su.locator('p').first()).toHaveText(
      'NOTE Unsure how to estimate a usage budget? Checkout this guide.',
    );
    await expect(su.getByRole('link', { name: 'this guide' })).toHaveAttribute(
      'href',
      '#usage_budget_modal',
    );
    await expect(page.locator('#usage_budget_modal .modal-title')).toHaveText(
      'Service Unit Budget Guide',
    );
    await expect(label(page, 'id_quota-rating.budget__nectar')).toHaveText('Budget');
    await expect(su.locator('.input-group-addon')).toHaveText('SUs');
    await expect(su).toContainText(
      'Specify a usage budget in service units. Service units are only used for compute resources.',
    );

    const values: [string, string][] = [
      ['rating.budget__nectar', '16000'],
      ['compute.cores__nectar', '256'],
      ['compute.ram__nectar', '640'],
      ['compute.instances__nectar', '160'],
      ['network.router__nectar', '8'],
      ['network.floatingip__nectar', '16'],
      ['network.loadbalancer__nectar', '16'],
      ['network.security_group__nectar', '90'],
      ['object.object__nectar', '3000'],
      ['object.object__pawsey', '3000'],
      ['database.ram__nectar', '64'],
      ['database.volumes__nectar', '1000'],
      ['nectar-reservation.reservation__nectar', '8'],
      ['nectar-reservation.days__nectar', '400'],
    ];
    for (const [codename, value] of values) {
      await expect(byId(page, `id_quota-${codename}`), codename).toHaveValue(value);
    }
    for (const [codename, text] of [
      ['compute.cores__nectar', 'Virtual Cores'],
      ['compute.ram__nectar', 'RAM'],
      ['compute.instances__nectar', 'Instances'],
      ['compute.flavor:hugeram-v3__nectar', 'Huge RAM Flavors'],
      ['nectar-reservation.flavor:GPU__nectar', 'GPU Flavors'],
      ['nectar-reservation.flavor:Huge RAM__nectar', 'Huge RAM Flavors'],
    ]) {
      await expect(label(page, `id_quota-${codename}`)).toHaveText(text);
    }
    // All three flavour toggles are On (checked) on a new request.
    for (const flavor of [
      'compute.flavor:hugeram-v3__nectar',
      'nectar-reservation.flavor:GPU__nectar',
      'nectar-reservation.flavor:Huge RAM__nectar',
    ]) {
      await expect(toggleOf(page, `id_quota-${flavor}`)).not.toHaveClass(/\boff\b/);
      await expect(toggleOf(page, `id_quota-${flavor}`)).toHaveClass(/btn-primary/);
      await expect(byId(page, `id_quota-${flavor}`)).toBeChecked();
    }

    await expect(modal.locator('.modal-header button.close')).toHaveText('×');
    await modal.locator('.modal-footer button', { hasText: 'Done' }).click();
    await expect(modal).toBeHidden();
    await expect(modal).toHaveCSS('display', 'none');
    await expect(byId(page, 'id_bundle')).toHaveValue('');
  });

  test('R13 Location Specific Resources grouped by zone', async ({ page }) => {
    const panel = await expandPanel(page, 'panelExtras');
    await expect(panel.locator('h3').first()).toHaveText('Location Specific Cloud Resources');
    await expect(panel.locator('h5').first()).toHaveText(
      'The following additional resources can be requested for specific locations.',
    );
    await expect(panel.locator('.mb-4 p').first()).toHaveText(
      'Not sure if you need additional resources? For more information read ' +
        'the Location Specific Resources support article.',
    );
    await expect(
      panel.getByRole('link', { name: 'Location Specific Resources support article' }),
    ).toHaveAttribute('href', 'https://support.ehelp.edu.au/support/solutions/articles/6000272093');

    const blocks = panel.locator('.extra-resource');
    await expect(blocks.locator('h4')).toHaveText(['Volume Service', 'Shared File System Service']);

    const volume = blocks.nth(0);
    await expect(toggleOf(page, 'volume')).toHaveClass(/\boff\b/);
    await expect(volume.locator('p.mb-4')).toContainText(
      'A persistent volume looks and acts like a hard drive',
    );
    await expect(volume.locator('fieldset p')).toHaveText(
      'NOTE University of Melbourne Performance is only available to UoM researchers',
    );
    const zoneFieldset = volume.locator('fieldset:has(legend)');
    await expect(zoneFieldset.locator('legend')).toHaveText('Zones');
    await expect(zoneFieldset).toBeHidden();
    const zones = [
      'auckland', 'encrypted-auckland', 'intersect', 'encrypted-intersect',
      'melbourne', 'encrypted-melbourne', 'performance-melbourne', 'monash',
      'encrypted-monash', 'QRIScloud', 'encrypted-QRIScloud', 'swinburne',
      'encrypted-swinburne', 'tasmania', 'encrypted-tasmania',
    ];
    const volumeInputs = zoneFieldset.locator('input');
    expect(await volumeInputs.evaluateAll((is) => is.map((i) => (i as HTMLInputElement).name))).toEqual(
      zones.map((z) => `quota-volume.gigabytes__${z}`),
    );
    expect(await volumeInputs.evaluateAll((is) => is.map((i) => (i as HTMLInputElement).value))).toEqual(
      zones.map(() => '0'),
    );
    expect(
      (await zoneFieldset.locator('label').allTextContents()).map(normalise),
    ).toEqual([
      'Auckland (NZ) Storage',
      'Auckland (NZ) encrypted Storage',
      'Intersect (NSW) Storage',
      'Intersect (NSW) encrypted Storage',
      'Melbourne University Storage',
      'Melbourne University encrypted Storage',
      'Melbourne University performance Storage',
      'Monash (VIC) Storage',
      'Monash (VIC) encrypted Storage',
      'QRIScloud Storage',
      'QRIScloud encrypted Storage',
      'Swinburne (VIC) Storage',
      'Swinburne (VIC) encrypted Storage',
      'Tasmania Storage',
      'Tasmania encrypted Storage',
    ]);

    const share = blocks.nth(1);
    await expect(toggleOf(page, 'share')).toHaveClass(/\boff\b/);
    const shareSets = share.locator('fieldset.boxed-field');
    await expect(shareSets.locator('legend')).toHaveText(['Auckland (NZ)', 'Monash (VIC)']);
    for (const [i, zone] of ['auckland', 'monash-02-cephfs'].entries()) {
      const set = shareSets.nth(i);
      expect((await set.locator('label').allTextContents()).map(normalise)).toEqual([
        'Shares',
        'Storage',
        'Snapshots',
        'Snapshot storage',
      ]);
      expect(await set.locator('input').evaluateAll((is) => is.map((i) => [(i as HTMLInputElement).name, (i as HTMLInputElement).value]))).toEqual(
        ['shares', 'gigabytes', 'snapshots', 'snapshot_gigabytes'].map((r) => [
          `quota-share.${r}__${zone}`,
          '0',
        ]),
      );
    }

    // Compute-style quotas are prefilled from the Extreme bundle.
    await expect(byId(page, 'id_quota-compute.cores__nectar')).toHaveValue('256');

    await expect(panel.locator('.step-nav p')).toHaveText('Step 2 out of 4');
    await expect(panel.locator('.step-nav a.btn')).toHaveText(['Previous', 'Next']);
  });

  test('R14 Resource Justification, Submit Checklist, Submit button, absent Allocation Classification panel', async ({
    page,
  }) => {
    const panel = await expandPanel(page, 'panelJustification');
    await expect(panel.locator('h3').first()).toHaveText('Resource Justification');
    await expect(panel.locator('h5').first()).toHaveText(
      'Provide some information about the project to justify your selected resources.',
    );
    await expect(label(page, 'id_usage_patterns')).toHaveText(
      'Justification and details of your Proposed Cloud Usage',
    );
    await expect(page.locator('#id_usage_patterns + .char-counter')).toHaveText('0 / 1024');
    await expect(label(page, 'id_geographic_requirements')).toHaveText(
      'Special location requirements',
    );
    await expect(page.locator('#id_geographic_requirements + .char-counter')).toHaveText(
      '0 / 1024',
    );

    const usageGroup = byId(page, 'id_usage_types-group');
    await expect(usageGroup.locator('> label')).toContainText('Usage types');
    await expect(usageGroup.locator('> label .glyphicon-asterisk')).toHaveCount(1);
    await expect(usageGroup.locator('input[type=checkbox]')).toHaveCount(11);
    expect(
      (await usageGroup.locator('label.checkbox-inline').allTextContents()).map(normalise),
    ).toEqual([
      'Hosting services to support research',
      'Collaboration platform',
      'Hosting a website',
      'Hosting a database',
      'Hosting and sharing data',
      'Collaborating with other institutions',
      'Collaborating internationally',
      'Machine learning',
      'Data analysis',
      'Modelling and simulation',
      'Other',
    ]);
    await expect(panel.locator('.step-nav p')).toHaveText('Step 3 out of 4');

    const checklist = await expandPanel(page, 'panelSubmit');
    await expect(checklist.locator('p').first()).toHaveText(
      'Before submitting this allocation request, please review the following checklist:',
    );
    await expect(checklist.locator('li')).toHaveText([
      'I have provided all required project information.',
      'I have provided the data sensitivity and classification details for this project.',
      'I have provided the Chief Investigator details and contact information.',
      'I have provided Research Grant information.',
      'I have provided the FoR code to describe the research for this project.',
    ]);
    await expect(checklist.locator('p', { hasText: 'Step' })).toHaveText('Step 4 out of 4');
    await expect(checklist.locator('a.btn')).toHaveText(['Previous']);

    const submitSection = page.locator('#submit-section');
    await expect(submitSection.locator('h4')).toHaveText(
      'Are you ready to submit this allocation request?',
    );
    await expect(submitSection.locator('.submit-form-button')).toHaveCount(1);
    await expect(submitSection.locator('.submit-form-button')).toHaveValue('Submit');

    // The Allocation Classification panel is only on the admin edit views.
    await expect(page.getByText('Allocation Classification')).toHaveCount(0);
  });

  test('R15 beforeunload prompt on leaving the form', async ({ page, context }) => {
    // Whether leaving is blocked: dispatch a cancelable beforeunload event
    // and see if the page's handler cancels it.
    const blocksLeaving = () =>
      page.evaluate(() => {
        const e = new Event('beforeunload', { cancelable: true });
        window.dispatchEvent(e);
        return e.defaultPrevented;
      });
    await byId(page, 'id_project_description').click();
    expect(await blocksLeaving()).toBe(true);

    // Any .submit-form-button click (here 'Propose an Organisation')
    // unbinds the handler.
    await expandPanel(page, 'panelFour');
    await page.locator('#panelFour input[value="Propose an Organisation"]').click();
    await expect(page.locator('#modal-propose')).toBeVisible();
    await page.locator('#modal-propose .form-actions button', { hasText: 'Close' }).click();
    await expect(page.locator('#modal-propose')).toBeHidden();
    expect(await blocksLeaving()).toBe(false);

    // The real prompt: a beforeunload dialog with an empty message, and
    // accepting it lets the page go.  (Accepting it during a navigation
    // proved unreliable under Playwright on this deployment, so close the
    // page with runBeforeUnload instead.)
    const other = await context.newPage();
    acceptDialogsOnce(other);
    const dialogs: { type: string; message: string }[] = [];
    other.on('dialog', (d) => dialogs.push({ type: d.type(), message: d.message() }));
    await openForm(other);
    await byId(other, 'id_project_description').click();
    const closed = other.waitForEvent('close');
    await other.close({ runBeforeUnload: true });
    await closed;
    expect(dialogs).toEqual([{ type: 'beforeunload', message: '' }]);
  });
});

