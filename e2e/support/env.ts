import * as fs from 'fs';
import * as path from 'path';

export const REPO_ROOT = path.resolve(__dirname, '..', '..');

export const BASE_URL =
  process.env.DASHBOARD_URL ?? 'http://dashboard-s.rcdev.nectar.org.au:8000';

const AUTH_DIR = path.join(REPO_ROOT, 'e2e', '.auth');
export const STORAGE_STATE = path.join(AUTH_DIR, 'admin.json');
const TOKEN_FILE = path.join(AUTH_DIR, 'token.json');

// A second, non-admin user: member and TenantManager of one project and no
// allocation admin role.  Its openrc is named by E2E_USER_OPENRC (default
// e2e-user.openrc in the repository root); tests needing it are skipped
// when the file is missing.
export const USER_OPENRC =
  process.env.E2E_USER_OPENRC ?? path.join(REPO_ROOT, 'e2e-user.openrc');
export const USER_STORAGE_STATE = path.join(AUTH_DIR, 'user.json');
const USER_TOKEN_FILE = path.join(AUTH_DIR, 'user-token.json');

export function hasUser(): boolean {
  return fs.existsSync(USER_OPENRC);
}

// Third-party widgets in the deployed page chrome that headless browsers
// cannot get past: the ARDC footer pulls in a Cloudflare Turnstile
// challenge, and the survey dialog covers the page and blocks clicks.
export const BLOCKED_URLS = [
  'https://challenges.cloudflare.com/**',
  'https://ardc.edu.au/**',
  '*://survey.rc.nectar.org.au/**',
];

export const ADMIN_OPENRC =
  process.env.OPENRC ?? path.join(REPO_ROOT, 'pt.openrc');

// username is the Keystone user name, which the dashboard compares with an
// allocation's contact_email.
export type IssuedToken = {
  id: string;
  user_id: string;
  project_id: string;
  username: string;
};

// Read the `export KEY=VALUE` lines of an openrc file.  Only literal
// values are supported; nothing in the file is executed.
export function parseOpenrc(openrc: string): Record<string, string> {
  const vars: Record<string, string> = {};
  for (const line of fs.readFileSync(openrc, 'utf-8').split('\n')) {
    const m = line.match(/^\s*(?:export\s+)?([A-Z_][A-Z0-9_]*)=(.*)$/);
    if (!m) continue;
    let value = m[2].trim();
    const quoted = value.match(/^"(.*)"$/) ?? value.match(/^'(.*)'$/);
    if (quoted) value = quoted[1];
    vars[m[1]] = value;
  }
  return vars;
}

// Ask Keystone for a project-scoped token with the openrc's password
// credentials.  This needs no openstack CLI on the test host.
export async function tokenFromOpenrc(openrc: string): Promise<IssuedToken> {
  const env = parseOpenrc(openrc);
  for (const key of ['OS_AUTH_URL', 'OS_USERNAME', 'OS_PASSWORD']) {
    if (!env[key]) throw new Error(`${key} is not set in ${openrc}`);
  }
  const userDomain = env.OS_USER_DOMAIN_NAME ?? 'Default';
  const projectDomain = env.OS_PROJECT_DOMAIN_NAME ?? 'Default';
  const project = env.OS_PROJECT_ID
    ? { id: env.OS_PROJECT_ID }
    : { name: env.OS_PROJECT_NAME, domain: { name: projectDomain } };
  const authUrl = env.OS_AUTH_URL.replace(/\/+$/, '').replace(/\/v3$/, '');
  const response = await fetch(`${authUrl}/v3/auth/tokens`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      auth: {
        identity: {
          methods: ['password'],
          password: {
            user: {
              name: env.OS_USERNAME,
              domain: { name: userDomain },
              password: env.OS_PASSWORD,
            },
          },
        },
        scope: { project },
      },
    }),
  });
  if (response.status !== 201) {
    throw new Error(
      `Keystone token request for ${env.OS_USERNAME} failed: ` +
        `${response.status} ${await response.text()}`,
    );
  }
  const body = await response.json();
  return {
    id: response.headers.get('x-subject-token')!,
    user_id: body.token.user.id,
    project_id: body.token.project.id,
    username: env.OS_USERNAME,
  };
}

// Issue a Keystone token for the allocation admin.  OS_TOKEN wins if set
// (with OS_USERNAME giving the admin's user name); otherwise use the
// openrc file named by OPENRC (default pt.openrc in the repository root).
export async function issueToken(): Promise<IssuedToken> {
  if (process.env.OS_TOKEN) {
    return {
      id: process.env.OS_TOKEN,
      user_id: '',
      project_id: '',
      username: process.env.OS_USERNAME ?? '',
    };
  }
  return tokenFromOpenrc(ADMIN_OPENRC);
}

export function saveToken(token: IssuedToken): void {
  fs.mkdirSync(AUTH_DIR, { recursive: true });
  fs.writeFileSync(TOKEN_FILE, JSON.stringify(token));
}

// The admin token saved by the auth setup project, for REST API calls.
export function savedToken(): string {
  return savedAdminToken().id;
}

// The admin's token and Keystone user name.  The user name is the
// admin's email address: the contact on requests the admin creates and
// the approver recorded when the admin approves.
export function savedAdminToken(): IssuedToken {
  return JSON.parse(fs.readFileSync(TOKEN_FILE, 'utf-8'));
}

export function saveUserToken(token: IssuedToken): void {
  fs.mkdirSync(AUTH_DIR, { recursive: true });
  fs.writeFileSync(USER_TOKEN_FILE, JSON.stringify(token));
}

// The non-admin user's token, Keystone user id and project id.
export function savedUserToken(): IssuedToken {
  return JSON.parse(fs.readFileSync(USER_TOKEN_FILE, 'utf-8'));
}
