#!/bin/bash

set -e

source dev-container-features-test-lib

check "check if redis is not installed" bash -c "php -m | grep -qi redis && exit 1 || exit 0"

reportResults
