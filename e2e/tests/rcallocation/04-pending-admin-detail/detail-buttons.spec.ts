import { Page } from '@playwright/test';

import { test, expect } from '../../../support/fixtures';
import { declineViaUi } from '../../../support/allocations';
import {
  PENDING_E,
  PENDING_X,
  adminNotes,
  detail,
  detailButtons,
  gotoDetail,
  recordRequests,
} from './helpers';

// Suite 04: action buttons, external links, admin notes and the NOTE
// block on the admin detail page.  Read-only, except that 4.21 declines
// fresh fixtures through the UI to reach status J and R.

const E_BUTTONS = [
  'Add/edit admin notes',
  'Review & Approve',
  'Decline with Reason',
  'View History',
  'Related tickets',
];
const X_BUTTONS = [
  'Add/edit admin notes',
  'Approve changes',
  'Decline changes',
  'View History',
  'Related tickets',
];
const A_BUTTONS = ['Add/edit admin notes', 'View History', 'Related tickets'];

// Fetch detail pages with a same-origin fetch and read their buttons and
// right-hand resources heading, without navigating the page each time.
async function readDetails(page: Page, ids: number[]) {
  return page.evaluate(async (ids: number[]) => {
    const out: Record<number, { buttons: string[]; resources: string[] }> = {};
    const read = async (id: number) => {
      const r = await fetch(`/allocation/requests/view/${id}/`);
      const doc = new DOMParser().parseFromString(await r.text(), 'text/html');
      out[id] = {
        buttons: [...doc.querySelectorAll('.allocation a.btn')].map((a) =>
          a.textContent!.replace(/\s+/g, ' ').trim(),
        ),
        resources: [...doc.querySelectorAll('.allocation h3')]
          .map((h) => h.textContent!.replace(/\s+/g, ' ').trim())
          .filter((h) => /Resources/.test(h)),
      };
    };
    // Each detail page takes a few seconds to render; fetch four at a
    // time to keep the load on the dev dashboard modest.
    const queue = [...ids];
    const worker = async () => {
      for (let id = queue.shift(); id !== undefined; id = queue.shift()) {
        await read(id);
      }
    };
    await Promise.all([worker(), worker(), worker(), worker()]);
    return out;
  }, ids);
}

const NOTE_TEXT =
  'NOTE To start a conversation with the user about their allocation ' +
  'request, first click "See Related Tickets" to see Freshdesk tickets ' +
  'tagged with this allocation. Next choose one from the list, change its ' +
  'status to "Open", change its group to "Allocations" and assign it to ' +
  'yourself. When you finish the conversation, please remember to ' +
  '"Resolve" the ticket in the normal way.';
const NOTE_SPINNER =
  'If the "See Related Tickets" page gets stuck with a "spinner", try ' +
  'refreshing the page. (We think it is a Freshdesk bug.)';

const TICKETS = (id: number) =>
  new RegExp(`&q\\[\\]=tags%3A%5B%22allocation-${id}%22%5D$`);

test.describe('Admin detail buttons and blocks', () => {
  test.describe('read-only', () => {
    let guard: ReturnType<typeof recordRequests>;

    test.beforeEach(async ({ page }) => {
      guard = recordRequests(page);
    });

    test.afterEach(async () => {
      guard.expectReadOnly();
    });

    test('4.13 Action buttons by state across the Pending records', async ({
      page,
      allocations,
    }) => {
      // Reads 34 detail pages.
      test.setTimeout(300_000);
      const e = await allocations.create();
      const x = await allocations.createAmendmentPending();
      const a = await allocations.createApproved();

      await page.goto('/allocation/requests/');
      const details = await readDetails(page, [
        ...PENDING_E,
        ...PENDING_X,
        e.id,
        x.id,
        a.id,
      ]);

      for (const id of [...PENDING_E, e.id]) {
        expect(details[id].buttons, `E ${id}`).toEqual(E_BUTTONS);
        expect(details[id].resources, `E ${id}`).toEqual([
          'Requested Resources',
          'Approved Resources (at the time of this record)',
        ]);
      }
      // The long-standing X records all have a project_id, so they also
      // have Project usage.
      for (const id of PENDING_X) {
        expect(details[id].buttons, `X ${id}`).toEqual([
          ...X_BUTTONS,
          'Project usage',
        ]);
        expect(details[id].resources, `X ${id}`).toEqual([
          'Requested Resources',
          'Current Resources',
        ]);
      }
      // A fresh amendment has no project_id, so no Project usage.  Its
      // resources heading is not asserted: the fixture approves and
      // amends back-to-back, and the dev backends' clock skew can order
      // the two timestamps either way (see 4.18).
      expect(details[x.id].buttons, `X ${x.id}`).toEqual(X_BUTTONS);
      expect(details[a.id].buttons, `A ${a.id}`).toEqual(A_BUTTONS);
      expect(details[a.id].resources).toEqual(['Current Resources']);

      // Hrefs and classes for an E record.
      await gotoDetail(page, e.id);
      let buttons = await detailButtons(page);
      expect(buttons).toEqual([
        {
          text: 'Add/edit admin notes',
          href: `/allocation/requests/edit_notes/${e.id}/`,
          className: 'btn btn-default',
          id: 'allocation_reject_view',
          target: null,
        },
        {
          text: 'Review & Approve',
          href: `/allocation/requests/approve_request/${e.id}/`,
          className: 'btn btn-success btn-lg',
          id: 'allocation_accept_view',
          target: null,
        },
        {
          text: 'Decline with Reason',
          href: `/allocation/requests/reject_request/${e.id}/`,
          className: 'btn btn-danger btn-lg',
          id: 'allocation_reject_view',
          target: null,
        },
        {
          text: 'View History',
          href: `/allocation/requests/view/${e.id}/history`,
          className: 'btn btn-default btn-lg',
          id: '',
          target: null,
        },
        expect.objectContaining({
          text: 'Related tickets',
          className: 'btn btn-default btn-lg',
          id: 'allocation_tickets',
          target: '_blank',
        }),
      ]);
      // Duplicate DOM ids: the notes button shares allocation_reject_view.
      await expect(page.locator('[id="allocation_reject_view"]')).toHaveCount(2);

      // Hrefs and classes for an X record.
      await gotoDetail(page, 135408);
      buttons = await detailButtons(page);
      expect(buttons.slice(1, 4)).toEqual([
        {
          text: 'Approve changes',
          href: '/allocation/requests/approve_change_request/135408/',
          className: 'btn btn-success btn-lg',
          id: 'allocation_accept_view',
          target: null,
        },
        {
          text: 'Decline changes',
          href: '/allocation/requests/reject_request/135408/',
          className: 'btn btn-danger btn-lg',
          id: 'allocation_reject_view',
          target: null,
        },
        {
          text: 'View History',
          href: '/allocation/requests/view/135408/history',
          className: 'btn btn-default btn-lg',
          id: '',
          target: null,
        },
      ]);
      expect(buttons[0]).toMatchObject({
        text: 'Add/edit admin notes',
        href: '/allocation/requests/edit_notes/135408/',
        className: 'btn btn-default',
      });
    });

    test('4.14 Related tickets and Project usage links (href and target only)', async ({
      page,
      allocations,
    }) => {
      // On dev the Freshdesk and Grafana base URLs are unset and render
      // as 'None'; assert only the suffix.  Never click these links.
      await gotoDetail(page, 135408);
      const tickets = page.locator('#allocation_tickets');
      const usage = page.locator('#allocation_project_usage');
      await expect(tickets).toHaveText('Related tickets');
      await expect(tickets).toHaveAttribute('target', '_blank');
      await expect(tickets).toHaveAttribute('href', TICKETS(135408));
      await expect(usage).toHaveText('Project usage');
      await expect(usage).toHaveAttribute('target', '_blank');
      await expect(usage).toHaveAttribute(
        'href',
        /&var-project_id=14813f18dc364a4c965aa7399a08614c$/,
      );

      const e = await allocations.create();
      await gotoDetail(page, e.id);
      await expect(tickets).toHaveAttribute('href', TICKETS(e.id));
      await expect(tickets).toHaveAttribute('target', '_blank');
      await expect(usage).toHaveCount(0);

      await gotoDetail(page, 152179);
      await expect(tickets).toHaveAttribute('href', TICKETS(152179));
      await expect(usage).toHaveCount(0);
    });

    test('4.15 Allocation admin notes block and edit button', async ({
      page,
      allocations,
    }) => {
      const editNotes = detail(page).getByRole('link', {
        name: 'Add/edit admin notes',
      });

      await gotoDetail(page, 135408);
      await expect(adminNotes(page)).toHaveText(
        'pending approval from UNSW, 20->120 vCPU',
      );
      await expect(editNotes).toHaveClass('btn btn-default');
      await expect(editNotes).toHaveId('allocation_reject_view');
      await expect(editNotes).toHaveAttribute(
        'href',
        '/allocation/requests/edit_notes/135408/',
      );
      // The button is in the row below the notes text.
      const notesRow = detail(page).locator('.row', {
        has: page.locator('h3', { hasText: 'Allocation admin notes' }),
      });
      await expect(notesRow.locator('a.btn')).toHaveText('Add/edit admin notes');

      // Empty notes render the literal text None.
      const e = await allocations.create();
      for (const id of [e.id, 152179]) {
        await gotoDetail(page, id);
        await expect(adminNotes(page)).toHaveText('None');
        await expect(editNotes).toHaveAttribute(
          'href',
          `/allocation/requests/edit_notes/${id}/`,
        );
      }

      const notes: Record<number, string | RegExp> = {
        58677: 'waiting for uts approval',
        84989:
          'Asked Simon Forsayeth to review as asking for volume storage at ' +
          'Swinburne and astronomy project. Does meet national merit criteria.',
        38655:
          /^\s*JR \(24\.06\.2022\) Contacted TM, asked why vCPU was reduced[\s\S]*so Intersect needs to approve this please\s*$/,
        145272: 'Sergio approved 1TB of volume storage - 2004-04-19',
        135339: 'changed volume quota from Melbourne Uni to Intersect',
      };
      for (const [id, text] of Object.entries(notes)) {
        await gotoDetail(page, Number(id));
        await expect(adminNotes(page)).toHaveText(text);
      }
      // 38655 spans several lines.
      await gotoDetail(page, 38655);
      expect((await adminNotes(page).textContent())!.trim()).toContain('\n');
    });

    test('4.16 Special approval reasons block is absent when not set', async ({
      page,
      allocations,
    }) => {
      const e = await allocations.create();
      for (const id of [e.id, 135408, 152179, 146946]) {
        await gotoDetail(page, id);
        await expect(
          detail(page).locator('h3', { hasText: 'Special approval reasons' }),
        ).toHaveCount(0);
        // No extra row above the admin notes: the heading before it is
        // the last main-content heading.
        const h3 = await detail(page).locator('h3').allInnerTexts();
        const notes = h3.indexOf('Allocation admin notes');
        expect(['Publication/Output and Impact', 'Reviewer Comment']).toContain(
          h3[notes - 1].trim(),
        );
      }
    });

    test('4.16 Special approval reasons block shows when set', async ({
      page,
      allocations,
    }) => {
      // No Pending record has special_approval set, but an admin can set
      // it when creating a fresh fixture.
      const reason = 'Playwright suite 04 special approval reason';
      const e = await allocations.create({ special_approval: reason });
      await gotoDetail(page, e.id);

      // The row comes first in extra_details, directly before the notes.
      const h3 = (await detail(page).locator('h3').allInnerTexts()).map((h) =>
        h.trim(),
      );
      const special = h3.indexOf('Special approval reasons');
      expect(special).toBeGreaterThan(0);
      expect(h3[special + 1]).toBe('Allocation admin notes');
      const block = detail(page).locator('.row > .col-md-12', {
        has: page.locator('h3', { hasText: 'Special approval reasons' }),
      });
      await expect(block).toHaveCount(1);
      await expect(block.locator('p')).toHaveText(reason);
      // It is its own row, separate from the notes row.
      await expect(
        block.locator('xpath=..').locator('h3', { hasText: 'Allocation admin notes' }),
      ).toHaveCount(0);
    });

    test('4.17 Freshdesk NOTE text on the admin detail', async ({
      page,
      allocations,
    }) => {
      const e = await allocations.create();
      for (const id of [e.id, 135408, 152179, 146946]) {
        await gotoDetail(page, id);
        const block = detail(page).locator('.col-md-6', {
          has: page.locator('span.label.label-info', { hasText: 'NOTE' }),
        });
        await expect(block).toHaveCount(1);
        const paragraphs = block.locator('p');
        await expect(paragraphs).toHaveCount(2);
        expect(
          (await paragraphs.nth(0).textContent())!.replace(/\s+/g, ' ').trim(),
        ).toBe(NOTE_TEXT);
        expect(
          (await paragraphs.nth(1).textContent())!.replace(/\s+/g, ' ').trim(),
        ).toBe(NOTE_SPINNER);
        // The NOTE says 'See Related Tickets' but the button reads
        // 'Related tickets'.
        await expect(page.locator('#allocation_tickets')).toHaveText('Related tickets');
        // The block sits in the row after the admin notes row.
        await expect(
          detail(page)
            .locator('.row', {
              has: page.locator('h3', { hasText: 'Allocation admin notes' }),
            })
            .locator('xpath=following-sibling::div[1]')
            .locator('span.label-info'),
        ).toHaveText('NOTE');
      }
    });
  });

  test('4.21 Buttons for J and R records', async ({ page, allocations }) => {
    // J: a declined amendment.  R: a declined new request.  Declining
    // submits the reject form; that is the only way to reach these states.
    const x = await allocations.createAmendmentPending();
    const e = await allocations.create();
    await declineViaUi(page, x.id, 'Playwright suite 04 J state');
    await declineViaUi(page, e.id, 'Playwright suite 04 R state');
    expect((await allocations.get(x.id)).status).toBe('J');
    expect((await allocations.get(e.id)).status).toBe('R');

    // J follows X: can_approve_change and can_reject_change.
    await gotoDetail(page, x.id);
    expect((await detailButtons(page)).map((b) => b.text)).toEqual(X_BUTTONS);
    await expect(page.getByRole('link', { name: 'Approve changes' })).toHaveAttribute(
      'href',
      `/allocation/requests/approve_change_request/${x.id}/`,
    );
    await expect(page.getByRole('link', { name: 'Decline changes' })).toHaveAttribute(
      'href',
      `/allocation/requests/reject_request/${x.id}/`,
    );
    await expect(detail(page).locator('table').nth(1).locator('tr').first())
      .toContainText('Update declined');

    // R: no approve or decline buttons.
    await gotoDetail(page, e.id);
    expect((await detailButtons(page)).map((b) => b.text)).toEqual(A_BUTTONS);
    await expect(detail(page).locator('table').nth(1).locator('tr').first())
      .toContainText('Declined');
  });

  test('4.21 Buttons for N records', async ({ page }) => {
    test.fixme(
      true,
      'No status N record exists and the allocations fixture cannot create ' +
        'one (the REST API creates Submitted requests).',
    );
    // Intended assertions: N follows E (can_be_approved, can_be_rejected).
    const id = 0;
    await gotoDetail(page, id);
    expect((await detailButtons(page)).map((b) => b.text)).toEqual(E_BUTTONS);
  });
});
