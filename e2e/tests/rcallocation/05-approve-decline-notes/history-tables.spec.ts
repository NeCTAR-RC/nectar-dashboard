import { test, expect } from '../../../support/fixtures';
import {
  HISTORY_HEADERS,
  STANDARD_VALUES,
  ZERO_DELTAS,
  declineUi,
  historyCells,
  possibleDates,
  readHistory,
  TEST_TIMEOUT,
} from './helpers';

// Suite 05: the history table after a full lifecycle, E to A to X to A to
// X to J, the chain the plan walked 152181 through.  The fixture REST API
// makes the steps up to the second X; the final decline is through the UI.
// The 5.6 test checks the E to R to E table (the plan's 152182).
test.describe('History tables', () => {
  test('5.16 Final history table after a full lifecycle', async ({
    page,
    allocations,
  }) => {
    test.setTimeout(TEST_TIMEOUT);
    // The database keeps whole seconds and the backends' clocks differ by
    // up to a second, so space the steps for a stable newest-first order.
    const gap = () => page.waitForTimeout(2_000);
    const e = await allocations.create({ associated_site: 'qcif' });
    const admin = e.contact_email as string;
    await gap();
    await allocations.approve(e.id);
    await gap();
    await allocations.amend(e.id);
    await gap();
    await allocations.approve(e.id);
    await gap();
    await allocations.amend(e.id);
    await gap();
    await declineUi(page, e.id, 'PW decline changes reason G1');

    const final = await allocations.get(e.id);
    expect(final.status).toBe('J');
    const copies = await allocations.history(e.id);
    expect(copies.map((h) => h.status).sort()).toEqual(['A', 'A', 'E', 'X', 'X']);

    const history = await readHistory(page, e.id);
    // The page heading is a hidden h1, not the plan's h2.
    await expect(page.locator('h1')).toHaveText(['History']);
    await expect(page.locator('h1')).toBeHidden();
    expect(history.headers).toEqual(HISTORY_HEADERS);
    await expect(page.locator('#datatableoptions .table_count').first()).toHaveText(
      'Displaying 6 items',
    );

    // Newest first: the current record, then the copies.
    expect(history.rows[0].id).toBe(e.id);
    const byId = new Map(copies.map((h) => [h.id, h]));
    const statuses = history.rows.slice(1).map((r) => byId.get(r.id)?.status);
    expect(statuses).toEqual(['X', 'A', 'X', 'A', 'E']);

    const name = e.project_description;
    expect(history.rows.map(historyCells)).toEqual([
      [name, admin, 'Standard', ...ZERO_DELTAS, 'Update declined'],
      [name, admin, 'Standard', ...ZERO_DELTAS, 'Update requested'],
      [name, admin, 'Standard', ...STANDARD_VALUES, 'Approved'],
      [name, admin, 'Standard', ...ZERO_DELTAS, 'Update requested'],
      [name, admin, 'Standard', ...STANDARD_VALUES, 'Approved'],
      [name, '', 'Standard', ...STANDARD_VALUES, 'Submitted'],
    ]);
    expect(history.rows.map((r) => r.href)).toEqual(
      history.rows.map((r) => `/allocation/requests/view/${r.id}/`),
    );
    const dates = possibleDates(final.modified_time as string);
    for (const r of history.rows) {
      expect(dates).toContain(r.cells[9].replace(/, [^,]+$/, ''));
    }
  });
});
