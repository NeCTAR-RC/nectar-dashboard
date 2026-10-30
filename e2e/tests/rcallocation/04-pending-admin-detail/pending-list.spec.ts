import { test, expect } from '../../../support/fixtures';
import {
  PENDING_E,
  PENDING_ORDER,
  PENDING_URL,
  PENDING_X,
  gotoPending,
  pendingRow,
  pendingTable,
  possibleDates,
  readPendingRows,
  recordRequests,
} from './helpers';

// Suite 04: the Pending Requests list (/allocation/requests/).  Read-only
// apart from creating fresh pwtest- allocations through the REST API.
test.describe('Pending Requests list', () => {
  let guard: ReturnType<typeof recordRequests>;

  test.beforeEach(async ({ page }) => {
    guard = recordRequests(page);
  });

  test.afterEach(async () => {
    guard.expectReadOnly();
  });

  test('4.1 Pending list contains the long-standing rows and fresh pwtest requests', async ({
    page,
    allocations,
  }) => {
    const e = await allocations.create();
    const x = await allocations.createAmendmentPending();

    await gotoPending(page);
    await expect(page).toHaveURL(new RegExp(`${PENDING_URL}$`));
    await expect(page).toHaveTitle('Allocation Requests - Nectar Dashboard');

    const rows = await readPendingRows(page);
    const footer = pendingTable(page).locator('tfoot');
    await expect(footer).toHaveText(
      new RegExp(`Displaying ${rows.length} items`),
    );

    // Only Pending states are listed; the long-standing rows are E or X.
    const states = new Set(rows.map((r) => r.cells[0]));
    for (const s of ['A', 'J', 'R', 'D']) {
      expect(states.has(s)).toBe(false);
    }
    const byId = new Map(rows.map((r) => [r.id, r]));
    for (const id of PENDING_E) {
      expect(byId.get(id)?.cells[0], `row ${id}`).toBe('E');
    }
    for (const id of PENDING_X) {
      expect(byId.get(id)?.cells[0], `row ${id}`).toBe('X');
    }
    for (const r of rows.filter((r) => !r.name.startsWith('pwtest-'))) {
      expect(['E', 'X'], `row ${r.id}`).toContain(r.cells[0]);
    }

    // The fresh rows sort after every long-standing row (newest
    // submit_date), the E before the X created after it.
    const index = (id: number) => rows.findIndex((r) => r.id === id);
    const lastKnown = Math.max(...PENDING_ORDER.map(index));
    expect(index(e.id)).toBeGreaterThan(lastKnown);
    expect(index(x.id)).toBeGreaterThan(index(e.id));

    const today = possibleDates(e.modified_time as string);
    const eCells = byId.get(e.id)!.cells;
    expect(eCells.slice(0, 6)).toEqual([
      'E',
      `${e.project_name} Playwright e2e fixture`,
      '-',
      'False',
      '',
      e.contact_email,
    ]);
    expect(today).toContain(eCells[6]);
    expect(eCells.slice(7, 9)).toEqual(['-', '(New)']);

    // The amendment shows the approval's site and approver.
    const xCells = byId.get(x.id)!.cells;
    expect(xCells.slice(0, 6)).toEqual([
      'X',
      `${x.project_name} Playwright e2e fixture`,
      'QCIF',
      'False',
      x.approver_email,
      x.contact_email,
    ]);
    expect(possibleDates(x.modified_time as string)).toContain(xCells[6]);
    expect(xCells.slice(7, 9)).toEqual(['-', '(New)']);
  });

  test('4.2 Pending list is ordered by submit date', async ({ page }) => {
    await gotoPending(page);
    const rows = await readPendingRows(page);
    const known = rows
      .map((r) => r.id)
      .filter((id) => PENDING_ORDER.includes(id));
    expect(known).toEqual(PENDING_ORDER);
    expect(known.slice(0, 4)).toEqual([137133, 137145, 145086, 144561]);
    expect(known.slice(4, 8)).toEqual([145986, 135408, 58677, 147462]);
    expect(known.slice(-2)).toEqual([152145, 129250]);

    // E and X rows are interleaved, not grouped by state.
    const states = known.map((id) => rows.find((r) => r.id === id)!.cells[0]);
    expect(states.slice(4, 9)).toEqual(['E', 'X', 'X', 'E', 'X']);

    // Last Updated shows modified_time, so it is not strictly ordered:
    // 129250 (Sept. 30, 2024) follows 135339 (Sept. 23, 2024) but
    // 38655 (Aug. 26, 2024) follows 84989 (Aug. 23, 2024) while its
    // expiry is earlier.  Check the first four dates as recorded.
    const updated = (id: number) => rows.find((r) => r.id === id)!.cells[6];
    expect([137133, 137145, 145086, 144561].map(updated)).toEqual([
      'March 1, 2024',
      'March 1, 2024',
      'April 10, 2024',
      'May 6, 2024',
    ]);
    expect(updated(152145)).toBe('Sept. 30, 2024');
    expect(updated(129250)).toBe('Sept. 30, 2024');
  });

  test('4.3 Pending list cell content for sample E and X rows', async ({
    page,
  }) => {
    await gotoPending(page);
    const rows = await readPendingRows(page);
    const cells = (id: number) => rows.find((r) => r.id === id)!.cells;

    expect(cells(137133)).toEqual([
      'E',
      'qui Assimilated composite help-desk',
      '-',
      'False',
      'graemejohnson@nicholls-akhtar.org',
      'rhysdawson@example.com',
      'March 1, 2024',
      '-',
      '(Overdue)',
      'Edit request View history',
    ]);
    expect(cells(135408)).toEqual([
      'X',
      'eum Automated composite intranet',
      'Intersect',
      'True',
      'martinstephen@brown.com',
      'xwoodward@example.net',
      'May 28, 2024',
      'June 15, 2024',
      '(Danger)',
      'Edit request View history',
    ]);
    expect(cells(129250)).toEqual([
      'X',
      'labore Universal asynchronous strategy',
      'TPAC',
      'False',
      'keith28@kaur-adams.com',
      'collinslawrence@example.net',
      'Sept. 30, 2024',
      'Sept. 26, 2024',
      '(Danger)',
      'Edit request View history',
    ]);
    // Django short date format with abbreviated months.
    expect(cells(150183)[6]).toBe('Aug. 11, 2024');

    const headers = pendingTable(page).locator('thead tr').last().locator('th');
    await expect(headers).toHaveText([
      'State',
      'Name',
      'Current Associated Site',
      'National',
      'Previous Approver',
      'Contact',
      'Last Updated',
      'Expiry Date',
      'Urgency',
      'Actions',
    ]);
    await expect(headers.first()).toHaveClass(/\btext-center\b/);
    await expect(headers.last()).toHaveClass(/\bactions_column\b/);
    await expect(headers.last()).toHaveClass(/\bsorter-false\b/);
    for (let i = 0; i < 9; i++) {
      await expect(headers.nth(i)).toHaveClass(/\bsortable normal_column\b/);
    }
  });

  test('4.4 Urgency values on the Pending list and client-side sort', async ({
    page,
  }) => {
    await gotoPending(page);
    const rows = await readPendingRows(page);
    const byId = new Map(rows.map((r) => [r.id, r]));

    for (const id of PENDING_E) {
      expect(byId.get(id)!.cells[8], `row ${id}`).toBe('(Overdue)');
    }
    for (const id of PENDING_X) {
      expect(byId.get(id)!.cells[8], `row ${id}`).toBe('(Danger)');
    }
    // Every cell is parenthesised for this user, so none has a
    // pending_warn_level_N class.
    for (const r of rows) {
      expect(r.cells[8], `row ${r.id}`).toMatch(/^\(\w+\)$/);
    }
    const urgencyCells = pendingTable(page).locator('tbody td:nth-child(9)');
    expect(
      await urgencyCells.evaluateAll((tds) =>
        tds.filter((td) => /pending_warn_level/.test(td.className)).length,
      ),
    ).toBe(0);
    // The long-standing rows show only Overdue and Danger.
    const knownValues = new Set(
      rows.filter((r) => !r.name.startsWith('pwtest-')).map((r) => r.cells[8]),
    );
    expect([...knownValues].sort()).toEqual(['(Danger)', '(Overdue)']);

    const footerText = await pendingTable(page).locator('tfoot').innerText();
    const header = pendingTable(page).locator('thead th', { hasText: 'Urgency' });

    // Ascending: (Danger) sorts first, keeping DOM order among ties.
    await header.click();
    await expect(header).toHaveClass(/tablesorter-headerAsc/);
    let sorted = await readPendingRows(page);
    let values = sorted.map((r) => r.cells[8]);
    expect(values).toEqual([...values].sort());
    expect(
      sorted.filter((r) => r.cells[8] === '(Danger)').slice(0, 2).map((r) => r.id),
    ).toEqual([135408, 58677]);
    if (values[0] === '(Danger)') {
      expect(sorted.slice(0, 2).map((r) => r.id)).toEqual([135408, 58677]);
    }

    // Descending: (Overdue) sorts first.
    await header.click();
    await expect(header).toHaveClass(/tablesorter-headerDesc/);
    sorted = await readPendingRows(page);
    values = sorted.map((r) => r.cells[8]);
    expect(values).toEqual([...values].sort().reverse());
    expect(
      sorted.filter((r) => r.cells[8] === '(Overdue)').slice(0, 2).map((r) => r.id),
    ).toEqual([137133, 137145]);
    if (values[0] === '(Overdue)') {
      expect(sorted.slice(0, 2).map((r) => r.id)).toEqual([137133, 137145]);
    }

    // The sort is client-side.
    await expect(page).toHaveURL(new RegExp(`${PENDING_URL}$`));
    await expect(pendingTable(page).locator('tfoot')).toHaveText(footerText);
  });

  test('4.7 Pending row actions and Name links', async ({
    page,
    allocations,
  }) => {
    const e = await allocations.create();
    await gotoPending(page);

    for (const id of [137133, 135408, e.id]) {
      const row = pendingRow(page, id);
      await expect(row).toHaveCount(1);
      await expect(row.locator('td').nth(1).locator('a')).toHaveAttribute(
        'href',
        `/allocation/requests/view/${id}/`,
      );
      const links = row.locator('td').last().locator('a');
      await expect(links).toHaveCount(3);
      await expect(links.nth(0)).toHaveText('Edit request');
      await expect(links.nth(0)).toHaveAttribute(
        'href',
        `/allocation/requests/edit_request/${id}/`,
      );
      await expect(links.nth(1)).toHaveAttribute('href', '#');
      await expect(links.nth(1)).toHaveText('');
      await expect(links.nth(2)).toHaveText('View history');
      await expect(links.nth(2)).toHaveAttribute(
        'href',
        `/allocation/requests/view/${id}/history`,
      );
    }

    // Every row, X included, has Edit request then View history.
    const rows = await readPendingRows(page);
    for (const r of rows) {
      expect(r.cells[9], `row ${r.id}`).toBe('Edit request View history');
    }

    // The only table action is the filter.
    const tableActions = page.locator('.table_actions');
    await expect(tableActions.locator('input[name="DataTableOptions__filter__q"]')).toHaveCount(1);
    await expect(tableActions.locator('a, button')).toHaveCount(0);
    await expect(page.getByText('Request a new allocation')).toHaveCount(0);
  });

  test('4.8 Pending filter is client-side and matches any column', async ({
    page,
    allocations,
  }) => {
    const e = await allocations.create();
    const x = await allocations.createAmendmentPending();
    await gotoPending(page);

    const footer = pendingTable(page).locator('tfoot .table_count');
    const footerText = (await footer.innerText()).trim();
    const box = page.locator('input[name="DataTableOptions__filter__q"]');
    await expect(box).toHaveAttribute('placeholder', 'Filter');

    const visibleIds = async () =>
      (await readPendingRows(page)).filter((r) => r.visible);

    // locator.fill alone does not trigger the filter; type the term.
    const filter = async (term: string) => {
      await box.fill('');
      await box.press('Backspace');
      await box.pressSequentially(term, { delay: 30 });
    };

    // Live: the footer count follows the filter ('Displaying 1 item').
    const expectFooterCount = async () => {
      const n = (await visibleIds()).length;
      await expect(footer).toHaveText(
        `Displaying ${n} ${n === 1 ? 'item' : 'items'}`,
      );
    };

    // The fixture's project name matches only its own row.
    await filter(e.project_name);
    await expect
      .poll(async () => (await visibleIds()).map((r) => r.id))
      .toEqual([e.id]);
    await expect(footer).toHaveText('Displaying 1 item');

    // The Urgency text is searchable.
    await filter('(New)');
    await expect
      .poll(async () => (await visibleIds()).map((r) => r.id))
      .toEqual(expect.arrayContaining([e.id, x.id]));
    for (const r of await visibleIds()) {
      expect(r.cells[8]).toBe('(New)');
    }
    await expectFooterCount();

    await filter('(Danger)');
    await expect
      .poll(async () => (await visibleIds()).map((r) => r.id).sort())
      .toEqual([...PENDING_X].sort());
    for (const r of await visibleIds()) {
      expect(r.cells[0]).toBe('X');
    }
    await expect(footer).toHaveText(`Displaying ${PENDING_X.length} items`);

    await filter('Overdue');
    await expect
      .poll(async () => (await visibleIds()).map((r) => r.id).sort())
      .toEqual(expect.arrayContaining(PENDING_E));
    for (const r of await visibleIds()) {
      expect(r.cells[0]).toBe('E');
      expect(r.cells[8]).toBe('(Overdue)');
    }
    await expectFooterCount();

    // Matches the Site column.
    await filter('Intersect');
    await expect
      .poll(async () =>
        (await visibleIds())
          .filter((r) => !r.name.startsWith('pwtest-'))
          .map((r) => r.id)
          .sort(),
      )
      .toEqual([135339, 135408, 58677].sort());
    await expectFooterCount();

    await filter('TPAC');
    await expect
      .poll(async () => (await visibleIds()).map((r) => r.id))
      .toEqual([129250]);
    await expect(footer).toHaveText('Displaying 1 item');

    // No match: a single 'No items to display.' row and an empty count.
    await filter('zzzzno');
    await expect.poll(async () => (await visibleIds()).length).toBe(0);
    const empty = pendingTable(page).locator('tbody tr:visible');
    await expect(empty).toHaveCount(1);
    await expect(empty).toHaveText('No items to display.');
    await expect(empty).toHaveClass(/\bempty\b/);
    await expect(footer).toHaveText('');

    // The filter never leaves the page.
    await expect(page).toHaveURL(new RegExp(`${PENDING_URL}$`));

    // Clearing the filter shows every row and the full count again.
    await box.fill('');
    await box.press('Backspace');
    const all = (await readPendingRows(page)).length;
    await expect.poll(async () => (await visibleIds()).length).toBe(all);
    await expect(footer).toHaveText(footerText);
  });

  test('4.9 Pending list has no pagination', async ({ page }) => {
    await gotoPending(page);
    await expect(page.locator('.pagination')).toHaveCount(0);
    await expect(page.locator('a[rel=next], a[rel=prev]')).toHaveCount(0);
    await expect(
      pendingTable(page).getByRole('link', { name: /^(Next|Prev)/ }),
    ).toHaveCount(0);
    const rows = await readPendingRows(page);
    const footer = pendingTable(page).locator('tfoot');
    await expect(footer).toHaveText(new RegExp(`Displaying ${rows.length} items`));
    await expect(footer.locator('a')).toHaveCount(0);
  });
});
