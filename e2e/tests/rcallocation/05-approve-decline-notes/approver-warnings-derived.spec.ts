import { test, expect } from '../../../support/fixtures';
import {
  APPROVER_PROBLEM,
  NO_VALID_GRANTS,
  WARNINGS_INTRO,
  WARNING_INFO_URL,
  submitInPlace,
  TEST_TIMEOUT,
} from './helpers';

// Suite 05: approver warnings other than APPROVER_PROBLEM (checkers.py).
test.describe('Approver warnings', () => {
  test('5.17 NO_VALID_GRANTS on a National approval without grants', async ({
    page,
    allocations,
  }) => {
    test.setTimeout(TEST_TIMEOUT);
    // The fixture has no grants, ARDC support or NCRIS facilities.
    const e = await allocations.create();
    const url = `/allocation/requests/approve_request/${e.id}/`;
    await page.goto(url);
    await page.locator('#id_associated_site').selectOption({ label: 'QCIF' });
    await page.locator('#id_national').check();
    const approve = page.locator('input[type=submit][value="Approve Request"]');
    await submitInPlace(page, approve);

    await expect(page).toHaveURL(url);
    const warning = page.locator('.alert.alert-warning');
    await expect(warning).toHaveText(
      `${WARNINGS_INTRO} ${APPROVER_PROBLEM} More information ` +
        `${NO_VALID_GRANTS} More information`,
    );
    // Each warning links to the support article anchor named by its code.
    expect(
      await warning.locator('li a').evaluateAll((as) =>
        as.map((a) => [a.textContent, a.getAttribute('href'), a.getAttribute('target')]),
      ),
    ).toEqual([
      ['More information', `${WARNING_INFO_URL}#APPROVER_PROBLEM`, '_blank'],
      ['More information', `${WARNING_INFO_URL}#NO_VALID_GRANTS`, '_blank'],
    ]);
    await expect(
      page.locator('input[type=button][value="Approve ignoring warnings"]'),
    ).toBeVisible();
    await expect(page.locator('#id_national')).toBeChecked();

    // A Special approval reason clears NO_VALID_GRANTS.
    await page.locator('#id_special_approval').fill('PW special approval reason');
    await submitInPlace(page, approve);
    await expect(page).toHaveURL(url);
    await expect(warning).toHaveText(`${WARNINGS_INTRO} ${APPROVER_PROBLEM} More information`);
    await expect(page.locator('#id_special_approval')).toHaveValue(
      'PW special approval reason',
    );

    // Not approved: left Submitted.
    expect((await allocations.get(e.id)).status).toBe('E');
    expect(await allocations.history(e.id)).toEqual([]);
  });

  test('5.17 APPROVER_NOT_AUTHORIZED for another site\'s storage', async ({
    page,
    allocations,
  }) => {
    test.fixme(
      true,
      'Needs an approver registered for a site (Site.approvers).  The test ' +
        'user has no site, so approver_checks() returns APPROVER_PROBLEM ' +
        'before the per-zone authorisation check runs.',
    );
    const e = await allocations.create();
    const url = `/allocation/requests/approve_request/${e.id}/`;
    await page.goto(url);
    await page.locator('#id_associated_site').selectOption({ label: 'QCIF' });
    // Storage in a zone that does not belong to the approver's site.
    await page.locator('[name="quota-volume.gigabytes__tasmania"]').fill('10');
    await submitInPlace(
      page,
      page.locator('input[type=submit][value="Approve Request"]'),
    );
    const warning = page.locator('.alert.alert-warning');
    await expect(warning).toContainText(
      "Quota should be authorized by the other site before approving " +
        "'tasmania' storage quota",
    );
    await expect(warning.locator('a[href$="#APPROVER_NOT_AUTHORIZED"]')).toHaveCount(1);
    await expect(
      page.locator('input[type=button][value="Approve ignoring warnings"]'),
    ).toBeVisible();
  });
});
