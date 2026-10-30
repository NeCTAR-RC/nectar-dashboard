import { test, expect } from '../../../support/fixtures';
import { declineViaUi } from '../../../support/allocations';

// Sanity checks for the allocation fixtures the other suites rely on.
test.describe('Allocation fixtures', () => {
  test('create, approve, amend and decline fresh allocations', async ({
    page,
    allocations,
  }) => {
    const submitted = await allocations.create();
    expect(submitted.status).toBe('E');
    expect(submitted.project_name).toMatch(/^pwtest-/);

    const pending = await allocations.createAmendmentPending();
    expect(pending.status).toBe('X');
    const history = await allocations.history(pending.id);
    expect(history.map((h) => h.status).sort()).toEqual(['A', 'E']);

    await declineViaUi(page, submitted.id, 'Playwright fixture decline');
    expect((await allocations.get(submitted.id)).status).toBe('R');

    await declineViaUi(page, pending.id, 'Playwright fixture decline');
    expect((await allocations.get(pending.id)).status).toBe('J');

    await page.goto('/allocation/user_requests/');
    await expect(page.getByRole('link', { name: submitted.project_name })).toBeVisible();
  });
});
