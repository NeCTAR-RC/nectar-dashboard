import { test, expect } from '../../../support/fixtures';
import { declineUi, expectGuarded400, TEST_TIMEOUT } from './helpers';

// Suite 05: the reject view refuses a GET for an already declined record.
test.describe('Decline guard', () => {
  test('5.5 Decline guard returns 400 for an already declined allocation', async ({
    page,
    allocations,
  }) => {
    test.setTimeout(TEST_TIMEOUT);
    const e = await allocations.create();
    await declineUi(page, e.id, 'PW decline guard');
    expect((await allocations.get(e.id)).status).toBe('R');

    await expectGuarded400(
      page,
      `/allocation/requests/reject_request/${e.id}/`,
      'Allocation already declined',
    );
    // The guard changes nothing.
    expect((await allocations.get(e.id)).status).toBe('R');
  });
});
