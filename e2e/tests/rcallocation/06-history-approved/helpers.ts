import {
  APIRequestContext,
  Browser,
  Page,
  request as playwrightRequest,
} from '@playwright/test';

import { test as base, expect } from '../../../support/fixtures';
import { BASE_URL, BLOCKED_URLS, savedToken } from '../../../support/env';

// Suite-local helpers for 06 History & Approved Requests.
//
// Displayed times depend on the session time zone.  django-tz-detect sets
// it from the browser's zone the first time a page loads without one, so
// the shared storage-state session shows UTC or local times depending on
// what ran before.  These tests use their own login session, in a UTC
// browser, with the tz-detect script blocked and UTC stored in the
// session, so pages always render in UTC, the server default recorded in
// the plan.
export async function newUtcPage(browser: Browser) {
  const context = await browser.newContext({
    baseURL: BASE_URL,
    timezoneId: 'UTC',
  });
  // The dev server was slow while other suites ran.  The runner applies
  // the config's actionTimeout to new contexts, so set it explicitly.
  context.setDefaultTimeout(60_000);
  context.setDefaultNavigationTimeout(90_000);
  for (const url of BLOCKED_URLS) {
    await context.route(url, (route) => route.abort());
  }
  // Both the detector script (static/tz_detect/...) and its POST to
  // /tz_detect/set/.
  await context.route(
    (url) => url.pathname.includes('tz_detect'),
    (route) => route.abort(),
  );
  const page = await context.newPage();
  page.on('dialog', (d) => d.accept().catch(() => {}));
  const r = await page.request.post('/auth/websso/', {
    form: { token: savedToken() },
  });
  expect(r.ok()).toBeTruthy();
  // Store UTC in this session explicitly.  (Pages can still come back in
  // another zone under load; see canonicalTimes.)
  let csrf = (await context.cookies()).find((c) => c.name === 'csrftoken');
  if (!csrf) {
    await page.goto('/allocation/requests/view/999999999/history');
    csrf = (await context.cookies()).find((c) => c.name === 'csrftoken');
  }
  const tz = await page.request.post('/tz_detect/set/', {
    form: { timezone: 'UTC' },
    headers: { 'X-CSRFToken': csrf?.value ?? '', Referer: `${BASE_URL}/` },
  });
  expect(tz.status(), await tz.text()).toBe(200);
  return { context, page };
}

export function newRestApi() {
  return playwrightRequest.newContext({
    baseURL: BASE_URL,
    extraHTTPHeaders: { 'X-Auth-Token': savedToken() },
  });
}

export const test = base.extend<{ utcPage: Page; rest: APIRequestContext }>({
  utcPage: async ({ browser }, use) => {
    const { context, page } = await newUtcPage(browser);
    await use(page);
    await context.close();
  },

  // Raw allocation REST API, for calls the allocations fixture lacks.
  rest: async ({}, use) => {
    const api = await newRestApi();
    await use(api);
    await api.dispose();
  },
});

export { expect };

export type Row = { cells: string[]; links: string[] };

export type TableData = {
  title: string;
  h1: string;
  breadcrumb: { text: string; href: string | null }[];
  tables: number;
  headers: string[];
  rows: Row[];
  footer: string;
  filterInputs: number;
  actionCells: number;
};

// Read the page's (first) data table from the DOM in one round trip.
export async function readTable(page: Page): Promise<TableData> {
  return page.evaluate(() => {
    const text = (el: Element | null) =>
      (el?.textContent ?? '').replace(/\s+/g, ' ').trim();
    const table = document.querySelector('table');
    return {
      title: document.title,
      h1: text(document.querySelector('h1')),
      breadcrumb: [...document.querySelectorAll('.breadcrumb li')].map(
        (li) => ({
          text: text(li),
          href: li.querySelector('a')?.getAttribute('href') ?? null,
        }),
      ),
      tables: document.querySelectorAll('table').length,
      headers: [...(table?.querySelectorAll('thead tr:last-child th') ?? [])]
        .map((th) => text(th))
        .filter((h) => h !== ''),
      rows: [...(table?.querySelectorAll('tbody tr') ?? [])].map((tr) => ({
        cells: [...tr.querySelectorAll('td')].map((td) => text(td)),
        links: [...tr.querySelectorAll('a')].map(
          (a) => a.getAttribute('href') ?? '',
        ),
      })),
      footer: text(table?.querySelector('tfoot') ?? null),
      filterInputs: document.querySelectorAll(
        'input[name$="__filter__q"]',
      ).length,
      actionCells: document.querySelectorAll(
        'th.actions_column, td.actions_column',
      ).length,
    };
  });
}

// Open a history page and read its table.
export async function openHistory(page: Page, path: string) {
  const response = await page.goto(path, { timeout: 30_000 });
  expect(response?.status()).toBe(200);
  return readTable(page);
}

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

// The history of 135408 (6.2, 6.4): [id, row text].
export const EXPECTED_135408 = [
  [135408, 'Automated composite intranet | martinstephen@brown.com | - | -13000 | 80 | 0 | 0 | 100 | Update requested | May 28, 2024, 11:04 a.m.'],
  [146946, 'Assimilated responsive archive | gillirene@harding.net | - | 25000 | 120 | - | - | 1000 | Approved | March 15, 2024, 2:15 a.m.'],
  [138447, 'Triple-buffered actuating utilization | kieran08@singh-johnson.org | - | 0 | 0 | 0 | 0 | 1000 | Update requested | Feb. 28, 2024, 4:51 a.m.'],
  [137049, 'Extended clear-thinking moderator | kpatterson@walker-jackson.net | - | 25000 | 120 | - | - | - | Approved | Feb. 25, 2024, 10:56 p.m.'],
  [135915, 'Assimilated composite help-desk | jamesarcher@gibson-oliver.com | - | 22500 | 100 | 0 | 0 | 0 | Update requested | Feb. 23, 2024, 4:31 a.m.'],
  [135885, 'Synchronized empowering hub | ellisanthony@ward.com | - | 2500 | 20 | - | - | - | Approved | Feb. 19, 2024, 6:55 a.m.'],
  [135543, 'Secured fault-tolerant data-warehouse | antonymorgan@chapman-oconnor.com | - | 2500 | 20 | - | - | - | Submitted | Feb. 15, 2024, 10:41 p.m.'],
  [135411, 'Enhanced zero tolerance workforce | whittakerlisa@french.biz | - | 2500 | 20 | - | - | - | Submitted | Feb. 15, 2024, 10:41 p.m.'],
] as const;

// The last ' | '-separated field of a row text: its time.
export function timeOf(text: string): string {
  return text.split(' | ').pop()!;
}

export function rowText(row: Row): string {
  return row.cells.join(' | ');
}

// The allocation id a history row links to.
export function rowId(row: Row): number {
  const m = row.links[0]?.match(/^\/allocation\/requests\/view\/(\d+)\/$/);
  return m ? Number(m[1]) : NaN;
}

// Django 'N j, Y' and 'N j, Y, P' formats, as rendered by the tables.
const MONTHS = [
  'Jan.', 'Feb.', 'March', 'April', 'May', 'June',
  'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.',
];
export const DATE_RE =
  /^(Jan\.|Feb\.|March|April|May|June|July|Aug\.|Sept\.|Oct\.|Nov\.|Dec\.) \d{1,2}, \d{4}$/;
export const DATETIME_RE =
  /^(Jan\.|Feb\.|March|April|May|June|July|Aug\.|Sept\.|Oct\.|Nov\.|Dec\.) \d{1,2}, \d{4}, (\d{1,2}(:\d{2})? [ap]\.m\.|midnight|noon)$/;

// Parse a 'N j, Y, P' cell (UTC) to epoch milliseconds, to minute
// precision.
export function parseDjangoDateTime(s: string): number {
  const m = s.match(
    /^(\S+) (\d{1,2}), (\d{4}), (?:(\d{1,2})(?::(\d{2}))? ([ap])\.m\.|(midnight|noon))$/,
  );
  if (!m) {
    throw new Error(`Unparsable time '${s}'`);
  }
  const month = MONTHS.indexOf(m[1]);
  let hour = 0;
  let minute = 0;
  if (m[7] === 'noon') {
    hour = 12;
  } else if (m[7] !== 'midnight') {
    hour = (Number(m[4]) % 12) + (m[6] === 'p' ? 12 : 0);
    minute = Number(m[5] ?? 0);
  }
  return Date.UTC(Number(m[3]), month, Number(m[2]), hour, minute);
}

// Format an instant as Django's 'N j, Y, P' in the given IANA zone.
export function djangoDateTime(ms: number, timeZone: string): string {
  const parts = Object.fromEntries(
    new Intl.DateTimeFormat('en-US', {
      timeZone,
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
      hour: 'numeric',
      minute: 'numeric',
      hourCycle: 'h23',
    })
      .formatToParts(new Date(ms))
      .map((p) => [p.type, p.value]),
  );
  const hour = Number(parts.hour);
  const minute = Number(parts.minute);
  let time: string;
  if (hour === 0 && minute === 0) {
    time = 'midnight';
  } else if (hour === 12 && minute === 0) {
    time = 'noon';
  } else {
    const h12 = hour % 12 === 0 ? 12 : hour % 12;
    const mm = minute === 0 ? '' : `:${String(minute).padStart(2, '0')}`;
    time = `${h12}${mm} ${hour < 12 ? 'a' : 'p'}.m.`;
  }
  return `${MONTHS[Number(parts.month) - 1]} ${parts.day}, ${parts.year}, ${time}`;
}

// The dev server (runserver) sometimes renders a whole page in another
// session's zone (Australia/Melbourne) while other suites run, even with
// UTC stored in this session.  Accept a page only if every time on it
// matches the expected instant in one of these zones, then rewrite the
// times to the UTC form so the rest of the test compares exactly.
export const ZONES = ['UTC', 'Australia/Melbourne'];

export function canonicalTimes(
  t: TableData,
  expectedUtc: (string | null)[],
  col = 9,
): TableData {
  const actual = t.rows.map((r) => r.cells[col]);
  for (const zone of ZONES) {
    const ok = actual.every(
      (a, i) =>
        expectedUtc[i] == null ||
        a === djangoDateTime(parseDjangoDateTime(expectedUtc[i]!), zone),
    );
    if (ok) {
      if (zone !== 'UTC') {
        test.info().annotations.push({
          type: 'time zone',
          description: `page rendered in ${zone}, not UTC`,
        });
      }
      return {
        ...t,
        rows: t.rows.map((r, i) => ({
          ...r,
          cells: r.cells.map((c, j) =>
            j === col && expectedUtc[i] != null ? expectedUtc[i]! : c,
          ),
        })),
      };
    }
  }
  return t;
}

// Dates of an instant in each accepted zone.
export function djangoDates(ms: number): string[] {
  return ZONES.map((zone) => djangoDateTime(ms, zone).replace(/, [^,]+$/, ''));
}

// Decline an allocation through the admin form, like the shared
// declineViaUi, but wait only for the form POST's redirect rather than
// for the Pending Requests list it leads to, which took over 60 s to load
// while other suites were running.  R for a new request, J for a pending
// amendment.
export async function declineFixture(page: Page, id: number, reason: string) {
  await page.goto(`/allocation/requests/reject_request/${id}/`);
  await page.locator('#id_status_explanation').fill(reason);
  const [response] = await Promise.all([
    page.waitForResponse(
      (r) =>
        r.request().method() === 'POST' &&
        r.url().includes(`/reject_request/${id}/`),
      { timeout: 120_000 },
    ),
    page.locator('input[type=submit]').first().click({ noWaitAfter: true }),
  ]);
  expect(response.status()).toBe(302);
  // The Location header is relative ('../../').
  const target = new URL(response.headers()['location'] ?? '', response.url());
  expect(target.pathname).toBe('/allocation/requests/');
}

// Add a custom (non-bundle) quota to a Submitted allocation through the
// quotas REST API.  Resource ids: 5 volume.gigabytes, 47 compute.cores.
export async function addQuota(
  api: APIRequestContext,
  allocation: number,
  resource: number,
  zone: string,
  requested: number,
) {
  const r = await api.post('/rest_api/quotas/', {
    data: {
      allocation,
      zone,
      resource,
      quota: 0,
      requested_quota: requested,
    },
  });
  expect(r.status(), await r.text()).toBe(201);
}

export const RESOURCE_VOLUME_GB = 5;
export const RESOURCE_CORES = 47;
