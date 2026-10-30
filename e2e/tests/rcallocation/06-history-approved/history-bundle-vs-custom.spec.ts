import { Page } from '@playwright/test';

import {
  DATETIME_RE,
  RESOURCE_CORES,
  RESOURCE_VOLUME_GB,
  TableData,
  addQuota,
  declineFixture,
  djangoDates,
  expect,
  openHistory,
  parseDjangoDateTime,
  rowId,
  test,
} from './helpers';

// 6.5 History cell formats: bundle versus no bundle, blank approver.
//
// The plan recorded these rules on 152181/152182, which are about to be
// deleted.  These tests build fresh allocations with the fixtures instead
// and assert the same rules.  Fixture steps happen within one second and
// history copies keep the original modified_time, so the order of the
// non-current rows is not fixed: compare those rows as a set.

const DESC = 'Playwright e2e fixture';
const STANDARD = '4000 | 64 | 128 | 500 | -';
const ZEROS = '0 | 0 | 0 | 0 | 0';

// The first nine cells (everything but the time) of each row, sorted.
function rowsWithoutTime(t: TableData): string[] {
  return t.rows.map((r) => r.cells.slice(0, 9).join(' | ')).sort();
}

// Times are well formed, dated the day the fixture was made (in UTC, or in
// Australia/Melbourne if the page came back in that zone; see
// canonicalTimes) and newest first.
function checkTimes(t: TableData, modified: string) {
  const dates = djangoDates(new Date(modified).getTime());
  const times = t.rows.map((r) => r.cells[9]);
  for (const time of times) {
    expect(time).toMatch(DATETIME_RE);
    expect(dates).toContain(time.replace(/, [^,]+$/, ''));
  }
  const parsed = times.map(parseDjangoDateTime);
  for (let i = 1; i < parsed.length; i++) {
    expect(parsed[i]).toBeLessThanOrEqual(parsed[i - 1]);
  }
}

async function history(page: Page, id: number) {
  const t = await openHistory(page, `/allocation/requests/view/${id}/history`);
  // The current record is always listed and links to itself.
  expect(t.rows.map(rowId)).toContain(id);
  return t;
}

test.describe('6.5 History cell formats: bundle versus no bundle', () => {
  test('6.5 Standard bundle: A and E rows show the bundle quotas, E approver blank', async ({
    utcPage: page,
    allocations,
  }) => {
    const a = await allocations.createApproved();
    const approver = (await allocations.get(a.id)).approver_email as string;
    expect(approver).toMatch(/@/);

    const t = await history(page, a.id);
    expect(t.footer).toBe('Displaying 2 items');
    expect(rowId(t.rows[0])).toBe(a.id);
    expect(t.rows[0].cells.slice(0, 9).join(' | ')).toBe(
      `${DESC} | ${approver} | Standard | ${STANDARD} | Approved`,
    );
    // The history copy of the submitted request has no approver yet.
    expect(t.rows[1].cells.slice(0, 9).join(' | ')).toBe(
      `${DESC} |  | Standard | ${STANDARD} | Submitted`,
    );
    checkTimes(t, (await allocations.get(a.id)).modified_time as string);
  });

  test('6.5 Standard bundle: X and J rows show zero deltas in every quota column', async ({
    utcPage: page,
    allocations,
  }) => {
    const x = await allocations.createAmendmentPending();
    const approver = (await allocations.get(x.id)).approver_email as string;

    let t = await history(page, x.id);
    expect(t.footer).toBe('Displaying 3 items');
    expect(rowsWithoutTime(t)).toEqual(
      [
        `${DESC} | ${approver} | Standard | ${ZEROS} | Update requested`,
        `${DESC} | ${approver} | Standard | ${STANDARD} | Approved`,
        `${DESC} |  | Standard | ${STANDARD} | Submitted`,
      ].sort(),
    );
    checkTimes(t, (await allocations.get(x.id)).modified_time as string);

    await declineFixture(page, x.id, 'Playwright suite 06 fixture decline');
    const j = await allocations.get(x.id);
    expect(j.status).toBe('J');

    t = await history(page, x.id);
    expect(t.footer).toBe('Displaying 4 items');
    // The declined amendment is newest, so it is the first row.
    expect(rowId(t.rows[0])).toBe(x.id);
    expect(t.rows[0].cells.slice(0, 9).join(' | ')).toBe(
      `${DESC} | ${j.approver_email} | Standard | ${ZEROS} | Update declined`,
    );
    expect(rowsWithoutTime(t)).toEqual(
      [
        `${DESC} | ${j.approver_email} | Standard | ${ZEROS} | Update declined`,
        `${DESC} | ${approver} | Standard | ${ZEROS} | Update requested`,
        `${DESC} | ${approver} | Standard | ${STANDARD} | Approved`,
        `${DESC} |  | Standard | ${STANDARD} | Submitted`,
      ].sort(),
    );
    checkTimes(t, j.modified_time as string);
  });

  test('6.5 Standard bundle: a Declined (R) row shows the requested values', async ({
    utcPage: page,
    allocations,
  }) => {
    const e = await allocations.create();
    await declineFixture(page, e.id, 'Playwright suite 06 fixture decline');
    const r = await allocations.get(e.id);
    expect(r.status).toBe('R');

    const t = await history(page, e.id);
    expect(t.footer).toBe('Displaying 2 items');
    expect(rowId(t.rows[0])).toBe(e.id);
    expect(t.rows[0].cells.slice(0, 9).join(' | ')).toBe(
      `${DESC} | ${r.approver_email} | Standard | ${STANDARD} | Declined`,
    );
    expect(t.rows[1].cells.slice(0, 9).join(' | ')).toBe(
      `${DESC} |  | Standard | ${STANDARD} | Submitted`,
    );
    checkTimes(t, r.modified_time as string);
  });

  test('6.5 no bundle (custom quotas): Bundle is "-" and E shows requested values', async ({
    utcPage: page,
    allocations,
    rest,
  }) => {
    // Omitting the bundle gives a custom-quota request.
    const custom = await allocations.create({
      bundle: undefined,
      associated_site: 'qcif',
    });
    expect(custom.bundle ?? null).toBeNull();
    await addQuota(rest, custom.id, RESOURCE_CORES, 'nectar', 100);
    await addQuota(rest, custom.id, RESOURCE_VOLUME_GB, 'melbourne', 100);

    let t = await history(page, custom.id);
    expect(t.footer).toBe('Displaying 1 item');
    expect(t.rows[0].cells.slice(0, 9).join(' | ')).toBe(
      `${DESC} |  | - | - | 100 | - | - | 100 | Submitted`,
    );

    // Approval through the REST API leaves the approved quota at 0, so
    // the A row shows '-' while its Submitted copy keeps the request.
    await allocations.approve(custom.id);
    const a = await allocations.get(custom.id);
    t = await history(page, custom.id);
    expect(t.footer).toBe('Displaying 2 items');
    expect(rowsWithoutTime(t)).toEqual(
      [
        `${DESC} | ${a.approver_email} | - | - | - | - | - | - | Approved`,
        `${DESC} |  | - | - | 100 | - | - | 100 | Submitted`,
      ].sort(),
    );
    expect(rowId(t.rows[0])).toBe(custom.id);
    checkTimes(t, a.modified_time as string);
  });

  test('6.5 bundle plus custom quota shows the sum of both', async ({
    utcPage: page,
    allocations,
    rest,
  }) => {
    // [derived from code] get_quota_by_resource adds the custom quota to
    // the bundle quota.  Standard has 64 cores; add 8 more.
    const e = await allocations.create();
    await addQuota(rest, e.id, RESOURCE_CORES, 'nectar', 8);

    const t = await history(page, e.id);
    expect(t.rows[0].cells.slice(0, 9).join(' | ')).toBe(
      `${DESC} |  | Standard | 4000 | 72 | 128 | 500 | - | Submitted`,
    );
  });

  test('6.5 other statuses (Deleted) render "Requested <want>, currently have <have>"', async ({
    utcPage: page,
    allocations,
    rest,
  }) => {
    // [derived from code] statuses other than X, J, A, E and R fall
    // through to the long form.  A fresh fixture would be soft-deleted (D)
    // through the REST API to show it live.
    test.fixme(
      true,
      'Needs a D/N/M record: the delete action requires the global ' +
        'allocation admin role (CanDelete), which the test user lacks ' +
        '(403), and no live history sampled has such a row',
    );
    const e = await allocations.create();
    const r = await rest.post(`/rest_api/allocations/${e.id}/delete/`);
    expect(r.status(), await r.text()).toBe(200);
    expect((await allocations.get(e.id)).status).toBe('D');

    const t = await history(page, e.id);
    expect(t.footer).toBe('Displaying 2 items');
    expect(rowsWithoutTime(t)).toEqual(
      [
        `${DESC} |  | Standard | Requested 4000, currently have 4000 | Requested 64, currently have 64 | Requested 128, currently have 128 | Requested 500, currently have 500 | Requested 0, currently have 0 | Deleted`,
        `${DESC} |  | Standard | ${STANDARD} | Submitted`,
      ].sort(),
    );
  });
});
