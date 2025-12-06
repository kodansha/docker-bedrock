#!/bin/bash

set -e

source dev-container-features-test-lib

check "check if redis is installed" bash -c "php -m | grep -i redis"
check "check if redis is enabled" bash -c "php -i | grep -i redis"
check "check if specified version of redis is installed" bash -c "php --ri redis | grep -i 'redis version' | grep '6.1.0RC2'"

reportResults
