import { execSync } from 'child_process';
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

// Issue a Keystone token for the test user.  OS_TOKEN wins if set;
// otherwise source the openrc file named by OPENRC (default pt.openrc in
// the repository root) and ask the openstack CLI for one.
export function issueToken(): string {
  if (process.env.OS_TOKEN) {
    return process.env.OS_TOKEN;
  }
  const openrc = process.env.OPENRC ?? path.join(REPO_ROOT, 'pt.openrc');
  return tokenFromOpenrc(openrc).id;
}

// username is the Keystone user name, which the dashboard compares with an
// allocation's contact_email.
export type IssuedToken = {
  id: string;
  user_id: string;
  project_id: string;
  username: string;
};

export function tokenFromOpenrc(openrc: string): IssuedToken {
  const run = (cmd: string) =>
    execSync(`bash -c 'source "${openrc}" && ${cmd}'`, {
      encoding: 'utf-8',
    });
  const token = JSON.parse(run('openstack token issue -f json'));
  return {
    id: token.id,
    user_id: token.user_id,
    project_id: token.project_id,
    username: run('echo "$OS_USERNAME"').trim(),
  };
}

export function saveToken(token: string): void {
  fs.mkdirSync(AUTH_DIR, { recursive: true });
  fs.writeFileSync(TOKEN_FILE, JSON.stringify({ token }));
}

// The token saved by the auth setup project, for REST API calls.
export function savedToken(): string {
  return JSON.parse(fs.readFileSync(TOKEN_FILE, 'utf-8')).token;
}

export function saveUserToken(token: IssuedToken): void {
  fs.mkdirSync(AUTH_DIR, { recursive: true });
  fs.writeFileSync(USER_TOKEN_FILE, JSON.stringify(token));
}

// The non-admin user's token, Keystone user id and project id.
export function savedUserToken(): IssuedToken {
  return JSON.parse(fs.readFileSync(USER_TOKEN_FILE, 'utf-8'));
}
