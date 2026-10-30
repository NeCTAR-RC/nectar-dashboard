import { test, expect } from '../../../support/fixtures';
import { expectGuarded400, TEST_TIMEOUT } from './helpers';

// Suite 05: the approve view refuses a GET for an already approved record.
test.describe('Approve guard', () => {
  test('5.11 Approve guard returns 400 for an already approved allocation', async ({
    page,
    allocations,
  }) => {
    test.setTimeout(TEST_TIMEOUT);
    const a = await allocations.createApproved();
    expect(a.status).toBe('A');

    await expectGuarded400(
      page,
      `/allocation/requests/approve_request/${a.id}/`,
      'Allocation already approved',
    );
    // approve_change_request is the same view, with the same guard.
    await expectGuarded400(
      page,
      `/allocation/requests/approve_change_request/${a.id}/`,
      'Allocation already approved',
    );
    expect((await allocations.get(a.id)).status).toBe('A');
  });
});
