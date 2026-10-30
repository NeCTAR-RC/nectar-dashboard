import { execSync } from 'child_process';
import * as fs from 'fs';
import * as path from 'path';

export const REPO_ROOT = path.resolve(__dirname, '..', '..');

export const BASE_URL =
  process.env.DASHBOARD_URL ?? 'http://dashboard-s.rcdev.nectar.org.au:8000';

const AUTH_DIR = path.join(REPO_ROOT, 'e2e', '.auth');
export const STORAGE_STATE = path.join(AUTH_DIR, 'admin.json');
const TOKEN_FILE = path.join(AUTH_DIR, 'token.json');

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
  return execSync(
    `bash -c 'source "${openrc}" && openstack token issue -f value -c id'`,
    { encoding: 'utf-8' },
  ).trim();
}

export function saveToken(token: string): void {
  fs.mkdirSync(AUTH_DIR, { recursive: true });
  fs.writeFileSync(TOKEN_FILE, JSON.stringify({ token }));
}

// The token saved by the auth setup project, for REST API calls.
export function savedToken(): string {
  return JSON.parse(fs.readFileSync(TOKEN_FILE, 'utf-8')).token;
}
