import { Page } from '@playwright/test';

import { test, expect } from '../../../support/fixtures';
import { uniqueProjectName } from '../../../support/allocations';
import {
  CREATE_TIMEOUT,
  acceptDialogsOnce,
  byId,
  expandPanel,
  idFromHref,
  openForm,
  possibleDates,
  select2Pick,
  submit,
} from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

const MY_REQUESTS_TITLE = 'Allocation Requests - Nectar Dashboard';

async function rowCells(page: Page, href: string): Promise<string[]> {
  return page
    .locator('table tbody tr', { has: page.locator(`a[href="${href}"]`) })
    .locator('td')
    .evaluateAll((tds) =>
      tds.map((td) => (td as HTMLElement).innerText.replace(/\s+/g, ' ').trim()),
    );
}

test.describe('New Request form: successful submit', () => {
  // Creates one Submitted (E) pwtest- allocation.  The dev server is
  // shared and slow, and this test loads three pages after the submit.
  test.setTimeout(600_000);
  test('S1 Successful submit, redirect, My Requests row, detail page and Pending Requests', async ({
    page,
    allocations,
  }) => {
    const name = uniqueProjectName('s1');
    const title = 'PW S1 submit test';
    await openForm(page);
    const contact = await byId(page, 'id_contact_email').inputValue();

    // Fill the whole form through the UI.
    await expandPanel(page, 'panelOne');
    await byId(page, 'id_project_description').fill(title);
    await byId(page, 'id_project_name').pressSequentially(name);
    await expect(byId(page, 'id_dns_domain')).toHaveValue(`${name}.cloud.edu.au`);

    await expandPanel(page, 'panelTwo');
    await byId(page, 'id_direct_access_user_estimate').fill('1');
    await byId(page, 'id_estimated_service_count').fill('1');
    await byId(page, 'id_estimated_service_active_users').fill('1');
    await byId(page, 'id_use_case').fill('Playwright S1 baseline');
    await byId(page, 'id_has_sensitive_data').selectOption('no_sensitive');
    // The classification is forced to Green and locked.
    await expect(byId(page, 'id_data_classification_level')).toHaveValue('green');

    await expandPanel(page, 'panelThree');
    await select2Pick(page, 'id_field_of_research_1', '4601', '4601 Applied computing');
    await expect(byId(page, 'id_field_of_research_1')).toHaveValue('4601');

    await expandPanel(page, 'panelFour');
    await select2Pick(page, 'id_supported_organisations', 'Monash University', 'Monash University (AU)');
    await expect(byId(page, 'id_supported_organisations')).toHaveValue('5');

    await expandPanel(page, 'panelFive');
    await byId(page, 'id_investigators-0-title').fill('Dr');
    await byId(page, 'id_investigators-0-given_name').fill('Pw');
    await byId(page, 'id_investigators-0-surname').fill('Tester');
    await byId(page, 'id_investigators-0-email').fill('pw@example.edu.au');
    await select2Pick(
      page,
      'id_investigators-0-primary_organisation',
      'Monash University',
      'Monash University (AU)',
    );
    await expect(byId(page, 'id_investigators-0-primary_organisation')).toHaveValue('5');

    await expandPanel(page, 'panelSeven');
    await byId(page, 'id_grants-0-grant_type').selectOption('inst');
    // Grant types without subtypes force 'unspecified' and hide the field.
    await expect(byId(page, 'id_grants-0-grant_subtype')).toHaveValue('unspecified');
    await expect(byId(page, 'id_grants-0-grant_subtype-group')).toBeHidden();
    await byId(page, 'id_grants-0-funding_body_scheme').fill('Uni fund');
    await byId(page, 'id_grants-0-total_funding').fill('1000');

    // Step 2: keep the default Standard bundle.
    await expandPanel(page, 'panelBundle');
    await expect(byId(page, 'id_bundle')).toHaveValue('3');
    await expandPanel(page, 'panelJustification');
    await byId(page, 'id_usage_patterns').fill('x');
    await page
      .locator('label.checkbox-inline', { hasText: 'Hosting services to support research' })
      .locator('input')
      .check();

    // No confirmation modal: Submit posts straight away and redirects.
    const submittedAt = new Date();
    await submit(page, CREATE_TIMEOUT);
    await expect(page).toHaveURL(/\/allocation\/user_requests\/$/);
    await expect(page).toHaveTitle(MY_REQUESTS_TITLE);
    await expect(page.locator('.modal.in')).toHaveCount(0);

    const nameLink = page.locator('table tbody a', { hasText: name });
    await expect(nameLink).toHaveCount(1);
    const id = idFromHref(await nameLink.getAttribute('href'));
    const viewHref = `/allocation/user_requests/view/${id}/`;
    await expect(nameLink).toHaveAttribute('href', viewHref);

    // The REST API agrees.
    const created = await allocations.get(id);
    expect(created.project_name).toBe(name);
    expect(created.status).toBe('E');
    expect(created.contact_email).toBe(contact);

    // My Requests.
    await expect(page.locator('table thead th')).toHaveText([
      'State',
      'Name',
      'Current Associated Site',
      'National',
      'Contact',
      'Last Updated',
      'Expiry Date',
      'Actions',
    ]);
    const cells = await rowCells(page, viewHref);
    expect(cells.slice(0, 5)).toEqual(['E', `${name} ${title}`, '-', 'False', contact]);
    expect(possibleDates(submittedAt)).toContain(cells[5]);
    expect(cells.slice(6)).toEqual(['-', 'Edit request']);
    const row = page.locator('table tbody tr', { has: page.locator(`a[href="${viewHref}"]`) });
    await expect(row.locator('td').first().locator('b, strong')).toHaveText('E');
    const actions = row.locator('td.actions_column a');
    await expect(actions).toHaveText(['Edit request']);
    await expect(actions).toHaveAttribute('href', `/allocation/user_requests/edit_request/${id}/`);

    // The detail page.
    await page.goto(viewHref);
    await expect(page).toHaveTitle('View allocation request - Nectar Dashboard');
    const detail = page.locator('.allocation');
    // The title is an H2.
    await expect(detail.locator('h2').first()).toHaveText(title);
    await expect(detail).toContainText('State Submitted');
    await expect(detail).toContainText(`Project Identifier ${name}`);
    await expect(detail).toContainText('Project ID (Project not linked)');
    const headings = await detail
      .locator('h3, h4')
      .evaluateAll((hs) => hs.map((h) => (h.textContent ?? '').replace(/\s+/g, ' ').trim()));
    expect(headings).toEqual(
      expect.arrayContaining([
        'Requested Resources',
        'Approved Resources (at the time of this record)',
        'Use Case',
        'Usage Patterns',
        'Additional Location Requirements',
        'Usage Types',
        'Usage Information',
        'Data Sensitivity Information',
        'Fields of Research (FOR)',
        'Supported Organisations',
        'Chief Investigator',
        'Research Grant Information',
        'ARDC (or ANDS, Nectar, or RDS) funded projects supporting this request:',
        'NCRIS Facilities supporting this request:',
        'Publication/Output and Impact',
      ]),
    );
    const buttons = detail.locator('a.btn');
    await expect(buttons).toHaveText(['Edit request']);
    await expect(buttons).toHaveAttribute('href', `/allocation/user_requests/edit_request/${id}/`);

    // Pending Requests.
    await page.goto('/allocation/requests/');
    await expect(page.locator('table thead th')).toHaveText([
      'State',
      'Name',
      'Current Associated Site',
      'National',
      'Previous Approver',
      'Contact',
      'Last Updated',
      'Expiry Date',
      'Urgency',
      'Actions',
    ]);
    const pendingHref = `/allocation/requests/view/${id}/`;
    const pending = await rowCells(page, pendingHref);
    expect(pending.slice(0, 6)).toEqual(['E', `${name} ${title}`, '-', 'False', '', contact]);
    expect(possibleDates(submittedAt)).toContain(pending[6]);
    expect(pending.slice(7, 9)).toEqual(['-', '(New)']);
    const pendingRow = page.locator('table tbody tr', {
      has: page.locator(`a[href="${pendingHref}"]`),
    });
    // The actions cell also holds an (empty) drop-down toggle link.
    const pendingActions = pendingRow.locator('td.actions_column a.data-table-action');
    await expect(pendingActions).toHaveText(['Edit request', 'View history']);
    expect(
      await pendingActions.evaluateAll((as) => as.map((a) => a.getAttribute('href'))),
    ).toEqual([`/allocation/requests/edit_request/${id}/`, `/allocation/requests/view/${id}/history`]);
  });
});
