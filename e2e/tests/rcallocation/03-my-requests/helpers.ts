import {
  APIRequestContext,
  Locator,
  Page,
  Response,
  request as playwrightRequest,
} from '@playwright/test';

import { expect } from '../../../support/fixtures';
import { Allocation, AllocationApi } from '../../../support/allocations';
import { BASE_URL, savedToken } from '../../../support/env';

// Local helpers for suite 03 (My Requests list and detail, user edit and
// amend forms).  Kept here rather than in e2e/support so the shared files
// stay untouched.

export const LIST_URL = '/allocation/user_requests/';

// The admin's My Requests list holds every allocation the e2e suites have
// created (586 rows on 2026-10-30, growing with each run) and takes about
// a minute to render on a quiet dev server, much longer while other suites
// run.  Allow well over the 90 s navigation timeout for it.
export const LIST_LOAD_TIMEOUT = 240_000;
export const LIST_TITLE = 'Allocation Requests - Nectar Dashboard';
export const DETAIL_TITLE = 'View allocation request - Nectar Dashboard';
export const EDIT_TITLE = 'Edit Allocation Request - Nectar Dashboard';
export const AMEND_TITLE = 'Request Allocation Extension - Nectar Dashboard';
export const ADMIN_EMAIL = 'sorrison@gmail.com';

export const viewUrl = (id: number) => `/allocation/user_requests/view/${id}/`;
export const editUrl = (id: number) =>
  `/allocation/user_requests/edit_request/${id}/`;
export const amendUrl = (id: number) =>
  `/allocation/user_requests/edit_change_request/${id}/`;

// The shared fixtures register two 'dialog' handlers on each page.  When a
// form page raises a beforeunload dialog the second accept() throws
// "Cannot accept dialog which is already handled!".  Replace both with a
// single handler that tolerates an already-handled dialog.
export function acceptDialogsOnce(page: Page): void {
  page.removeAllListeners('dialog');
  page.on('dialog', (d) => {
    d.accept().catch(() => {});
  });
}

// Navigate and return the main response, failing if there was none.
export async function open(page: Page, url: string): Promise<Response> {
  const response = await page.goto(url);
  expect(response, `no response for ${url}`).not.toBeNull();
  return response!;
}

export const FORBIDDEN_TEXT =
  'You do not have the required privileges to access this content. ' +
  'If you believe this message to be in error, please contact your ' +
  'project manager.';

// The Horizon 'Forbidden' page served with HTTP 403 and no redirect.
export async function expectForbidden(page: Page, url: string) {
  const response = await open(page, url);
  expect(response.status(), url).toBe(403);
  await expect(page).toHaveURL(url);
  await expect(page).toHaveTitle('- Forbidden - Nectar Dashboard');
  await expect(page.getByRole('heading', { name: 'Forbidden' })).toBeVisible();
  await expect(page.getByText(FORBIDDEN_TEXT)).toBeVisible();
}

export const EDIT_STATE_TEXT =
  'Allocation request cannot be edited in its current state';
export const AMEND_STATE_TEXT =
  'Allocation cannot be amended in its current state';

// A view refusing an allocation in the wrong status: HTTP 400 with a
// plain-text message (NECTAR-17320).
export async function expectGuarded400(
  page: Page,
  url: string,
  message: string,
) {
  const response = await open(page, url);
  expect(response.status(), url).toBe(400);
  expect(await response.text()).toMatch(
    new RegExp(`^${message}<!-- \\S+ -->$`),
  );
  await expect(page.locator('#sidebar')).toHaveCount(0);
}

// The Django debug 404 page (the dev deployment runs with DEBUG on).
export async function expectNotFound(page: Page, url: string) {
  const response = await open(page, url);
  expect(response.status(), url).toBe(404);
  await expect(page).toHaveTitle(`Page not found at ${url}`);
  await expect(
    page.getByRole('heading', { name: 'Page not found (404)' }),
  ).toBeVisible();
}

// ---------------------------------------------------------------------
// Test data.  The shared AllocationApi creates bare requests with no
// Chief Investigator, which the edit and amend forms then reject.  These
// add the related records through the REST API while the allocation is
// still Submitted (the API refuses changes in other states).
// ---------------------------------------------------------------------

export const CI = {
  title: 'Dr',
  given_name: 'Pw',
  surname: 'Tester',
  email: 'pw@example.edu.au',
  // Monash University
  primary_organisation: 'https://ror.org/02bfwt286',
  additional_researchers: '',
};

export const GRANT = {
  grant_type: 'inst',
  grant_subtype: 'unspecified',
  funding_body_scheme: 'Uni fund',
  grant_id: 'PW-03',
  first_year_funded: 2026,
  last_year_funded: 2027,
  total_funding: 1000,
};

export class ExtraApi {
  private constructor(private readonly api: APIRequestContext) {}

  // token: the admin's saved token by default, or the non-admin user's.
  static async create(token = savedToken()): Promise<ExtraApi> {
    return new ExtraApi(
      await playwrightRequest.newContext({
        baseURL: BASE_URL,
        extraHTTPHeaders: { 'X-Auth-Token': token },
      }),
    );
  }

  async addInvestigator(id: number) {
    const r = await this.api.post('/rest_api/chiefinvestigators/', {
      data: { allocation: id, ...CI },
    });
    expect(r.status(), await r.text()).toBe(201);
  }

  async addGrant(id: number) {
    const r = await this.api.post('/rest_api/grants/', {
      data: { allocation: id, ...GRANT },
    });
    expect(r.status(), await r.text()).toBe(201);
  }

  async dispose() {
    await this.api.dispose();
  }
}

// A Submitted (E) allocation that the edit form accepts: it has a Chief
// Investigator and, if asked, a grant.
export async function createEditable(
  allocations: AllocationApi,
  opts: { grant?: boolean; overrides?: Record<string, unknown> } = {},
  token?: string,
): Promise<Allocation> {
  const extra = await ExtraApi.create(token);
  const e = await allocations.create(opts.overrides ?? {});
  await extra.addInvestigator(e.id);
  if (opts.grant) {
    await extra.addGrant(e.id);
  }
  await extra.dispose();
  return e;
}

// An Approved (A) allocation with a Chief Investigator, for the amend form.
export async function createAmendable(
  allocations: AllocationApi,
): Promise<Allocation> {
  const e = await createEditable(allocations, {
    overrides: { associated_site: 'qcif' },
  });
  return allocations.approve(e.id);
}

// A slow page load after a click can outlast the 15 s action timeout,
// which a click also spends waiting for the navigation it starts.  Click
// without that wait and wait for the URL with the navigation timeout.
export async function clickAndWaitForURL(
  page: Page,
  target: Locator,
  url: string | RegExp,
) {
  await Promise.all([
    page.waitForURL(url, { timeout: LIST_LOAD_TIMEOUT, waitUntil: 'domcontentloaded' }),
    target.click({ noWaitAfter: true }),
  ]);
}

// declineViaUi from support/allocations, with clickAndWaitForURL: the
// decline POST sends notifications and can take longer than 15 s on dev.
// Status becomes R for a new request and J for a pending amendment.
export async function decline(page: Page, id: number, reason: string) {
  await page.goto(`/allocation/requests/reject_request/${id}/`);
  await page.locator('#id_status_explanation').fill(reason);
  await clickAndWaitForURL(
    page,
    page.locator('input[type=submit]').first(),
    /\/allocation\/requests\/$/,
  );
}

// ---------------------------------------------------------------------
// Dates.  The displayed time zone is not stable within a session, so
// accept the date of a timestamp in any time zone from UTC-12 to UTC+14.
// ---------------------------------------------------------------------

const MONTHS = [
  'Jan.', 'Feb.', 'March', 'April', 'May', 'June',
  'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.',
];

export function djangoDate(d: Date): string {
  return `${MONTHS[d.getUTCMonth()]} ${d.getUTCDate()}, ${d.getUTCFullYear()}`;
}

export function possibleDates(iso: string): string[] {
  const t = new Date(iso).getTime();
  const dates = new Set<string>();
  for (let h = -12; h <= 14; h++) {
    dates.add(djangoDate(new Date(t + h * 3600_000)));
  }
  return [...dates];
}

// The date part of a Django 'N j, Y, P' datetime ('Oct. 30, 2026, 6:37 p.m.').
export function datePart(text: string): string {
  const m = text.match(/^(\S+ \d{1,2}, \d{4})/);
  expect(m, `not a Django datetime: '${text}'`).not.toBeNull();
  return m![1];
}

// ---------------------------------------------------------------------
// My Requests list.
// ---------------------------------------------------------------------

export const TABLE = '#datatableoptions';

export function row(page: Page, id: number): Locator {
  return page.locator(`#DataTableOptions__row__${id}`);
}

export async function gotoList(page: Page) {
  const response = await page.goto(LIST_URL, {
    timeout: LIST_LOAD_TIMEOUT,
    waitUntil: 'domcontentloaded',
  });
  expect(response, 'no response for the list').not.toBeNull();
  expect(response!.status()).toBe(200);
  await expect(page).toHaveTitle(LIST_TITLE);
}

export async function columnHeaders(page: Page): Promise<string[]> {
  return (await page.locator(`${TABLE} thead th`).allInnerTexts()).map((t) =>
    t.trim(),
  );
}

export type TableRow = {
  id: string;
  cells: string[];
  stateTitle: string;
  stateClass: string;
  name: string;
  nameHref: string;
  actions: { text: string; href: string; id: string; className: string }[];
};

// Read the whole table in one round trip: the admin's list has hundreds of
// rows from earlier test runs.
export async function readTable(page: Page): Promise<TableRow[]> {
  return page.locator(TABLE).evaluate((table) =>
    Array.from(table.querySelectorAll('tbody tr[data-object-id]')).map(
      (tr) => {
        const tds = Array.from(tr.querySelectorAll('td'));
        const state = tr.querySelector('td p.alloc-icon');
        const link = tr.querySelector('td:not(.actions_column) a');
        return {
          id: tr.getAttribute('data-object-id') ?? '',
          cells: tds.map((td) =>
            (td as HTMLElement).innerText.replace(/\s+/g, ' ').trim(),
          ),
          stateTitle: state?.getAttribute('title') ?? '',
          stateClass: state?.className ?? '',
          name: (link?.textContent ?? '').trim(),
          nameHref: link?.getAttribute('href') ?? '',
          actions: Array.from(tr.querySelectorAll('td.actions_column a')).map(
            (a) => ({
              text: (a.textContent ?? '').trim(),
              href: a.getAttribute('href') ?? '',
              id: a.id,
              className: a.className,
            }),
          ),
        };
      },
    ),
  );
}

export function findRow(rows: TableRow[], id: number): TableRow {
  const r = rows.find((x) => x.id === String(id));
  expect(r, `row ${id} listed`).toBeDefined();
  return r!;
}

// ---------------------------------------------------------------------
// User detail page.
// ---------------------------------------------------------------------

export function detail(page: Page): Locator {
  return page.locator('.allocation');
}

export async function gotoDetail(page: Page, id: number) {
  const response = await open(page, viewUrl(id));
  expect(response.status()).toBe(200);
  await expect(page).toHaveTitle(DETAIL_TITLE);
}

export async function texts(scope: Locator, selector: string): Promise<string[]> {
  return scope
    .locator(selector)
    .evaluateAll((els) =>
      els.map((e) => e.textContent!.replace(/\s+/g, ' ').trim()),
    );
}

// The rows of every table inside .allocation, as 'th td' text.
export async function detailTables(page: Page): Promise<string[][]> {
  return detail(page)
    .locator('table')
    .evaluateAll((tables) =>
      tables.map((t) =>
        [...t.querySelectorAll('tr')].map((tr) =>
          tr.textContent!.replace(/\s+/g, ' ').trim(),
        ),
      ),
    );
}

// The text of the elements between an h3 and the next h3, joined.
export async function section(page: Page, heading: string): Promise<string> {
  return detail(page)
    .locator('h3', { hasText: heading })
    .first()
    .evaluate((h) => {
      const out: string[] = [];
      for (let el = h.nextElementSibling; el && el.tagName !== 'H3'; el = el.nextElementSibling) {
        out.push(el.textContent!);
      }
      return out.join(' ').replace(/\s+/g, ' ').trim();
    });
}

export async function detailButtons(page: Page) {
  return detail(page)
    .locator('a.btn')
    .evaluateAll((as) =>
      as.map((a) => ({
        text: a.textContent!.replace(/\s+/g, ' ').trim(),
        href: a.getAttribute('href'),
        id: a.id,
        className: a.className,
      })),
    );
}

// ---------------------------------------------------------------------
// Edit and amend forms.
// ---------------------------------------------------------------------

export const FIX_ERRORS = 'Please fix the errors highlighted below and resubmit.';

export function form(page: Page): Locator {
  return page.locator('form#new-allocation');
}

// Expand a collapsed accordion panel by its heading link and wait for it
// to finish opening.
export async function expandPanel(page: Page, heading: string, id: string) {
  const panel = page.locator(`#${id}`);
  if (!(await panel.evaluate((p) => p.classList.contains('in')))) {
    await page.getByRole('link', { name: heading, exact: true }).click();
  }
  await expect(panel).toHaveClass(/\bin\b/);
  await expect(panel).toBeVisible();
}

// The ids of the open accordion panels, in DOM order.
export async function openPanels(page: Page): Promise<string[]> {
  return page
    .locator('.request-collapse.in')
    .evaluateAll((ps) => ps.map((p) => p.id));
}

// Field errors: [panel id, label, help text].
export async function fieldErrors(page: Page): Promise<string[][]> {
  return form(page)
    .locator('.form-group.has-error')
    .evaluateAll((gs) =>
      gs.map((g) => [
        g.closest('.panel-collapse')?.id ?? '',
        g.querySelector('label')?.textContent?.replace(/\s+/g, ' ').trim() ?? '',
        g.querySelector('.help-block')?.textContent?.replace(/\s+/g, ' ').trim() ?? '',
      ]),
    );
}

// The amend form opens the 'Attention Required' modal on load; close it
// before touching anything else.
export async function closeNags(page: Page) {
  const modal = page.locator('#modal-nags');
  await expect(modal).toBeVisible();
  // A CSS locator: the modal keeps aria-hidden="true" while shown, which
  // hides its buttons from role queries.
  await modal.locator('.modal-footer button', { hasText: 'Close' }).click();
  await expect(modal).toBeHidden();
}

// Click a submit control and wait for the POST and the page it renders or
// redirects to.  Returns the POST response.
export async function submitForm(
  page: Page,
  button: Locator,
): Promise<Response> {
  // The POST sends notifications and can take longer than the 15 s action
  // timeout, so the click does not wait for it; the navigation timeout
  // applies instead.  waitForNavigation follows a redirect to the page it
  // lands on.
  const post = page.waitForResponse(
    (r) => r.request().method() === 'POST' && r.request().isNavigationRequest(),
    { timeout: 90_000 },
  );
  // A successful submit redirects to the slow My Requests list.
  const navigation = page.waitForNavigation({
    waitUntil: 'domcontentloaded',
    timeout: LIST_LOAD_TIMEOUT,
  });
  await button.click({ noWaitAfter: true });
  const response = await post;
  await navigation;
  return response;
}

export function submitButton(page: Page): Locator {
  return page.locator('input[type=submit].submit-form-button[value="Submit"]');
}

export function ignoreWarningsButton(page: Page): Locator {
  return page.locator('input[type=button][value="Submit ignoring warnings"]');
}

// Go to STEP 2 of the edit form, pick the Custom bundle and switch on the
// Huge RAM flavors, which (with an empty justification) raises the
// FLAVORS_NOT_JUSTIFIED warning on submit.
export async function requestHugeRam(page: Page) {
  await expandPanel(page, '8. Continue', 'panelEight');
  await page.locator('#panelEight').getByText('Continue', { exact: true }).click();
  await expect(page.locator('#panelBundle')).toBeVisible();
  const custom = page.locator('.bundle', { has: page.locator('h4', { hasText: 'Custom' }) });
  await custom.locator('> .btn').click();
  const modal = page.locator('#modal-custom-bundle');
  await expect(modal).toBeVisible();
  await expect(page.locator('select#id_bundle')).toHaveValue('');
  const hugeRam = modal.locator(
    'input[name="quota-compute.flavor:hugeram-v3__nectar"]',
  );
  // A bootstrap-toggle switch: click its visible wrapper.
  await hugeRam.locator('xpath=..').click();
  await expect(hugeRam).toBeChecked();
  await modal.getByRole('button', { name: 'Done' }).click();
  await expect(modal).toBeHidden();
}

export const FLAVORS_WARNING =
  'Requests for access to special flavors must be explained in the ' +
  '"Justification ..." field.';
export const FLAVORS_HREF =
  'https://support.ehelp.edu.au/support/solutions/articles/6000220088#FLAVORS_NOT_JUSTIFIED';

export const NO_PUBLICATIONS_NAG =
  'Please provide an impact and benefit statement for your project. Also ' +
  'include any publications which have occurred since your last renewal. ' +
  'Providing this information supports the ongoing sustainability of the ' +
  'ARDC Nectar Research Cloud.';
