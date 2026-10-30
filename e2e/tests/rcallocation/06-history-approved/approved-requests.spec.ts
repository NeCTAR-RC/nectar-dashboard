import { APIRequestContext, BrowserContext, Page } from '@playwright/test';

import {
  Allocation,
  AllocationApi,
  uniqueProjectName,
} from '../../../support/allocations';
import {
  DATE_RE,
  declineFixture,
  djangoDates,
  expect,
  newRestApi,
  newUtcPage,
  openHistory,
  readTable,
  rowId,
  test,
} from './helpers';

// 6.6 to 6.9: the Approved Requests list.  The page renders every
// approved allocation (~1600 rows) and takes ~30 s, so it is loaded once
// and shared by the serial tests below.  Row counts are not asserted:
// other runs add and remove rows.
//
// The plan used pwtest-valid (152181) as its J and filter example; it is
// about to be deleted, so fresh A, X and J fixtures stand in for it.

const LIST = '/allocation/approved_requests/';

type ListRow = {
  id: number;
  state: string;
  stateTitle: string;
  stateClass: string;
  name: string;
  description: string;
  cells: string[];
  nameHtml: string;
  actions: { text: string; href: string }[];
};

async function readList(page: Page): Promise<ListRow[]> {
  return page.evaluate(() => {
    const text = (el: Element | null) =>
      (el?.textContent ?? '').replace(/\s+/g, ' ').trim();
    return [...document.querySelectorAll('table tbody tr')].map((tr) => {
      const tds = [...tr.querySelectorAll('td')];
      const link = tds[1]?.querySelector('a');
      const p = tds[0]?.querySelector('p');
      return {
        id: Number(link?.getAttribute('href')?.match(/(\d+)\/$/)?.[1]),
        state: text(p?.querySelector('strong') ?? null),
        stateTitle: p?.getAttribute('title') ?? '',
        stateClass: p?.getAttribute('class') ?? '',
        name: link?.textContent ?? '',
        description: text(tds[1]?.querySelector('small.muted') ?? null),
        cells: tds.map((td) => text(td)),
        nameHtml: tds[1]?.innerHTML.trim() ?? '',
        actions: [...(tds[8]?.querySelectorAll('a, button') ?? [])].map(
          (a) => ({ text: text(a), href: a.getAttribute('href') ?? '' }),
        ),
      };
    });
  });
}

// Rows the client-side filter leaves visible.
async function visibleRows(page: Page) {
  return page.evaluate(() =>
    [...document.querySelectorAll('table tbody tr')]
      .filter((tr) => (tr as HTMLElement).offsetParent !== null)
      .map((tr) => (tr.textContent ?? '').replace(/\s+/g, ' ').trim()),
  );
}

async function footer(page: Page) {
  return page.evaluate(() =>
    (document.querySelector('table tfoot')?.textContent ?? '')
      .replace(/\s+/g, ' ')
      .trim(),
  );
}

test.describe.serial('6.6-6.9 Approved Requests list', () => {
  let context: BrowserContext;
  let page: Page;
  let rest: APIRequestContext;
  let rows: ListRow[];
  let loadMs: number;
  // Fresh fixtures: A, X and J.  The J one has a description word that
  // appears nowhere else, for the description filter.
  let fixA: Allocation;
  let fixX: Allocation;
  let fixJ: Allocation;
  const descWord = `zq06${Math.random().toString(36).slice(2, 8)}`;

  test.beforeAll(async ({ browser }) => {
    test.setTimeout(540_000);
    ({ context, page } = await newUtcPage(browser));
    rest = await newRestApi();
    const allocations = new AllocationApi(rest);

    fixA = await allocations.createApproved({
      project_name: uniqueProjectName('h06a'),
    });
    fixX = await allocations.createAmendmentPending({
      project_name: uniqueProjectName('h06x'),
    });
    const j = await allocations.createAmendmentPending({
      project_name: uniqueProjectName('h06j'),
      project_description: `PW06 ${descWord} fixture`,
    });
    await declineFixture(page, j.id, 'Playwright suite 06 fixture decline');
    fixJ = await allocations.get(j.id);
    expect(fixJ.status).toBe('J');
    fixA = await allocations.get(fixA.id);
    fixX = await allocations.get(fixX.id);

    // ~30 s when the dev server is idle, but over 90 s was seen while
    // other suites were running against it (over 180 s at worst).
    const start = Date.now();
    await page.goto(LIST, { timeout: 300_000, waitUntil: 'domcontentloaded' });
    await page.waitForSelector('table tbody tr', { timeout: 60_000 });
    loadMs = Date.now() - start;
    rows = await readList(page);
  });

  test.afterAll(async () => {
    await rest?.dispose();
    await context?.close();
  });

  test('6.6 Approved Requests page structure and load', async () => {
    test.info().annotations.push({
      type: 'load time',
      description: `${loadMs} ms to the first table row`,
    });

    expect(new URL(page.url()).pathname).toBe(LIST);
    const t = await readTable(page);
    expect(t.title).toBe('Allocation Requests - Nectar Dashboard');
    expect(t.h1).toBe('Approved Requests');
    expect(t.breadcrumb.map((b) => b.text).slice(0, 2)).toEqual([
      'Allocations',
      'Approved Requests',
    ]);
    const sidebar = page.locator(`#sidebar-accordion a[href="${LIST}"]`);
    await expect(sidebar).toHaveCount(1);
    await expect(sidebar).toHaveText('Approved Requests');

    expect(t.headers).toEqual([
      'State',
      'Name',
      'Current Associated Site',
      'National',
      'Approver',
      'Contact',
      'Last Updated',
      'Expiry Date',
      'Actions',
    ]);
    // Every row is on one page: the footer counts them all and there is
    // no pagination.
    expect(rows.length).toBeGreaterThan(1000);
    expect(t.footer).toBe(`Displaying ${rows.length} items`);
    expect(
      await page.locator('.pagination, .page-link, a[href*="marker="]').count(),
    ).toBe(0);
    await expect(page.getByRole('link', { name: /^next/i })).toHaveCount(0);

    // State letters: only A, X and J, each shown with its display name.
    const titles: Record<string, string> = {
      A: 'Approved',
      X: 'Update requested',
      J: 'Update declined',
    };
    const counts: Record<string, number> = {};
    for (const row of rows) {
      counts[row.state] = (counts[row.state] ?? 0) + 1;
      expect(Object.keys(titles), `state of ${row.id}`).toContain(row.state);
      expect(row.stateTitle).toBe(titles[row.state]);
      expect(row.stateClass).toBe(
        row.state === 'A' ? 'alloc-icon alloc-icon-ok' : 'alloc-icon alloc-icon-wip',
      );
    }
    test.info().annotations.push({
      type: 'state counts',
      description: JSON.stringify(counts),
    });
    for (const s of ['A', 'X', 'J']) {
      expect(counts[s], `rows in state ${s}`).toBeGreaterThan(0);
    }

    const byId = new Map(rows.map((r) => [r.id, r]));
    expect(byId.get(fixA.id)?.state).toBe('A');
    expect(byId.get(fixX.id)?.state).toBe('X');
    expect(byId.get(fixJ.id)?.state).toBe('J');
    // Long-standing J rows recorded in the plan.
    const jText = rows.filter((r) => r.state === 'J').map((r) => r.cells[1]);
    expect(jText).toContain('cumCross-platform systemic synergy');
    expect(jText).toContain('placeatEnhanced mission-critical synergy');
  });

  test('6.7 Approved Requests row cell formats, links and actions', async () => {
    const first = rows[0];
    expect(first.id).toBe(98355);
    expect(first.cells[0]).toBe('A');
    expect(first.stateTitle).toBe('Approved');
    expect(first.nameHtml).toBe(
      '<a href="/allocation/requests/view/98355/">a</a><br><small class="muted">Enhanced mission-critical synergy</small>',
    );
    expect(first.cells.slice(1)).toEqual([
      'aEnhanced mission-critical synergy',
      'University of Melbourne',
      'False',
      'brownlouis@carter.biz',
      'conwaystewart@example.net',
      'Sept. 4, 2024',
      'Sept. 4, 2025',
      'View history',
    ]);
    // Only a View history link: no Edit request action, no dropdown.
    expect(first.actions).toEqual([
      { text: 'View history', href: '/allocation/requests/view/98355/history' },
    ]);

    const last = rows[rows.length - 1];
    expect(last.id).toBe(147375);
    expect(last.name).toBe('voluptatem');
    expect(last.description).toBe('Public-key leadingedge concept');
    expect(last.cells).toEqual([
      'A',
      'voluptatemPublic-key leadingedge concept',
      'QCIF',
      'True',
      'kieranbartlett@kay-stevens.info',
      'umarsh@example.com',
      'June 12, 2024',
      'June 12, 2025',
      'View history',
    ]);
    expect(last.actions).toEqual([
      { text: 'View history', href: '/allocation/requests/view/147375/history' },
    ]);

    // The J fixture stands in for the plan's pwtest-valid row.
    const j = rows.find((r) => r.id === fixJ.id)!;
    expect(j).toBeTruthy();
    expect(j.cells).toEqual([
      'J',
      `${fixJ.project_name}${fixJ.project_description}`,
      'QCIF',
      'False',
      fixJ.approver_email,
      fixJ.contact_email,
      j.cells[6],
      // An empty end_date shows '-'.
      '-',
      'View history',
    ]);
    // Last Updated is the date only ('N j, Y'), in UTC (or Melbourne if
    // the page came back in that zone; see canonicalTimes).
    expect(j.cells[6]).toMatch(DATE_RE);
    expect(djangoDates(new Date(fixJ.modified_time as string).getTime())).toContain(
      j.cells[6],
    );
    expect(j.name).toBe(fixJ.project_name);
    expect(j.description).toBe(`PW06 ${descWord} fixture`);
    expect(j.actions).toEqual([
      { text: 'View history', href: `/allocation/requests/view/${fixJ.id}/history` },
    ]);
    for (const row of rows) {
      expect(row.actions.map((a) => a.text), `actions of ${row.id}`).toEqual([
        'View history',
      ]);
    }

    // Follow the first row's links in a second tab, keeping the list.
    const tab = await context.newPage();
    try {
      const h = await openHistory(tab, first.actions[0].href);
      expect(new URL(tab.url()).pathname).toBe('/allocation/requests/view/98355/history');
      expect(h.breadcrumb.map((b) => b.text)).toEqual([
        'Allocations',
        'Pending Requests',
        'History',
      ]);
      expect(h.footer).toBe('Displaying 8 items');
      expect(h.rows.map(rowId)).toEqual([
        98355, 151311, 151305, 129763, 129706, 113777, 113747, 98358,
      ]);

      await tab.goto('/allocation/requests/view/98355/', { timeout: 30_000 });
      expect(new URL(tab.url()).pathname).toBe('/allocation/requests/view/98355/');
      await expect(tab.locator('h1')).toHaveText('View Allocation Request');
    } finally {
      await tab.close();
    }
  });

  test('6.8 Approved Requests ordering by project_name', async ({
    allocations,
  }) => {
    const names = rows.map((r) => r.name);
    expect(names.slice(0, 5)).toEqual(['a', 'a', 'a', 'a', 'a']);
    expect(rows.slice(0, 5).map((r) => r.id)).toEqual([
      98355, 145002, 130198, 131488, 58545,
    ]);
    expect(names.slice(-5)).toEqual(Array(5).fill('voluptatem'));
    expect(rows.slice(-5).map((r) => r.id)).toEqual([
      6472, 41837, 125569, 117929, 147375,
    ]);

    const binary = [...names].sort();
    const caseless = [...names].sort((p, q) =>
      p.toLowerCase() < q.toLowerCase() ? -1 : p.toLowerCase() > q.toLowerCase() ? 1 : 0,
    );
    expect(names.findIndex((n, i) => n !== binary[i])).toBe(-1);
    expect(names.findIndex((n, i) => n !== caseless[i])).toBe(-1);

    // Case sensitivity cannot be shown on this data: no name has an
    // upper-case letter and every name starts with a lower-case letter.
    expect(names.filter((n) => /[A-Z]/.test(n))).toEqual([]);
    expect(names.filter((n) => !/^[a-z]/.test(n))).toEqual([]);

    // Only top-level allocations are listed, each once; history records
    // (children) are not.
    const ids = rows.map((r) => r.id);
    expect(new Set(ids).size).toBe(ids.length);
    const children = [146946, 138447];
    for (const fix of [fixA, fixX, fixJ]) {
      children.push(...(await allocations.history(fix.id)).map((h) => h.id));
    }
    expect(children.length).toBeGreaterThan(2);
    expect(ids.filter((id) => children.includes(id))).toEqual([]);
  });

  test('6.9 Approved Requests NameFilter (client-side)', async () => {
    test.setTimeout(240_000);
    const filter = page.locator("input[name='DataTableOptions__filter__q']");
    await expect(filter).toHaveClass(/form-control/);
    await expect(filter).toHaveAttribute('placeholder', 'Filter');

    const requests: string[] = [];
    const onRequest = (r: { url: () => string; resourceType: () => string }) => {
      if (['document', 'xhr', 'fetch'].includes(r.resourceType())) {
        requests.push(r.url());
      }
    };
    page.on('request', onRequest);

    const typeFilter = async (value: string) => {
      await filter.fill('', { timeout: 10_000 });
      await filter.pressSequentially(value, { delay: 30, timeout: 60_000 });
    };
    const fixJText = `${fixJ.project_name}${fixJ.project_description}`;
    const expectOnly = async (row: string) => {
      await expect
        .poll(() => visibleRows(page), { timeout: 30_000 })
        .toEqual([expect.stringContaining(row)]);
      await expect.poll(() => footer(page)).toBe('Displaying 1 item');
    };

    await test.step("'pwtest' matches only the pwtest- rows", async () => {
      // The plan saw one row (pwtest-valid); other runs' fixtures are
      // also listed now, so assert the rule rather than the count.
      await typeFilter('pwtest');
      const expected = rows.filter((r) => r.cells[1].includes('pwtest')).length;
      await expect.poll(async () => (await visibleRows(page)).length).toBe(expected);
      for (const text of await visibleRows(page)) {
        expect(text).toContain('pwtest');
      }
      await expect
        .poll(() => footer(page))
        .toBe(`Displaying ${expected} item${expected === 1 ? '' : 's'}`);
    });

    await test.step('the full project name matches one row', async () => {
      await typeFilter(fixJ.project_name);
      await expectOnly(fixJText);
    });

    await test.step('the filter is case-insensitive', async () => {
      await typeFilter(fixJ.project_name.toUpperCase());
      await expectOnly(fixJText);
    });

    await test.step('the filter matches the description too', async () => {
      await typeFilter(descWord);
      await expectOnly(fixJText);
    });

    await test.step('no match shows "No items to display."', async () => {
      await typeFilter('zzzznomatch');
      await expect
        .poll(() => visibleRows(page), { timeout: 30_000 })
        .toEqual(['No items to display.']);
      expect(await footer(page)).toBe('');
    });

    await test.step('clearing the filter restores every row', async () => {
      await filter.press('Control+a');
      await filter.press('Backspace');
      await expect
        .poll(async () => (await visibleRows(page)).length, { timeout: 30_000 })
        .toBe(rows.length);
      await expect.poll(() => footer(page)).toBe(`Displaying ${rows.length} items`);
      const visible = await visibleRows(page);
      expect(visible[0]).toMatch(/^A ?aEnhanced mission-critical synergy/);
      expect((await readList(page)).map((r) => r.id)).toEqual(rows.map((r) => r.id));
    });

    page.off('request', onRequest);
    expect(requests).toEqual([]);
    expect(new URL(page.url()).pathname).toBe(LIST);
  });
});
