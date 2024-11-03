#!/usr/bin/env bash

set -e

OPTIONS_LOCALE="${LOCALE:-"none"}"

if [ "$OPTIONS_LOCALE" != "none" ]; then
    # Install packages
    apt-get update && apt-get install -y \
        locales \
        && apt-get clean \
        && rm -rf /var/lib/apt/lists/*

    sed -i -E "s/# (${OPTIONS_LOCALE})/\1/" /etc/locale.gen
    locale-gen
fi
