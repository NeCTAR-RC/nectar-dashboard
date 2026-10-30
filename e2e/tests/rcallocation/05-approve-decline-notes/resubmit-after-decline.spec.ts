import { test, expect } from '../../../support/fixtures';
import {
  E_BUTTONS,
  EDIT_TITLE,
  HISTORY_HEADERS,
  STANDARD_VALUES,
  createEditable,
  declineUi,
  detail,
  detailButtonTexts,
  gotoDetail,
  historyCells,
  myRequestsRow,
  newHistory,
  readHistory,
  stateRow,
  submitButton,
  submitTo,
  TEST_TIMEOUT,
} from './helpers';

const REASON = 'PW decline reason B1';

// Suite 05: the user resubmits a declined request (R to E).  A plain
// fixture has no chief investigator or grant and the edit form rejects
// it, so the request is created with both.
test.describe('Resubmit after decline', () => {
  test('5.6 Resubmit a declined request: R to E', async ({
    page,
    allocations,
  }) => {
    // Decline, then a slow user submit.
    test.setTimeout(TEST_TIMEOUT);
    const e = await createEditable(allocations);
    const admin = e.contact_email as string;
    await declineUi(page, e.id, REASON);
    const before = await allocations.history(e.id);
    expect(before.map((h) => h.status)).toEqual(['E']);

    const url = `/allocation/user_requests/edit_request/${e.id}/`;
    await page.goto(url);
    await expect(page).toHaveTitle(EDIT_TITLE);
    await expect(page.locator('input[name=ignore_warnings]')).toHaveValue('');

    // Unlike the plan's Custom-bundle record, the Standard-bundle fixture
    // raises no warnings: the first Submit saves and redirects.
    await submitTo(page, submitButton(page).first(), /\/allocation\/user_requests\/$/);
    await expect(page.locator('h1')).toHaveText('My Requests');

    const resubmitted = await allocations.get(e.id);
    expect(resubmitted.status).toBe('E');
    // The decline reason is kept.
    expect(resubmitted.status_explanation).toBe(REASON);

    // One new history record: the Declined copy.
    const after = await allocations.history(e.id);
    const added = newHistory(before, after);
    expect(added.map((h) => [h.status, h.status_explanation])).toEqual([
      ['R', REASON],
    ]);

    const row = await myRequestsRow(page, e.id);
    expect(row.cells[0]).toBe('E');
    expect(row.actions.map((a) => a.text)).toEqual(['Edit request']);

    // History: current E, the R copy, then the first E copy.  The two
    // Submitted rows keep the approver of the decline on the current one.
    const history = await readHistory(page, e.id);
    expect(history.headers).toEqual(HISTORY_HEADERS);
    expect(history.rows.map((r) => r.id)).toEqual([
      e.id,
      added[0].id,
      before[0].id,
    ]);
    expect(history.rows.map(historyCells)).toEqual([
      [e.project_description, admin, 'Standard', ...STANDARD_VALUES, 'Submitted'],
      [e.project_description, admin, 'Standard', ...STANDARD_VALUES, 'Declined'],
      [e.project_description, '', 'Standard', ...STANDARD_VALUES, 'Submitted'],
    ]);

    // Admin detail: Submitted again, with the approve/decline buttons and
    // the previous decline reason still shown.
    await gotoDetail(page, e.id);
    await expect(stateRow(page)).toHaveText(/^\s*State\s+Submitted\s*$/);
    expect(await detailButtonTexts(page)).toEqual(E_BUTTONS);
    await expect(detail(page).locator('h3', { hasText: 'Reviewer Comment' })).toHaveCount(1);
  });
});
