# End-to-end tests

Playwright tests for the Allocations dashboard (`rcallocation`). They run
against a deployed dashboard, by default the dev dashboard
`http://dashboard-s.rcdev.nectar.org.au:8000`, not a local server: the
allocation pages need Keystone, manuka and real allocation data.

The suites are a regression baseline. They record what the UI does today,
including known quirks, so that refactoring `rcallocation` can be checked
for unintended UI changes.

## Layout

- `specs/`: the test plans, one per suite, written by the Playwright
  planner agent. Each scenario is tagged "verified live" or "derived from
  code".
- `tests/rcallocation/`: the tests, one directory per suite.
- `support/env.ts`: base URL, credentials and blocked third-party URLs.
- `support/fixtures.ts`: the `test` and `expect` every test imports. It
  blocks third-party widgets, accepts `beforeunload` dialogs and provides
  the `allocations` REST fixture.
- `support/allocations.ts`: creates fresh `pwtest-` allocations in a given
  state through the allocation REST API.
- `auth.setup.ts`: logs in once and saves the session.
- `seed.spec.ts`: the seed page for the Playwright test agents.
- `tools/cleanup.sh`: hard-deletes the `pwtest-` allocations afterwards.

## Running

```
npm ci
npx playwright install chromium
npx playwright test
npm run report
```

Credentials come from `OS_TOKEN`, or from the openrc file named by `OPENRC`
(default `pt.openrc` in the repository root, which is git-ignored). The
user must be an allocation admin. Set `DASHBOARD_URL` to test a different
deployment.

Tests run serially because they share one dev database.

## Test data

Tests that change data create their own allocations with the
`allocations` fixture. Each is named `pwtest-<tag>-<timestamp>`.
Notifications from the dev dashboard go to the dev system. Remove the test
allocations afterwards:

```
e2e/tools/cleanup.sh            # dry run
e2e/tools/cleanup.sh --delete   # hard-delete over ssh
```

## Writing tests

- Import `test` and `expect` from `support/fixtures`, never from
  `@playwright/test` directly.
- Allocation forms are split into collapsed accordion panels. Expand a
  field's panel before interacting with it; actions on hidden fields time
  out.
- Never follow links off the dashboard (support.ehelp.edu.au, ORCID,
  Freshdesk, Grafana, doi.org). Assert their `href` instead.
- Don't assert global row counts on shared lists. Other people's data and
  earlier test runs change them. Assert on rows the test created, or on
  structure.
- Assert dates rather than times. The displayed time zone is not stable
  within a session.
