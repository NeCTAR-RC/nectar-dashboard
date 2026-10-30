import {
  HISTORY_HEADERS,
  canonicalTimes,
  expect,
  openHistory,
  rowId,
  rowText,
  test,
} from './helpers';

// 6.1 History table structure and header list.
test.describe('6.1 History table structure', () => {
  test('6.1 history of 135408: page, headers, footer, no actions or filter', async ({
    utcPage: page,
    allocations,
  }) => {
    const t = await openHistory(page, '/allocation/requests/view/135408/history');

    expect(t.title).toBe('Allocation Requests - Nectar Dashboard');
    expect(t.h1).toBe('History');
    expect(t.breadcrumb.map((b) => b.text)).toEqual([
      'Allocations',
      'Pending Requests',
      'History',
    ]);
    expect(t.tables).toBe(1);
    expect(t.headers).toEqual(HISTORY_HEADERS);
    expect(t.footer).toBe('Displaying 8 items');
    expect(t.rows).toHaveLength(8);
    expect(t.filterInputs).toBe(0);
    expect(t.actionCells).toBe(0);
    for (const row of t.rows) {
      expect(row.cells).toHaveLength(10);
      expect(row.links).toHaveLength(1);
    }

    // The first column links to the row's own record and shows that
    // record's project_description.
    expect(t.rows[0].links[0]).toBe('/allocation/requests/view/135408/');
    expect(t.rows[1].links[0]).toBe('/allocation/requests/view/146946/');
    expect(t.rows[0].cells[0]).toBe('Automated composite intranet');
    expect(t.rows[1].cells[0]).toBe('Assimilated responsive archive');
    for (const row of t.rows) {
      const id = rowId(row);
      expect(id).not.toBeNaN();
      const record = await allocations.get(id);
      expect(row.cells[0], `row ${id}`).toBe(record.project_description);
    }
  });

  test('6.1 history of a record with no children has one row, singular footer', async ({
    utcPage: page,
  }) => {
    const t = canonicalTimes(
      await openHistory(page, '/allocation/requests/view/146946/history'),
      ['March 15, 2024, 2:15 a.m.'],
    );

    expect(t.rows.map(rowText)).toEqual([
      'Assimilated responsive archive | gillirene@harding.net | - | 25000 | 120 | - | - | 1000 | Approved | March 15, 2024, 2:15 a.m.',
    ]);
    expect(t.footer).toBe('Displaying 1 item');
  });
});
