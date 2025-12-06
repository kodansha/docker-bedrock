#!/usr/bin/env bash

set -e

OPTIONS_LOCALE="${LOCALE:-"none"}"
OPTIONS_XDEBUG="${XDEBUG:-"false"}"
OPTIONS_XDEBUG_VERSION="${XDEBUGVERSION:-"latest"}"
OPTIONS_XDEBUG_CLIENT_HOST="${XDEBUGCLIENTHOST:-"localhost"}"
OPTIONS_XDEBUG_CLIENT_PORT="${XDEBUGCLIENTPORT:-"9003"}"
OPTIONS_REDIS="${REDIS:-"false"}"
OPTIONS_REDIS_VERSION="${REDISVERSION:-"latest"}"

# Check if pie is available
use_pie() {
    command -v pie &> /dev/null
}

# Install PHP extension using pie or pecl
install_php_extension() {
    local extension_name=$1
    local pecl_name=$2
    local version=$3

    if use_pie; then
        if [ "$version" != "latest" ]; then
            pie install "${extension_name}:${version}"
        else
            pie install "${extension_name}"
        fi
    else
        if [ "$version" != "latest" ]; then
            pecl install "${pecl_name}-${version}"
        else
            pecl install "${pecl_name}"
        fi
        docker-php-ext-enable "${pecl_name}"
    fi
}

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
if [ "$OPTIONS_XDEBUG" = "true" ]; then
    install_php_extension "xdebug/xdebug" "xdebug" "$OPTIONS_XDEBUG_VERSION"

    cat <<EOL | tee /usr/local/etc/php/conf.d/xdebug.ini
[xdebug]
xdebug.mode=debug
xdebug.start_with_request=yes
xdebug.client_host=${OPTIONS_XDEBUG_CLIENT_HOST}
xdebug.client_port=${OPTIONS_XDEBUG_CLIENT_PORT}
EOL
fi

# Redis installation
if [ "$OPTIONS_REDIS" = "true" ]; then
    install_php_extension "phpredis/phpredis" "redis" "$OPTIONS_REDIS_VERSION"
fi
