import { test, expect } from '../../../support/fixtures';

// 6.10 approved_requests/edit_request GET for an A record: an existing
// HTTP 500.  Nothing is submitted.  page.request is used so the 500 does
// not fail a navigation.
function pageText(html: string): string {
  return html
    .replace(/<[^>]+>/g, ' ')
    .replace(/&amp;/g, '&')
    .replace(/&#x27;|&#39;/g, "'")
    .replace(/&quot;/g, '"')
    .replace(/\s+/g, ' ');
}

test.describe('6.10 approved_requests/edit_request for an A record', () => {
  test('6.10 GET edit_request/98355 returns the existing TypeError 500', async ({
    page,
  }) => {
    const path = '/allocation/approved_requests/edit_request/98355/';
    const r = await page.request.get(path, { timeout: 20_000 });

    expect(r.status()).toBe(500);
    const html = await r.text();
    const title = html.match(/<title>([\s\S]*?)<\/title>/)?.[1] ?? '';
    expect(title.replace(/\s+/g, ' ').trim()).toBe(`TypeError at ${path}`);

    const text = pageText(html);
    expect(text).toContain('Exception Type: TypeError');
    expect(text).toContain("'NoneType' object is not callable");
    expect(text).toMatch(
      /Exception Location: \S*django\/views\/generic\/edit\.py , line \d+, in get_form/,
    );
    expect(text).toContain(
      'Raised during: nectar_dashboard.rcallocation.allocation.views.AllocationUpdateView',
    );

    // The plan also recorded line 39, Django 4.2.19 and Python 3.12.3.
    // Those track the platform rather than this UI, so they are recorded
    // as annotations instead of asserted.
    for (const [key, re] of [
      ['line', /generic\/edit\.py , line (\d+)/],
      ['Django', /Django Version: (\S+)/],
      ['Python', /Python Version: (\S+)/],
    ] as const) {
      test.info().annotations.push({
        type: key,
        description: text.match(re)?.[1] ?? 'not found',
      });
    }
  });
});
