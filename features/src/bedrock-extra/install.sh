#!/usr/bin/env bash

set -e

OPTIONS_LOCALE="${LOCALE:-"none"}"

if [ "$OPTIONS_LOCALE" != "none" ]; then
    sed -i -E "s/# (${OPTIONS_LOCALE})/\1/" /etc/locale.gen
    locale-gen
fi
