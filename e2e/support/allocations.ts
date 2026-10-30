import { APIRequestContext, Page, expect } from '@playwright/test';

// Every allocation the tests create is named with this prefix so the
// cleanup script can find and hard-delete them afterwards.
export const TEST_PREFIX = 'pwtest-';

export type Allocation = {
  id: number;
  project_name: string;
  project_description: string;
  status: string;
  [key: string]: unknown;
};

export function uniqueProjectName(tag = 'e2e'): string {
  const stamp = new Date()
    .toISOString()
    .replace(/[-:T]/g, '')
    .slice(0, 14);
  const rand = Math.random().toString(36).slice(2, 6);
  // Project identifiers are limited to 32 characters.
  return `${TEST_PREFIX}${tag}-${stamp}${rand}`.slice(0, 32);
}

// A minimal request the allocation REST API accepts.  It is created by the
// test (admin) user, so it lands in that user's My Requests as status E.
function minimalRequest(overrides: Record<string, unknown>) {
  return {
    project_name: uniqueProjectName(),
    project_description: 'Playwright e2e fixture',
    use_case: 'Playwright end-to-end test fixture',
    estimated_project_duration: 12,
    usage_types: ['Hosting services to support research'],
    ardc_support: [],
    ncris_facilities: [],
    supported_organisations: ['https://ror.org/02bfwt286'],
    field_of_research_1: '4601',
    for_percentage_1: 100,
    has_sensitive_data: 'no_sensitive',
    data_classification_level: 'green',
    multiple_allocations_check: false,
    direct_access_user_estimate: 1,
    estimated_service_count: 1,
    estimated_service_active_users: 1,
    bundle: 'Standard',
    ...overrides,
  };
}

export class AllocationApi {
  constructor(private readonly api: APIRequestContext) {}

  async get(id: number): Promise<Allocation> {
    const r = await this.api.get(`/rest_api/allocations/${id}/`);
    expect(r.status(), await r.text()).toBe(200);
    return r.json();
  }

  async history(id: number): Promise<Allocation[]> {
    const r = await this.api.get(
      `/rest_api/allocations/?parent_request=${id}&limit=1000`,
    );
    expect(r.status(), await r.text()).toBe(200);
    return (await r.json()).results;
  }

  // Create a Submitted (E) allocation.
  async create(overrides: Record<string, unknown> = {}): Promise<Allocation> {
    const r = await this.api.post('/rest_api/allocations/', {
      data: minimalRequest(overrides),
    });
    expect(r.status(), await r.text()).toBe(201);
    return r.json();
  }

  // Create an Approved (A) allocation.  Approval needs an associated site,
  // which only an allocation admin may set.
  async createApproved(
    overrides: Record<string, unknown> = {},
  ): Promise<Allocation> {
    const created = await this.create({ associated_site: 'qcif', ...overrides });
    return this.approve(created.id);
  }

  // Create an allocation with an amendment pending (X).
  async createAmendmentPending(
    overrides: Record<string, unknown> = {},
  ): Promise<Allocation> {
    const approved = await this.createApproved(overrides);
    return this.amend(approved.id);
  }

  async approve(id: number): Promise<Allocation> {
    const r = await this.api.post(`/rest_api/allocations/${id}/approve/`);
    expect(r.status(), await r.text()).toBe(200);
    return r.json();
  }

  async amend(id: number): Promise<Allocation> {
    const r = await this.api.post(`/rest_api/allocations/${id}/amend/`);
    expect(r.status(), await r.text()).toBe(200);
    return r.json();
  }
}

// The REST API has no decline action, so decline through the admin UI.
// Status becomes R for a new request and J for a pending amendment.
export async function declineViaUi(page: Page, id: number, reason: string) {
  await page.goto(`/allocation/requests/reject_request/${id}/`);
  await page.locator('#id_status_explanation').fill(reason);
  await Promise.all([
    page.waitForURL(/\/allocation\/requests\/$/),
    page.locator('input[type=submit]').first().click(),
  ]);
}
