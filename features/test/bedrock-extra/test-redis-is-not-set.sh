#!/bin/bash

set -e

source dev-container-features-test-lib

check "check if redis is not installed" bash -c "pecl list | grep -q redis && exit 1 || exit 0"

reportResults
