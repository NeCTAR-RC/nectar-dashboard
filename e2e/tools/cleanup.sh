#!/bin/bash
# Hard-delete the pwtest- allocations (and their history) that the
# end-to-end tests create on the dev dashboard.
#
# Usage: e2e/tools/cleanup.sh [--delete]
#
# Without --delete this is a dry run.  Lists allocations through the REST
# API, then runs the hard_delete_allocation management command on the
# dashboard host over ssh.
#
# Environment:
#   DASHBOARD_URL   default http://dashboard-s.rcdev.nectar.org.au:8000
#   E2E_SSH_HOST    default dashboard-s.rcdev.nectar.org.au
#   E2E_SSH_OPTS    extra ssh options, e.g. "-F ~/.ssh/claude_config"
#   E2E_HORIZON_DIR default /opt/horizon
#   E2E_PYTHON      default /opt/2025.1/bin/python3
#   OS_TOKEN / OPENRC as for the tests (default OPENRC is pt.openrc)

set -euo pipefail

repo_root=$(cd "$(dirname "$0")/../.." && pwd)
dashboard_url=${DASHBOARD_URL:-http://dashboard-s.rcdev.nectar.org.au:8000}
ssh_host=${E2E_SSH_HOST:-dashboard-s.rcdev.nectar.org.au}
horizon_dir=${E2E_HORIZON_DIR:-/opt/horizon}
python=${E2E_PYTHON:-/opt/2025.1/bin/python3}

delete_flag=""
if [ "${1:-}" = "--delete" ]; then
    delete_flag="--no-dry-run"
fi

if [ -z "${OS_TOKEN:-}" ]; then
    # shellcheck disable=SC1090
    source "${OPENRC:-$repo_root/pt.openrc}"
    OS_TOKEN=$(openstack token issue -f value -c id)
fi

ids=$(curl -sf -H "X-Auth-Token: $OS_TOKEN" \
    "$dashboard_url/rest_api/allocations/?project_name__startswith=pwtest-&parent_request__isnull=true&limit=1000" \
    | python3 -c 'import json, sys; print(" ".join(str(a["id"]) for a in json.load(sys.stdin)["results"]))')

if [ -z "$ids" ]; then
    echo "No pwtest- allocations found"
    exit 0
fi

echo "pwtest- allocations: $(echo "$ids" | wc -w)"
dry_run=True
if [ -n "$delete_flag" ]; then
    dry_run=False
fi
# Run every delete in one Django process: starting Horizon once per
# allocation takes several seconds each.
script="from nectar_dashboard.rcallocation.management.commands.hard_delete_allocation import Command
cmd = Command()
for i in '$ids'.split():
    cmd.delete_allocation(int(i), dry_run=$dry_run)"
# shellcheck disable=SC2086
ssh ${E2E_SSH_OPTS:-} "$ssh_host" \
    "cd $horizon_dir && DJANGO_SETTINGS_MODULE=openstack_dashboard.settings $python manage.py shell -c \"\$(cat)\"" \
    <<< "$script" 2>&1 | grep -v '^DEBUG '

if [ -z "$delete_flag" ]; then
    echo "Dry run only; rerun with --delete to delete these allocations"
fi
