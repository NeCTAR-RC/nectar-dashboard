import {
  EXPECTED_135408,
  HISTORY_HEADERS,
  canonicalTimes,
  expect,
  openHistory,
  rowText,
  test,
  timeOf,
} from './helpers';

// 6.4 History of a history record (146946) and approved_requests history
// route parity.
const ROW_146946 =
  'Assimilated responsive archive | gillirene@harding.net | - | 25000 | 120 | - | - | 1000 | Approved | March 15, 2024, 2:15 a.m.';
const TIMES_146946 = [timeOf(ROW_146946)];
const TIMES_135408 = EXPECTED_135408.map(([, text]) => timeOf(text));

test.describe('6.4 History route parity', () => {
  test('6.4 detail pages of a history record link to the requests history route', async ({
    utcPage: page,
  }) => {
    for (const base of ['requests', 'approved_requests']) {
      await page.goto(`/allocation/${base}/view/146946/`, { timeout: 30_000 });
      await expect(page).toHaveTitle('View allocation request - Nectar Dashboard');
      await expect(page.locator('h1')).toHaveText('View Allocation Request');
      await expect(page.getByRole('link', { name: 'View History' })).toHaveAttribute(
        'href',
        '/allocation/requests/view/146946/history',
      );
    }
  });

  test('6.4 history of history record 146946 shows only itself', async ({
    utcPage: page,
  }) => {
    const t = canonicalTimes(
      await openHistory(page, '/allocation/requests/view/146946/history'),
      TIMES_146946,
    );

    expect(t.rows.map(rowText)).toEqual([ROW_146946]);
    expect(t.footer).toBe('Displaying 1 item');
    expect(t.rows[0].links).toEqual(['/allocation/requests/view/146946/']);
  });

  test('6.4 approved_requests history matches requests history', async ({
    utcPage: page,
  }) => {
    const pending = canonicalTimes(
      await openHistory(page, '/allocation/requests/view/135408/history'),
      TIMES_135408,
    );
    const approved = canonicalTimes(
      await openHistory(page, '/allocation/approved_requests/view/135408/history'),
      TIMES_135408,
    );

    expect(approved.title).toBe('Allocation Requests - Nectar Dashboard');
    expect(approved.h1).toBe('History');
    expect(approved.breadcrumb.map((b) => b.text)).toEqual([
      'Allocations',
      'Approved Requests',
      'History',
    ]);
    expect(approved.breadcrumb[1].href).toBe('/allocation/approved_requests/');
    expect(pending.breadcrumb[1].text).toBe('Pending Requests');
    expect(approved.breadcrumb[0]).toEqual(pending.breadcrumb[0]);
    expect(approved.breadcrumb[2]).toEqual(pending.breadcrumb[2]);

    expect(approved.headers).toEqual(HISTORY_HEADERS);
    expect(approved.footer).toBe('Displaying 8 items');
    expect(approved.rows).toEqual(pending.rows);
    expect(approved.rows.map(rowText)).toEqual(
      EXPECTED_135408.map(([, text]) => text),
    );
    for (const row of approved.rows) {
      expect(row.links[0]).toMatch(/^\/allocation\/requests\/view\/\d+\/$/);
    }

    const single = canonicalTimes(
      await openHistory(page, '/allocation/approved_requests/view/146946/history'),
      TIMES_146946,
    );
    expect(single.rows.map(rowText)).toEqual([ROW_146946]);
    expect(single.footer).toBe('Displaying 1 item');
  });

  test('6.4 history of a non-existent allocation is an empty 200 page', async ({
    utcPage: page,
  }) => {
    const t = await openHistory(page, '/allocation/requests/view/999999999/history');

    expect(t.h1).toBe('History');
    expect(t.breadcrumb.map((b) => b.text)).toEqual([
      'Allocations',
      'Pending Requests',
      'History',
    ]);
    expect(t.rows.map((r) => r.cells)).toEqual([['No items to display.']]);
    expect(t.footer).not.toMatch(/Displaying/);
  });
});
