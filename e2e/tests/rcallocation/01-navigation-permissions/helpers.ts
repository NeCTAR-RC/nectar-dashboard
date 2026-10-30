import {
  Locator,
  Page,
  Response,
  request as playwrightRequest,
} from '@playwright/test';

import { BASE_URL } from '../../../support/env';
import { expect } from '../../../support/fixtures';

// Local helpers for suite 01.  Kept here rather than in e2e/support so the
// shared files stay untouched.

// The shared fixtures register two 'dialog' handlers on each page (one from
// the context fixture's 'page' event and one from the page fixture).  When a
// form page raises a beforeunload dialog, the second accept() throws
// "Cannot accept dialog which is already handled!" and fails the test.
// Replace both with a single handler that tolerates an already-handled
// dialog.
export function acceptDialogsOnce(page: Page): void {
  page.removeAllListeners('dialog');
  page.on('dialog', (d) => {
    d.accept().catch(() => {});
  });
}

// A slow page load after a click can outlast the 15 s action timeout,
// which a click also spends waiting for the navigation it starts.  Click
// without that wait and wait for the URL, by default with the navigation
// timeout.
export async function clickAndWaitForURL(
  page: Page,
  target: Locator,
  url: string | RegExp | ((url: URL) => boolean),
  timeout?: number,
) {
  await Promise.all([
    page.waitForURL(url, { timeout }),
    target.click({ noWaitAfter: true }),
  ]);
}

// A form POST that saves an allocation (decline, user edit) sends
// notifications and has taken over 90 s on dev while other suites load
// it.  A test making N such saves should allow N * SAVE_TIMEOUT.
export const SAVE_TIMEOUT = 240_000;

// declineViaUi from support/allocations, with clickAndWaitForURL and
// SAVE_TIMEOUT.  Status becomes R for a new request and J for a pending
// amendment.
export async function decline(page: Page, id: number, reason: string) {
  await page.goto(`/allocation/requests/reject_request/${id}/`);
  await page.locator('#id_status_explanation').fill(reason);
  await clickAndWaitForURL(
    page,
    page.locator('input[type=submit]').first(),
    /\/allocation\/requests\/$/,
    SAVE_TIMEOUT,
  );
}

// The same Chief Investigator suite 03 uses.  The user edit form rejects
// an allocation without one, and the allocations fixture creates none.
const CHIEF_INVESTIGATOR = {
  title: 'Dr',
  given_name: 'Pw',
  surname: 'Tester',
  email: 'pw@example.edu.au',
  // Monash University
  primary_organisation: 'https://ror.org/02bfwt286',
  additional_researchers: '',
};

// Add a Chief Investigator through the REST API with the given token
// (the non-admin user's for their own allocation).
export async function addInvestigator(token: string, id: number) {
  const api = await playwrightRequest.newContext({
    baseURL: BASE_URL,
    extraHTTPHeaders: { 'X-Auth-Token': token },
  });
  const r = await api.post('/rest_api/chiefinvestigators/', {
    data: { allocation: id, ...CHIEF_INVESTIGATOR },
  });
  expect(r.status(), await r.text()).toBe(201);
  await api.dispose();
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

// Horizon's NotAuthorized page (horizon/templates/not_authorized.html),
// served with HTTP 403 and no redirect when a user lacks a panel's
// permissions.  Non-admins get it for every /allocation/requests/ and
// /allocation/approved_requests/ URL (observed live).
export async function expectNotAuthorized(page: Page, url: string) {
  const response = await open(page, url);
  expect(response.status(), url).toBe(403);
  await expect(page).toHaveURL(url);
  await expect(page).toHaveTitle(
    'Unauthorized. Please try logging in again. - Nectar Dashboard',
  );
  await expect(
    page.getByText('You are not authorized to access this page'),
  ).toBeVisible();
  await expect(page.locator('.breadcrumb li')).toHaveCount(0);
}

// The plain-text 400 bodies returned by the approve and reject guards.
// The body is the message plus a random HTML comment token.
export async function expectGuarded400(
  page: Page,
  url: string,
  message: string,
) {
  const response = await open(page, url);
  expect(response.status(), url).toBe(400);
  const body = await response.text();
  expect(body).toMatch(new RegExp(`^${message}<!-- \\S+ -->$`));
  await expect(page).toHaveTitle('');
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

export const TABLE = '#datatableoptions';

// The Approved Requests list renders ~1600 rows.  It takes about 30 s
// alone, and has taken over 240 s while other suites load the dev
// server, so allow much longer than the 90 s navigation timeout.
export const APPROVED_LOAD_TIMEOUT = 480_000;

export async function openApproved(page: Page): Promise<void> {
  await page.goto('/allocation/approved_requests/', {
    timeout: APPROVED_LOAD_TIMEOUT,
  });
}

export function row(page: Page, id: number) {
  return page.locator(`#DataTableOptions__row__${id}`);
}

export function visibleRows(page: Page) {
  return page.locator(`${TABLE} tbody tr`).filter({ visible: true });
}

export async function columnHeaders(page: Page): Promise<string[]> {
  return (await page.locator(`${TABLE} thead th`).allInnerTexts()).map((t) =>
    t.trim(),
  );
}

export type TableRow = {
  id: string;
  cells: string[];
  cellClasses: string[];
  stateTitle: string;
  stateClass: string;
  name: string;
  nameHref: string;
  actions: { text: string; href: string }[];
};

// Read the whole data table in one round trip.  The Approved Requests list
// has ~1600 rows, so per-row locators would be far too slow.
export async function readTable(page: Page): Promise<TableRow[]> {
  return page.locator(TABLE).evaluate((table) =>
    Array.from(table.querySelectorAll('tbody tr[data-object-id]')).map(
      (tr) => {
        const tds = Array.from(tr.querySelectorAll('td'));
        const state = tr.querySelector('td p.alloc-icon');
        // The name link: second column in the lists, first in History.
        const link = tr.querySelector('td:not(.actions_column) a');
        return {
          id: tr.getAttribute('data-object-id') ?? '',
          // innerText keeps the line break between a name and its
          // description; textContent would run them together.
          cells: tds.map((td) =>
            (td as HTMLElement).innerText.replace(/\s+/g, ' ').trim(),
          ),
          cellClasses: tds.map((td) => td.className),
          stateTitle: state?.getAttribute('title') ?? '',
          stateClass: state?.className ?? '',
          name: (link?.textContent ?? '').trim(),
          nameHref: link?.getAttribute('href') ?? '',
          actions: Array.from(
            tr.querySelectorAll('td.actions_column a.data-table-action'),
          ).map((a) => ({
            text: (a.textContent ?? '').trim(),
            href: a.getAttribute('href') ?? '',
          })),
        };
      },
    ),
  );
}

const MONTHS: Record<string, number> = {
  'Jan.': 0, 'Feb.': 1, March: 2, April: 3, May: 4, June: 5, July: 6,
  'Aug.': 7, 'Sept.': 8, 'Oct.': 9, 'Nov.': 10, 'Dec.': 11,
};

// Parse a Django 'N j, Y' date such as 'Sept. 2, 2024' or 'March 1, 2024'.
export function parseDjangoDate(text: string): Date {
  const m = text.match(/^(\S+) (\d{1,2}), (\d{4})$/);
  if (!m || !(m[1] in MONTHS)) {
    throw new Error(`not a Django date: '${text}'`);
  }
  return new Date(Number(m[3]), MONTHS[m[1]], Number(m[2]));
}
