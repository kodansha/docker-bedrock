#!/bin/bash

set -e

source dev-container-features-test-lib

check "check if redis is installed" bash -c "pecl list | grep redis"
check "check if redis is enabled" bash -c "php -i | grep redis"
check "check if specified version of xdebug is installed" bash -c "pecl list | grep redis | grep '6.1.0RC2'"

reportResults
