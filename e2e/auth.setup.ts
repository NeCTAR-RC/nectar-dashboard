import { Page, test as setup, expect } from '@playwright/test';

import {
  BLOCKED_URLS,
  STORAGE_STATE,
  USER_OPENRC,
  USER_STORAGE_STATE,
  hasUser,
  issueToken,
  saveToken,
  saveUserToken,
  tokenFromOpenrc,
} from './support/env';

// Log in by posting a Keystone token to Horizon's WebSSO endpoint and save
// the session for the test projects.
async function login(page: Page, token: string, storageState: string) {
  for (const url of BLOCKED_URLS) {
    await page.context().route(url, (route) => route.abort());
  }
  const response = await page.request.post('/auth/websso/', {
    form: { token },
  });
  expect(response.ok()).toBeTruthy();

  await page.goto('/allocation/');
  await expect(page).not.toHaveURL(/\/auth\/login/);
  await page.context().storageState({ path: storageState });
}

setup('authenticate', async ({ page }) => {
  const token = issueToken();
  saveToken(token);
  await login(page, token, STORAGE_STATE);
});

setup('authenticate non-admin user', async ({ page }) => {
  setup.skip(!hasUser(), `no non-admin openrc at ${USER_OPENRC}`);
  const token = tokenFromOpenrc(USER_OPENRC);
  saveUserToken(token);
  await login(page, token.id, USER_STORAGE_STATE);
});
