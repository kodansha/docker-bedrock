# Docker Image for Bedrock

This is a configured PHP Docker image as a base environment for
[Bedrock](https://roots.io/bedrock/) WordPress boilerplate.

## Package

https://github.com/orgs/kodansha/packages/container/package/bedrock

## Typical Usage Example

### Apache

```dockerfile
FROM ghcr.io/kodansha/bedrock:php8.0 AS base

ENV WEB_ROOT /var/www/html
ENV APACHE_DOCUMENT_ROOT ${WEB_ROOT}/web
ENV COMPOSER_ALLOW_SUPERUSER 1

# PHP file upload configuration
RUN { \
  echo 'memory_limit = 256M'; \
  echo 'post_max_size = 128M'; \
  echo 'upload_max_filesize = 64M'; \
  echo 'max_execution_time = 300'; \
  echo 'max_input_time = 1000'; \
  } > /usr/local/etc/php/conf.d/custom-upload.ini

################################################################################
FROM base AS production

WORKDIR ${WEB_ROOT}

# Install PHP package dependencies
COPY --chown=www-data:www-data composer.json composer.lock ${WEB_ROOT}/
RUN composer install

COPY --chown=www-data:www-data . ${WEB_ROOT}

################################################################################
FROM base AS development

# Install and enable Xdebug
RUN pecl install xdebug \
  && docker-php-ext-enable xdebug
RUN { \
  echo '[xdebug]'; \
  echo 'xdebug.mode=debug'; \
  echo 'xdebug.start_with_request=yes'; \
  echo 'xdebug.client_host=host.docker.internal'; \
  echo 'xdebug.client_port=9003'; \
  } > /usr/local/etc/php/conf.d/custom-xdebug.ini

COPY --from=production --chown=www-data:www-data ${WEB_ROOT}/ ${WEB_ROOT}/
```

### PHP-FPM + Nginx

WIP
