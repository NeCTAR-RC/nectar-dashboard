import { test, expect } from '../../../support/fixtures';
import {
  ADMIN_EMAIL,
  LIST_URL,
  TABLE,
  acceptDialogsOnce,
  clickAndWaitForURL,
  decline,
  columnHeaders,
  findRow,
  gotoList,
  possibleDates,
  readTable,
  row,
} from './helpers';

// Suite 03: the My Requests list (/allocation/user_requests/) as the
// allocation admin.  Every test creates its own allocations and asserts on
// those rows only: the list grows with every test run.

// The dev dashboard is shared with other suites running at the same time;
// form posts and page loads (the My Requests list above all) can take
// minutes under that load.
test.describe.configure({ timeout: 600_000 });

test.beforeEach(({ page }) => acceptDialogsOnce(page));

const ACTION_CLASS = 'btn data-table-action btn-default btn-associate';

test.describe('My Requests list', () => {
  test('1.1 My Requests page chrome and table layout', async ({
    page,
    allocations,
  }) => {
    const e = await allocations.create();

    await page.goto('/allocation/');
    await clickAndWaitForURL(
      page,
      page
        .locator('#sidebar-accordion-allocation')
        .getByRole('link', { name: 'My Requests' }),
      LIST_URL,
    );
    await expect(page).toHaveTitle('Allocation Requests - Nectar Dashboard');
    await expect(page.locator('h1')).toHaveText(['My Requests']);
    await expect(page.locator('.breadcrumb li')).toHaveText([
      'Allocations',
      'My Requests',
    ]);
    expect(await columnHeaders(page)).toEqual([
      'State',
      'Name',
      'Current Associated Site',
      'National',
      'Contact',
      'Last Updated',
      'Expiry Date',
      'Actions',
    ]);

    // The footer count matches the rows (the number itself grows with
    // every test run, so it is not pinned).
    const rows = await readTable(page);
    findRow(rows, e.id);
    await expect(page.locator(`${TABLE} tfoot .table_count`)).toHaveText(
      `Displaying ${rows.length} items`,
    );

    // No filter or search box.
    await expect(page.locator('input[type=search]')).toHaveCount(0);
    await expect(page.locator('input[name*=filter]')).toHaveCount(0);

    // One table action.
    const actions = page.locator('.table_actions a');
    await expect(actions).toHaveCount(1);
    await expect(actions).toHaveText('Request a new allocation');
    await expect(actions).toHaveAttribute('href', '/allocation/');
    await expect(actions).toHaveId('DataTableOptions__action_create');
    await expect(actions.locator('span.fa.fa-plus')).toHaveCount(1);
  });

  test('1.2 Approved row cell content', async ({ page, allocations }) => {
    const a = await allocations.createApproved();
    await gotoList(page);

    const tr = row(page, a.id);
    await expect(tr).toHaveAttribute('data-object-id', String(a.id));
    const cells = tr.locator('td');
    await expect(cells).toHaveCount(8);

    // State: a centred cell with the green 'ok' icon.
    await expect(cells.nth(0)).toHaveClass(/\btext-center\b/);
    const icon = cells.nth(0).locator('p');
    await expect(icon).toHaveAttribute('title', 'Approved');
    await expect(icon).toHaveClass('alloc-icon alloc-icon-ok');
    await expect(icon.locator('strong')).toHaveText('A');

    // Name: link, line break, muted description.
    const name = cells.nth(1);
    await expect(name.locator('a')).toHaveText(a.project_name);
    await expect(name.locator('a')).toHaveAttribute(
      'href',
      `/allocation/user_requests/view/${a.id}/`,
    );
    expect(
      await name.evaluate((td) =>
        [...td.children].map((c) => `${c.tagName}.${c.className}`),
      ),
    ).toEqual(['A.', 'BR.', 'SMALL.muted']);
    await expect(name.locator('small.muted')).toHaveText('Playwright e2e fixture');

    await expect(cells.nth(2)).toHaveText('QCIF');
    await expect(cells.nth(3)).toHaveText('False');
    await expect(cells.nth(4)).toHaveText(ADMIN_EMAIL);
    // Date only, no time.
    const updated = (await cells.nth(5).innerText()).trim();
    expect(possibleDates(a.modified_time as string)).toContain(updated);
    await expect(cells.nth(6)).toHaveText('-');

    const action = cells.nth(7).locator('a');
    await expect(action).toHaveCount(1);
    await expect(action).toHaveText('Amend/Extend allocation');
    await expect(action).toHaveId(`DataTableOptions__row_${a.id}__action_amend`);
    await expect(action).toHaveClass(ACTION_CLASS);
    await expect(action).toHaveAttribute(
      'href',
      `/allocation/user_requests/edit_change_request/${a.id}/`,
    );
  });

  test('1.3 Submitted rows cell content and ordering', async ({
    page,
    allocations,
  }) => {
    const e1 = await allocations.create();
    const e2 = await allocations.create({
      project_description: 'PW 03 second submitted',
    });
    const a = await allocations.createApproved();
    await gotoList(page);
    const rows = await readTable(page);

    // Rows sort by status code: the A row comes before the E rows.
    const states = rows.map((r) => r.cells[0]);
    expect(states).toEqual([...states].sort());
    const index = (id: number) => rows.findIndex((r) => r.id === String(id));
    expect(index(a.id)).toBeLessThan(index(e1.id));
    expect(index(a.id)).toBeLessThan(index(e2.id));

    for (const [alloc, description] of [
      [e1, 'Playwright e2e fixture'],
      [e2, 'PW 03 second submitted'],
    ] as const) {
      const r = findRow(rows, alloc.id);
      expect(r.stateTitle).toBe('Submitted');
      expect(r.stateClass).toBe('alloc-icon alloc-icon-wip');
      expect(r.name).toBe(alloc.project_name);
      expect(r.nameHref).toBe(`/allocation/user_requests/view/${alloc.id}/`);
      // Empty site and expiry render '-'; dates are Django 'N j, Y'.
      expect(r.cells.slice(0, 5)).toEqual([
        'E',
        `${alloc.project_name} ${description}`,
        '-',
        'False',
        ADMIN_EMAIL,
      ]);
      expect(possibleDates(alloc.modified_time as string)).toContain(r.cells[5]);
      expect(r.cells[5]).toMatch(/^(Jan\.|Feb\.|March|April|May|June|July|Aug\.|Sept\.|Oct\.|Nov\.|Dec\.) \d{1,2}, \d{4}$/);
      expect(r.cells[6]).toBe('-');
    }

    // alloc-icon-ok only on A rows.
    for (const r of rows) {
      if (r.cells[0] === 'A') {
        expect(r.stateClass, `row ${r.id}`).toBe('alloc-icon alloc-icon-ok');
      } else {
        expect(r.stateClass, `row ${r.id}`).toBe('alloc-icon alloc-icon-wip');
      }
    }
  });

  test('1.4 Row actions for A and E statuses', async ({ page, allocations }) => {
    const a = await allocations.createApproved();
    const e = await allocations.create();
    await gotoList(page);
    const rows = await readTable(page);

    expect(findRow(rows, a.id).actions).toEqual([
      {
        text: 'Amend/Extend allocation',
        href: `/allocation/user_requests/edit_change_request/${a.id}/`,
        id: `DataTableOptions__row_${a.id}__action_amend`,
        className: ACTION_CLASS,
      },
    ]);
    expect(findRow(rows, e.id).actions).toEqual([
      {
        text: 'Edit request',
        href: `/allocation/user_requests/edit_request/${e.id}/`,
        id: `DataTableOptions__row_${e.id}__action_user_edit`,
        className: ACTION_CLASS,
      },
    ]);

    // No dropdown menu and no 'View history' action anywhere in the table.
    const table = page.locator(TABLE);
    await expect(table.locator('.btn-group .dropdown-toggle')).toHaveCount(0);
    await expect(table.locator('.dropdown-menu')).toHaveCount(0);
    await expect(table.getByText('View history', { exact: false })).toHaveCount(0);
  });

  test('1.5 Row actions and state cells for R, X and J statuses', async ({
    page,
    allocations,
  }) => {
    // Derived from code in the plan; verified live here with fresh data.
    const r = await allocations.create();
    const x = await allocations.createAmendmentPending();
    const j = await allocations.createAmendmentPending();
    await decline(page, r.id, 'Playwright suite 03 R state');
    await decline(page, j.id, 'Playwright suite 03 J state');

    await gotoList(page);
    const rows = await readTable(page);
    const cases: [number, string, string, string, string, string][] = [
      [r.id, 'R', 'Declined', '-', 'user_edit', 'Edit request'],
      [x.id, 'X', 'Update requested', 'QCIF', 'user_edit_change', 'Edit amend/extend request'],
      [j.id, 'J', 'Update declined', 'QCIF', 'user_edit_change', 'Edit amend/extend request'],
    ];
    for (const [id, status, title, site, action, text] of cases) {
      const tr = findRow(rows, id);
      expect(tr.cells[0], `row ${id}`).toBe(status);
      expect(tr.stateTitle, `row ${id}`).toBe(title);
      expect(tr.stateClass, `row ${id}`).toBe('alloc-icon alloc-icon-wip');
      expect(tr.cells[2], `row ${id}`).toBe(site);
      const view = action === 'user_edit' ? 'edit_request' : 'edit_change_request';
      expect(tr.actions, `row ${id}`).toEqual([
        {
          text,
          href: `/allocation/user_requests/${view}/${id}/`,
          id: `DataTableOptions__row_${id}__action_${action}`,
          className: ACTION_CLASS,
        },
      ]);
    }
  });

  test('1.5 Row action for N status', async () => {
    test.fixme(
      true,
      'No status N allocation can be created: the REST API creates ' +
        'Submitted (E) requests.',
    );
    // Intended: N shows 'Edit request' (user_edit) like E and R, with
    // alloc-icon-wip and the title 'New'.
  });

  test('1.6 List scope for the allocation admin: top-level own allocations only', async ({
    page,
    allocations,
  }) => {
    // createAmendmentPending leaves history records (A and E) behind the
    // current X record.
    const x = await allocations.createAmendmentPending();
    const history = await allocations.history(x.id);
    expect(history.length).toBeGreaterThan(0);

    await gotoList(page);
    const rows = await readTable(page);
    const ids = rows.map((r) => r.id);
    expect(ids).toContain(String(x.id));
    for (const h of history) {
      expect(ids, `history record ${h.id}`).not.toContain(String(h.id));
    }

    // Ordered by status.
    const states = rows.map((r) => r.cells[0]);
    expect(states).toEqual([...states].sort());

    // The admin role does not widen My Requests: every row is the admin's
    // own (the admin manages no other projects).
    for (const r of rows) {
      expect(r.cells[4], `row ${r.id}`).toBe(ADMIN_EMAIL);
    }
  });

  test('1.7 Name link and table action navigation', async ({
    page,
    allocations,
  }) => {
    const a = await allocations.createApproved();
    await gotoList(page);

    await clickAndWaitForURL(
      page,
      row(page, a.id).getByRole('link', { name: a.project_name }),
      `/allocation/user_requests/view/${a.id}/`,
    );
    await expect(page).toHaveTitle('View allocation request - Nectar Dashboard');

    // Back to the list.  page.goBack() is aborted by the detail page's
    // in-flight requests on dev, so navigate instead.
    await gotoList(page);
    await clickAndWaitForURL(
      page,
      page.getByRole('link', { name: 'Request a new allocation' }),
      '/allocation/',
    );
    await expect(page).toHaveTitle('Allocation Request - Nectar Dashboard');
    await expect(page.locator('h3').first()).toHaveText(
      'New Allocation Request: About the Project',
    );

    // Leaving the form raises a beforeunload dialog, accepted by the
    // handler from acceptDialogsOnce.
    await clickAndWaitForURL(
      page,
      page.getByRole('link', { name: 'All My Requests' }),
      LIST_URL,
    );
    await expect(page.locator('h1')).toHaveText(['My Requests']);
  });
});
