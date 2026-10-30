import {
  DATETIME_RE,
  EXPECTED_135408,
  canonicalTimes,
  expect,
  openHistory,
  parseDjangoDateTime,
  rowId,
  rowText,
  test,
  timeOf,
} from './helpers';

// 6.2 History of an X allocation: delta and mixed-status cell rules.

test.describe('6.2 History of an X allocation (135408)', () => {
  test('6.2 rows, cell formats and ordering', async ({ utcPage: page }) => {
    const t = canonicalTimes(
      await openHistory(page, '/allocation/requests/view/135408/history'),
      EXPECTED_135408.map(([, text]) => timeOf(text)),
    );

    await test.step('all rows in rendered order', async () => {
      expect(t.rows.map((r) => [rowId(r), rowText(r)])).toEqual(
        EXPECTED_135408.map(([id, text]) => [id, text]),
      );
    });

    await test.step('cell formats by status', async () => {
      for (const row of t.rows) {
        const [, approver, , ...rest] = row.cells;
        const quotas = rest.slice(0, 5);
        const status = rest[5];
        const time = rest[6];
        // No units and no thousands separators.
        for (const q of quotas) {
          expect(q).not.toMatch(/,|\s/);
        }
        if (status === 'Update requested') {
          // Requested minus current, as a signed integer.
          for (const q of quotas) {
            expect(q).toMatch(/^-?\d+$/);
          }
        } else {
          expect(['Approved', 'Submitted']).toContain(status);
          // The value, or a single '-' when it is 0 or absent.
          for (const q of quotas) {
            expect(q).toMatch(/^(-|-?[1-9]\d*)$/);
          }
        }
        expect(approver).toMatch(/^(|\S+@\S+)$/);
        expect(time).toMatch(DATETIME_RE);
      }
      // A negative delta has a leading hyphen-minus.
      expect(t.rows[0].cells[3]).toBe('-13000');
    });

    await test.step('newest modification time first', async () => {
      const times = t.rows.map((r) => parseDjangoDateTime(r.cells[9]));
      for (let i = 1; i < times.length; i++) {
        expect(times[i], `row ${i + 1}`).toBeLessThanOrEqual(times[i - 1]);
      }
      // Rows 7 and 8 share a minute; observed order is 135543 then 135411.
      expect(rowId(t.rows[6])).toBe(135543);
      expect(rowId(t.rows[7])).toBe(135411);
    });
  });
});
