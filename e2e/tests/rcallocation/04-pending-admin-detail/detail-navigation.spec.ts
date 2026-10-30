import { test, expect } from '../../../support/fixtures';
import { BASE_URL } from '../../../support/env';
import { detail, gotoDetail, gotoPending, recordRequests } from './helpers';

// Suite 04: the admin detail page's back button and the read-only guard.

test.describe('Admin detail navigation', () => {
  let guard: ReturnType<typeof recordRequests>;

  test.beforeEach(async ({ page }) => {
    guard = recordRequests(page);
  });

  test.afterEach(async () => {
    guard.expectReadOnly();
  });

  test('4.20 Back button depends on the Referer', async ({ page }) => {
    const back = page.locator('.btn-back');

    // From the history page the button links to the viewed record's own
    // history, not the history it was reached from.
    await page.goto('/allocation/requests/view/135408/history');
    await Promise.all([
      page.waitForURL(/\/allocation\/requests\/view\/146946\/$/),
      page.locator('a[href="/allocation/requests/view/146946/"]').first().click(),
    ]);
    await expect(back).toHaveCount(1);
    await expect(back).toHaveText('Back to History');
    await expect(back).toHaveAttribute(
      'href',
      '/allocation/requests/view/146946/history',
    );
    // It sits above the record's h2.
    const backBox = (await back.boundingBox())!;
    const h2Box = (await detail(page).locator('h2').boundingBox())!;
    expect(backBox.y).toBeLessThan(h2Box.y);

    // The other cases set the Referer header rather than loading the
    // lists; the Approved Requests list takes about 30 s to render.
    const viaReferer = async (path: string) => {
      const response = await page.goto('/allocation/requests/view/137133/', {
        referer: `${BASE_URL}${path}`,
      });
      expect(response?.status()).toBe(200);
    };

    await viaReferer('/allocation/approved_requests/');
    await expect(back).toHaveText('Back to Approved Requests');
    await expect(back).toHaveAttribute('href', '/allocation/approved_requests/');

    await viaReferer('/allocation/user_requests/');
    await expect(back).toHaveText('Back to My Requests');
    await expect(back).toHaveAttribute('href', '/allocation/user_requests/');

    await viaReferer('/allocation/requests/');
    await expect(back).toHaveCount(0);

    // Direct navigation, no Referer.
    await gotoDetail(page, 137133);
    await expect(back).toHaveCount(0);

    // From the Pending list itself.
    await gotoPending(page);
    await Promise.all([
      page.waitForURL(/\/allocation\/requests\/view\/137133\/$/),
      page.locator('#datatableoptions a[href="/allocation/requests/view/137133/"]').click(),
    ]);
    await expect(detail(page).locator('h2')).toBeVisible();
    await expect(back).toHaveCount(0);
  });

  test('4.22 Missing id returns 404 and the suite issues only GETs', async ({
    page,
  }) => {
    const response = await page.goto('/allocation/requests/view/99999999/');
    expect(response?.status()).toBe(404);

    // Walk the suite's pages; the afterEach guard asserts that no
    // POST, PUT or DELETE reached the dashboard (apart from the page
    // chrome's time zone detection) and no navigation left it.
    await gotoPending(page);
    for (const id of [135408, 146946, 137133, 152179]) {
      await gotoDetail(page, id);
    }
    expect(guard.requests.length).toBeGreaterThan(0);
  });
});
