import { test, expect } from '../../../support/fixtures';
import {
  DECLINE_TITLE,
  contentHeadings,
  detail,
  formControls,
  gotoDetail,
  TEST_TIMEOUT,
} from './helpers';

// Suite 05: the decline form for a new request.  Read-only apart from the
// fixture.
test.describe('Decline form', () => {
  test('5.3 Decline form structure for a new request', async ({
    page,
    allocations,
  }) => {
    test.setTimeout(TEST_TIMEOUT);
    const e = await allocations.create();
    const url = `/allocation/requests/reject_request/${e.id}/`;

    await gotoDetail(page, e.id);
    const link = detail(page).getByRole('link', { name: 'Decline with Reason' });
    await expect(link).toHaveAttribute('href', url);
    await link.click();

    await expect(page).toHaveURL(url);
    await expect(page).toHaveTitle(DECLINE_TITLE);
    await expect(page.locator('h1')).toHaveText(['']);
    await expect(contentHeadings(page)).toHaveText([
      'Allocation Classification',
    ]);
    await expect(page.locator('.breadcrumb li')).toHaveText([
      'Allocations',
      'Pending Requests',
      'None',
    ]);

    const form = page.locator('form#new-allocation');
    await expect(form).toHaveAttribute('action', url);
    await expect(form).toHaveAttribute('method', 'post');

    expect(await formControls(page)).toEqual([
      expect.objectContaining({ type: 'hidden', name: 'csrfmiddlewaretoken' }),
      {
        tag: 'input',
        type: 'text',
        name: 'project_name',
        id: 'id_project_name',
        value: e.project_name,
        required: false,
        readOnly: true,
        disabled: false,
        label: 'Project identifier',
        help:
          'A short name used to identify your project.<br>Must contain ' +
          'only letters and numbers.<br>16 characters max.',
      },
      {
        tag: 'input',
        type: 'text',
        name: 'project_description',
        id: 'id_project_description',
        value: e.project_description,
        required: false,
        readOnly: true,
        disabled: false,
        label: 'Project allocation title',
        help: 'A human-friendly descriptive name for your research project.',
      },
      {
        tag: 'textarea',
        type: 'textarea',
        name: 'status_explanation',
        id: 'id_status_explanation',
        value: '',
        required: false,
        readOnly: false,
        disabled: false,
        label: 'Reason',
        help:
          'A brief explanation of the reason the request has been sent ' +
          'back to the user for changes',
      },
      expect.objectContaining({
        type: 'submit',
        name: '',
        value: 'Decline Request',
      }),
    ]);
    // Popover help on every field (the plan saw none).
    await expect(form.locator('.help-popover')).toHaveCount(3);
    await expect(form.locator('input[type=submit]')).toHaveCount(1);
  });
});
