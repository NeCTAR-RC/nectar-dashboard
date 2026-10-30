import { test as base, request as playwrightRequest } from '@playwright/test';

import { AllocationApi } from './allocations';
import { BASE_URL, BLOCKED_URLS, savedToken } from './env';

type Fixtures = {
  allocations: AllocationApi;
};

// All tests import { test, expect } from here.  The fixture blocks the
// third-party widgets that stall headless browsers, accepts the forms'
// beforeunload dialogs, and provides a REST client for creating fresh
// pwtest- allocations.
export const test = base.extend<Fixtures>({
  context: async ({ context }, use) => {
    for (const url of BLOCKED_URLS) {
      await context.route(url, (route) => route.abort());
    }
    context.on('page', (page) => page.on('dialog', (d) => d.accept()));
    await use(context);
  },

  page: async ({ page }, use) => {
    page.on('dialog', (d) => d.accept());
    await use(page);
  },

  allocations: async ({}, use) => {
    const api = await playwrightRequest.newContext({
      baseURL: BASE_URL,
      extraHTTPHeaders: { 'X-Auth-Token': savedToken() },
    });
    await use(new AllocationApi(api));
    await api.dispose();
  },
});

export { expect } from '@playwright/test';
