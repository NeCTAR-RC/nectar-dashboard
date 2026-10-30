import {
  canonicalTimes,
  expect,
  openHistory,
  rowId,
  rowText,
  test,
} from './helpers';

// 6.3 History of A allocations: 98355, 145002, 130198.
//
// Each expected row is [id, status, modification time, quota cells or
// null when the plan did not record them].
type Expected = [number, string, string, string | null];

function check(rows: { cells: string[]; links: string[] }[], want: Expected[]) {
  expect(rows.map(rowId)).toEqual(want.map((w) => w[0]));
  want.forEach(([id, status, time, quotas], i) => {
    const cells = rows[i].cells;
    expect(cells[8], `row ${i + 1} (${id}) status`).toBe(status);
    expect(cells[9], `row ${i + 1} (${id}) time`).toBe(time);
    if (quotas !== null) {
      expect(cells.slice(3, 8).join(' | '), `row ${i + 1} (${id}) quotas`).toBe(
        quotas,
      );
    }
  });
}

const WANT_98355: Expected[] = [
  [98355, 'Approved', 'Sept. 4, 2024, 1:20 a.m.', '- | 16 | -1 | - | 500'],
  [151311, 'Update requested', 'Sept. 4, 2024, 1:15 a.m.', '0 | 0 | 0 | 0 | 0'],
  [151305, 'Approved', 'Oct. 3, 2023, 6:20 a.m.', null],
  [129763, 'Update requested', 'Oct. 3, 2023, 6:15 a.m.', null],
  [129706, 'Approved', 'Oct. 31, 2022, 5:50 a.m.', null],
  [113777, 'Update requested', 'Oct. 31, 2022, 5:45 a.m.', null],
  [113747, 'Approved', 'Nov. 26, 2021, 1:05 a.m.', null],
  // On the hour, Django's 'P' format drops the minutes.
  [98358, 'Submitted', 'Nov. 26, 2021, 1 a.m.', null],
];

const WANT_130198: Expected[] = [
  // 20 minutes past midnight is '12:20 a.m.', not '0:20'.
  [130198, 'Approved', 'Jan. 22, 2024, 12:20 a.m.', '6000 | 20 | - | 16000 | 10'],
  [134112, 'Update requested', 'Jan. 19, 2024, 12:54 a.m.', '0 | 0 | 0 | 0 | 0'],
  [134055, 'Approved', 'Nov. 15, 2023, 4:35 a.m.', '6000 | 20 | - | 16000 | 10'],
  [131731, 'Update requested', 'Nov. 15, 2023, 4:31 a.m.', '3000 | 12 | 0 | 0 | 10'],
  [131725, 'Approved', 'Oct. 16, 2023, 1:05 a.m.', '3000 | 8 | - | 16000 | -'],
  [130240, 'Submitted', 'Oct. 13, 2023, 5:15 a.m.', null],
];

test.describe('6.3 History of A allocations', () => {
  test('6.3 history of 98355', async ({ utcPage: page }) => {
    const t = canonicalTimes(
      await openHistory(page, '/allocation/requests/view/98355/history'),
      WANT_98355.map((w) => w[2]),
    );

    expect(t.footer).toBe('Displaying 8 items');
    expect(rowText(t.rows[0])).toBe(
      'Enhanced mission-critical synergy | brownlouis@carter.biz | - | - | 16 | -1 | - | 500 | Approved | Sept. 4, 2024, 1:20 a.m.',
    );
    expect(t.rows[0].links).toEqual(['/allocation/requests/view/98355/']);
    expect(rowText(t.rows[1])).toBe(
      'Sharable interactive flexibility | tbarton@moss.co.uk | - | 0 | 0 | 0 | 0 | 0 | Update requested | Sept. 4, 2024, 1:15 a.m.',
    );
    check(t.rows, WANT_98355);
    // A stored quota of -1 is shown as is, not as '-'.
    for (const row of t.rows.filter((r) => r.cells[8] === 'Approved')) {
      expect(row.cells[5], `RAM of ${rowId(row)}`).toBe('-1');
    }
  });

  test('6.3 history of 145002', async ({ utcPage: page }) => {
    const t = canonicalTimes(
      await openHistory(page, '/allocation/requests/view/145002/history'),
      ['April 10, 2024, 3:31 a.m.', 'April 10, 2024, 3:27 a.m.'],
    );

    expect(t.footer).toBe('Displaying 2 items');
    expect(t.rows.map((r) => [rowId(r), rowText(r)])).toEqual([
      [145002, 'Triple-buffered leadingedge moderator | whittakerlisa@french.biz | - | - | 2 | 8 | - | - | Approved | April 10, 2024, 3:31 a.m.'],
      [145005, 'Assimilated empowering alliance | wporter@ball.com | - | - | 2 | 8 | - | - | Submitted | April 10, 2024, 3:27 a.m.'],
    ]);
  });

  test('6.3 history of 130198', async ({ utcPage: page }) => {
    const t = canonicalTimes(
      await openHistory(page, '/allocation/requests/view/130198/history'),
      WANT_130198.map((w) => w[2]),
    );

    expect(t.footer).toBe('Displaying 6 items');
    expect(rowText(t.rows[0])).toBe(
      'Team-oriented content-based ability | hollandbeth@davidson-hill.net | - | 6000 | 20 | - | 16000 | 10 | Approved | Jan. 22, 2024, 12:20 a.m.',
    );
    check(t.rows, WANT_130198);
  });
});
