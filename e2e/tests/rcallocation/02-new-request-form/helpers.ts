import { Locator, Page } from '@playwright/test';

import { expect } from '../../../support/fixtures';
import { uniqueProjectName } from '../../../support/allocations';

// Local helpers for suite 02 (New Request form).  Kept here rather than in
// e2e/support so the shared files stay untouched.

export const FORM_URL = '/allocation/';
export const FORM_TITLE = 'Allocation Request - Nectar Dashboard';
export const FIX_ERRORS = 'Please fix the errors highlighted below and resubmit.';

// The shared fixtures register two 'dialog' handlers on each page, and the
// second accept() of a beforeunload dialog throws "Cannot accept dialog
// which is already handled!".  Replace both with one tolerant handler.
export function acceptDialogsOnce(page: Page): void {
  page.removeAllListeners('dialog');
  page.on('dialog', (d) => {
    d.accept().catch(() => {});
  });
}

// Open a fresh New Request form and wait until its scripts have run
// (select2 has built its containers and form-nav has opened panel 1).
export async function openForm(page: Page): Promise<void> {
  await page.goto(FORM_URL);
  await expect(page).toHaveTitle(FORM_TITLE);
  await expect(page.locator('#s2id_id_supported_organisations')).toBeAttached();
  await expect(page.locator('#panelOne')).toBeVisible();
}

const STEP2_PANELS = [
  'panelBundle',
  'panelExtras',
  'panelJustification',
  'panelSubmit',
];

// Show 'STEP 1: About the project' or 'STEP 2: Cloud resources'.
export async function showStep(page: Page, step: 1 | 2): Promise<void> {
  const section = page.locator(`section#form-step${step}`);
  if (!(await section.isVisible())) {
    await page.locator(`#allocation_form_nav a[href="#form-step${step}"]`).click();
  }
  await expect(section).toBeVisible();
}

// Expand an accordion panel (and its step) so its fields can be used.
// Bootstrap ignores a collapse click while another panel is still
// animating, so retry the click until the panel is fully open.
export async function expandPanel(page: Page, panelId: string): Promise<Locator> {
  await showStep(page, STEP2_PANELS.includes(panelId) ? 2 : 1);
  const panel = page.locator(`#${panelId}`);
  const header = page
    .locator(`.panel-heading a[href="#${panelId}"]`)
    .filter({ visible: true });
  await expect(async () => {
    if (!(await panel.isVisible())) {
      await header.click();
    }
    await expect(panel).toHaveClass(/\bin\b/, { timeout: 2_000 });
    await expect(panel).not.toHaveClass(/collapsing/, { timeout: 2_000 });
  }).toPass({ timeout: 30_000 });
  return panel;
}

export function byId(page: Page, id: string): Locator {
  return page.locator(`[id="${id}"]`);
}

// The help-block errors rendered for the field with the given element id.
export function fieldErrors(page: Page, id: string): Locator {
  return byId(page, id)
    .first()
    .locator(
      'xpath=ancestor::div[contains(concat(" ", normalize-space(@class), " "), " form-group ")][1]',
    )
    .locator('.help-block');
}

// Every server-rendered error on the form, keyed by field name.  The FoR
// errors that clean() raises have no field and are keyed 'FOR'.
export async function errorMap(page: Page): Promise<Record<string, string[]>> {
  return page.locator('#new-allocation').evaluate((form) => {
    const out: Record<string, string[]> = {};
    for (const g of Array.from(form.querySelectorAll('.has-error'))) {
      let key: string;
      if (g.id.endsWith('-group')) {
        key = g.id.replace(/^id_/, '').replace(/-group$/, '');
      } else {
        const named = g.querySelector('[name]');
        key = named ? named.getAttribute('name')! : 'FOR';
      }
      const texts = Array.from(g.querySelectorAll('.help-block')).map((b) =>
        (b.textContent ?? '').replace(/\s+/g, ' ').trim(),
      );
      out[key] = [...(out[key] ?? []), ...texts];
    }
    return out;
  });
}

// Ids of the open accordion panels of one step.
export async function openPanels(page: Page, accordion: string): Promise<string[]> {
  return page
    .locator(`#${accordion} .request-collapse.in`)
    .evaluateAll((els) => els.map((e) => e.id));
}

type FieldValue = string | string[] | boolean;

// Set form values directly by field name, without the UI.  Used by the
// validation scenarios, which test the server-side checks rather than the
// widgets.  Strings set inputs and selects; string arrays select options
// of a multi-select or tick the matching checkboxes; booleans tick a
// single checkbox.  The select2 fields are hidden inputs holding ids
// ('5', '314402,5', '4601').  data_classification_level has a visible
// select and a hidden twin of the same name: both are set.
export async function fillForm(
  page: Page,
  values: Record<string, FieldValue>,
): Promise<void> {
  await page.locator('#new-allocation').evaluate((form, values) => {
    for (const [name, value] of Object.entries(values)) {
      const els = Array.from(
        form.querySelectorAll(`[name="${CSS.escape(name)}"]`),
      ) as (HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement)[];
      if (!els.length) {
        throw new Error(`no form field named ${name}`);
      }
      for (const el of els) {
        if (el instanceof HTMLSelectElement) {
          const wanted = Array.isArray(value) ? value : [String(value)];
          for (const o of Array.from(el.options)) {
            o.selected = wanted.includes(o.value);
          }
          if (!el.multiple && el.value !== wanted[0]) {
            throw new Error(`${name} has no option ${wanted[0]}`);
          }
        } else if (el instanceof HTMLInputElement && el.type === 'checkbox') {
          el.checked = Array.isArray(value)
            ? value.includes(el.value)
            : Boolean(value);
        } else {
          el.value = Array.isArray(value) ? value.join(',') : String(value);
        }
      }
    }
  }, values);
}

// The valid baseline from the plan, minus the project identifier.
export const BASELINE: Record<string, FieldValue> = {
  project_description: 'PW validation test',
  use_case: 'Playwright validation baseline',
  direct_access_user_estimate: '1',
  estimated_service_count: '1',
  estimated_service_active_users: '1',
  has_sensitive_data: 'no_sensitive',
  data_classification_level: 'green',
  field_of_research_1: '4601',
  for_percentage_1: '100',
  supported_organisations: '5',
  'investigators-0-title': 'Dr',
  'investigators-0-given_name': 'Pw',
  'investigators-0-surname': 'Tester',
  'investigators-0-email': 'pw@example.edu.au',
  'investigators-0-primary_organisation': '5',
  'grants-0-grant_type': 'inst',
  'grants-0-grant_subtype': 'unspecified',
  'grants-0-funding_body_scheme': 'Uni fund',
  'grants-0-total_funding': '1000',
  usage_types: ['Hosting services to support research'],
  usage_patterns: 'x',
};

// Fill the baseline plus overrides.  The identifier defaults to a fresh
// pwtest- name, so a scenario that unexpectedly passes validation still
// creates a test allocation the cleanup script will find.
export async function fillBaseline(
  page: Page,
  overrides: Record<string, FieldValue> = {},
  tag = 'v',
): Promise<void> {
  await fillForm(page, {
    project_name: uniqueProjectName(tag),
    ...BASELINE,
    ...overrides,
  });
}

// Click a submit-section button and wait for the next document.  The form
// re-renders at the same URL on failure, so wait for the main frame to
// commit a new document rather than for a URL change.
//
// A submit that creates an allocation answers only after the server has
// saved it and sent the notifications, which took over 90 s on the shared
// dev server, so those submits pass a longer timeout.
export const CREATE_TIMEOUT = 300_000;

export async function submitWith(
  page: Page,
  button: Locator,
  timeout = 90_000,
): Promise<void> {
  const navigated = page.waitForEvent('framenavigated', {
    predicate: (f) => f === page.mainFrame(),
    timeout,
  });
  // Creating an allocation can take longer than the action timeout, so
  // don't let the click itself wait for the navigation.
  await button.click({ noWaitAfter: true });
  await navigated;
  await page.waitForLoadState('domcontentloaded');
}

export function submitButton(page: Page): Locator {
  return page.locator('#submit-section input[type=submit][value="Submit"]');
}

export function ignoreWarningsButton(page: Page): Locator {
  return page.locator('#submit-section input[value="Submit ignoring warnings"]');
}

export async function submit(page: Page, timeout?: number): Promise<void> {
  await submitWith(page, submitButton(page), timeout);
}

// Submit a form that must fail validation, and check it came back with
// the error alert.
export async function submitExpectingErrors(page: Page): Promise<void> {
  await submit(page);
  await expect(page).toHaveURL(FORM_URL);
  await expect(page.locator('.alert-danger', { hasText: FIX_ERRORS })).toBeVisible();
}

// Pick a select2 (v3) option by typing into its search box.  Multi-value
// widgets search inline; single-value widgets open a drop-down with its
// own search input.
export async function select2Pick(
  page: Page,
  fieldId: string,
  query: string,
  label: string,
): Promise<void> {
  const container = byId(page, `s2id_${fieldId}`);
  const multi = await container.evaluate((e) =>
    e.classList.contains('select2-container-multi'),
  );
  let search: Locator;
  if (multi) {
    search = container.locator('input.select2-input');
    await search.click();
  } else {
    await container.locator('a.select2-choice').click();
    search = openDrop(page).locator('input.select2-input');
  }
  await search.pressSequentially(query);
  await openDrop(page)
    .locator('.select2-result-label')
    .filter({ hasText: new RegExp(`^\\s*${escapeRegExp(label)}\\s*$`) })
    .first()
    .click();
  await expect(openDrop(page)).toHaveCount(0);
}

// The open select2 drop-down.  select2 leaves the 'select2-drop-active'
// class on a drop-down after closing it, so filter on visibility.
export function openDrop(page: Page): Locator {
  return page.locator('.select2-drop-active').filter({ visible: true });
}

export function escapeRegExp(s: string): string {
  return s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

export function normalise(text: string | null): string {
  return (text ?? '').replace(/\s+/g, ' ').trim();
}

export async function optionTexts(select: Locator): Promise<string[]> {
  return select
    .locator('option')
    .evaluateAll((os) => os.map((o) => (o.textContent ?? '').trim()));
}

export async function optionValues(select: Locator): Promise<string[]> {
  return select
    .locator('option')
    .evaluateAll((os) => os.map((o) => (o as HTMLOptionElement).value));
}

// The Django 'N j, Y' date format, as rendered by the dashboard.
const MONTHS = [
  'Jan.', 'Feb.', 'March', 'April', 'May', 'June',
  'July', 'Aug.', 'Sept.', 'Oct.', 'Nov.', 'Dec.',
];

function djangoDate(d: Date): string {
  return `${MONTHS[d.getUTCMonth()]} ${d.getUTCDate()}, ${d.getUTCFullYear()}`;
}

// The displayed time zone is not stable within a session, so accept the
// date of the given instant in any time zone from UTC-12 to UTC+14.
export function possibleDates(at: Date): string[] {
  const dates = new Set<string>();
  for (let h = -12; h <= 14; h++) {
    dates.add(djangoDate(new Date(at.getTime() + h * 3600_000)));
  }
  return [...dates];
}

// The allocation id from a '/allocation/.../<id>/' link.
export function idFromHref(href: string | null): number {
  const m = (href ?? '').match(/\/(\d+)\/$/);
  expect(m, `no allocation id in ${href}`).not.toBeNull();
  return Number(m![1]);
}

