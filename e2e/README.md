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

Or, as CI does: `tox -e e2e` (extra arguments go to `playwright test`).

Credentials come from `OS_TOKEN` (with `OS_USERNAME`), or from the openrc
file named by `OPENRC` (default `pt.openrc` in the repository root, which
is git-ignored). The user must be an allocation admin. The token is
requested from Keystone directly with the openrc's password credentials,
so the openstack CLI is not needed; the openrc is parsed, not sourced, and
must use literal `export KEY=VALUE` lines. Set `DASHBOARD_URL` to test a
different deployment.

Tests run serially because they share one dev database.

## CI

Each nectar-dashboard patchset gets its own dev env,
`https://review-<change>-<patchset>.rcdev.nectar.org.au`, from the
Jenkins job `dashboard-devenv-create` (nectar-ci `data/dashboard.yaml`).
Once the env is deployed, that job starts `dashboard-devenv-e2e`, which:

1. checks out the patchset and skips if `tox.ini` has no `e2e` env;
2. waits up to 40 minutes for `/auth/login/` on the env to return 200;
3. runs `tox -e e2e` with `CI=true` and `DASHBOARD_URL` set to the env,
   and `OPENRC` and `E2E_USER_OPENRC` from the Jenkins file credentials
   `dashboard-e2e-admin-openrc` and `dashboard-e2e-user-openrc`;
4. publishes `e2e/junit.xml` (written only when `CI` is set), archives
   the HTML report and traces, and comments the result on the review.

The comment does not vote. Review envs are deleted with their namespace,
so CI runs need no cleanup.

To reproduce a CI run locally:

```
DASHBOARD_URL=https://review-<change>-<patchset>.rcdev.nectar.org.au CI=1 tox -e e2e
```

Review envs load the same Faker-generated `dev.sql` as dashboard-s, but
not the data created on dashboard-s since, so tests that rely on that data
can fail there.

## Test data

Tests that change data create their own allocations with the
`allocations` fixture. Each is named `pwtest-<tag>-<timestamp>`.
Notifications from the dev dashboard go to the dev system. Remove the test
allocations afterwards:

```
e2e/tools/cleanup.sh            # dry run
e2e/tools/cleanup.sh --delete   # hard-delete over ssh
```

The cleanup needs ssh access to the dashboard host. Each full run creates
about 250 allocations, so run it after every full run; a backlog makes
the shared lists, and so the tests, much slower.

## Baseline

Recorded on 2026-10-31 against dashboard-s running the change "test: wait
for the decline redirect in the history e2e suite" (Change-Id
Icfb7f1590b8d259520fab7c5491def1b54b956b0), with nothing else using the
server: 171 passed, 8 skipped (test.fixme) and 0 failed, in 30 minutes. The tests marked fixme need data the fixtures
cannot create (status N, a disabled organisation, a soft-deleted record,
a stale modified time, an approver registered for a site).

To check a change for UI regressions, deploy it to dashboard-s, clean
up, run the whole suite with nothing else using the server, and compare
with this result. A failure means the UI now behaves differently from
the baseline: either a regression, or an intended change that needs the
test and its plan in `specs/` updating.

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
