import { Page, Response } from '@playwright/test';

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
// alone and well over the default 90 s navigation timeout while other
// suites load the dev server, so allow longer.
export const APPROVED_LOAD_TIMEOUT = 240_000;

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
