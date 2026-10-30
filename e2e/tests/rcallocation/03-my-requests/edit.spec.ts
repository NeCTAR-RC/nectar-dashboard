import { Page } from '@playwright/test';

import { test, expect } from '../../../support/fixtures';
import {
  ADMIN_EMAIL,
  EDIT_TITLE,
  FIX_ERRORS,
  FLAVORS_HREF,
  FLAVORS_WARNING,
  LIST_TITLE,
  LIST_URL,
  acceptDialogsOnce,
  createEditable,
  datePart,
  detailButtons,
  detailTables,
  editUrl,
  expandPanel,
  fieldErrors,
  form,
  gotoDetail,
  ignoreWarningsButton,
  open,
  openPanels,
  possibleDates,
  readTable,
  findRow,
  requestHugeRam,
  section,
  submitButton,
  submitForm,
} from './helpers';

// Suite 03: the user edit form (/allocation/user_requests/edit_request/)
// on fresh Submitted allocations created by the admin, who is their
// contact.  Each has a Chief Investigator so that only the field a test
// clears fails validation.

// The dev dashboard is shared with other suites running at the same time;
// form posts and page loads (the My Requests list above all) can take
// minutes under that load.
test.describe.configure({ timeout: 600_000 });

test.beforeEach(({ page }) => acceptDialogsOnce(page));

const DETAIL_PANELS = [
  '1. Project Details',
  '2. Usage Information',
  '3. Fields of Research (FOR)',
  '4. Supported Institutions',
  '5. Investigator',
  '6. Project Support',
  '7. Research Grant Information',
  '8. Publication/Output and Impact',
  '8. Continue',
];
const RESOURCE_PANELS = [
  '1. Resource Bundles',
  '2. Location Specific Resources',
  '3. Resource Justification',
  '4. Submit Checklist',
];
const APPENDED = ' [regression edit 03]';

async function gotoEdit(page: Page, id: number) {
  const response = await open(page, editUrl(id));
  expect(response.status()).toBe(200);
  await expect(page).toHaveTitle(EDIT_TITLE);
}

// Append to the use case and ask for Huge RAM flavors without a
// justification, then submit: the form comes back with a warning.
async function submitWithWarning(page: Page) {
  await expandPanel(page, '2. Usage Information', 'panelTwo');
  const useCase = page.locator('#id_use_case');
  await useCase.fill(`${await useCase.inputValue()}${APPENDED}`);
  await requestHugeRam(page);
  const response = await submitForm(page, submitButton(page));
  expect(response.status()).toBe(200);
  await expect(page.locator('.alert-warning', { hasText: 'Warnings' })).toBeVisible();
}

test.describe('My Requests user edit form', () => {
  test('1.11 (3.1) User edit form render', async ({ page, allocations }) => {
    const e = await createEditable(allocations, { grant: true });
    await gotoEdit(page, e.id);

    await expect(page.locator('.breadcrumb li')).toHaveText([
      'Allocations',
      'My Requests',
      'None',
    ]);
    await expect(page.locator('h3').first()).toHaveText(
      'Edit Allocation Request: About the Project',
    );
    await expect(page.getByRole('heading', { name: 'ORCID Connected' })).toHaveCount(1);
    await expect(page.getByRole('heading', { name: 'Before you begin...' })).toBeVisible();
    // No nags and no warnings on a fresh load.
    await expect(page.locator('#modal-nags')).toHaveCount(0);
    await expect(page.getByRole('heading', { name: 'Attention' })).toHaveCount(0);
    await expect(page.locator('.alert-warning', { hasText: 'Warnings' })).toHaveCount(0);

    await expect(form(page)).toHaveAttribute('method', 'post');
    await expect(form(page)).toHaveAttribute('action', editUrl(e.id));
    await expect(form(page)).toHaveAttribute('novalidate', 'novalidate');
    await expect(page.locator('#form-step1')).toHaveCount(1);
    await expect(page.locator('#form-step2')).toHaveCount(1);

    // Panels.  The publications panel exists but is hidden (and has no
    // id) for a Submitted request, so two panels are numbered 8.
    const headings = await page
      .locator('#request_accordion .panel-title a')
      .allInnerTexts();
    expect(headings.map((h) => h.trim())).toEqual(DETAIL_PANELS);
    await expect(
      page.getByRole('link', { name: '8. Publication/Output and Impact' }),
    ).toBeHidden();
    expect(
      (await page.locator('#resources_accordion .panel-title a').allInnerTexts()).map(
        (h) => h.trim(),
      ),
    ).toEqual(RESOURCE_PANELS);
    expect(await openPanels(page)).toEqual(['panelOne', 'panelBundle']);
    await expect(page.locator('#panelOne')).toContainText('Step 1 out of 8');

    // Panel 1.
    await expect(page.locator('#id_project_description')).toHaveValue('Playwright e2e fixture');
    await expect(page.locator('#id_contact_email')).toHaveValue(ADMIN_EMAIL);
    await expect(page.locator('#id_contact_email')).toHaveAttribute('readonly', /.*/);
    await expect(page.locator('#id_project_name')).toHaveValue(e.project_name);
    await expect(page.locator('#id_project_name')).toBeEditable();
    await expect(page.getByLabel('Generated project DNS zone name')).toHaveValue(
      `${e.project_name}.cloud.edu.au`,
    );
    await expect(page.locator('#id_estimated_project_duration')).toHaveValue('12');
    await expect(
      page.locator('#id_estimated_project_duration option:checked'),
    ).toHaveText('12-months');
    await expect(page.locator('#id_convert_trial_project option:checked')).toHaveText(
      'No, start with a blank project.',
    );

    // Panel 2.
    await expandPanel(page, '2. Usage Information', 'panelTwo');
    await expect(page.locator('#panelTwo')).toContainText('Step 2 out of 8');
    await expect(page.locator('#id_multiple_allocations_check option:checked')).toHaveText(
      'No, this is the only allocation for this project.',
    );
    for (const [field, label] of [
      ['direct_access_user_estimate', 'Estimated number of users who will directly access the instances'],
      ['estimated_service_count', 'Estimated number of research services or platforms to be hosted using this allocation'],
      ['estimated_service_active_users', 'Estimated total number of unique active users of these services'],
    ]) {
      await expect(page.locator(`label[for=id_${field}]`)).toHaveText(label);
      await expect(page.locator(`#id_${field}`)).toHaveValue('1');
    }
    await expect(page.locator('label[for=id_use_case]')).toHaveText('Research project description');
    await expect(page.locator('#id_use_case')).toHaveValue('Playwright end-to-end test fixture');
    await expect(page.locator('#id_has_sensitive_data option:checked')).toHaveText(
      'No, the project does not involve sensitive data.',
    );
    await expect(page.locator('#id_data_classification_level option:checked')).toHaveText('Green');
    await expect(page.locator('#id_data_classification_level')).toBeDisabled();
    await expect(page.locator('#id_institutional_data_review option:checked')).toHaveText(
      'Please select...',
    );

    // Panel 3: FOR percentages.
    for (const [n, pct] of [[1, '100%'], [2, '0%'], [3, '0%']]) {
      await expect(page.locator(`#id_for_percentage_${n} option:checked`)).toHaveText(pct as string);
    }
    // Panel 4: organisations.
    await expect(page.locator('#panelFour input[name=anz]')).toBeChecked();
    await expect(page.locator('#panelFour')).toContainText('Propose an Organisation');
    // Panel 5: the Chief Investigator added through the API.
    await expect(page.locator('#id_investigators-0-title')).toHaveValue('Dr');
    await expect(page.locator('#id_investigators-0-given_name')).toHaveValue('Pw');
    await expect(page.locator('#id_investigators-0-surname')).toHaveValue('Tester');
    await expect(page.locator('#id_investigators-0-email')).toHaveValue('pw@example.edu.au');
    await expect(page.locator('#id_investigators-0-additional_researchers')).toHaveValue('');
    // Panel 6: no ARDC or NCRIS support.
    await expect(page.locator('#id_ardc_explanation')).toHaveValue('');
    await expect(page.locator('#id_ncris_explanation')).toHaveValue('');
    // Panel 7: the grant added through the API.
    await expect(page.locator('#id_grants-0-grant_type option:checked')).toHaveText(
      'Institutional research funding',
    );
    await expect(page.locator('#id_grants-0-grant_subtype')).toHaveValue('unspecified');
    await expect(page.locator('#id_grants-0-funding_body_scheme')).toHaveValue('Uni fund');
    await expect(page.locator('#id_grants-0-first_year_funded')).toHaveValue('2026');
    await expect(page.locator('#id_grants-0-last_year_funded')).toHaveValue('2027');
    await expect(page.locator('#id_grants-0-total_funding')).toHaveValue(/^1000(\.0+)?$/);
    // Panel 8: Continue.
    await expect(page.locator('#panelEight')).toContainText('Continue to select cloud resources.');

    // Resources step: bundle cards and justification.
    const bundles = page.locator('#panelBundle .bundle h4');
    await expect(bundles).toHaveText(['Standard', 'Powerful', 'Extreme', 'Custom']);
    await expect(page.locator('#panelBundle')).toContainText('4000 SU / year');
    await expect(page.locator('#panelBundle')).toContainText('8000 SU / year');
    await expect(page.locator('#panelBundle')).toContainText('16000 SU / year');
    await expect(page.locator('#panelJustification #id_usage_patterns')).toHaveCount(1);
    await expect(page.locator('#panelJustification #id_geographic_requirements')).toHaveCount(1);
    await expect(page.locator('#panelJustification input[name=usage_types]')).toHaveCount(11);

    await expect(
      page.getByRole('heading', { name: 'Are you ready to submit this allocation request?' }),
    ).toHaveCount(1);
    await expect(submitButton(page)).toHaveClass('btn btn-primary submit-form-button');
    await expect(ignoreWarningsButton(page)).toHaveCount(0);
  });

  test('1.12 (3.2) Invalid edit submit with an error in the open panel', async ({
    page,
    allocations,
  }) => {
    const e = await createEditable(allocations);
    await gotoEdit(page, e.id);
    await page.locator('#id_project_description').fill('');
    await submitForm(page, submitButton(page));

    await expect(page).toHaveURL(editUrl(e.id));
    await expect(page).toHaveTitle(EDIT_TITLE);
    await expect(page.locator('.alert-danger').filter({ visible: true })).toHaveText(FIX_ERRORS);
    expect(await fieldErrors(page)).toEqual([
      ['panelOne', 'Project allocation title', 'This field is required.'],
    ]);
    expect(await openPanels(page)).toEqual(['panelOne', 'panelBundle']);
    await expect(page.locator('#id_project_description')).toHaveValue('');

    // Nothing saved.
    expect(await allocations.history(e.id)).toEqual([]);
    expect((await allocations.get(e.id)).project_description).toBe('Playwright e2e fixture');
  });

  test('1.13 (3.3) Invalid edit submit in a collapsed panel auto-expands it', async ({
    page,
    allocations,
  }) => {
    const e = await createEditable(allocations);
    await gotoEdit(page, e.id);
    await expandPanel(page, '2. Usage Information', 'panelTwo');
    await page.locator('#id_direct_access_user_estimate').fill('');
    await submitForm(page, submitButton(page));

    await expect(page).toHaveURL(editUrl(e.id));
    await expect(page.locator('.alert-danger').filter({ visible: true })).toHaveText(FIX_ERRORS);
    expect(await fieldErrors(page)).toEqual([
      [
        'panelTwo',
        'Estimated number of users who will directly access the instances',
        'This field is required',
      ],
    ]);
    // The panel with the error opens; panelOne is now closed.
    expect(await openPanels(page)).toEqual(['panelTwo', 'panelBundle']);
    expect(await allocations.history(e.id)).toEqual([]);
  });

  test('1.14 (3.4) Edit submit with special flavors shows the Warnings block', async ({
    page,
    allocations,
  }) => {
    const e = await createEditable(allocations);
    await gotoEdit(page, e.id);
    await submitWithWarning(page);

    await expect(page).toHaveURL(editUrl(e.id));
    await expect(page).toHaveTitle(EDIT_TITLE);
    await expect(page.locator('.alert-danger').filter({ visible: true })).toHaveCount(0);

    const warning = page.locator('.alert.alert-warning').filter({ visible: true });
    await expect(warning).toHaveCount(1);
    await expect(warning.locator('h4')).toHaveText('Warnings');
    await expect(warning.locator('h4 i.fa-exclamation-triangle')).toHaveCount(1);
    await expect(warning.locator('p')).toHaveText(
      'Please review the following warnings. Then either modify the form and ' +
        '"Submit" it again, or "Submit ignoring warnings".',
    );
    await expect(warning.locator('hr')).toHaveCount(1);
    const items = warning.locator('li');
    await expect(items).toHaveCount(1);
    await expect(items).toHaveText(`${FLAVORS_WARNING} More information`);
    const more = items.getByRole('link', { name: 'More information' });
    await expect(more).toHaveAttribute('href', FLAVORS_HREF);
    await expect(more).toHaveAttribute('target', '_blank');

    await expect(submitButton(page)).toBeVisible();
    await expect(ignoreWarningsButton(page)).toBeVisible();
    await expect(ignoreWarningsButton(page)).toHaveAttribute('onclick', 'submit_ignore()');

    // The posted use case persists in the re-rendered form.
    await expect(page.locator('#id_use_case')).toHaveValue(
      `Playwright end-to-end test fixture${APPENDED}`,
    );
    // The DOI checker's failure alert is in the DOM but hidden.
    await expect(page.locator('.alert-danger', { hasText: 'DOI lookup failure' })).toBeHidden();

    // Nothing saved yet.
    expect(await allocations.history(e.id)).toEqual([]);
    expect((await allocations.get(e.id)).use_case).toBe('Playwright end-to-end test fixture');
  });

  test('1.15 (3.5) Successful edit via Submit ignoring warnings', async ({
    page,
    allocations,
  }) => {
    const e = await createEditable(allocations);
    await gotoEdit(page, e.id);
    await submitWithWarning(page);
    const response = await submitForm(page, ignoreWarningsButton(page));
    expect(response.status()).toBe(302);

    await expect(page).toHaveURL(LIST_URL);
    await expect(page).toHaveTitle(LIST_TITLE);
    await expect(page.locator('h1')).toHaveText(['My Requests']);
    // No success message.
    await expect(page.locator('.messages .alert')).toHaveCount(0);

    const r = findRow(await readTable(page), e.id);
    expect(r.stateTitle).toBe('Submitted');
    expect(r.stateClass).toBe('alloc-icon alloc-icon-wip');
    expect(r.cells.slice(0, 2)).toEqual(['E', `${e.project_name} Playwright e2e fixture`]);
    expect(r.actions.map((a) => a.text)).toEqual(['Edit request']);

    const after = await allocations.get(e.id);
    expect(after.status).toBe('E');
    expect(after.use_case).toBe(`Playwright end-to-end test fixture${APPENDED}`);
    // Custom bundle with Huge RAM.
    expect(after.bundle).toBeNull();
    expect(possibleDates(after.modified_time as string)).toContain(r.cells[5]);
  });

  test('1.16 (3.6) History and detail after a successful edit', async ({
    page,
    allocations,
  }) => {
    const e = await createEditable(allocations);
    await gotoEdit(page, e.id);
    await submitWithWarning(page);
    await submitForm(page, ignoreWarningsButton(page));
    await expect(page).toHaveURL(LIST_URL);

    // The edit copied the old record into one history record.
    const history = await allocations.history(e.id);
    expect(history.map((h) => h.status)).toEqual(['E']);
    const old = history[0].id;

    const response = await open(page, `/allocation/requests/view/${e.id}/history`);
    expect(response.status()).toBe(200);
    await expect(page).toHaveTitle(LIST_TITLE);
    await expect(page.locator('.table_count').first()).toHaveText('Displaying 2 items');
    expect(
      (await page.locator('#datatableoptions thead th').allInnerTexts()).map((t) => t.trim()),
    ).toEqual([
      'Project name',
      'Approver',
      'Bundle',
      'SUs',
      'Cores',
      'RAM',
      'Object Storage',
      'Volume Storage',
      'Status',
      'Modification time',
    ]);
    // Newest first: the edit came well over a second after the create, so
    // clock skew between the dev backends cannot reorder them.
    const links = page.locator('#datatableoptions tbody tr td:first-child a');
    await expect(links).toHaveText(['Playwright e2e fixture', 'Playwright e2e fixture']);
    expect(await links.evaluateAll((as) => as.map((a) => a.getAttribute('href')))).toEqual([
      `/allocation/requests/view/${e.id}/`,
      `/allocation/requests/view/${old}/`,
    ]);
    const statuses = page.locator('#datatableoptions tbody tr td:nth-child(9)');
    await expect(statuses).toHaveText(['Submitted', 'Submitted']);
    // The current record is Custom ('-'), the old one Standard.
    const bundles = page.locator('#datatableoptions tbody tr td:nth-child(3)');
    await expect(bundles).toHaveText(['-', 'Standard']);

    await gotoDetail(page, e.id);
    const after = await allocations.get(e.id);
    const tables = await detailTables(page);
    expect(tables[1][0]).toBe('State Submitted');
    expect(possibleDates(after.submit_date as string)).toContain(
      datePart(tables[0][1].replace(/^Submit date /, '')),
    );
    expect(possibleDates(after.modified_time as string)).toContain(
      datePart(tables[0][2].replace(/^Last updated /, '')),
    );
    expect(await section(page, 'Use Case')).toBe(`Playwright end-to-end test fixture${APPENDED}`);
    expect((await detailButtons(page)).map((b) => b.text)).toEqual(['Edit request']);
  });
});
