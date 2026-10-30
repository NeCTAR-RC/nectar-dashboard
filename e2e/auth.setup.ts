import { test as setup, expect } from '@playwright/test';

import { BLOCKED_URLS, STORAGE_STATE, issueToken, saveToken } from './support/env';

// Log in once by posting a Keystone token to Horizon's WebSSO endpoint and
// save the session for the test projects.
setup('authenticate', async ({ page }) => {
  for (const url of BLOCKED_URLS) {
    await page.context().route(url, (route) => route.abort());
  }
  const token = issueToken();
  saveToken(token);

  const response = await page.request.post('/auth/websso/', {
    form: { token },
  });
  expect(response.ok()).toBeTruthy();

  await page.goto('/allocation/');
  await expect(page).not.toHaveURL(/\/auth\/login/);
  await page.context().storageState({ path: STORAGE_STATE });
});
