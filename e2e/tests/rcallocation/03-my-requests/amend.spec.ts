import { Page } from '@playwright/test';

import { test, expect } from '../../../support/fixtures';
import {
  ADMIN_EMAIL,
  AMEND_TITLE,
  FIX_ERRORS,
  LIST_URL,
  NO_PUBLICATIONS_NAG,
  acceptDialogsOnce,
  amendUrl,
  closeNags,
  createAmendable,
  expandPanel,
  fieldErrors,
  findRow,
  form,
  ignoreWarningsButton,
  open,
  openPanels,
  readTable,
  submitButton,
  submitForm,
} from './helpers';

// Suite 03: the user amend form (/allocation/user_requests/
// edit_change_request/) on fresh Approved allocations with a Chief
// Investigator, created by the admin, who is their contact.

// The dev dashboard is shared with other suites running at the same time;
// form posts and page loads (the My Requests list above all) can take
// minutes under that load.
test.describe.configure({ timeout: 600_000 });

test.beforeEach(({ page }) => acceptDialogsOnce(page));

const AMEND_PANELS = [
  '1. Project Details',
  '2. Usage Information',
  '3. Fields of Research (FOR)',
  '4. Supported Institutions',
  '5. Investigator',
  '6. Project Support',
  '7. Research Grant Information',
  '8. Publication/Output and Impact',
  '9. Continue',
];

async function gotoAmend(page: Page, id: number) {
  const response = await open(page, amendUrl(id));
  expect(response.status()).toBe(200);
  await expect(page).toHaveTitle(AMEND_TITLE);
}

test.describe('My Requests user amend form', () => {
  test('1.17 (4.1) User amend form render', async ({ page, allocations }) => {
    const a = await createAmendable(allocations);
    await gotoAmend(page, a.id);
    await closeNags(page);

    await expect(page.locator('.breadcrumb li')).toHaveText([
      'Allocations',
      'My Requests',
      'None',
    ]);
    // The visible heading is the edit form's, unlike the page title.
    await expect(page.locator('h3').first()).toHaveText(
      'Edit Allocation Request: About the Project',
    );
    await expect(form(page)).toHaveAttribute('method', 'post');
    await expect(form(page)).toHaveAttribute('action', amendUrl(a.id));

    expect(
      (await page.locator('#request_accordion .panel-title a').allInnerTexts()).map((h) => h.trim()),
    ).toEqual(AMEND_PANELS);
    await expect(page.locator('#panelNine')).toHaveCount(1);
    for (const id of ['panelBundle', 'panelExtras', 'panelJustification', 'panelSubmit']) {
      await expect(page.locator(`#${id}`)).toHaveCount(1);
    }
    expect(await openPanels(page)).toEqual(['panelOne', 'panelBundle']);
    // The Standard bundle is selected.
    await expect(page.locator('select#id_bundle option:checked')).toHaveText('Standard');
    await expect(page.locator('.bundle.active h4')).toHaveText('Standard');

    // Panel 1: title, contact and identifier are read-only.
    await expect(page.locator('#id_project_description')).toHaveValue('Playwright e2e fixture');
    await expect(page.locator('#id_contact_email')).toHaveValue(ADMIN_EMAIL);
    await expect(page.locator('#id_project_name')).toHaveValue(a.project_name);
    for (const id of ['project_description', 'contact_email', 'project_name']) {
      await expect(page.locator(`#id_${id}`), id).toHaveAttribute('readonly', /.*/);
    }
    await expect(page.locator('label[for=id_project_name]')).toHaveText('Project identifier');
    await expect(page.getByLabel('Generated project DNS zone name')).toHaveValue(
      `${a.project_name}.cloud.edu.au`,
    );
    await expect(page.locator('label[for=id_estimated_project_duration]')).toHaveText(
      'Estimated extension duration',
    );
    await expect(page.locator('#id_estimated_project_duration option:checked')).toHaveText(
      '12-months',
    );

    // Panel 2: the past-year figures replace the estimates.  They are
    // prefilled from the estimates (1, 1, 1).
    await expandPanel(page, '2. Usage Information', 'panelTwo');
    await expect(page.locator('#id_multiple_allocations_check')).toHaveCount(1);
    for (const [field, label] of [
      ['direct_access_user_past_year', 'Number of users directly accessing instances over the past year'],
      ['active_service_count', 'Number of active research services or platforms hosted using this allocation'],
      ['service_active_users_past_year', 'Total number of unique active users of these services over the past year'],
    ]) {
      await expect(page.locator(`label[for=id_${field}]`)).toHaveText(label);
      await expect(page.locator(`#id_${field}`)).toHaveValue('1');
    }
    await expect(page.locator('label[for=id_users_figure_type]')).toHaveText(
      'Are the above figures measured or estimated?',
    );
    await expect(page.locator('#id_users_figure_type option:checked')).toHaveText('Measured');
    // No blank option.
    await expect(page.locator('#id_users_figure_type option')).toHaveText([
      'Measured',
      'Estimated',
    ]);
    await expect(page.locator('#id_use_case')).toHaveValue('Playwright end-to-end test fixture');
    await expect(page.locator('#id_has_sensitive_data option:checked')).toHaveText(
      'No, the project does not involve sensitive data.',
    );
    await expect(page.locator('#id_data_classification_level option:checked')).toHaveText('Green');
    await expect(page.locator('#id_data_classification_level')).toBeDisabled();
    await expect(page.locator('#id_institutional_data_review option:checked')).toHaveText(
      'Please select...',
    );
    for (const field of [
      'direct_access_user_estimate',
      'estimated_service_count',
      'estimated_service_active_users',
    ]) {
      await expect(page.locator(`#id_${field}`), field).toHaveCount(0);
    }

    // Panels 3 to 5.
    for (const [n, pct] of [[1, '100%'], [2, '0%'], [3, '0%']]) {
      await expect(page.locator(`#id_for_percentage_${n} option:checked`)).toHaveText(pct as string);
    }
    await expect(page.locator('#panelFour input[name=anz]')).toBeChecked();
    await expect(page.locator('#id_investigators-0-given_name')).toHaveValue('Pw');
    await expect(page.locator('#id_investigators-0-surname')).toHaveValue('Tester');
    await expect(page.locator('#id_investigators-0-email')).toHaveValue('pw@example.edu.au');

    // Panel 7: an empty grant row with the years prefilled.
    const year = new Date().getFullYear();
    await expect(page.locator('#id_grants-0-grant_type')).toHaveValue('');
    await expect(page.locator('#id_grants-0-first_year_funded')).toHaveValue(String(year));
    await expect(page.locator('#id_grants-0-last_year_funded')).toHaveValue(String(year + 1));
    await expect(page.locator('#id_grants-0-total_funding')).toHaveValue('');
    await expect(page.locator('#panelSeven')).toContainText("I don't have any grants");

    // Panel 8: publications and impact.
    await expandPanel(page, '8. Publication/Output and Impact', 'panelEight');
    const p8 = page.locator('#panelEight');
    await expect(p8).toHaveClass(/\bpanel-collapse\b/);
    await expect(p8).toContainText('Step 8 out of 9');
    await expect(p8).toContainText(
      'List any publications or other research outputs from work on this ' +
        'project that has been supported by use of the Nectar cloud.',
    );
    await expect(p8.getByText('Add publication')).toBeVisible();
    for (const [field, label] of [
      ['nectar_benefit_description', 'Benefits of Nectar'],
      ['nectar_research_impact', 'Research Impact'],
    ]) {
      await expect(page.locator(`label[for=id_${field}]`)).toHaveText(label);
      const textarea = page.locator(`#id_${field}`);
      await expect(textarea).toHaveValue('');
      await expect(textarea.locator('xpath=following-sibling::small[1]')).toHaveText('0 / 4096');
    }
    await expect(p8.getByText('Previous')).toBeVisible();
    await expect(p8.getByText('Next')).toBeVisible();

    // Justification: empty, with the usage type from the fixture.
    await expect(page.locator('#id_usage_patterns')).toHaveValue('');
    await expect(page.locator('#id_geographic_requirements')).toHaveValue('');
    const checked = await page
      .locator('#panelJustification input[name=usage_types]:checked')
      .evaluateAll((cs) =>
        cs.map((c) => c.closest('label')?.textContent?.trim() ?? ''),
      );
    expect(checked).toEqual(['Hosting services to support research']);

    await expect(submitButton(page)).toHaveCount(1);
    await expect(ignoreWarningsButton(page)).toHaveCount(0);
  });

  test('1.18 (4.2) Attention alert and Attention Required modal', async ({
    page,
    allocations,
  }) => {
    const a = await createAmendable(allocations);
    await gotoAmend(page, a.id);

    const alert = page.locator('.alert.alert-warning[role=alert]', {
      has: page.locator('h4', { hasText: 'Attention' }),
    });
    await expect(alert).toBeVisible();
    await expect(alert.locator('h4 .fa-warning')).toHaveCount(1);
    await expect(alert.locator('p')).toHaveText(
      'There are items that require your attention before you submit this form.',
    );
    const review = alert.locator('input[type=button][value="Review Reminders"]');
    await expect(review).toHaveAttribute('onclick', 'show_nags()');

    // The modal is open on load.
    const modal = page.locator('#modal-nags');
    await expect(modal).toBeVisible();
    await expect(modal).toHaveClass(/\bmodal\b.*\bin\b/);
    await expect(modal.locator('.modal-title')).toHaveText('Attention Required');
    await expect(modal.locator('.modal-header button.close')).toHaveText('×');
    await expect(modal.locator('.modal-body p').first()).toHaveText(
      'The following items require your attention before you submit this ' +
        'amendment. These may be a result of changes that we have made to ' +
        'this form since your last submission.',
    );
    await expect(modal.locator('.modal-body li')).toHaveText([NO_PUBLICATIONS_NAG]);
    await expect(modal.locator('.modal-footer button')).toHaveText(['Close']);

    await closeNags(page);
    await expect(modal).toHaveCSS('display', 'none');

    // Review Reminders reopens it.
    await review.click();
    await expect(modal).toBeVisible();
    await expect(modal.locator('.modal-body li')).toHaveText([NO_PUBLICATIONS_NAG]);
    await closeNags(page);
  });

  test('1.19 (4.3) Invalid amend submit with past-year fields cleared', async ({
    page,
    allocations,
  }) => {
    const a = await createAmendable(allocations);
    const historyBefore = (await allocations.history(a.id)).map((h) => h.id);
    await gotoAmend(page, a.id);
    await closeNags(page);

    await expandPanel(page, '2. Usage Information', 'panelTwo');
    for (const field of [
      'direct_access_user_past_year',
      'active_service_count',
      'service_active_users_past_year',
    ]) {
      await page.locator(`#id_${field}`).fill('');
    }
    // The select has no blank option (the model has a default), so a user
    // cannot clear it; set an empty value by script as the plan does.
    await page.locator('#id_users_figure_type').evaluate((el) => {
      const select = el as HTMLSelectElement;
      select.add(new Option('', ''));
      select.value = '';
      select.dispatchEvent(new Event('change', { bubbles: true }));
    });
    await submitForm(page, submitButton(page));

    await expect(page).toHaveURL(amendUrl(a.id));
    await expect(page).toHaveTitle(AMEND_TITLE);
    await expect(page.locator('.alert-danger').filter({ visible: true })).toHaveText(FIX_ERRORS);
    expect(await fieldErrors(page)).toEqual([
      ['panelTwo', 'Number of users directly accessing instances over the past year', 'This field is required'],
      ['panelTwo', 'Number of active research services or platforms hosted using this allocation', 'This field is required'],
      ['panelTwo', 'Total number of unique active users of these services over the past year', 'This field is required'],
      ['panelTwo', 'Are the above figures measured or estimated?', 'This field is required.'],
      // The prefilled grant years make the empty grant row invalid.
      ['panelSeven', 'Grant Type', 'This field is required.'],
      ['panelSeven', 'Grant Subtype', 'This field is required.'],
      ['panelSeven', 'Total funding (AUD)', 'This field is required.'],
    ]);
    // Only the panel with the first error opens.
    expect(await openPanels(page)).toEqual(['panelTwo', 'panelBundle']);
    // No nags modal after a POST.
    await expect(page.locator('#modal-nags')).toHaveCount(0);

    const after = await allocations.get(a.id);
    expect(after.status).toBe('A');
    expect((await allocations.history(a.id)).map((h) => h.id)).toEqual(historyBefore);
  });

  test('1.19 (4.3) Valid amend submit without grants moves A to X', async ({
    page,
    allocations,
  }) => {
    const a = await createAmendable(allocations);
    const historyBefore = await allocations.history(a.id);
    await gotoAmend(page, a.id);
    await closeNags(page);

    // Drop the empty grant row, then submit.
    await expandPanel(page, '7. Research Grant Information', 'panelSeven');
    await page.locator('#panelSeven').getByText("I don't have any grants").click();
    await expect(page.locator('#id_grants-0-grant_type')).toBeHidden();
    const response = await submitForm(page, submitButton(page));
    expect(response.status()).toBe(302);

    await expect(page).toHaveURL(LIST_URL);
    await expect(page.locator('.messages .alert')).toHaveCount(0);
    const r = findRow(await readTable(page), a.id);
    expect(r.cells[0]).toBe('X');
    expect(r.stateTitle).toBe('Update requested');
    expect(r.actions.map((x) => x.text)).toEqual(['Edit amend/extend request']);

    const after = await allocations.get(a.id);
    expect(after.status).toBe('X');
    // The approved record was copied into one more history record.
    const history = await allocations.history(a.id);
    expect(history.length).toBe(historyBefore.length + 1);
    expect(history.map((h) => h.status)).toContain('A');
  });
});
