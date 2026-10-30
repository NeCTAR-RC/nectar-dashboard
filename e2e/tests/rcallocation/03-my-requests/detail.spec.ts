import { test, expect } from '../../../support/fixtures';
import {
  ADMIN_EMAIL,
  acceptDialogsOnce,
  createAmendable,
  createEditable,
  datePart,
  decline,
  detail,
  detailButtons,
  detailTables,
  gotoDetail,
  possibleDates,
  section,
  texts,
} from './helpers';

// Suite 03: the user detail page (/allocation/user_requests/view/<id>/)
// as the allocation admin, who is the contact of the fresh allocations.

// The dev dashboard is shared with other suites running at the same time;
// form posts and page loads (the My Requests list above all) can take
// minutes under that load.
test.describe.configure({ timeout: 600_000 });

test.beforeEach(({ page }) => acceptDialogsOnce(page));

const ESTIMATE_H4 = [
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
const SENSITIVITY_ROWS = [
  'Contains sensitive data? No, the project does not involve sensitive data.',
  'Data classification Level Framework details Green',
  'Discussed the use of sensitive data on the Nectar Research Cloud with your institution? None',
];
const CI_ROWS = [
  'Name Dr Pw Tester',
  'Email pw@example.edu.au',
  'Primary Organisation Monash University',
  // Shown even when additional_researchers is empty.
  'Other primary investigators, partner investigators and other research collaborators',
];

async function expectChrome(page: import('@playwright/test').Page) {
  await expect(page.locator('.breadcrumb li')).toHaveText([
    'Allocations',
    'My Requests',
    'View Allocation Request',
  ]);
  await expect(page.locator('h1')).toHaveText(['View Allocation Request']);
  await expect(detail(page).locator('h2')).toHaveText(['Playwright e2e fixture']);
}

// No admin controls: notes, approve, decline, history or tickets.
async function expectNoAdminControls(page: import('@playwright/test').Page) {
  for (const name of [
    'Add/edit admin notes',
    'Review & Approve',
    'Decline with Reason',
    'Approve changes',
    'Decline changes',
    'View History',
    'Related tickets',
  ]) {
    await expect(page.getByRole('link', { name }), name).toHaveCount(0);
  }
  await expect(detail(page).locator('h3', { hasText: 'Allocation admin notes' }))
    .toHaveCount(0);
}

test.describe('My Requests user detail', () => {
  test('1.8 (2.1) User detail page for an Approved allocation', async ({
    page,
    allocations,
  }) => {
    const a = await createAmendable(allocations);
    await gotoDetail(page, a.id);
    await expectChrome(page);

    const tables = await detailTables(page);
    // Summary: dates only, the time of day depends on the time zone.
    const summary = tables[0];
    expect(summary[0]).toBe(`Contact email ${ADMIN_EMAIL}`);
    expect(possibleDates(a.submit_date as string)).toContain(
      datePart(summary[1].replace(/^Submit date /, '')),
    );
    expect(possibleDates(a.modified_time as string)).toContain(
      datePart(summary[2].replace(/^Last updated /, '')),
    );
    expect(summary.slice(3)).toEqual([
      'Start date None',
      'End date None',
      'Estimated project duration 12 month(s)',
      'Convert trial? No',
    ]);
    expect(tables[1]).toEqual([
      'State Approved',
      `Approver ${ADMIN_EMAIL}`,
      `Project Identifier ${a.project_name}`,
      'Project ID (Project not linked)',
      'Associated Site QCIF',
      'National funded no',
      'Provisioned no',
    ]);
    // A records show Current Resources only.
    expect(tables[2]).toEqual(['Bundle Details Standard']);
    expect(tables.slice(3)).toEqual([
      SENSITIVITY_ROWS,
      ['FOR 1 4601 Applied computing (100%)'],
      ['Organisations Monash University'],
      CI_ROWS,
    ]);

    expect(await texts(detail(page), 'h3')).toEqual([
      'Current Resources',
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
    ]);
    // The past-year figures appear for A records.
    expect(await texts(detail(page), 'h4')).toEqual([
      ...ESTIMATE_H4,
      ...PAST_YEAR_H4,
      'Data Sensitivity Information',
      ...SUPPORT_H4,
      'Benefits of Nectar',
      'Research Impact',
    ]);
    await expect(detail(page).locator('h5')).toHaveText(['Current Values:']);
    await expect(detail(page).locator('.data-classification-box')).toHaveText(
      'Data misuse would have little to no impact.',
    );

    expect(await section(page, 'Use Case')).toBe('Playwright end-to-end test fixture');
    expect(await section(page, 'Usage Patterns')).toBe('No Submission');
    expect(await section(page, 'Additional Location Requirements')).toBe('No Submission');
    expect(await section(page, 'Usage Types')).toBe('Hosting services to support research');
    expect(await section(page, 'Research Grant Information')).toBe(
      `No Submission ${SUPPORT_H4[0]} No Submission ${SUPPORT_H4[1]} No Submission`,
    );
    expect(await section(page, 'Publication/Output and Impact')).toBe(
      'No Submission Benefits of Nectar No Submission Research Impact No Submission',
    );
    // Usage figures: estimates 1, past year None, Measured.
    expect(
      await detail(page)
        .locator('h4 + p')
        .evaluateAll((ps) => ps.map((p) => p.textContent!.trim()).slice(0, 7)),
    ).toEqual(['1', '1', '1', 'None', 'None', 'None', 'Measured']);

    // Exactly one action: Request amendment.
    expect(await detailButtons(page)).toEqual([
      {
        text: 'Request amendment',
        href: `/allocation/user_requests/edit_change_request/${a.id}/`,
        id: 'allocation_edit_change_view',
        className: 'btn btn-default',
      },
    ]);
    await expectNoAdminControls(page);
    await expect(page.getByRole('link', { name: 'Edit request' })).toHaveCount(0);
  });

  test('1.9 (2.2) User detail page for a Submitted allocation', async ({
    page,
    allocations,
  }) => {
    const e = await createEditable(allocations, { grant: true });
    await gotoDetail(page, e.id);
    await expectChrome(page);

    const tables = await detailTables(page);
    expect(tables[0].slice(3)).toEqual([
      'Start date None',
      'End date None',
      'Estimated project duration 12 month(s)',
      'Convert trial? No',
    ]);
    // No Approver row before approval.
    expect(tables[1]).toEqual([
      'State Submitted',
      `Project Identifier ${e.project_name}`,
      'Project ID (Project not linked)',
      'Associated Site None',
      'National funded no',
      'Provisioned no',
    ]);
    expect(tables[2]).toEqual(['Bundle Details Standard']);
    expect(tables[3]).toEqual(['No allocation.']);

    expect(await texts(detail(page), 'h3')).toEqual([
      'Requested Resources',
      'Approved Resources (at the time of this record)',
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
    ]);
    // Only the three estimates; the past-year h4s are for A records.
    expect(await texts(detail(page), 'h4')).toEqual([
      ...ESTIMATE_H4,
      'Data Sensitivity Information',
      ...SUPPORT_H4,
    ]);
    expect(await section(page, 'Usage Types')).toBe('Hosting services to support research');
    expect(await section(page, 'Chief Investigator')).toBe(CI_ROWS.join(' '));
    expect(await section(page, 'Research Grant Information')).toMatch(
      /Grant Type Institutional research funding/,
    );
    expect(await section(page, 'Publication/Output and Impact')).toBe(
      'No Submission. (None expected for new requests.)',
    );

    expect(await detailButtons(page)).toEqual([
      {
        text: 'Edit request',
        href: `/allocation/user_requests/edit_request/${e.id}/`,
        id: 'allocation_edit_view',
        className: 'btn btn-default',
      },
    ]);
    await expectNoAdminControls(page);
    await expect(page.getByRole('link', { name: 'Request amendment' })).toHaveCount(0);
  });

  test('1.10 (2.3) Detail button by status: E, R, A, X and J', async ({
    page,
    allocations,
  }) => {
    // Derived from code in the plan for X and J; verified live here.
    const e = await allocations.create();
    const r = await allocations.create();
    const a = await allocations.createApproved();
    const x = await allocations.createAmendmentPending();
    const j = await allocations.createAmendmentPending();
    await decline(page, r.id, 'Playwright suite 03 R state');
    await decline(page, j.id, 'Playwright suite 03 J state');

    const edit = (id: number) => ({
      text: 'Edit request',
      href: `/allocation/user_requests/edit_request/${id}/`,
      id: 'allocation_edit_view',
      className: 'btn btn-default',
    });
    const change = (id: number, text: string) => ({
      text,
      href: `/allocation/user_requests/edit_change_request/${id}/`,
      id: 'allocation_edit_change_view',
      className: 'btn btn-default',
    });
    const cases: [number, string, object][] = [
      [e.id, 'Submitted', edit(e.id)],
      [r.id, 'Declined', edit(r.id)],
      [a.id, 'Approved', change(a.id, 'Request amendment')],
      [x.id, 'Update requested', change(x.id, 'Edit change request')],
      [j.id, 'Update declined', change(j.id, 'Edit change request')],
    ];
    for (const [id, state, button] of cases) {
      await gotoDetail(page, id);
      expect((await detailTables(page))[1][0], `${id}`).toBe(`State ${state}`);
      // Only one button ever renders.
      expect(await detailButtons(page), `${state} ${id}`).toEqual([button]);
      await expectNoAdminControls(page);
    }
    // Declined records show the reviewer comment.
    for (const [id, reason] of [
      [r.id, 'Playwright suite 03 R state'],
      [j.id, 'Playwright suite 03 J state'],
    ] as const) {
      await gotoDetail(page, id);
      expect(await section(page, 'Reviewer Comment')).toBe(reason);
    }
  });

  test('1.10 (2.3) External links on the detail page (hrefs only)', async ({
    page,
    allocations,
  }) => {
    const e = await allocations.create();
    await gotoDetail(page, e.id);
    const hrefs = await page
      .locator('a[href^="http"]')
      .evaluateAll((as) => as.map((a) => a.getAttribute('href')));
    for (const href of [
      'http://support.nectar.org.au/',
      'https://desktop.rc.nectar.org.au/',
      'https://jupyterhub.rc.nectar.org.au/',
      'https://binderhub.rc.nectar.org.au/',
      'https://tutorials.rc.nectar.org.au/',
      'https://support.ehelp.edu.au/support/solutions/articles/6000171494-project-allocation-expiry-and-renewal#pt',
      'https://dashboard.rc.nectar.org.au/terms',
      'https://status.rc.nectar.org.au/',
      'https://ardc.edu.au/',
    ]) {
      expect(hrefs, href).toContain(href);
    }
    // No Freshdesk tickets or Grafana usage links on the user view.
    await expect(page.locator('#allocation_tickets')).toHaveCount(0);
    await expect(page.locator('#allocation_project_usage')).toHaveCount(0);
  });
});
