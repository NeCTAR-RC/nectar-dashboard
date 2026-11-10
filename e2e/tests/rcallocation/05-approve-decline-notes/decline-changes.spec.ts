import { test, expect } from '../../../support/fixtures';
import {
  A_BUTTONS,
  DECLINE_TITLE,
  X_BUTTONS,
  ZERO_DELTAS,
  afterHeading,
  dateTime,
  detail,
  detailButtonTexts,
  detailButtons,
  formControls,
  gotoDetail,
  gotoPending,
  gotoUserDetail,
  headings,
  historyCells,
  myRequestsRow,
  newHistory,
  pendingLink,
  possibleDates,
  readHistory,
  stateRow,
  submitTo,
  tableRows,
  TEST_TIMEOUT,
} from './helpers';

const REASON = 'PW decline changes reason G1';

// Suite 05: declining a pending amendment (X to J).  The plan reached X by
// amending again through the user form (covered by 5.12); here the X comes
// from the fixture.
test.describe('Decline changes', () => {
  test('5.14 Decline changes: X to J', async ({ page, allocations }) => {
    test.setTimeout(TEST_TIMEOUT);
    const x = await allocations.createAmendmentPending();
    const admin = x.contact_email as string;
    const before = await allocations.history(x.id);
    const url = `/allocation/requests/reject_request/${x.id}/`;

    await gotoDetail(page, x.id);
    expect(await detailButtonTexts(page)).toEqual(X_BUTTONS);
    const link = detail(page).getByRole('link', { name: 'Decline changes' });
    await expect(link).toHaveAttribute('href', url);
    await link.click();

    // The same form as 5.3.
    await expect(page).toHaveURL(url);
    await expect(page).toHaveTitle(DECLINE_TITLE);
    expect(
      (await formControls(page)).map((c) => [c.name, c.value, c.readOnly, c.label]),
    ).toEqual([
      ['csrfmiddlewaretoken', '<token>', false, ''],
      ['project_name', x.project_name, true, 'Project identifier'],
      ['project_description', x.project_description, true, 'Project allocation title'],
      ['status_explanation', '', false, 'Reason'],
      ['', 'Decline Request', false, ''],
    ]);

    await page.locator('#id_status_explanation').fill(REASON);
    await submitTo(page, page.locator('input[type=submit]'), /\/allocation\/requests\/$/);
    await gotoPending(page);
    await expect(pendingLink(page, x.id)).toHaveCount(0);

    const j = await allocations.get(x.id);
    expect(j.status).toBe('J');
    expect(j.status_explanation).toBe(REASON);
    expect(j.approver_email).toBe(admin);

    // Admin detail: the J record offers no change buttons.  Before the
    // allocation status fix (NECTAR-17320) it still offered both.
    await gotoDetail(page, x.id);
    await expect(stateRow(page)).toHaveText(/^\s*State\s+Update declined\s*$/);
    expect((await tableRows(page, 1))[1]).toBe(`Approver ${admin}`);
    expect((await tableRows(page, 0))[2]).toMatch(
      dateTime('Last updated ', possibleDates(j.modified_time as string)),
    );
    const h3 = await headings(page, 'h3');
    expect(h3.slice(0, 2)).toEqual(['Requested Resources', 'Current Resources']);
    expect(h3.slice(-2)).toEqual(['Reviewer Comment', 'Allocation admin notes']);
    await expect(afterHeading(page, 'Reviewer Comment')).toHaveText(REASON);
    expect(await detailButtonTexts(page)).toEqual(A_BUTTONS);

    // My Requests and the user detail page.
    const amendUrl = `/allocation/user_requests/edit_change_request/${x.id}/`;
    const row = await myRequestsRow(page, x.id);
    expect(row.stateTitle).toBe('Update declined');
    expect(row.cells[0]).toBe('J');
    expect(row.actions).toEqual([{ text: 'Edit amend/extend request', href: amendUrl }]);

    await gotoUserDetail(page, x.id);
    await expect(stateRow(page)).toHaveText(/^\s*State\s+Update declined\s*$/);
    await expect(afterHeading(page, 'Reviewer Comment')).toHaveText(REASON);
    expect(await detailButtons(page)).toEqual([
      { text: 'Edit change request', href: amendUrl },
    ]);

    // One new history record: the Update requested copy, zero deltas.
    const added = newHistory(before, await allocations.history(x.id));
    expect(added.map((h) => h.status)).toEqual(['X']);
    const history = await readHistory(page, x.id);
    expect(history.rows[0].id).toBe(x.id);
    expect(historyCells(history.rows[0])).toEqual([
      x.project_description, admin, 'Standard', ...ZERO_DELTAS, 'Update declined',
    ]);
    const copy = history.rows.find((r) => r.id === added[0].id);
    expect(copy && historyCells(copy)).toEqual([
      x.project_description, admin, 'Standard', ...ZERO_DELTAS, 'Update requested',
    ]);
  });
});
