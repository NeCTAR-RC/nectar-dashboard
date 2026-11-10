import { test, expect } from '../../../support/fixtures';
import {
  PENDING_E,
  PENDING_X,
  gotoPending,
  pendingRow,
  readPendingRows,
  recordRequests,
} from './helpers';

// Suite 04: urgency.py rules (get_urgency) and the Urgency cell CSS
// classes (allocation/tables.py get_highlight_attribute), checked through
// the Pending list.  Fresh fixtures get controlled end dates; their
// modified_time is always today.

function isoDaysFromToday(days: number): string {
  const d = new Date(Date.now() + days * 86_400_000);
  return d.toISOString().slice(0, 10);
}

// The view orders amendments and approvals by modified_time, and the dev
// backends' clocks disagree by up to about a second.  Space the approval
// and the amendment out so the amendment is recorded after the approval.
const settle = () => new Promise((r) => setTimeout(r, 2_500));

test.describe('Urgency rules', () => {
  let guard: ReturnType<typeof recordRequests>;

  test.beforeEach(async ({ page }) => {
    guard = recordRequests(page);
  });

  test.afterEach(async () => {
    guard.expectReadOnly();
  });

  test('4.5 urgency.py mapping rules: live states', async ({
    page,
    allocations,
  }) => {
    // Wait time: modified today with no expiry gives New.
    const fresh = await allocations.create();
    // Expiry: an end date in the future is not expiring, so New.
    const future = await allocations.create({ end_date: isoDaysFromToday(30) });
    // Expiry: past end date with no approval to find a clock stop from
    // gives Unknown, which takes precedence over New.
    const unknown = await allocations.create({ end_date: isoDaysFromToday(-5) });

    // Past end date with an amendment after the approval: the clock stop
    // is the amendment (today), compared with the end date.
    const amended = async (endOffset: number) => {
      const approved = await allocations.createApproved({
        end_date: isoDaysFromToday(endOffset),
      });
      await settle();
      return allocations.amend(approved.id);
    };
    const expired = await amended(-5); // clock stop after end_date
    const stopped = await amended(-20); // after end_date + 14 days
    const archived = await amended(-40); // after end_date + 28 days

    await gotoPending(page);
    const urgency = async (id: number) =>
      (await pendingRow(page, id).locator('td').nth(8).textContent())!.trim();

    expect(await urgency(fresh.id)).toBe('(New)');
    expect(await urgency(future.id)).toBe('(New)');
    expect(await urgency(unknown.id)).toBe('(Unknown)');
    expect(await urgency(expired.id)).toBe('(Expired)');
    expect(await urgency(stopped.id)).toBe('(Stopped)');
    expect(await urgency(archived.id)).toBe('(Archived)');

    // Long-standing rows: E rows untouched for more than 21 days are
    // Overdue; X rows whose amendment is more than 150 days old are Danger.
    const rows = await readPendingRows(page);
    const byId = new Map(rows.map((r) => [r.id, r.cells[8]]));
    for (const id of PENDING_E) {
      expect(byId.get(id), `row ${id}`).toBe('(Overdue)');
    }
    for (const id of PENDING_X) {
      expect(byId.get(id), `row ${id}`).toBe('(Danger)');
    }

    // The test user is not an approver for any interested site (and the
    // ARDC fallback), so every value is parenthesised.
    for (const r of rows) {
      expect(r.cells[8], `row ${r.id}`).toMatch(/^\(.+\)$/);
    }
  });

  test('4.5 urgency.py mapping rules: Warning and Attention', async ({ page }) => {
    test.fixme(
      true,
      'Warning (modified 15-21 days ago) and Attention (8-14 days ago) need ' +
        'a backdated modified_time; fixtures are always modified today and ' +
        'no long-standing Pending row is in those ranges.  Danger is only ' +
        'covered by long-standing rows.',
    );
    // Intended assertions, given ids of rows modified 15-21 and 8-14
    // days ago with no expiry.
    const warningId = 0;
    const attentionId = 0;
    await gotoPending(page);
    await expect(pendingRow(page, warningId).locator('td').nth(8)).toHaveText(
      '(Warning)',
    );
    await expect(pendingRow(page, attentionId).locator('td').nth(8)).toHaveText(
      '(Attention)',
    );
  });

  test('4.6 Urgency cell CSS class: parenthesised cells have no class', async ({
    page,
    allocations,
  }) => {
    const e = await allocations.create();
    await gotoPending(page);

    // Values starting with '(' get no extra attributes: only the column's
    // own classes.  Horizon builds cell classes from a set, so their order
    // varies between server processes.
    const columnClasses = ['normal_column', 'sortable'];
    const cells = page.locator('#datatableoptions tbody td:nth-child(9)');
    const classes = await cells.evaluateAll((tds) =>
      tds.map((td) => td.className),
    );
    expect(classes.length).toBeGreaterThan(0);
    for (const c of classes) {
      expect(c.split(' ').sort()).toEqual(columnClasses);
    }
    const own = await pendingRow(page, e.id)
      .locator('td')
      .nth(8)
      .evaluate((td) => td.className);
    expect(own.split(' ').sort()).toEqual(columnClasses);
  });

  test('4.6 Urgency cell CSS class: unparenthesised mapping', async ({ page }) => {
    test.fixme(
      true,
      'Unparenthesised urgency needs a logged-in approver whose site ' +
        'matches a pending request; the test user is not an approver for ' +
        'any site.',
    );
    // Intended assertions, as an approver for the rows' sites:
    //   Danger -> pending_warn_level_4
    //   Stopped, Archived, Expired, Overdue, Unknown -> pending_warn_level_3
    //   Warning -> pending_warn_level_2
    //   Attention, New -> pending_warn_level_0
    //   pending_warn_level_1 is unreachable: Overdue matches the level_3
    //   branch first.  Existing behaviour; do not 'fix' in the refactor.
    const expected: Record<string, string> = {
      Danger: 'pending_warn_level_4',
      Stopped: 'pending_warn_level_3',
      Archived: 'pending_warn_level_3',
      Expired: 'pending_warn_level_3',
      Overdue: 'pending_warn_level_3',
      Unknown: 'pending_warn_level_3',
      Warning: 'pending_warn_level_2',
      Attention: 'pending_warn_level_0',
      New: 'pending_warn_level_0',
    };
    await gotoPending(page);
    const cells = page.locator('#datatableoptions tbody td:nth-child(9)');
    for (const cell of await cells.all()) {
      const text = (await cell.textContent())!.trim();
      if (text.startsWith('(')) {
        continue;
      }
      await expect(cell).toHaveClass(new RegExp(`\\b${expected[text]}\\b`));
    }
    await expect(page.locator('.pending_warn_level_1')).toHaveCount(0);
  });
});
