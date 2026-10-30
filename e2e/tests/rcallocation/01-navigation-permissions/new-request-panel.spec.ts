import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: New Request panel', () => {
  test('1.2 New Request panel renders at /allocation/ as the default panel', async ({
    page,
  }) => {
    await page.goto('/allocation/');

    await expect(
      page.getByRole('heading', {
        level: 3,
        name: 'New Allocation Request: About the Project',
      }),
    ).toBeVisible();
    await expect(
      page.getByRole('link', { name: 'All My Requests' }),
    ).toHaveAttribute('href', '/allocation/user_requests/');
    await expect(
      page.locator('p a[href="/allocation/user_requests/"]', {
        hasText: /^My Requests$/,
      }),
    ).toBeVisible();

    const steps = page.locator('a[href^="#form-step"]');
    await expect(steps).toHaveText([
      'STEP 1: About the project',
      'STEP 2: Cloud resources',
    ]);
    expect(
      await steps.evaluateAll((as) => as.map((a) => a.getAttribute('href'))),
    ).toEqual(['#form-step1', '#form-step2']);

    // Visible accordion headings of step 1.  A further panel,
    // '8. Publication/Output and Impact', exists in the markup but is
    // hidden (observed live).
    const headings = page.locator('#request_accordion .panel-heading');
    await expect(headings.filter({ visible: true })).toHaveText([
      '1. Project Details',
      '2. Usage Information',
      '3. Fields of Research (FOR)',
      '4. Supported Institutions',
      '5. Investigator',
      '6. Project Support',
      '7. Research Grant Information',
      '8. Continue',
    ]);
    await expect(
      headings.filter({ hasText: '8. Publication/Output and Impact' }),
    ).toBeHidden();

    // Project Details is the first panel; expand it if collapsed.
    const details = page.locator('#panelOne');
    if (!(await details.isVisible())) {
      await page.locator('a[href="#panelOne"]').first().click();
    }
    await expect(details).toBeVisible();

    const label = (forId: string) => page.locator(`label[for="${forId}"]`);
    await expect(label('id_project_description')).toContainText(
      'Project allocation title',
    );
    await expect(label('id_contact_email')).toContainText('Contact e-mail');
    await expect(page.locator('#id_contact_email')).toHaveValue(
      'sorrison@gmail.com',
    );
    await expect(label('id_project_name')).toContainText('Project Identifier');
    await expect(label('id_dns_domain')).toContainText(
      'Generated project DNS zone name',
    );
    await expect(page.locator('#id_dns_domain')).toBeDisabled();
    await expect(label('id_estimated_project_duration')).toContainText(
      'Estimated project duration',
    );
    const duration = page.locator('#id_estimated_project_duration');
    await expect(duration.locator('option')).toHaveText([
      '1-month',
      '3-months',
      '6-months',
      '12-months',
    ]);
    await expect(duration).toHaveValue('12');
    await expect(label('id_convert_trial_project')).toContainText(
      'Convert trial project?',
    );

    // Required fields carry an asterisk glyph in the label ('*' in the
    // plan).
    const asterisk = (forId: string) =>
      label(forId).locator('span.glyphicon-asterisk');
    for (const id of [
      'id_project_description',
      'id_project_name',
      'id_estimated_project_duration',
    ]) {
      await expect(asterisk(id), id).toHaveCount(1);
    }
    for (const id of [
      'id_contact_email',
      'id_dns_domain',
      'id_convert_trial_project',
    ]) {
      await expect(asterisk(id), id).toHaveCount(0);
    }

    // The submit button exists. Never click it.
    await expect(
      page.getByText('Are you ready to submit this allocation request?'),
    ).toHaveCount(1);
    await expect(
      page.locator('input[type=submit][value="Submit"]'),
    ).toHaveCount(1);
  });
});
