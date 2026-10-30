import { test, expect } from '../../../support/fixtures';
import {
  DECLINE_TITLE,
  HISTORY_HEADERS,
  STANDARD_VALUES,
  afterHeading,
  detail,
  detailButtons,
  gotoPending,
  gotoUserDetail,
  historyCells,
  myRequestsRow,
  newHistory,
  pendingLink,
  possibleDates,
  readHistory,
  stateRow,
  submitTo,
  TEST_TIMEOUT,
} from './helpers';

const REASON = 'PW decline reason B1';

// Suite 05: declining a new request (E to R).
test.describe('Decline a new request', () => {
  test('5.4 Decline a new request: E to R', async ({ page, allocations }) => {
    test.setTimeout(TEST_TIMEOUT);
    const e = await allocations.create();
    const admin = e.contact_email as string;
    const before = await allocations.history(e.id);

    await page.goto(`/allocation/requests/reject_request/${e.id}/`);
    await expect(page).toHaveTitle(DECLINE_TITLE);
    await page.locator('#id_status_explanation').fill(REASON);
    await submitTo(
      page,
      page.locator('input[type=submit]'),
      /\/allocation\/requests\/$/,
    );

    // Pending Requests, with no flash message, and the request gone.
    await expect(page).toHaveTitle('Allocation Requests - Nectar Dashboard');
    await expect(page.locator('h1')).toHaveText('Allocation Requests');
    await expect(page.locator('.messages .alert')).toHaveCount(0);
    await gotoPending(page);
    await expect(pendingLink(page, e.id)).toHaveCount(0);

    const declined = await allocations.get(e.id);
    expect(declined.status).toBe('R');
    expect(declined.status_explanation).toBe(REASON);
    expect(declined.approver_email).toBe(admin);

    // One new history record: the Submitted copy.
    const added = newHistory(before, await allocations.history(e.id));
    expect(added.map((h) => [h.status, h.approver_email])).toEqual([['E', '']]);

    const history = await readHistory(page, e.id);
    expect(history.headers).toEqual(HISTORY_HEADERS);
    expect(history.rows.map((r) => r.id)).toEqual([e.id, added[0].id]);
    expect(history.rows.map(historyCells)).toEqual([
      [e.project_description, admin, 'Standard', ...STANDARD_VALUES, 'Declined'],
      [e.project_description, '', 'Standard', ...STANDARD_VALUES, 'Submitted'],
    ]);
    for (const r of history.rows) {
      expect(possibleDates(declined.modified_time as string)).toContain(
        r.cells[9].replace(/, [^,]+$/, ''),
      );
    }

    // My Requests: the user may edit and resubmit an R record.
    const row = await myRequestsRow(page, e.id);
    expect(row.stateTitle).toBe('Declined');
    expect(row.cells.slice(0, 7)).toEqual([
      'R',
      `${e.project_name} ${e.project_description}`,
      '-',
      'False',
      admin,
      expect.any(String),
      '-',
    ]);
    expect(possibleDates(declined.modified_time as string)).toContain(row.cells[5]);
    expect(row.actions).toEqual([
      {
        text: 'Edit request',
        href: `/allocation/user_requests/edit_request/${e.id}/`,
      },
    ]);

    // The user detail page shows the reason last.
    await gotoUserDetail(page, e.id);
    await expect(stateRow(page)).toHaveText(/^\s*State\s+Declined\s*$/);
    const h3 = await detail(page).locator('h3').allTextContents();
    const sections = h3.map((h) => h.replace(/\s+/g, ' ').trim());
    expect(sections.slice(0, 2)).toEqual([
      'Requested Resources',
      'Approved Resources (at the time of this record)',
    ]);
    expect(sections.at(-1)).toBe('Reviewer Comment');
    await expect(afterHeading(page, 'Reviewer Comment')).toHaveText(REASON);
    expect(await detailButtons(page)).toEqual([
      {
        text: 'Edit request',
        href: `/allocation/user_requests/edit_request/${e.id}/`,
      },
    ]);
  });
});
