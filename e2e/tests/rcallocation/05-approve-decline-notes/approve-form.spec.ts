import { test, expect } from '../../../support/fixtures';
import {
  APPROVE_TITLE,
  ZONE_HEADINGS,
  detail,
  expectApproveForm,
  gotoDetail,
  TEST_TIMEOUT,
} from './helpers';

// Suite 05: the approve form.  Read-only apart from the fixture.
test.describe('Approve form', () => {
  test('5.7 Approve form structure', async ({ page, allocations }) => {
    test.setTimeout(TEST_TIMEOUT);
    const e = await allocations.create();
    const url = `/allocation/requests/approve_request/${e.id}/`;

    await gotoDetail(page, e.id);
    const link = detail(page).getByRole('link', { name: 'Review & Approve' });
    await expect(link).toHaveAttribute('href', url);
    await link.click();

    await expect(page).toHaveURL(url);
    await expect(page).toHaveTitle(APPROVE_TITLE);
    await expect(page.locator('h1')).toHaveText(['']);
    await expect(page.locator('h2').filter({ visible: true })).toHaveText(['Cloud Resources']);
    await expect(page.locator('h3').filter({ visible: true })).toHaveText([
      'Availability Zone Resources',
    ]);
    await expect(page.locator('h4').filter({ visible: true })).toHaveText([
      ...ZONE_HEADINGS,
      'Allocation Classification',
    ]);
    await expect(page.locator('fieldset legend')).toHaveText([
      'Volume Service',
      'Shared File System Service',
    ]);
    await expect(page.locator('.breadcrumb li')).toHaveText([
      'Allocations',
      'Pending Requests',
      'None',
    ]);

    const form = page.locator('form#new-allocation');
    await expect(form).toHaveAttribute('action', url);
    await expect(form).toHaveAttribute('method', 'post');
    await expectApproveForm(page, e, '---------');
  });
});
