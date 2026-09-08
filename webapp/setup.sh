#!/usr/bin/env bash
# First-time setup for the site. Run from anywhere:
#
#   ./setup.sh          install dependencies
#   ./setup.sh --dev    install, then start the dev server
#
# Works in Git Bash on Windows as well as macOS/Linux.

set -euo pipefail

REQUIRED_NODE_MAJOR=24
here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$here"

fail() { printf 'setup: %s\n' "$*" >&2; exit 1; }

command -v node >/dev/null 2>&1 || fail "node not found. Install Node.js $REQUIRED_NODE_MAJOR from https://nodejs.org"
command -v npm  >/dev/null 2>&1 || fail "npm not found. It ships with Node.js; reinstall Node $REQUIRED_NODE_MAJOR"

node_version="$(node -v)"                 # e.g. v24.18.1
node_major="${node_version#v}"
node_major="${node_major%%.*}"
if [ "$node_major" -lt "$REQUIRED_NODE_MAJOR" ]; then
  fail "Node $node_version found, but $REQUIRED_NODE_MAJOR.x is required (same as the deploy workflow)"
fi
if [ "$node_major" -gt "$REQUIRED_NODE_MAJOR" ]; then
  printf 'setup: warning: Node %s is newer than the %s.x used in CI; continuing\n' "$node_version" "$REQUIRED_NODE_MAJOR" >&2
fi

printf 'setup: node %s, npm %s\n' "$node_version" "$(npm -v)"
printf 'setup: installing dependencies from package-lock.json\n'
npm ci

printf '\nsetup: done. Next:\n'
printf '  npm run dev      # http://localhost:5173\n'
printf '  npm run build    # production build into ./dist\n'
printf '  npm run preview  # serve ./dist at http://localhost:4173\n'

if [ "${1:-}" = "--dev" ]; then
  printf '\nsetup: starting the dev server\n'
  exec npm run dev
fi
