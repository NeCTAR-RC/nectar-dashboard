import { test, expect } from '../../../support/fixtures';
import { declineUi, expectGuarded400, TEST_TIMEOUT } from './helpers';

// Suite 05: the decline status mapping (allocation/forms.py
// AllocationRejectForm): X goes to J, anything else to R.  E to R is
// checked in 5.4, X to J in 5.14, and the 400 guards in 5.5, 5.11 and 5.15.
test.describe('Decline status mapping', () => {
  test('5.18 Decline of a New (N) request goes to R', async ({
    page,
    allocations,
  }) => {
    test.setTimeout(TEST_TIMEOUT);
    test.fixme(
      true,
      'No way to create a status N (New) allocation: the REST API creates ' +
        'E, and the plan says not to create one in this suite.',
    );
    const n = await allocations.create({ status: 'N' });
    expect(n.status).toBe('N');
    await declineUi(page, n.id, 'PW decline N');
    expect((await allocations.get(n.id)).status).toBe('R');
    await expectGuarded400(
      page,
      `/allocation/requests/reject_request/${n.id}/`,
      'Allocation already declined',
    );
  });
});
