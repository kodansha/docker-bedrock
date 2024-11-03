#!/bin/bash

set -e

source dev-container-features-test-lib

check "check if xdebug is installed" bash -c "pecl list | grep xdebug"
check "check if xdebug is enabled" bash -c "php -i | grep xdebug"
check "check if xdebug config file exists" bash -c "ls -l /usr/local/etc/php/conf.d/xdebug.ini"
check "check if xdebug config file contains xdebug.mode=debug" bash -c "grep 'xdebug.mode=debug' /usr/local/etc/php/conf.d/xdebug.ini"
check "check if xdebug config file contains xdebug.start_with_request=yes" bash -c "grep 'xdebug.start_with_request=yes' /usr/local/etc/php/conf.d/xdebug.ini"
check "check if xdebug config file contains xdebug.client_host=localhost" bash -c "grep 'xdebug.client_host=localhost' /usr/local/etc/php/conf.d/xdebug.ini"
check "check if xdebug config file contains xdebug.client_port=9003" bash -c "grep 'xdebug.client_port=9003' /usr/local/etc/php/conf.d/xdebug.ini"

reportResults
