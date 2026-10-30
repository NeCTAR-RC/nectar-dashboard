import { test, expect } from '../../../support/fixtures';
import {
  NOTES_TITLE,
  contentHeadings,
  detail,
  formControls,
  gotoDetail,
  TEST_TIMEOUT,
} from './helpers';

// Suite 05: the admin notes form.  Read-only apart from the fixture.
test.describe('Admin notes form', () => {
  test('5.1 Edit admin notes form structure', async ({ page, allocations }) => {
    test.setTimeout(TEST_TIMEOUT);
    const e = await allocations.create();
    const url = `/allocation/requests/edit_notes/${e.id}/`;

    await gotoDetail(page, e.id);
    const link = detail(page).getByRole('link', { name: 'Add/edit admin notes' });
    await expect(link).toHaveAttribute('href', url);
    await link.click();

    await expect(page).toHaveURL(url);
    await expect(page).toHaveTitle(NOTES_TITLE);
    // An empty h1 and no other heading.
    await expect(page.locator('h1')).toHaveText(['']);
    await expect(contentHeadings(page)).toHaveCount(0);
    await expect(page.locator('.breadcrumb li')).toHaveText([
      'Allocations',
      'Pending Requests',
      'None',
    ]);
    await expect(
      page.locator('.breadcrumb li').getByRole('link', { name: 'Pending Requests' }),
    ).toHaveAttribute('href', '/allocation/requests/');

    const form = page.locator('form#new-allocation');
    await expect(form).toHaveAttribute('action', url);
    await expect(form).toHaveAttribute('method', 'post');

    expect(await formControls(page)).toEqual([
      expect.objectContaining({ type: 'hidden', name: 'csrfmiddlewaretoken' }),
      {
        tag: 'textarea',
        type: 'textarea',
        name: 'notes',
        id: 'id_notes',
        value: '',
        required: false,
        readOnly: false,
        disabled: false,
        label: 'Private notes for admins',
        // The plan saw no help; the popover is there.
        help: 'These notes are only visible to allocation admins',
      },
      expect.objectContaining({ type: 'submit', name: '', value: 'Submit' }),
    ]);
    await expect(page.locator('#id_notes-group .glyphicon-asterisk')).toHaveCount(0);
    await expect(form.getByRole('link', { name: 'Cancel' })).toHaveCount(0);
    await expect(form.locator('a')).toHaveCount(0);
  });
});
