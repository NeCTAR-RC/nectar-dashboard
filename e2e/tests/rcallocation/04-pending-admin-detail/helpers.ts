import { Locator, Page, Request } from '@playwright/test';

import { expect } from '../../../support/fixtures';
import { BASE_URL } from '../../../support/env';

// Local helpers for suite 04 (Pending Requests and admin detail).

export const PENDING_URL = '/allocation/requests/';

// Long-standing Pending records in submit_date order, as recorded live
// on 2026-10-30 (the pwtest rows of that day are left out).
export const PENDING_E = [
  137133, 137145, 145086, 144561, 145986, 147462, 146607, 149088, 150183,
  150633, 151164, 151473, 151521, 151599, 151632, 151638, 151713, 151878,
  151884, 151554, 152142, 152145,
];
export const PENDING_X = [
  135408, 58677, 62718, 84989, 38655, 145272, 123439, 135339, 129250,
];
export const PENDING_ORDER = [
  137133, 137145, 145086, 144561, 145986, 135408, 58677, 147462, 62718,
  146607, 149088, 150183, 150633, 84989, 38655, 145272, 151164, 151473,
  123439, 151521, 151599, 151632, 151638, 151713, 151878, 151884, 135339,
  151554, 152142, 152145, 129250,
];

export const DETAIL_TITLE = 'View allocation request - Nectar Dashboard';

// The Django 'N j, Y' date format, as rendered by the dashboard.
const MONTHS = [
  'Jan.', 'Feb.', 'March', 'April', 'May', 'June',
  'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.',
];

export function djangoDate(d: Date): string {
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

export function pendingTable(page: Page): Locator {
  return page.locator('#datatableoptions');
}

// The Pending list row whose Name links to the given allocation.
export function pendingRow(page: Page, id: number): Locator {
  return pendingTable(page).locator('tbody tr', {
    has: page.locator(`a[href="/allocation/requests/view/${id}/"]`),
  });
}

export async function gotoPending(page: Page) {
  await page.goto(PENDING_URL);
  await expect(pendingTable(page).locator('tbody tr').first()).toBeVisible();
}

export type PendingRow = {
  id: number;
  name: string;
  visible: boolean;
  cells: string[];
};

// Read every Pending row in DOM order.  The Name cell joins the project
// name and the description with a single space.
export async function readPendingRows(page: Page): Promise<PendingRow[]> {
  return pendingTable(page).evaluate((table) =>
    [...table.querySelectorAll('tbody tr')]
      .filter((tr) => tr.querySelector('a[href^="/allocation/requests/view/"]'))
      .map((tr) => {
        const link = tr.querySelector('td a[href^="/allocation/requests/view/"]')!;
        const tds = [...tr.querySelectorAll('td')];
        const cells = tds.map((td, i) => {
          if (i === 1) {
            const small = td.querySelector('small');
            return `${link.textContent!.trim()} ${small?.textContent!.trim() ?? ''}`.trim();
          }
          return td.textContent!.replace(/\s+/g, ' ').trim();
        });
        return {
          id: Number(link.getAttribute('href')!.match(/view\/(\d+)\//)![1]),
          name: link.textContent!.trim(),
          visible: (tr as HTMLElement).offsetParent !== null,
          cells,
        };
      }),
  );
}

// Detail page readers.
export function detail(page: Page): Locator {
  return page.locator('.allocation');
}

export async function headings(page: Page, tag: string): Promise<string[]> {
  return detail(page)
    .locator(tag)
    .evaluateAll((els) => els.map((e) => e.textContent!.replace(/\s+/g, ' ').trim()));
}

// The rows of the n-th table inside .allocation, as 'th td' text.
export async function tableRows(page: Page, n: number): Promise<string[]> {
  return detail(page)
    .locator('table')
    .nth(n)
    .locator('tr')
    .evaluateAll((trs) => trs.map((tr) => tr.textContent!.replace(/\s+/g, ' ').trim()));
}

// The resources table that follows the given h3.
export async function resourcesTable(page: Page, heading: string): Promise<string[]> {
  return detail(page)
    .locator('h3', { hasText: heading })
    .locator('xpath=following-sibling::table[1]')
    .locator('tr')
    .evaluateAll((trs) => trs.map((tr) => tr.textContent!.replace(/\s+/g, ' ').trim()));
}

export type Button = {
  text: string;
  href: string | null;
  className: string;
  id: string;
  target: string | null;
};

export async function detailButtons(page: Page): Promise<Button[]> {
  return detail(page)
    .locator('a.btn')
    .evaluateAll((as) =>
      as.map((a) => ({
        text: a.textContent!.replace(/\s+/g, ' ').trim(),
        href: a.getAttribute('href'),
        className: a.className,
        id: a.id,
        target: a.getAttribute('target'),
      })),
    );
}

export async function gotoDetail(page: Page, id: number) {
  const response = await page.goto(`/allocation/requests/view/${id}/`);
  expect(response?.status()).toBe(200);
  await expect(page).toHaveTitle(DETAIL_TITLE);
}

// The paragraph after the 'Allocation admin notes' heading.
export function adminNotes(page: Page): Locator {
  return detail(page)
    .locator('h3', { hasText: 'Allocation admin notes' })
    .locator('xpath=following-sibling::p[1]');
}

// Records every request a page makes so a test can assert it stayed
// read-only and on the dashboard.  The page chrome itself loads Google
// Fonts and the Freshworks help widget, so only main-frame navigations
// are checked for leaving the dashboard.  Every request to the dashboard
// must be a GET, except the page chrome's time zone detection
// (django-tz-detect POSTs the browser offset on every page load).
const ALLOWED_POSTS = ['/tz_detect/set/'];

export function recordRequests(page: Page) {
  const requests: Request[] = [];
  page.on('request', (r) => requests.push(r));
  return {
    requests,
    expectReadOnly() {
      const origin = new URL(BASE_URL).origin;
      const sameOrigin = (r: Request) =>
        !r.url().startsWith('data:') && new URL(r.url()).origin === origin;
      const offSite = requests
        .filter((r) => r.isNavigationRequest() && r.frame() === page.mainFrame())
        .filter((r) => !sameOrigin(r))
        .map((r) => r.url());
      expect(offSite, 'navigations that left the dashboard').toEqual([]);
      const writes = requests
        .filter((r) => sameOrigin(r) && r.method() !== 'GET')
        .filter((r) => !ALLOWED_POSTS.includes(new URL(r.url()).pathname))
        .map((r) => `${r.method()} ${r.url()}`);
      expect(writes, 'non-GET requests to the dashboard').toEqual([]);
    },
  };
}
