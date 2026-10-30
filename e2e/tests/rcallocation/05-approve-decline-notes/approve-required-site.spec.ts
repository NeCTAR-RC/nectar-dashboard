import { test, expect } from '../../../support/fixtures';
import { APPROVE_TITLE, submitInPlace, TEST_TIMEOUT } from './helpers';

// Suite 05: Associated site is required on approval, in the browser and
// on the server.
test.describe('Approve validation', () => {
  test('5.8 Approve: Associated site required validation', async ({
    page,
    allocations,
  }) => {
    test.setTimeout(TEST_TIMEOUT);
    const e = await allocations.create();
    const url = `/allocation/requests/approve_request/${e.id}/`;
    await page.goto(url);
    await expect(page).toHaveTitle(APPROVE_TITLE);

    // Client side: the empty required select blocks the submit.
    const site = page.locator('#id_associated_site');
    await expect(site).toHaveValue('');
    expect(await site.evaluate((s: HTMLSelectElement) => s.validity.valid)).toBe(false);
    expect(
      await site.evaluate((s: HTMLSelectElement) => s.validationMessage),
    ).toBe('Please select an item in the list.');
    expect(
      await page
        .locator('form#new-allocation')
        .evaluate((f: HTMLFormElement) => f.checkValidity()),
    ).toBe(false);
    await page.locator('input[type=submit][value="Approve Request"]').click();
    await expect(page).toHaveURL(url);
    await expect(page.locator('.alert-danger')).toHaveCount(0);

    // Server side: without the required attribute the POST re-renders the
    // form with the error.
    await site.evaluate((s) => s.removeAttribute('required'));
    await submitInPlace(
      page,
      page.locator('input[type=submit][value="Approve Request"]'),
    );
    await expect(page).toHaveURL(url);
    await expect(page).toHaveTitle(APPROVE_TITLE);
    await expect(page.locator('.alert.alert-danger')).toHaveText(
      'Please fix the errors highlighted below and resubmit.',
    );
    const group = page.locator('#id_associated_site-group');
    await expect(group).toHaveClass(/\bhas-error\b/);
    await expect(group.locator('.help-block')).toHaveText('This field is required.');
    await expect(page.locator('.has-error')).toHaveCount(1);
    // Other values are kept.
    await expect(page.locator('#id_bundle option:checked')).toHaveText('Standard');
    await expect(page.locator('.alert-warning')).toHaveCount(0);

    // Nothing saved.
    expect((await allocations.get(e.id)).status).toBe('E');
    expect(await allocations.history(e.id)).toEqual([]);
  });
});
