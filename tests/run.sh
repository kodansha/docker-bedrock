#!/usr/bin/env bash
# Run bats tests with passing tests suppressed from output.
# Usage: tests/run.sh [bats options] [test files...]
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
"$SCRIPT_DIR/bats/bin/bats" --formatter tap "$@" | grep -v '^ok [0-9]'
exit "${PIPESTATUS[0]}"
