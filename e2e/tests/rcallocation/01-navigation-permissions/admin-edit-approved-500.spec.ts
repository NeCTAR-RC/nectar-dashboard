import { test } from '../../../support/fixtures';
import { acceptDialogsOnce, expectGuarded400 } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: admin edit of approved records', () => {
  // Before the allocation status fix (NECTAR-17320) this returned a 500
  // TypeError, as the view had no form for an Approved record.  The
  // 'Edit request' row action is not offered for Approved rows.
  test('1.15 Admin edit_request on an Approved record returns 400', async ({
    page,
    allocations,
  }) => {
    const approved = await allocations.createApproved();

    // A fresh Approved allocation and an Approved history record of 135408.
    for (const id of [approved.id, 146946]) {
      await expectGuarded400(
        page,
        `/allocation/requests/edit_request/${id}/`,
        'Allocation cannot be edited in its current state',
      );
    }
  });
});
