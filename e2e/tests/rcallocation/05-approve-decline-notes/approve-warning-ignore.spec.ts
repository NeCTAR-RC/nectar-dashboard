import { test, expect } from '../../../support/fixtures';
import {
  APPROVER_PROBLEM,
  APPROVE_TITLE,
  WARNINGS_INTRO,
  WARNING_INFO_URL,
  gotoPending,
  pendingLink,
  submitInPlace,
  submitTo,
  TEST_TIMEOUT,
} from './helpers';

// Suite 05: the test user is not registered as an approver for any site,
// so every approval raises APPROVER_PROBLEM and needs 'Approve ignoring
// warnings'.
test.describe('Approve warnings', () => {
  test('5.9 Approve: approver registration warning and ignore', async ({
    page,
    allocations,
  }) => {
    test.setTimeout(TEST_TIMEOUT);
    const e = await allocations.create();
    const url = `/allocation/requests/approve_request/${e.id}/`;
    await page.goto(url);
    await page.locator('#id_associated_site').selectOption({ label: 'QCIF' });
    await submitInPlace(
      page,
      page.locator('input[type=submit][value="Approve Request"]'),
    );

    // Re-rendered at the same URL with the warning.
    await expect(page).toHaveURL(url);
    await expect(page).toHaveTitle(APPROVE_TITLE);
    const warning = page.locator('.alert.alert-warning');
    await expect(warning).toHaveText(
      `${WARNINGS_INTRO} ${APPROVER_PROBLEM} More information`,
      { useInnerText: true },
    );
    await expect(warning.locator('li')).toHaveCount(1);
    const info = warning.getByRole('link', { name: 'More information' });
    await expect(info).toHaveAttribute('href', `${WARNING_INFO_URL}#APPROVER_PROBLEM`);
    await expect(info).toHaveAttribute('target', '_blank');

    expect(
      await page
        .locator('form#new-allocation .form-actions input')
        .evaluateAll((els) =>
          els.map((e) => [(e as HTMLInputElement).type, (e as HTMLInputElement).value]),
        ),
    ).toEqual([
      ['submit', 'Approve Request'],
      ['button', 'Approve ignoring warnings'],
    ]);

    // Values kept.
    await expect(page.locator('#id_associated_site option:checked')).toHaveText('QCIF');
    await expect(page.locator('#id_bundle option:checked')).toHaveText('Standard');
    await expect(page.locator('#id_national')).not.toBeChecked();

    // Nothing saved yet.
    expect((await allocations.get(e.id)).status).toBe('E');
    expect(await allocations.history(e.id)).toEqual([]);

    await submitTo(
      page,
      page.locator('input[type=button][value="Approve ignoring warnings"]'),
      /\/allocation\/requests\/$/,
    );
    await expect(page.locator('h1')).toHaveText('Allocation Requests');
    await expect(page.locator('.messages .alert')).toHaveCount(0);
    expect((await allocations.get(e.id)).status).toBe('A');
    await gotoPending(page);
    await expect(pendingLink(page, e.id)).toHaveCount(0);
  });
});
