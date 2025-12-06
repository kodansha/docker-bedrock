#!/bin/bash

set -e

source dev-container-features-test-lib

check "check if xdebug is not installed" bash -c "php -m | grep -qi xdebug && exit 1 || exit 0"
check "check if xdebug is not enabled" bash -c "php -i | grep -qi 'xdebug.version' && exit 1 || exit 0"

reportResults
