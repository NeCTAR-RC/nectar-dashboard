import { defineConfig, devices } from '@playwright/test';

import { BASE_URL, STORAGE_STATE } from './e2e/support/env';

// End-to-end tests run against a deployed dashboard (dashboard-s by
// default) rather than a local server: the allocation pages need Keystone,
// manuka and the real allocation data.  Tests share one dev database, so
// run them serially.
export default defineConfig({
  testDir: './e2e',
  outputDir: './e2e/test-results',
  fullyParallel: false,
  workers: 1,
  retries: 0,
  timeout: 120_000,
  expect: { timeout: 15_000 },
  reporter: [
    ['list'],
    ['html', { outputFolder: 'e2e/playwright-report', open: 'never' }],
    // Jenkins publishes the JUnit results of CI runs.
    ...(process.env.CI
      ? [['junit', { outputFile: 'e2e/junit.xml' }] as const]
      : []),
  ],
  use: {
    baseURL: BASE_URL,
    // Form fields sit in collapsed accordion panels; an action on a hidden
    // field would otherwise wait for it to become visible indefinitely.
    actionTimeout: 15_000,
    // The Approved Requests list renders ~1600 rows and takes ~30s.
    navigationTimeout: 90_000,
    trace: 'retain-on-failure',
  },
  projects: [
    {
      name: 'setup',
      testMatch: /auth\.setup\.ts/,
    },
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'], storageState: STORAGE_STATE },
      dependencies: ['setup'],
    },
  ],
});
