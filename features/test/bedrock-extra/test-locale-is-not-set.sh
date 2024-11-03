#!/bin/bash

set -e

source dev-container-features-test-lib

check "check if locale is installed" bash -c "which locale | grep 'locale'"
check "check if LANG is not set" bash -c "locale | grep '^LANG=$'"

reportResults
