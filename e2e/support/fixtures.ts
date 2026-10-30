import {
  BrowserContext,
  Page,
  test as base,
  request as playwrightRequest,
} from '@playwright/test';

import { AllocationApi } from './allocations';
import {
  BASE_URL,
  BLOCKED_URLS,
  IssuedToken,
  USER_STORAGE_STATE,
  hasUser,
  savedToken,
  savedUserToken,
} from './env';

type Fixtures = {
  allocations: AllocationApi;
  user: IssuedToken;
  userPage: Page;
  userAllocations: AllocationApi;
};

async function prepareContext(context: BrowserContext) {
  for (const url of BLOCKED_URLS) {
    await context.route(url, (route) => route.abort());
  }
  // Registered before any page exists, so it also covers the test's own
  // page.  A test may add its own handler too, so tolerate a dialog that
  // has already been handled.
  context.on('page', (page) =>
    page.on('dialog', (d) => d.accept().catch(() => {})),
  );
}

async function allocationApi(token: string, use: (a: AllocationApi) => Promise<void>) {
  const api = await playwrightRequest.newContext({
    baseURL: BASE_URL,
    extraHTTPHeaders: { 'X-Auth-Token': token },
  });
  await use(new AllocationApi(api));
  await api.dispose();
}

// All tests import { test, expect } from here.  The fixtures block the
// third-party widgets that stall headless browsers, accept the forms'
// beforeunload dialogs, and provide REST clients for creating fresh
// pwtest- allocations.
//
// `page` and `allocations` act as the allocation admin.  `userPage`,
// `user` and `userAllocations` act as the non-admin e2e user; tests using
// them are skipped when that user is not configured.
export const test = base.extend<Fixtures>({
  context: async ({ context }, use) => {
    await prepareContext(context);
    await use(context);
  },

  allocations: async ({}, use) => {
    await allocationApi(savedToken(), use);
  },

  user: async ({}, use, testInfo) => {
    testInfo.skip(!hasUser(), 'non-admin e2e user is not configured');
    await use(savedUserToken());
  },

  userPage: async ({ browser, user }, use) => {
    void user;
    const context = await browser.newContext({
      baseURL: BASE_URL,
      storageState: USER_STORAGE_STATE,
    });
    await prepareContext(context);
    const page = await context.newPage();
    await use(page);
    await context.close();
  },

  userAllocations: async ({ user }, use) => {
    await allocationApi(user.id, use);
  },
});

export { expect } from '@playwright/test';
