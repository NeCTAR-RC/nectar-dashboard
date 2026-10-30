import { test, expect } from '../../../support/fixtures';
import {
  APPROVER_PROBLEM,
  APPROVE_TITLE,
  A_BUTTONS,
  STANDARD_VALUES,
  WARNINGS_INTRO,
  ZERO_DELTAS,
  dateTime,
  detail,
  detailButtonTexts,
  expectApproveForm,
  gotoDetail,
  gotoPending,
  historyCells,
  myRequestsRow,
  newHistory,
  pendingLink,
  possibleDates,
  readHistory,
  stateRow,
  submitInPlace,
  submitTo,
  tableRows,
  TEST_TIMEOUT,
} from './helpers';

// Suite 05: approving a pending amendment (X to A).  The form is served at
// approve_change_request/ but posts to approve_request/.
test.describe('Approve changes', () => {
  test('5.13 Approve changes: X to A', async ({ page, allocations }) => {
    test.setTimeout(TEST_TIMEOUT);
    const x = await allocations.createAmendmentPending();
    const admin = x.contact_email as string;
    const before = await allocations.history(x.id);

    await gotoDetail(page, x.id);
    const link = detail(page).getByRole('link', { name: 'Approve changes' });
    await expect(link).toHaveAttribute(
      'href',
      `/allocation/requests/approve_change_request/${x.id}/`,
    );
    await link.click();
    await expect(page).toHaveURL(`/allocation/requests/approve_change_request/${x.id}/`);
    await expect(page).toHaveTitle(APPROVE_TITLE);
    const approveUrl = `/allocation/requests/approve_request/${x.id}/`;
    await expect(page.locator('form#new-allocation')).toHaveAttribute('action', approveUrl);
    // Same form as 5.7, with the site already set.
    await expectApproveForm(page, x, 'QCIF');

    await submitInPlace(page, page.locator('input[type=submit][value="Approve Request"]'));
    // The warning re-renders at the approve_request URL.
    await expect(page).toHaveURL(approveUrl);
    await expect(page.locator('.alert.alert-warning')).toHaveText(
      `${WARNINGS_INTRO} ${APPROVER_PROBLEM} More information`,
    );
    expect((await allocations.get(x.id)).status).toBe('X');
    await expect(page.locator('#id_associated_site option:checked')).toHaveText('QCIF');

    await page.waitForTimeout(2_000); // a clear gap after the fixture's amend
    await submitTo(
      page,
      page.locator('input[type=button][value="Approve ignoring warnings"]'),
      /\/allocation\/requests\/$/,
    );
    await gotoPending(page);
    await expect(pendingLink(page, x.id)).toHaveCount(0);

    const a = await allocations.get(x.id);
    expect(a.status).toBe('A');
    expect(a.approver_email).toBe(admin);

    await gotoDetail(page, x.id);
    await expect(stateRow(page)).toHaveText(/^\s*State\s+Approved\s*$/);
    expect((await tableRows(page, 0))[2]).toMatch(
      dateTime('Last updated ', possibleDates(a.modified_time as string)),
    );
    expect(await detailButtonTexts(page)).toEqual(A_BUTTONS);

    const row = await myRequestsRow(page, x.id);
    expect(row.cells[0]).toBe('A');
    expect(row.actions.map((r) => r.text)).toEqual(['Amend/Extend allocation']);

    // One new history record: the Update requested copy, with zero deltas.
    const added = newHistory(before, await allocations.history(x.id));
    expect(added.map((h) => h.status)).toEqual(['X']);
    const history = await readHistory(page, x.id);
    expect(history.rows[0].id).toBe(x.id);
    expect(historyCells(history.rows[0])).toEqual([
      x.project_description, admin, 'Standard', ...STANDARD_VALUES, 'Approved',
    ]);
    const copy = history.rows.find((r) => r.id === added[0].id);
    expect(copy && historyCells(copy)).toEqual([
      x.project_description, admin, 'Standard', ...ZERO_DELTAS, 'Update requested',
    ]);
    expect(history.rows).toHaveLength(before.length + 2);
  });
});
