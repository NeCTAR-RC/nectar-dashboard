import { test, expect } from '../../../support/fixtures';
import {
  gotoDetail,
  headings,
  possibleDates,
  recordRequests,
  resourcesTable,
  tableRows,
  detail,
} from './helpers';

// Suite 04: the admin detail page (/allocation/requests/view/<id>/) for
// records in different states.  Read-only.

const COMMON_H3 = [
  'Use Case',
  'Usage Patterns',
  'Additional Location Requirements',
  'Usage Types',
  'Usage Information',
  'Fields of Research (FOR)',
  'Supported Organisations',
  'Chief Investigator',
  'Research Grant Information',
  'Publication/Output and Impact',
];

const NEW_USAGE_H4 = [
  'Estimated number of users who will directly access the instances',
  'Estimated number of research services or platforms to be hosted using this allocation',
  'Estimated total number of unique active users of these services',
];

const PAST_YEAR_H4 = [
  'Number of users directly accessing instances over the past year',
  'Number of active research services or platforms hosted using this allocation',
  'Total number of unique active users of these services over the past year',
  'Are the above figures measured or estimated?',
];

const SUPPORT_H4 = [
  'ARDC (or ANDS, Nectar, or RDS) funded projects supporting this request:',
  'NCRIS Facilities supporting this request:',
];

// The displayed time depends on the session's detected time zone, so
// only the date is asserted; the time just has to be present.
const TIME = String.raw`(\d{1,2}(:\d{2})? [ap]\.m\.|noon|midnight)`;

function dateTime(label: string, dates: string[]): RegExp {
  const alt = dates.map((d) => d.replace(/\./g, '\\.')).join('|');
  return new RegExp(`^${label} (${alt}), ${TIME}$`);
}

test.describe('Admin detail records', () => {
  let guard: ReturnType<typeof recordRequests>;

  test.beforeEach(async ({ page }) => {
    guard = recordRequests(page);
  });

  test.afterEach(async () => {
    guard.expectReadOnly();
  });

  test('4.10 Admin detail for a submitted record (E)', async ({
    page,
    allocations,
  }) => {
    // A fresh Submitted fixture stands in for the plan's 152182.
    const e = await allocations.create();
    await gotoDetail(page, e.id);

    await expect(page.locator('h1')).toHaveText('View Allocation Request');
    await expect(detail(page).locator('h2')).toHaveText('Playwright e2e fixture');
    expect(await headings(page, 'h3')).toEqual([
      'Requested Resources',
      'Approved Resources (at the time of this record)',
      ...COMMON_H3,
      'Allocation admin notes',
    ]);
    // A new request cannot have publications.
    expect(await headings(page, 'h4')).toEqual([
      ...NEW_USAGE_H4,
      'Data Sensitivity Information',
      ...SUPPORT_H4,
    ]);

    const left = await tableRows(page, 0);
    const dates = possibleDates(e.submit_date as string);
    expect(left[0]).toBe(`Contact email ${e.contact_email}`);
    expect(left[1]).toMatch(dateTime('Submit date', dates));
    expect(left[2]).toMatch(dateTime('Last updated', dates));
    expect(left.slice(3)).toEqual([
      'Start date None',
      'End date None',
      'Estimated project duration 12 month(s)',
      'Convert trial? No',
    ]);

    // No Approver row before the first approval.
    expect(await tableRows(page, 1)).toEqual([
      'State Submitted',
      `Project Identifier ${e.project_name}`,
      'Project ID (Project not linked)',
      'Associated Site None',
      'National funded no',
      'Provisioned no',
    ]);
    await expect(detail(page).locator('table').nth(1).locator('tr').first())
      .toHaveClass(/\bdanger\b/);

    // The fixture uses the Standard bundle with no extra quotas.
    expect(await resourcesTable(page, 'Requested Resources')).toEqual([
      'Bundle Details Standard',
    ]);
    expect(
      await resourcesTable(page, 'Approved Resources (at the time of this record)'),
    ).toEqual(['No allocation.']);
    await expect(detail(page).locator('h5')).toHaveText(['Current Values:']);
  });

  test('4.11 Admin detail for update-requested record 135408 (X)', async ({
    page,
  }) => {
    await gotoDetail(page, 135408);
    await expect(page.locator('h1')).toHaveText('View Allocation Request');
    await expect(detail(page).locator('h2')).toHaveText('Automated composite intranet');
    expect(await headings(page, 'h3')).toEqual([
      'Requested Resources',
      'Current Resources',
      ...COMMON_H3,
      'Reviewer Comment',
      'Allocation admin notes',
    ]);
    await expect(
      detail(page)
        .locator('h3', { hasText: 'Reviewer Comment' })
        .locator('xpath=following-sibling::p[1]'),
    ).toHaveText('dolorem');
    expect(await headings(page, 'h4')).toEqual([
      'Estimated Number of Users',
      'Data Sensitivity Information',
      ...SUPPORT_H4,
      'Benefits of Nectar',
      'Research Impact',
    ]);

    const left = await tableRows(page, 0);
    expect(left[0]).toBe('Contact email xwoodward@example.net');
    expect(left[1]).toMatch(dateTime('Submit date', ['May 28, 2024']));
    expect(left[2]).toMatch(dateTime('Last updated', ['May 28, 2024']));
    expect(left.slice(3)).toEqual([
      'Start date March 15, 2024',
      'End date June 15, 2024',
      'Estimated project duration 3 month(s)',
      'Convert trial? No',
    ]);
    expect(await tableRows(page, 1)).toEqual([
      'State Update requested',
      'Approver martinstephen@brown.com',
      'Project Identifier eum',
      'Project ID 14813f18dc364a4c965aa7399a08614c',
      'Associated Site Intersect',
      'National funded yes',
      'Provisioned no',
    ]);

    // Boolean resources show 'Enabled'; others show quota and unit, with
    // the zone label after the resource name.
    expect(await resourcesTable(page, 'Requested Resources')).toEqual([
      'Bundle Details Custom',
      'Volume Service Storage Monash (VIC) 1000 GB',
      'Compute Service Limits Virtual Cores NeCTAR 200 VCPUs',
      'Compute Service Limits Instances NeCTAR 2 Servers',
      'Reservation Service Reservations NeCTAR 3 Reservations',
      'Reservation Service Duration NeCTAR 14 Days',
      'Reservation Service GPU Flavors NeCTAR Enabled',
      'Service Units Budget NeCTAR 12000 SUs',
      'Volume Service Storage QRIScloud 100 GB',
    ]);
    expect(await resourcesTable(page, 'Current Resources')).toEqual(
      APPROVED_135408,
    );
    await expect(
      detail(page).locator('h3', { hasText: 'Requested Resources' })
        .locator('xpath=following-sibling::table[1]')
        .locator('span.label.label-primary').first(),
    ).toHaveText('Monash (VIC)');

    // Requested Changes: an approval exists and this record is not active.
    // The sensitive-data fields match the approval, so one column only.
    await expect(detail(page).locator('h5')).toHaveText(['Requested Changes:']);
  });

  test('4.12 Admin detail for approved record 152179 (A)', async ({ page }) => {
    await gotoDetail(page, 152179);
    await expect(page.locator('h1')).toHaveText('View Allocation Request');
    await expect(detail(page).locator('h2')).toHaveText('fsdgfdsgdsfg');
    expect(await headings(page, 'h3')).toEqual([
      'Current Resources',
      ...COMMON_H3,
      'Allocation admin notes',
    ]);
    expect(await resourcesTable(page, 'Current Resources')).toEqual([
      'Bundle Details Powerful',
      'Object Store Storage NeCTAR 3000 GB',
      'Object Store Storage Pawsey (WA) 3000 GB',
    ]);
    expect(await tableRows(page, 1)).toEqual([
      'State Approved',
      'Approver sorrison@gmail.com',
      'Project Identifier gdfgdfgdf',
      'Project ID (Project not linked)',
      'Associated Site QCIF',
      'National funded yes',
      'Provisioned no',
    ]);
    await expect(detail(page).locator('table').nth(1).locator('tr').first())
      .toHaveClass(/\bsuccess\b/);

    const left = await tableRows(page, 0);
    expect(left[0]).toBe('Contact email sorrison@gmail.com');
    expect(left[1]).toMatch(dateTime('Submit date', ['April 30, 2026']));
    expect(left[2]).toMatch(dateTime('Last updated', ['April 30, 2026']));
    expect(left.slice(3)).toEqual([
      'Start date None',
      'End date None',
      'Estimated project duration 12 month(s)',
      'Convert trial? No',
    ]);

    // An approved record can have publications.
    expect(await headings(page, 'h4')).toEqual([
      ...NEW_USAGE_H4,
      ...PAST_YEAR_H4,
      'Data Sensitivity Information',
      ...SUPPORT_H4,
      'Benefits of Nectar',
      'Research Impact',
    ]);
    await expect(detail(page).locator('h5')).toHaveText(['Current Values:']);
  });

  test('4.18 Prior approval context: which approved record is shown', async ({
    page,
    allocations,
  }) => {
    const rightHeading = async () =>
      (await headings(page, 'h3')).filter((h) => /Resources/.test(h));

    // Active, not history: shows itself as Current Resources.
    await gotoDetail(page, 152179);
    expect(await rightHeading()).toEqual(['Current Resources']);

    // Active history record: shows itself, 'at the time of this record'.
    await gotoDetail(page, 146946);
    expect(await rightHeading()).toEqual([
      'Approved Resources (at the time of this record)',
    ]);

    // Not approved, no approved children: 'No allocation.'
    const e = await allocations.create();
    await gotoDetail(page, e.id);
    expect(await rightHeading()).toEqual([
      'Requested Resources',
      'Approved Resources (at the time of this record)',
    ]);
    expect(
      await resourcesTable(page, 'Approved Resources (at the time of this record)'),
    ).toEqual(['No allocation.']);

    // Not approved, with the newest approval earlier than itself:
    // Current Resources, using the approval's quota.
    await gotoDetail(page, 135408);
    expect(await rightHeading()).toEqual(['Requested Resources', 'Current Resources']);
    const current = await resourcesTable(page, 'Current Resources');
    expect(current).toContain('Compute Service Limits Virtual Cores NeCTAR 120 VCPUs');
    expect(current).toContain('Compute Service Limits Instances NeCTAR 10 Servers');
    expect(current).toContain('Service Units Budget NeCTAR 25000 SUs');

    // Not approved, with a newer approval than the one before it: an
    // older amendment in the history shows the approval of its time.
    //
    // The view picks the prior approval by modified_time, and the dev
    // dashboard's backends disagree on the clock by up to about a second,
    // so back-to-back steps can be recorded out of order.  Space each
    // state change out so the timestamps follow the real order.
    const settle = () => new Promise((r) => setTimeout(r, 2_500));
    const approved = await allocations.createApproved();
    await settle();
    const x = await allocations.amend(approved.id);
    await settle();
    await allocations.approve(x.id);
    await settle();
    await allocations.amend(x.id);
    const history = await allocations.history(x.id);
    const oldAmendments = history.filter((h) => h.status === 'X');
    expect(oldAmendments).toHaveLength(1);
    await gotoDetail(page, oldAmendments[0].id);
    expect(await rightHeading()).toEqual([
      'Requested Resources',
      'Approved Resources (at the time of this record)',
    ]);
    expect(
      await resourcesTable(page, 'Approved Resources (at the time of this record)'),
    ).toEqual(['Bundle Details Standard']);

    // The current amendment shows the newest approval as Current.
    await gotoDetail(page, x.id);
    expect(await rightHeading()).toEqual(['Requested Resources', 'Current Resources']);
  });

  test('4.19 History record 146946 differs from the current record', async ({
    page,
  }) => {
    await gotoDetail(page, 146946);
    await expect(detail(page).locator('h2')).toHaveText('Assimilated responsive archive');

    // The notes text stays, only the edit button goes.
    await expect(
      detail(page).locator('h3', { hasText: 'Allocation admin notes' })
        .locator('xpath=following-sibling::p[1]'),
    ).toHaveText('pending approval from UNSW, 20->120 vCPU');
    await expect(detail(page).getByText('Add/edit admin notes')).toHaveCount(0);

    const buttons = detail(page).locator('a.btn');
    await expect(buttons).toHaveText(['View History', 'Related tickets', 'Project usage']);
    await expect(buttons.nth(0)).toHaveAttribute(
      'href',
      '/allocation/requests/view/146946/history',
    );
    // Related tickets uses the parent's id (primary_id).
    expect(await buttons.nth(1).getAttribute('href')).toMatch(
      /&q\[\]=tags%3A%5B%22allocation-135408%22%5D$/,
    );
    expect(await buttons.nth(2).getAttribute('href')).toMatch(
      /&var-project_id=14813f18dc364a4c965aa7399a08614c$/,
    );

    expect(await headings(page, 'h3')).toEqual([
      'Approved Resources (at the time of this record)',
      ...COMMON_H3,
      'Reviewer Comment',
      'Allocation admin notes',
    ]);
    await expect(
      detail(page).locator('h3', { hasText: 'Reviewer Comment' })
        .locator('xpath=following-sibling::p[1]'),
    ).toHaveText('officiis');

    const left = await tableRows(page, 0);
    expect(left[0]).toBe('Contact email jamespauline@example.org');
    expect(left[1]).toMatch(dateTime('Submit date', ['Feb. 28, 2024']));
    expect(left[2]).toMatch(dateTime('Last updated', ['March 15, 2024']));
    expect(left.slice(3)).toEqual([
      'Start date March 15, 2024',
      'End date June 15, 2024',
      'Estimated project duration 3 month(s)',
      'Convert trial? No',
    ]);
    expect(await tableRows(page, 1)).toEqual([
      'State Approved',
      'Approver gillirene@harding.net',
      'Project Identifier dolore',
      'Project ID 14813f18dc364a4c965aa7399a08614c',
      'Associated Site Intersect',
      'National funded yes',
      'Provisioned yes',
    ]);
    await expect(detail(page).locator('table').nth(1).locator('tr').first())
      .toHaveClass(/\bsuccess\b/);

    // Equal to the Current Resources of 135408.
    expect(
      await resourcesTable(page, 'Approved Resources (at the time of this record)'),
    ).toEqual(APPROVED_135408);
    await expect(detail(page).locator('h5')).toHaveText(['Current Values:']);
  });
});

const APPROVED_135408 = [
  'Bundle Details Custom',
  'Volume Service Storage Monash (VIC) 1000 GB',
  'Compute Service Limits Virtual Cores NeCTAR 120 VCPUs',
  'Compute Service Limits Instances NeCTAR 10 Servers',
  'Reservation Service Reservations NeCTAR 3 Reservations',
  'Reservation Service Duration NeCTAR 14 Days',
  'Reservation Service GPU Flavors NeCTAR Enabled',
  'Service Units Budget NeCTAR 25000 SUs',
];
