import { test, expect } from '../../../support/fixtures';
import { acceptDialogsOnce } from './helpers';

test.beforeEach(({ page }) => acceptDialogsOnce(page));

test.describe('Navigation & permissions: external links', () => {
  // Hrefs only: never follow links off the dashboard.
  test('1.18 External links on allocation pages (record only, never follow)', async ({
    page,
  }) => {
    await page.goto('/allocation/');

    // Match on text, not accessible name: Font Awesome icons inside some
    // links add a glyph to the accessible name.
    const hrefOf = (text: string) =>
      page.locator('a', { hasText: text }).first();

    await expect(hrefOf('Learn more about project trials')).toHaveAttribute(
      'href',
      'https://support.ehelp.edu.au/support/solutions/articles/' +
        '6000171494-project-allocation-expiry-and-renewal#pt',
    );
    await expect(hrefOf('eligibility criteria')).toHaveAttribute(
      'href',
      'https://support.ehelp.edu.au/support/solutions/articles/6000226889',
    );
    await expect(hrefOf('create a support ticket')).toHaveAttribute(
      'href',
      'https://support.ehelp.edu.au/support/tickets/new',
    );
    await expect(page.getByRole('link', { name: 'View ORCID record' })).toHaveAttribute(
      'href',
      'https://sandbox.orcid.org/0009-0006-2369-9936',
    );
    await expect(hrefOf('orcid.org')).toHaveAttribute(
      'href',
      'https://sandbox.orcid.org',
    );
    await expect(hrefOf('Eligibility Assessment Tool')).toHaveAttribute(
      'href',
      'https://eligibility.rc.nectar.org.au/',
    );
    await expect(hrefOf('Sensitive Data Guidelines')).toHaveAttribute(
      'href',
      'https://support.ehelp.edu.au/support/solutions/articles/6000277743',
    );

    // Footer links.
    const hrefs = await page
      .locator('a[href]')
      .evaluateAll((as) => as.map((a) => a.getAttribute('href') ?? ''));
    for (const prefix of [
      'https://dashboard.rc.nectar.org.au/',
      'https://status.rc.nectar.org.au/',
      'https://tutorials.rc.nectar.org.au/',
      'https://ardc.edu.au/',
    ]) {
      expect(
        hrefs.some((h) => h.startsWith(prefix)),
        `a link to ${prefix}`,
      ).toBe(true);
    }

    // The survey ('Start survey', https://www.surveymonkey.com/r/YGWYNMB)
    // is injected by survey.rc.nectar.org.au, which the shared fixtures
    // block, so it is not asserted here.  The Freshdesk 'Related tickets'
    // and Grafana 'Project usage' links on detail pages are not covered by
    // the plan.
  });
});
