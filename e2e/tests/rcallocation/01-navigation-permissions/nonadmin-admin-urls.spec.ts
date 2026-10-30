import { test } from '../../../support/fixtures';
import { acceptDialogsOnce, expectNotAuthorized } from './helpers';

test.beforeEach(({ userPage }) => acceptDialogsOnce(userPage));

// Verified live with the non-admin e2e user.
test.describe('Navigation & permissions: regular user and admin URLs', () => {
  test('1.20 Regular user is denied admin URLs', async ({
    userPage: page,
  }) => {
    // Every admin URL, the panel lists included, returns 403 with Horizon's
    // NotAuthorized page rather than the 'Forbidden' page of the user
    // views: the Horizon panel permission denies the request before the
    // view's test_func runs.  Since the access-check fix (75886a2) the
    // edit, approve and reject views also deny non-admins in the view
    // itself, which this does not reach.
    const submitted = 137133;
    const amendment = 135408;
    for (const url of [
      '/allocation/requests/',
      '/allocation/approved_requests/',
      `/allocation/requests/view/${submitted}/`,
      `/allocation/requests/view/${submitted}/history`,
      `/allocation/requests/edit_request/${submitted}/`,
      `/allocation/requests/approve_request/${submitted}/`,
      `/allocation/requests/reject_request/${submitted}/`,
      `/allocation/requests/approve_change_request/${amendment}/`,
      `/allocation/requests/edit_notes/${submitted}/`,
    ]) {
      await expectNotAuthorized(page, url);
    }
  });
});
