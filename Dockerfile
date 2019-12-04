FROM php:7.4-apache

################################################################################
# From the official WordPress image
# https://github.com/docker-library/wordpress/blob/master/php7.3/apache/Dockerfile
################################################################################
# install the PHP extensions we need (https://make.wordpress.org/hosting/handbook/handbook/server-environment/#php-extensions)
RUN set -ex; \
  \
  savedAptMark="$(apt-mark showmanual)"; \
  \
  apt-get update; \
  apt-get install -y --no-install-recommends \
  libfreetype6-dev \
  libjpeg-dev \
  libmagickwand-dev \
  libpng-dev \
  libzip-dev \
  ; \
  \
  docker-php-ext-configure gd --with-freetype --with-jpeg; \
  docker-php-ext-install -j "$(nproc)" \
  bcmath \
  exif \
  gd \
  mysqli \
  opcache \
  zip \
  ; \
  pecl install imagick-3.4.4; \
  docker-php-ext-enable imagick; \
  \
  # reset apt-mark's "manual" list so that "purge --auto-remove" will remove all build dependencies
  apt-mark auto '.*' > /dev/null; \
  apt-mark manual $savedAptMark; \
  ldd "$(php -r 'echo ini_get("extension_dir");')"/*.so \
  | awk '/=>/ { print $3 }' \
  | sort -u \
  | xargs -r dpkg-query -S \
  | cut -d: -f1 \
  | sort -u \
  | xargs -rt apt-mark manual; \
  \
  apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
  rm -rf /var/lib/apt/lists/*

# set recommended PHP.ini settings
# see https://secure.php.net/manual/en/opcache.installation.php
RUN { \
  echo 'opcache.memory_consumption=128'; \
  echo 'opcache.interned_strings_buffer=8'; \
  echo 'opcache.max_accelerated_files=4000'; \
  echo 'opcache.revalidate_freq=2'; \
  echo 'opcache.fast_shutdown=1'; \
  } > /usr/local/etc/php/conf.d/opcache-recommended.ini
# https://wordpress.org/support/article/editing-wp-config-php/#configure-error-logging
RUN { \
  # https://www.php.net/manual/en/errorfunc.constants.php
  # https://github.com/docker-library/wordpress/issues/420#issuecomment-517839670
  echo 'error_reporting = E_ERROR | E_WARNING | E_PARSE | E_CORE_ERROR | E_CORE_WARNING | E_COMPILE_ERROR | E_COMPILE_WARNING | E_RECOVERABLE_ERROR'; \
  echo 'display_errors = Off'; \
  echo 'display_startup_errors = Off'; \
  echo 'log_errors = On'; \
  echo 'error_log = /dev/stderr'; \
  echo 'log_errors_max_len = 1024'; \
  echo 'ignore_repeated_errors = On'; \
  echo 'ignore_repeated_source = Off'; \
  echo 'html_errors = Off'; \
  } > /usr/local/etc/php/conf.d/error-logging.ini

RUN set -eux; \
  a2enmod rewrite expires; \
  \
  # https://httpd.apache.org/docs/2.4/mod/mod_remoteip.html
  a2enmod remoteip; \
  { \
  echo 'RemoteIPHeader X-Forwarded-For'; \
  # these IP ranges are reserved for "private" use and should thus *usually* be safe inside Docker
  echo 'RemoteIPTrustedProxy 10.0.0.0/8'; \
  echo 'RemoteIPTrustedProxy 172.16.0.0/12'; \
  echo 'RemoteIPTrustedProxy 192.168.0.0/16'; \
  echo 'RemoteIPTrustedProxy 169.254.0.0/16'; \
  echo 'RemoteIPTrustedProxy 127.0.0.0/8'; \
  } > /etc/apache2/conf-available/remoteip.conf; \
  a2enconf remoteip; \
  # https://github.com/docker-library/wordpress/issues/383#issuecomment-507886512
  # (replace all instances of "%h" with "%a" in LogFormat)
  find /etc/apache2 -type f -name '*.conf' -exec sed -ri 's/([[:space:]]*LogFormat[[:space:]]+"[^"]*)%h([^"]*")/\1%a\2/g' '{}' +
################################################################################

# PHP file upload configuration
RUN { \
  echo 'file_uploads = On'; \
  echo 'memory_limit = 256M'; \
  echo 'upload_max_size = 64M'; \
  echo 'post_max_size = 64M'; \
  echo 'upload_max_filesize = 64M'; \
  echo 'max_execution_time = 300'; \
  echo 'max_input_time = 1000'; \
  } > /usr/local/etc/php/conf.d/upload.ini

# Install extra package dependencies
RUN apt-get update \
  && apt-get install --yes --no-install-recommends \
  git \
  && apt-get clean \
  && rm --recursive --force /var/lib/apt/lists/*

# Install Composer
RUN curl -s http://getcomposer.org/installer | php \
  && mv composer.phar /usr/local/bin/composer

# Install WP-CLI
RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
  && chmod +x wp-cli.phar \
  && mv wp-cli.phar /usr/local/bin/wp

ENV WEB_ROOT /var/www/html
ENV APACHE_DOCUMENT_ROOT ${WEB_ROOT}/web

# Replace webroot strings in Apache config files
RUN sed -ri -e 's!/var/www/html!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/sites-available/*.conf
RUN sed -ri -e 's!/var/www/!${APACHE_DOCUMENT_ROOT}!g' /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf
