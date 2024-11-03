#!/usr/bin/env bash

set -e

OPTIONS_LOCALE="${LOCALE:-"none"}"
OPTIONS_XDEBUG="${XDEBUG:-"false"}"
OPTIONS_XDEBUG_VERSION="${XDEBUG_VERSION:-"latest"}"
OPTIONS_XDEBUG_CLIENT_HOST="${XDEBUG_CLIENT_HOST:-"localhost"}"
OPTIONS_XDEBUG_CLIENT_PORT="${XDEBUG_CLIENT_PORT:-"9003"}"

# Install packages
apt-get update && apt-get install -y \
    locales \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Locale configuration
if [ "$OPTIONS_LOCALE" != "none" ]; then
    sed -i -E "s/# (${OPTIONS_LOCALE})/\1/" /etc/locale.gen
    locale-gen
fi

# Xdebug installation
if [ "$OPTIONS_XDEBUG" != "false" ]; then
    if [ "$OPTIONS_XDEBUG_VERSION" != "latest" ]; then
        pecl install xdebug-${OPTIONS_XDEBUG_VERSION}
    else
        pecl install xdebug
    fi

    docker-php-ext-enable xdebug

    cat <<EOL | tee /usr/local/etc/php/conf.d/xdebug.ini
[xdebug]
xdebug.mode=debug
xdebug.start_with_request=yes
xdebug.client_host=${OPTIONS_XDEBUG_CLIENT_HOST}
xdebug.client_port=${OPTIONS_XDEBUG_CLIENT_PORT}
EOL
fi
