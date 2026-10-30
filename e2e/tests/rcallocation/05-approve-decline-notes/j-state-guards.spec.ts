import { test, expect } from '../../../support/fixtures';
import {
  APPROVE_TITLE,
  declineUi,
  expectGuarded400,
  open,
  TEST_TIMEOUT,
} from './helpers';

// Suite 05: the guards on an Update declined (J) record.
test.describe('J state guards', () => {
  test('5.15 Decline guard on a J record, and approve_change GET on J', async ({
    page,
    allocations,
  }) => {
    test.setTimeout(TEST_TIMEOUT);
    const x = await allocations.createAmendmentPending();
    await declineUi(page, x.id, 'PW J guard');
    expect((await allocations.get(x.id)).status).toBe('J');

    await expectGuarded400(
      page,
      `/allocation/requests/reject_request/${x.id}/`,
      'Allocation already declined',
    );

    // No guard for approving a J record: the GET serves the form.  Not
    // submitted.
    const response = await open(
      page,
      `/allocation/requests/approve_change_request/${x.id}/`,
    );
    expect(response.status()).toBe(200);
    await expect(page).toHaveTitle(APPROVE_TITLE);
    await expect(page.locator('form#new-allocation')).toHaveAttribute(
      'action',
      `/allocation/requests/approve_request/${x.id}/`,
    );
    await expect(
      page.locator('input[type=submit][value="Approve Request"]'),
    ).toBeVisible();
    expect((await allocations.get(x.id)).status).toBe('J');
  });
});
