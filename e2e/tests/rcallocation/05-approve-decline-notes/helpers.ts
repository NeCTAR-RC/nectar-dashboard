import {
  Locator,
  Page,
  Response,
  request as playwrightRequest,
} from '@playwright/test';

import { expect } from '../../../support/fixtures';
import { Allocation, AllocationApi } from '../../../support/allocations';
import { BASE_URL, savedToken } from '../../../support/env';

// Local helpers for suite 05 (approve, decline and admin notes).  Kept
// here rather than in e2e/support so the shared files stay untouched.

// Form submissions that change an allocation's state send notifications
// and copy the record into history.  On the dev dashboard they take 10 to
// 20 s, longer than the 15 s default action timeout, so every submit that
// navigates waits this long.
export const SUBMIT_TIMEOUT = 150_000;

// Tests that change state, and the slow My Requests list (several hundred
// pwtest rows for the admin), need more than the 120 s default while
// other suites load the dev server.
export const TEST_TIMEOUT = 480_000;

// The lists and forms carry many scripts and images; 'load' can lag the
// usable page by a minute under load, so wait for the DOM only.
const READY = { waitUntil: 'domcontentloaded' as const, timeout: SUBMIT_TIMEOUT };

export const PENDING_URL = '/allocation/requests/';
export const MY_REQUESTS_URL = '/allocation/user_requests/';

export const DETAIL_TITLE = 'View allocation request - Nectar Dashboard';
export const NOTES_TITLE = 'Edit allocation Admin notes - Nectar Dashboard';
export const DECLINE_TITLE =
  'Decline or Request Amendment from User - Nectar Dashboard';
export const APPROVE_TITLE = 'Approve Request - Nectar Dashboard';
export const AMEND_TITLE = 'Request Allocation Extension - Nectar Dashboard';
export const EDIT_TITLE = 'Edit Allocation Request - Nectar Dashboard';

export const WARNINGS_INTRO =
  'Warnings Please review the following warnings. Then either modify the ' +
  'form and "Submit" it again, or "Submit ignoring warnings".';
export const APPROVER_PROBLEM =
  'Problem with approver registration: contact Core Services';
export const NO_VALID_GRANTS =
  'There are no current competitive grants for this request. Either ' +
  'approve it as Local, or add a Special approval reason.';
export const WARNING_INFO_URL =
  'https://support.ehelp.edu.au/support/solutions/articles/6000220088';

export const NAGS_TEXT =
  '× Attention Required The following items require your attention ' +
  'before you submit this amendment. These may be a result of changes ' +
  'that we have made to this form since your last submission. Please ' +
  'provide an impact and benefit statement for your project. Also ' +
  'include any publications which have occurred since your last ' +
  'renewal. Providing this information supports the ongoing ' +
  'sustainability of the ARDC Nectar Research Cloud. Close';

// Admin detail buttons by status.
export const E_BUTTONS = [
  'Add/edit admin notes',
  'Review & Approve',
  'Decline with Reason',
  'View History',
  'Related tickets',
];
export const X_BUTTONS = [
  'Add/edit admin notes',
  'Approve changes',
  'Decline changes',
  'View History',
  'Related tickets',
];
export const A_BUTTONS = [
  'Add/edit admin notes',
  'View History',
  'Related tickets',
];

export const HISTORY_HEADERS = [
  'Project name',
  'Approver',
  'Bundle',
  'SUs',
  'Cores',
  'RAM',
  'Object Storage',
  'Volume Storage',
  'Status',
  'Modification time',
];

// The Standard bundle's values in the history table (SUs, cores, RAM,
// object storage, volume storage).  A and E/R rows show the values;
// X and J rows show the change against the approval, all zero for the
// fixtures.
export const STANDARD_VALUES = ['4000', '64', '128', '500', '-'];
export const ZERO_DELTAS = ['0', '0', '0', '0', '0'];

const text = (s: string | null | undefined) =>
  (s ?? '').replace(/\s+/g, ' ').trim();

// ---------------------------------------------------------------------
// Dates

// The Django 'N j, Y' date format, as rendered by the dashboard.
const MONTHS = [
  'Jan.', 'Feb.', 'March', 'April', 'May', 'June',
  'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.',
];

function djangoDate(d: Date): string {
  return `${MONTHS[d.getUTCMonth()]} ${d.getUTCDate()}, ${d.getUTCFullYear()}`;
}

// The displayed time zone is not stable within a session, so accept the
// date of the timestamp in any time zone from UTC-12 to UTC+14.
export function possibleDates(iso: string): string[] {
  const t = new Date(iso).getTime();
  const dates = new Set<string>();
  for (let h = -12; h <= 14; h++) {
    dates.add(djangoDate(new Date(t + h * 3600_000)));
  }
  return [...dates];
}

// A REST timestamp as epoch milliseconds.  The API renders the same
// instant as UTC ('Z') or +11:00 depending on the request.
export function instant(value: unknown): number {
  return new Date(value as string).getTime();
}

const escape = (s: string) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

// '<prefix><one of dates>, <a time>' with the time left unchecked.
export function dateTime(prefix: string, dates: string[]): RegExp {
  return new RegExp(
    `^${escape(prefix)}(${dates.map(escape).join('|')}), ` +
      `(\\d{1,2}(:\\d{2})? [ap]\\.m\\.|noon|midnight)$`,
  );
}

// ---------------------------------------------------------------------
// Fixture set-up beyond the shared allocations fixture

// The REST API, for the chief investigator and grant endpoints that the
// shared fixture does not wrap.
export async function withRest<T>(
  fn: (api: Awaited<ReturnType<typeof playwrightRequest.newContext>>) => Promise<T>,
): Promise<T> {
  const api = await playwrightRequest.newContext({
    baseURL: BASE_URL,
    extraHTTPHeaders: { 'X-Auth-Token': savedToken() },
  });
  try {
    return await fn(api);
  } finally {
    await api.dispose();
  }
}

// A fixture allocation has no chief investigator and no grant, so the
// user edit forms (edit_request, edit_change_request) reject it with
// 'This field is required.' errors.  Create a Submitted (E) allocation
// with both, which the REST API only accepts while the record is E or X.
export async function createEditable(
  allocations: AllocationApi,
  overrides: Record<string, unknown> = {},
): Promise<Allocation> {
  const created = await allocations.create(overrides);
  await withRest(async (api) => {
    const ci = await api.post('/rest_api/chiefinvestigators/', {
      data: {
        allocation: created.id,
        title: 'Dr',
        given_name: 'Playwright',
        surname: 'Tester',
        email: 'pwtest-ci@example.org',
        primary_organisation: 'https://ror.org/02bfwt286',
      },
    });
    expect(ci.status(), await ci.text()).toBe(201);
    const grant = await api.post('/rest_api/grants/', {
      data: {
        allocation: created.id,
        grant_type: 'arc',
        grant_subtype: 'arc-discovery',
        funding_body_scheme: 'Playwright test grant',
        grant_id: 'DP000001',
        first_year_funded: 2025,
        last_year_funded: 2030,
        total_funding: 100000,
      },
    });
    expect(grant.status(), await grant.text()).toBe(201);
  });
  return created;
}

// An Approved (A) allocation the user amend form accepts.
export async function createAmendable(
  allocations: AllocationApi,
): Promise<Allocation> {
  const created = await createEditable(allocations, {
    associated_site: 'qcif',
  });
  return allocations.approve(created.id);
}

// The ids of history records in `after` that are not in `before`.
export function newHistory(before: Allocation[], after: Allocation[]) {
  const old = new Set(before.map((h) => h.id));
  return after.filter((h) => !old.has(h.id));
}

// ---------------------------------------------------------------------
// UI actions

// Click a control that submits a form and wait for the resulting page.
export async function submitTo(page: Page, control: Locator, url: RegExp) {
  await Promise.all([
    page.waitForURL(url, READY),
    control.click({ timeout: SUBMIT_TIMEOUT }),
  ]);
}

// Submit a form that re-renders at the same URL (validation or warnings).
export async function submitInPlace(page: Page, control: Locator) {
  await Promise.all([
    page.waitForEvent('framenavigated', { timeout: SUBMIT_TIMEOUT }),
    control.click({ timeout: SUBMIT_TIMEOUT }),
  ]);
  await page.waitForLoadState('domcontentloaded', { timeout: SUBMIT_TIMEOUT });
}

export function submitButton(page: Page): Locator {
  return page.locator('input[type=submit]').filter({ visible: true });
}

// Decline through the admin form.  The shared declineViaUi() uses the
// 15 s default action timeout, which the slow decline POST can exceed.
export async function declineUi(page: Page, id: number, reason: string) {
  await page.goto(`/allocation/requests/reject_request/${id}/`, READY);
  await page.locator('#id_status_explanation').fill(reason);
  await submitTo(
    page,
    page.locator('input[type=submit][value="Decline Request"]'),
    /\/allocation\/requests\/$/,
  );
}

// Approve through the admin form, ignoring the approver registration
// warning that the test user always triggers.
export async function approveUi(page: Page, id: number, site = 'QCIF') {
  await page.goto(`/allocation/requests/approve_request/${id}/`, READY);
  await page.locator('#id_associated_site').selectOption({ label: site });
  await submitInPlace(page, page.locator('input[type=submit][value="Approve Request"]'));
  await submitTo(
    page,
    page.locator('input[type=button][value="Approve ignoring warnings"]'),
    /\/allocation\/requests\/$/,
  );
}

// Open the user amend form and close the 'Attention Required' modal that
// opens on load.
export async function openAmendForm(page: Page, id: number) {
  await page.goto(`/allocation/user_requests/edit_change_request/${id}/`, READY);
  const modal = page.locator('#modal-nags');
  await expect(modal).toHaveClass(/\bin\b/);
  await expect(modal).toBeVisible();
  return modal;
}

export async function closeNags(page: Page) {
  const modal = page.locator('#modal-nags');
  // The modal is aria-hidden even while shown, so match by text.
  await modal.locator('button', { hasText: 'Close' }).click();
  await expect(modal).toBeHidden();
}

// Amend an approved allocation through the user form (A to X).
export async function amendUi(page: Page, id: number) {
  await openAmendForm(page, id);
  await closeNags(page);
  await submitTo(page, submitButton(page).first(), /\/allocation\/user_requests\/$/);
}

export async function open(page: Page, url: string): Promise<Response> {
  const response = await page.goto(url);
  expect(response, `no response for ${url}`).not.toBeNull();
  return response!;
}

// The plain-text 400 bodies returned by the approve and reject guards: the
// message plus a random HTML comment token, with no page template.
export async function expectGuarded400(
  page: Page,
  url: string,
  message: string,
) {
  const response = await open(page, url);
  expect(response.status(), url).toBe(400);
  expect(await response.text()).toMatch(
    new RegExp(`^${escape(message)}<!-- \\S+ -->$`),
  );
  await expect(page).toHaveTitle('');
  await expect(page.locator('#sidebar')).toHaveCount(0);
}

// ---------------------------------------------------------------------
// Page readers

// Headings h2 to h6 outside the header's project switcher, whose
// dropdown holds an h6 'Select Project'.
export function contentHeadings(page: Page): Locator {
  return page.locator(':is(h2, h3, h4, h5, h6):not(.dropdown *)');
}

export function detail(page: Page): Locator {
  return page.locator('.allocation');
}

export async function gotoDetail(page: Page, id: number) {
  const response = await page.goto(`/allocation/requests/view/${id}/`, READY);
  expect(response?.status()).toBe(200);
  await expect(page).toHaveTitle(DETAIL_TITLE);
}

export async function gotoUserDetail(page: Page, id: number) {
  const response = await page.goto(`/allocation/user_requests/view/${id}/`, READY);
  expect(response?.status()).toBe(200);
  await expect(page).toHaveTitle(DETAIL_TITLE);
}

export async function headings(page: Page, tag: string): Promise<string[]> {
  await expect(detail(page).first()).toBeVisible();
  return detail(page)
    .locator(tag)
    .evaluateAll((els) =>
      els.map((e) => e.textContent!.replace(/\s+/g, ' ').trim()),
    );
}

// The rows of the n-th table inside .allocation, as 'th td' text.
export async function tableRows(page: Page, n: number): Promise<string[]> {
  await expect(detail(page).first()).toBeVisible();
  return detail(page)
    .locator('table')
    .nth(n)
    .locator('tr')
    .evaluateAll((trs) =>
      trs.map((tr) => tr.textContent!.replace(/\s+/g, ' ').trim()),
    );
}

// The 'State ...' row of the right-hand detail table.
export function stateRow(page: Page): Locator {
  return detail(page).locator('table').nth(1).locator('tr').first();
}

export async function detailButtons(
  page: Page,
): Promise<{ text: string; href: string | null }[]> {
  await expect(detail(page).first()).toBeVisible();
  return detail(page)
    .locator('a.btn')
    .evaluateAll((as) =>
      as.map((a) => ({
        text: a.textContent!.replace(/\s+/g, ' ').trim(),
        href: a.getAttribute('href'),
      })),
    );
}

export async function detailButtonTexts(page: Page): Promise<string[]> {
  return (await detailButtons(page)).map((b) => b.text);
}

// The paragraph after the given h3 on a detail page.
export function afterHeading(page: Page, heading: string): Locator {
  return detail(page)
    .locator('h3', { hasText: heading })
    .locator('xpath=following-sibling::p[1]');
}

export function adminNotes(page: Page): Locator {
  return afterHeading(page, 'Allocation admin notes');
}

// The Pending list link to an allocation.
export function pendingLink(page: Page, id: number): Locator {
  return page.locator(`#datatableoptions a[href="/allocation/requests/view/${id}/"]`);
}

export async function gotoPending(page: Page) {
  await page.goto(PENDING_URL, READY);
  await expect(page.locator('#datatableoptions tbody tr').first()).toBeVisible();
}

export type ListRow = {
  cells: string[];
  stateTitle: string;
  actions: { text: string; href: string }[];
};

// One row of My Requests, by allocation id.
export async function myRequestsRow(page: Page, id: number): Promise<ListRow> {
  await page.goto(MY_REQUESTS_URL, READY);
  const row = page.locator(`#DataTableOptions__row__${id}`);
  await expect(row).toHaveCount(1, { timeout: SUBMIT_TIMEOUT });
  return row.evaluate((tr) => ({
    cells: [...tr.querySelectorAll('td')].map((td) =>
      (td as HTMLElement).innerText.replace(/\s+/g, ' ').trim(),
    ),
    stateTitle: tr.querySelector('p.alloc-icon')?.getAttribute('title') ?? '',
    actions: [
      ...tr.querySelectorAll('td.actions_column a.data-table-action'),
    ].map((a) => ({
      text: (a.textContent ?? '').trim(),
      href: a.getAttribute('href') ?? '',
    })),
  }));
}

export type HistoryRow = { id: number; cells: string[]; href: string };

// Open an allocation's history page and read its table.
export async function readHistory(
  page: Page,
  id: number,
): Promise<{ headers: string[]; rows: HistoryRow[] }> {
  const response = await page.goto(`/allocation/requests/view/${id}/history`, READY);
  expect(response?.status()).toBe(200);
  await expect(page).toHaveTitle('Allocation Requests - Nectar Dashboard');
  return page.locator('#datatableoptions').evaluate((table) => ({
    headers: [...table.querySelectorAll('thead tr:last-child th')]
      .map((th) => (th.textContent ?? '').replace(/\s+/g, ' ').trim())
      .filter((h) => h !== ''),
    rows: [...table.querySelectorAll('tbody tr[data-object-id]')].map(
      (tr) => ({
        id: Number(tr.getAttribute('data-object-id')),
        cells: [...tr.querySelectorAll('td')].map((td) =>
          (td.textContent ?? '').replace(/\s+/g, ' ').trim(),
        ),
        href: tr.querySelector('td a')?.getAttribute('href') ?? '',
      }),
    ),
  }));
}

// A history row as [name, approver, bundle, 5 values, status] with the
// modification time checked separately (dates only).
export function historyCells(row: HistoryRow): string[] {
  return row.cells.slice(0, 9);
}

// Visible form controls of the allocation form, in DOM order.
export type FormControl = {
  tag: string;
  type: string;
  name: string;
  id: string;
  value: string;
  required: boolean;
  readOnly: boolean;
  disabled: boolean;
  label: string;
  help: string | null;
};

export async function formControls(page: Page): Promise<FormControl[]> {
  return page.locator('form#new-allocation').evaluate((form) =>
    [...form.querySelectorAll('input, select, textarea')]
      .filter(
        (e) =>
          (e as HTMLInputElement).type === 'hidden' ||
          (e as HTMLElement).offsetParent !== null,
      )
      .map((e) => {
        const el = e as HTMLInputElement;
        const label = el.id
          ? form.querySelector(`label[for="${el.id}"]`)
          : null;
        return {
          tag: el.tagName.toLowerCase(),
          type: el.type,
          name: el.name,
          id: el.id,
          value:
            el.name === 'csrfmiddlewaretoken' ? '<token>' : el.value,
          required: el.required,
          readOnly: el.readOnly,
          disabled: el.disabled,
          label: (label?.textContent ?? '').replace(/\s+/g, ' ').trim(),
          help:
            label
              ?.querySelector('.help-popover')
              ?.getAttribute('data-content')
              ?.replace(/\s+/g, ' ')
              .trim() ?? null,
        };
      }),
  );
}

export async function selectOptions(page: Page, selector: string) {
  return page.locator(selector).evaluate((s) =>
    [...(s as HTMLSelectElement).options].map((o) => ({
      text: o.text,
      selected: o.selected,
    })),
  );
}

// ---------------------------------------------------------------------
// The approve form

// The per-zone volume storage inputs and the Shared File System inputs,
// in page order.  All empty and optional; there are no compute, SU, RAM or
// object storage inputs for a bundle request.
export const VOLUME_ZONES = [
  'auckland', 'encrypted-auckland', 'intersect', 'encrypted-intersect',
  'melbourne', 'encrypted-melbourne', 'performance-melbourne', 'monash',
  'encrypted-monash', 'QRIScloud', 'encrypted-QRIScloud', 'swinburne',
  'encrypted-swinburne', 'tasmania', 'encrypted-tasmania',
];
export const ZONE_HEADINGS = [
  'Auckland (NZ)', 'Auckland (NZ) encrypted', 'Intersect (NSW)',
  'Intersect (NSW) encrypted', 'Melbourne University',
  'Melbourne University encrypted', 'Melbourne University performance',
  'Monash (VIC)', 'Monash (VIC) encrypted', 'QRIScloud',
  'QRIScloud encrypted', 'Swinburne (VIC)', 'Swinburne (VIC) encrypted',
  'Tasmania', 'Tasmania encrypted',
  // Shared File System zones.
  'Auckland (NZ)', 'Monash (VIC)',
];
export const QUOTA_INPUTS: [string, string][] = [
  ...VOLUME_ZONES.map(
    (z) => [`quota-volume.gigabytes__${z}`, 'Storage'] as [string, string],
  ),
  ...['auckland', 'monash-02-cephfs'].flatMap((z) => [
    [`quota-share.shares__${z}`, 'Shares'] as [string, string],
    [`quota-share.gigabytes__${z}`, 'Storage'] as [string, string],
    [`quota-share.snapshots__${z}`, 'Snapshots'] as [string, string],
    [`quota-share.snapshot_gigabytes__${z}`, 'Snapshot storage'] as [string, string],
  ]),
];

const SITES = [
  '---------', 'Auckland', 'Intersect', 'Monash', 'QCIF', 'Swinburne',
  'TPAC', 'University of Melbourne', 'ARDC',
];

const PROJECT_NAME_HELP =
  'A short name used to identify your project.<br>Must contain only ' +
  'letters and numbers.<br>16 characters max.';
const SITE_HELP =
  'The Approver will normally set the Associated Site to their own node.';
const NATIONAL_HELP =
  "The Approver should check 'National funding' for all allocations that " +
  'meet the Nectar national funding criteria.';
const SPECIAL_HELP =
  'Use this field to record reasons the allocation is approved as ' +
  'National despite not meeting the primary criteria; i.e. a current ' +
  'competitive, NCRIS support or ARDC support. See the RC-NAS policy for ' +
  'the possible reasons. This is only visible to allocation admins';

// Check the approve form's controls for a Standard-bundle fixture.
// `site` is the Associated site label expected to be selected.
export async function expectApproveForm(
  page: Page,
  e: { project_name: string; project_description: string },
  site: string,
) {
  const controls = await formControls(page);
  const byName = (n: string) => controls.find((c) => c.name === n) as FormControl;

  expect(controls.map((c) => c.name)).toEqual([
    'csrfmiddlewaretoken',
    'ignore_warnings',
    'project_name',
    'project_description',
    'estimated_project_duration',
    'bundle',
    ...QUOTA_INPUTS.map(([n]) => n),
    'associated_site',
    'national',
    'special_approval',
    'status_explanation',
    '',
  ]);
  expect(byName('ignore_warnings')).toMatchObject({ type: 'hidden', value: '' });
  expect(byName('project_name')).toMatchObject({
    type: 'text',
    value: e.project_name,
    readOnly: true,
    disabled: true,
    required: false,
    label: 'Project identifier',
    help: PROJECT_NAME_HELP,
  });
  expect(byName('project_description')).toMatchObject({
    type: 'text',
    value: e.project_description,
    readOnly: true,
    disabled: true,
    label: 'Project allocation title',
  });
  expect(byName('estimated_project_duration')).toMatchObject({
    tag: 'select',
    value: '12',
    label: 'Estimated project duration',
  });
  expect(
    await selectOptions(page, '#id_estimated_project_duration'),
  ).toEqual(
    ['1-month', '3-months', '6-months', '12-months'].map((text) => ({
      text,
      selected: text === '12-months',
    })),
  );
  expect(byName('bundle')).toMatchObject({
    tag: 'select',
    required: true,
    label: 'Bundle',
  });
  await expect(page.locator('#id_bundle-group .glyphicon-asterisk')).toHaveCount(1);
  expect(await selectOptions(page, '#id_bundle')).toEqual(
    ['---------', 'Standard', 'Powerful', 'Extreme'].map((text) => ({
      text,
      selected: text === 'Standard',
    })),
  );
  await expect(page.locator('p', { hasText: 'Is this a suitable bundle?' })).toHaveText(
    'Is this a suitable bundle? Review the Resource Bundle Table before approving.',
  );

  for (const [name, label] of QUOTA_INPUTS) {
    expect(byName(name), name).toMatchObject({
      type: 'number',
      value: '',
      required: false,
      label,
    });
  }

  expect(byName('associated_site')).toMatchObject({
    tag: 'select',
    required: true,
    label: 'Associated site',
    help: SITE_HELP,
  });
  expect(await selectOptions(page, '#id_associated_site')).toEqual(
    SITES.map((text) => ({ text, selected: text === site })),
  );
  expect(byName('national')).toMatchObject({
    type: 'checkbox',
    label: 'National funding',
    help: NATIONAL_HELP,
  });
  await expect(page.locator('#id_national')).not.toBeChecked();
  expect(byName('special_approval')).toMatchObject({
    type: 'text',
    value: '',
    label: 'Special RC-NAS approval reasons',
    help: SPECIAL_HELP,
  });
  await expect(page.locator('#id_special_approval')).toHaveAttribute('maxlength', '1024');
  // The initial comment is forced to ''.
  expect(byName('status_explanation')).toMatchObject({
    tag: 'textarea',
    value: '',
    label: 'Comment',
    help: 'Reviewer Comment',
  });
  expect(controls.at(-1)).toMatchObject({ type: 'submit', value: 'Approve Request' });
  await expect(page.locator('input[type=button]')).toHaveCount(0);
}

export { text };

