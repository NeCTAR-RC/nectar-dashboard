import { test, expect } from '../../../support/fixtures';

// 6.10 approved_requests/edit_request GET for an A record.  Nothing is
// submitted.  Before the allocation status fix (NECTAR-17320) this was a
// 500 TypeError; the view now refuses the Approved record with a 400.
test.describe('6.10 approved_requests/edit_request for an A record', () => {
  test('6.10 GET edit_request/98355 returns 400', async ({ page }) => {
    const path = '/allocation/approved_requests/edit_request/98355/';
    const r = await page.request.get(path, { timeout: 20_000 });

    expect(r.status()).toBe(400);
    expect(await r.text()).toMatch(
      /^Allocation cannot be edited in its current state<!-- \S+ -->$/,
    );
  });
});
