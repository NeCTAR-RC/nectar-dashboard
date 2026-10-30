import { test, expect } from '../../../support/fixtures';
import { uniqueProjectName } from '../../../support/allocations';
import {
  CREATE_TIMEOUT,
  FIX_ERRORS,
  FORM_URL,
  acceptDialogsOnce,
  byId,
  errorMap,
  expandPanel,
  fillBaseline,
  idFromHref,
  ignoreWarningsButton,
  openForm,
  submit,
  submitButton,
  submitWith,
} from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('New Request form: warnings', () => {
  // Creates one Submitted (E) pwtest- allocation.
  test.setTimeout(600_000);
  test('W1 Quota warning FLAVORS_NOT_JUSTIFIED with ignore and resubmit', async ({
    page,
    allocations,
  }) => {
    const name = uniqueProjectName('w1');
    await openForm(page);
    await fillBaseline(page, {
      project_name: name,
      project_description: 'PW warnings flow test',
      usage_patterns: '',
    });

    // Choose Custom.  Huge RAM Flavors (compute) is already On by default,
    // so leave it as it is.
    const panel = await expandPanel(page, 'panelBundle');
    await panel.locator('.bundle').nth(3).getByText('Select Custom').click();
    const modal = page.locator('#modal-custom-bundle');
    await expect(modal).toBeVisible();
    await expect(byId(page, 'id_quota-compute.flavor:hugeram-v3__nectar')).toBeChecked();
    await modal.locator('.modal-footer button', { hasText: 'Done' }).click();
    await expect(modal).toBeHidden();
    await expect(byId(page, 'id_bundle')).toHaveValue('');

    await submit(page);
    await expect(page).toHaveURL(FORM_URL);
    expect(await errorMap(page)).toEqual({});
    await expect(page.getByText(FIX_ERRORS)).toHaveCount(0);

    const warning = page.locator('.alert-warning', { hasText: 'Warnings' });
    await expect(warning).toHaveText(
      'Warnings Please review the following warnings. Then either modify ' +
        'the form and "Submit" it again, or "Submit ignoring warnings". ' +
        'Requests for access to special flavors must be explained in the ' +
        '"Justification ..." field. More information',
    );
    await expect(warning.locator('li')).toHaveCount(1);
    await expect(warning.getByRole('link', { name: 'More information' })).toHaveAttribute(
      'href',
      /#FLAVORS_NOT_JUSTIFIED$/,
    );
    await expect(warning.getByRole('link', { name: 'More information' })).toHaveAttribute(
      'target',
      '_blank',
    );

    const buttons = page.locator('#submit-section .submit-form-button');
    await expect(buttons).toHaveCount(2);
    expect(
      await buttons.evaluateAll((bs) => bs.map((b) => (b as HTMLInputElement).value)),
    ).toEqual(['Submit', 'Submit ignoring warnings']);
    await expect(submitButton(page)).toHaveAttribute('type', 'submit');
    await expect(ignoreWarningsButton(page)).toHaveAttribute('type', 'button');
    await expect(byId(page, 'id_ignore_warnings')).toHaveValue('');

    // The form kept its values, including the Custom bundle.
    await expect(byId(page, 'id_project_name')).toHaveValue(name);
    await expect(byId(page, 'id_bundle')).toHaveValue('');

    // Submit ignoring warnings: the flag is set, the buttons are disabled
    // and the form posts natively.
    const posted = page.waitForRequest(
      (r) => r.method() === 'POST' && new URL(r.url()).pathname === FORM_URL,
    );
    await submitWith(page, ignoreWarningsButton(page), CREATE_TIMEOUT);
    expect((await posted).postData()).toContain('ignore_warnings=1');
    await expect(page).toHaveURL(/\/allocation\/user_requests\/$/);
    await expect(page).toHaveTitle('Allocation Requests - Nectar Dashboard');

    const link = page.locator('table tbody a', { hasText: name });
    await expect(link).toHaveCount(1);
    const id = idFromHref(await link.getAttribute('href'));
    const row = page.locator('table tbody tr', {
      has: page.locator(`a[href="/allocation/user_requests/view/${id}/"]`),
    });
    const cells = await row
      .locator('td')
      .evaluateAll((tds) =>
        tds.map((td) => (td as HTMLElement).innerText.replace(/\s+/g, ' ').trim()),
      );
    expect(cells.slice(0, 4)).toEqual(['E', `${name} PW warnings flow test`, '-', 'False']);
    expect(cells.slice(6)).toEqual(['-', 'Edit request']);
    await expect(row.locator('td.actions_column a')).toHaveAttribute(
      'href',
      `/allocation/user_requests/edit_request/${id}/`,
    );

    const created = await allocations.get(id);
    expect(created.status).toBe('E');
    expect(created.project_name).toBe(name);
  });
});
