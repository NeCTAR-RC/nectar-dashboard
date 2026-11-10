import { test, expect } from '../../../support/fixtures';
import { declineUi, expectGuarded400, TEST_TIMEOUT } from './helpers';

// Suite 05: the guards on an Update declined (J) record.
test.describe('J state guards', () => {
  test('5.15 Decline and approve guards on a J record', async ({
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

    // Approving a J record is guarded since the allocation status fix
    // (NECTAR-17320); before it the GET served the approve form.
    for (const view of ['approve_change_request', 'approve_request']) {
      await expectGuarded400(
        page,
        `/allocation/requests/${view}/${x.id}/`,
        'Allocation is not awaiting approval',
      );
    }
    expect((await allocations.get(x.id)).status).toBe('J');
  });
});
