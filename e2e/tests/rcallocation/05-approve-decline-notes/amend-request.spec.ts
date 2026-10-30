import { test, expect } from '../../../support/fixtures';
import {
  AMEND_TITLE,
  HISTORY_HEADERS,
  NAGS_TEXT,
  STANDARD_VALUES,
  X_BUTTONS,
  ZERO_DELTAS,
  closeNags,
  createAmendable,
  dateTime,
  detail,
  detailButtons,
  gotoDetail,
  gotoPending,
  headings,
  historyCells,
  myRequestsRow,
  newHistory,
  openAmendForm,
  pendingLink,
  possibleDates,
  readHistory,
  stateRow,
  submitButton,
  submitTo,
  tableRows,
  TEST_TIMEOUT,
} from './helpers';

// Suite 05: the user amends an approved allocation (A to X).  The admin
// is the fixture's contact, so the admin page acts as the user.  A plain
// fixture has no chief investigator or grant and the amend form rejects
// it, so the allocation is created with both.
test.describe('Amend an approved allocation', () => {
  test('5.12 Amend an approved allocation: A to X', async ({
    page,
    allocations,
  }) => {
    test.setTimeout(TEST_TIMEOUT);
    const a = await createAmendable(allocations);
    const admin = a.contact_email as string;
    const before = await allocations.history(a.id);
    expect(before.map((h) => h.status)).toEqual(['E']);
    const url = `/allocation/user_requests/edit_change_request/${a.id}/`;

    const modal = await openAmendForm(page, a.id);
    await expect(page).toHaveTitle(AMEND_TITLE);
    await expect(page.locator('h3').filter({ visible: true }).first()).toHaveText(
      'Edit Allocation Request: About the Project',
    );
    await expect(modal).toHaveText(NAGS_TEXT, { useInnerText: false });
    expect(
      await modal.locator('button').evaluateAll((bs) =>
        bs.map((b) => [
          b.textContent!.replace(/\s+/g, ' ').trim(),
          b.getAttribute('data-dismiss'),
        ]),
      ),
    ).toEqual([
      ['×', 'modal'],
      ['Close', 'modal'],
    ]);
    await expect(page.locator('form#new-allocation')).toHaveAttribute('action', url);

    await closeNags(page);
    await submitTo(page, submitButton(page).first(), /\/allocation\/user_requests\/$/);
    await expect(page.locator('h1')).toHaveText('My Requests');
    await expect(page.locator('.alert-warning, .alert-danger').filter({ visible: true }))
      .toHaveCount(0);

    const x = await allocations.get(a.id);
    expect(x.status).toBe('X');

    // My Requests row, then the user detail page reached from it.
    const row = await myRequestsRow(page, a.id);
    expect(row.stateTitle).toBe('Update requested');
    expect(row.cells[0]).toBe('X');
    expect(row.actions).toEqual([{ text: 'Edit amend/extend request', href: url }]);
    await page
      .locator(`#DataTableOptions__row__${a.id}`)
      .getByRole('link', { name: a.project_name })
      .click();
    await expect(page).toHaveURL(`/allocation/user_requests/view/${a.id}/`);
    expect(await detailButtons(page)).toEqual([
      { text: 'Edit change request', href: url },
    ]);
    // Shown above the detail block because the referrer is My Requests.
    await expect(page.locator('.dash_block > a.btn-back')).toHaveText(
      'Back to My Requests',
    );
    await expect(page.locator('.dash_block > a.btn-back')).toHaveAttribute(
      'href',
      '/allocation/user_requests/',
    );

    // Admin detail.
    await gotoDetail(page, a.id);
    await expect(stateRow(page)).toHaveText(/^\s*State\s+Update requested\s*$/);
    const left = await tableRows(page, 0);
    expect(left[2]).toMatch(
      dateTime('Last updated ', possibleDates(x.modified_time as string)),
    );
    expect((await headings(page, 'h3')).slice(0, 2)).toEqual([
      'Requested Resources',
      'Current Resources',
    ]);
    const buttons = await detailButtons(page);
    expect(buttons.map((b) => b.text)).toEqual(X_BUTTONS);
    expect(buttons.find((b) => b.text === 'Approve changes')!.href).toBe(
      `/allocation/requests/approve_change_request/${a.id}/`,
    );
    expect(buttons.find((b) => b.text === 'Decline changes')!.href).toBe(
      `/allocation/requests/reject_request/${a.id}/`,
    );
    await expect(detail(page).locator('h3', { hasText: 'Reviewer Comment' })).toHaveCount(0);

    await gotoPending(page);
    await expect(pendingLink(page, a.id)).toHaveCount(1);

    // One new history record: the Approved copy.
    const added = newHistory(before, await allocations.history(a.id));
    expect(added.map((h) => [h.status, h.approver_email])).toEqual([['A', admin]]);

    // The current X row shows the change against the approval (all zero),
    // the copies show their own values.  The fixture's E and A copies were
    // made within a second, so their relative order is not asserted.
    const history = await readHistory(page, a.id);
    expect(history.headers).toEqual(HISTORY_HEADERS);
    expect(history.rows[0].id).toBe(a.id);
    expect(historyCells(history.rows[0])).toEqual([
      a.project_description, admin, 'Standard', ...ZERO_DELTAS, 'Update requested',
    ]);
    expect(history.rows.slice(1).map((r) => r.id).sort()).toEqual(
      [added[0].id, before[0].id].sort(),
    );
    expect(history.rows.slice(1).map(historyCells).sort()).toEqual(
      [
        [a.project_description, admin, 'Standard', ...STANDARD_VALUES, 'Approved'],
        [a.project_description, '', 'Standard', ...STANDARD_VALUES, 'Submitted'],
      ].sort(),
    );
  });
});
