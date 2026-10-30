import { test, expect } from '../../../support/fixtures';
import {
  A_BUTTONS,
  HISTORY_HEADERS,
  STANDARD_VALUES,
  adminNotes,
  approveUi,
  dateTime,
  detail,
  detailButtonTexts,
  detailButtons,
  gotoDetail,
  gotoUserDetail,
  headings,
  historyCells,
  myRequestsRow,
  newHistory,
  possibleDates,
  readHistory,
  submitTo,
  tableRows,
  TEST_TIMEOUT,
  instant,
} from './helpers';

const NOTE = 'PW regression note A1';

// Suite 05: the state, pages and history after an approval (E to A).
test.describe('Approve outcome', () => {
  test('5.10 State and actions after approval: E to A', async ({
    page,
    allocations,
  }) => {
    test.setTimeout(TEST_TIMEOUT);
    const created = await allocations.create();
    const admin = created.contact_email as string;

    // Admin notes first, so they can be seen to survive the approval.
    await page.goto(`/allocation/requests/edit_notes/${created.id}/`);
    await page.locator('#id_notes').fill(NOTE);
    await submitTo(
      page,
      page.locator('input[type=submit]'),
      new RegExp(`/allocation/requests/view/${created.id}/$`),
    );
    const e = await allocations.get(created.id);
    const before = await allocations.history(e.id);

    // Leave a gap so the approval's modified time is clearly later than
    // the submission's, whatever the backends' clock skew.
    await page.waitForTimeout(2_000);
    await approveUi(page, e.id);

    const a = await allocations.get(e.id);
    expect(a.status).toBe('A');
    expect(a.approver_email).toBe(admin);
    expect(a.associated_site).toBe('qcif');
    expect(a.status_explanation).toBe('');
    // The modified time did change, the submit date did not.
    expect(instant(a.modified_time)).toBeGreaterThan(instant(e.modified_time));
    expect(instant(a.submit_date)).toBe(instant(e.submit_date));

    await gotoDetail(page, e.id);
    expect(await tableRows(page, 1)).toEqual([
      'State Approved',
      `Approver ${admin}`,
      `Project Identifier ${e.project_name}`,
      'Project ID (Project not linked)',
      'Associated Site QCIF',
      'National funded no',
      'Provisioned no',
    ]);
    const left = await tableRows(page, 0);
    expect(left[1]).toMatch(dateTime('Submit date ', possibleDates(e.submit_date as string)));
    expect(left[2]).toMatch(
      dateTime('Last updated ', possibleDates(a.modified_time as string)),
    );
    const h3 = await headings(page, 'h3');
    expect(h3[0]).toBe('Current Resources');
    expect(h3).not.toContain('Requested Resources');
    expect(h3).not.toContain('Reviewer Comment');
    expect(h3.at(-1)).toBe('Allocation admin notes');
    await expect(adminNotes(page)).toHaveText(NOTE);
    expect(await detailButtonTexts(page)).toEqual(A_BUTTONS);

    // My Requests and the user detail page offer an amendment.
    const amendUrl = `/allocation/user_requests/edit_change_request/${e.id}/`;
    const row = await myRequestsRow(page, e.id);
    expect(row.stateTitle).toBe('Approved');
    expect(row.cells.slice(0, 5)).toEqual([
      'A',
      `${e.project_name} ${e.project_description}`,
      'QCIF',
      'False',
      admin,
    ]);
    expect(row.actions).toEqual([{ text: 'Amend/Extend allocation', href: amendUrl }]);

    await gotoUserDetail(page, e.id);
    expect(await detailButtons(page)).toEqual([
      { text: 'Request amendment', href: amendUrl },
    ]);
    await expect(detail(page).getByRole('link', { name: 'Edit request' })).toHaveCount(0);

    // One new history record: the Submitted copy, which keeps the notes.
    const added = newHistory(before, await allocations.history(e.id));
    expect(added.map((h) => [h.status, h.approver_email, h.notes])).toEqual([
      ['E', '', NOTE],
    ]);
    const history = await readHistory(page, e.id);
    expect(history.headers).toEqual(HISTORY_HEADERS);
    expect(history.rows.map((r) => r.id)).toEqual([e.id, added[0].id]);
    expect(history.rows.map(historyCells)).toEqual([
      [e.project_description, admin, 'Standard', ...STANDARD_VALUES, 'Approved'],
      [e.project_description, '', 'Standard', ...STANDARD_VALUES, 'Submitted'],
    ]);
    expect(history.rows.map((r) => r.href)).toEqual(
      history.rows.map((r) => `/allocation/requests/view/${r.id}/`),
    );
  });
});
