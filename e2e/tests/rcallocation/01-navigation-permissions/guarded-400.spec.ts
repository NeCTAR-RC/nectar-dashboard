import { test, expect } from '../../../support/fixtures';
import {
  SAVE_TIMEOUT,
  acceptDialogsOnce,
  decline,
  expectGuarded400,
} from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

const APPROVED = 'Allocation already approved';
const DECLINED = 'Allocation already declined';

test.describe('Navigation & permissions: guarded pages', () => {
  test('1.14 Guarded pages return 400 with plain-text message', async ({
    page,
    allocations,
  }) => {
    // Two declines, each of which can be slow under load.
    test.setTimeout(2 * SAVE_TIMEOUT + 120_000);
    const approved = await allocations.createApproved();
    const declined = await allocations.create();
    await decline(page, declined.id, 'Playwright 01 guarded pages');
    const amendDeclined = await allocations.createAmendmentPending();
    await decline(page, amendDeclined.id, 'Playwright 01 guarded pages');
    expect((await allocations.get(declined.id)).status).toBe('R');
    expect((await allocations.get(amendDeclined.id)).status).toBe('J');

    // Steps 1 and 2: approving an Approved allocation.
    await expectGuarded400(page,
      `/allocation/requests/approve_request/${approved.id}/`, APPROVED);
    await expectGuarded400(page,
      `/allocation/requests/approve_change_request/${approved.id}/`, APPROVED);

    // Step 3: declining a Declined (R) or Update declined (J) allocation,
    // fresh and long-standing (132752 is J, 63117 is an R history record).
    for (const id of [amendDeclined.id, declined.id, 132752, 63117]) {
      await expectGuarded400(page,
        `/allocation/requests/reject_request/${id}/`, DECLINED);
    }

    // Step 4: declining an Approved allocation is guarded too since the
    // allocation status fix (NECTAR-17320); before it the form opened.
    await expectGuarded400(page,
      `/allocation/requests/reject_request/${approved.id}/`,
      'Allocation is not awaiting approval');
  });
});
