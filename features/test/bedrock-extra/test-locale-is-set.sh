#!/bin/bash

set -e

source dev-container-features-test-lib

check "check if locale is installed" bash -c "which locale | grep 'locale'"
check "check if locale config for specified language is enabled" bash -c "locale -a | grep '^ja_JP.utf8$'"
check "check if LANG is set via containerEnv" bash -c "locale | grep '^LANG=ja_JP.UTF-8$'"

reportResults
