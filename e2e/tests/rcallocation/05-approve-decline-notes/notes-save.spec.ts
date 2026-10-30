import { test, expect } from '../../../support/fixtures';
import {
  DETAIL_TITLE,
  E_BUTTONS,
  SUBMIT_TIMEOUT,
  adminNotes,
  dateTime,
  detail,
  detailButtonTexts,
  gotoDetail,
  gotoPending,
  pendingLink,
  possibleDates,
  readHistory,
  stateRow,
  submitTo,
  tableRows,
  TEST_TIMEOUT,
  instant,
} from './helpers';

const NOTE = 'PW regression note A1';

// Suite 05: saving admin notes changes neither the modified time nor the
// history.  The plan recorded this on 152181; here a fresh fixture.
test.describe('Admin notes save', () => {
  test('5.2 Save admin notes: redirect, display, no timestamp change, no history', async ({
    page,
    allocations,
  }) => {
    test.setTimeout(TEST_TIMEOUT);
    // associated_site lets the REST API approve it afterwards.
    const created = await allocations.create({ associated_site: 'qcif' });
    // The create response carries microseconds that the database does not
    // keep, so compare against the stored record.
    const e = await allocations.get(created.id);
    const dates = possibleDates(e.submit_date as string);

    await gotoDetail(page, e.id);
    await expect(adminNotes(page)).toHaveText('None');
    const left = await tableRows(page, 0);
    expect(left[1]).toMatch(dateTime('Submit date ', dates));
    expect(left[2]).toMatch(dateTime('Last updated ', dates));
    let history = await readHistory(page, e.id);
    expect(history.rows.map((r) => [r.id, r.cells[8]])).toEqual([
      [e.id, 'Submitted'],
    ]);

    await page.goto(`/allocation/requests/edit_notes/${e.id}/`);
    await page.locator('#id_notes').fill(NOTE);
    // A plain save: no notifications, so the default timeout would do,
    // but keep the shared submit helper.
    await submitTo(
      page,
      page.locator('input[type=submit]'),
      new RegExp(`/allocation/requests/view/${e.id}/$`),
    );

    // Back on the admin detail page, with no flash message.
    await expect(page).toHaveTitle(DETAIL_TITLE);
    await expect(page.locator('.alert, .messages .alert')).toHaveCount(0);
    await expect(adminNotes(page)).toHaveText(NOTE);
    await expect(
      detail(page).getByRole('link', { name: 'Add/edit admin notes' }),
    ).toBeVisible();
    await expect(stateRow(page)).toHaveText(/^\s*State\s+Submitted\s*$/);
    expect(await detailButtonTexts(page)).toEqual(E_BUTTONS);

    // save_without_updating_timestamps: neither date moves.
    // Compare dates only: the displayed time zone can change between page
    // loads; the stored values are compared exactly below.
    const after = await tableRows(page, 0);
    expect(after[1]).toMatch(dateTime('Submit date ', dates));
    expect(after[2]).toMatch(dateTime('Last updated ', dates));
    const saved = await allocations.get(e.id);
    expect(saved.notes).toBe(NOTE);
    expect(saved.status).toBe('E');
    // The REST API renders times in UTC or +11:00 from one call to the
    // next, so compare instants.
    expect(instant(saved.modified_time)).toBe(instant(e.modified_time));
    expect(instant(saved.submit_date)).toBe(instant(e.submit_date));

    // No history record.
    expect(await allocations.history(e.id)).toEqual([]);
    history = await readHistory(page, e.id);
    expect(history.rows.map((r) => [r.id, r.cells[8]])).toEqual([
      [e.id, 'Submitted'],
    ]);

    await gotoPending(page);
    await expect(pendingLink(page, e.id)).toHaveCount(1);

    // The notes survive a later transition (the plan checks this after
    // the UI approval in 5.10; approved here through the REST API).
    await allocations.approve(e.id);
    await gotoDetail(page, e.id);
    await expect(stateRow(page)).toHaveText(/State\s+Approved/, {
      timeout: SUBMIT_TIMEOUT,
    });
    await expect(adminNotes(page)).toHaveText(NOTE);
    const copies = await allocations.history(e.id);
    expect(copies.map((h) => [h.status, h.notes])).toEqual([['E', NOTE]]);
  });
});
