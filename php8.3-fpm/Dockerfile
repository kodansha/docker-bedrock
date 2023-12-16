FROM php:8.3.0-fpm

################################################################################
# From the official WordPress image
# https://github.com/docker-library/wordpress
################################################################################
# The official WordPress Dockerfile START
# persistent dependencies
RUN set -eux; \
	apt-get update; \
	apt-get install -y --no-install-recommends \
	# Ghostscript is required for rendering PDF previews
	ghostscript \
	; \
	rm -rf /var/lib/apt/lists/*

# install the PHP extensions we need (https://make.wordpress.org/hosting/handbook/handbook/server-environment/#php-extensions)
RUN set -ex; \
	\
	savedAptMark="$(apt-mark showmanual)"; \
	\
	apt-get update; \
	apt-get install -y --no-install-recommends \
	libfreetype6-dev \
	libicu-dev \
	libjpeg-dev \
	libmagickwand-dev \
	libpng-dev \
	libwebp-dev \
	libzip-dev \
	; \
	\
	docker-php-ext-configure gd \
	--with-freetype \
	--with-jpeg \
	--with-webp \
	; \
	docker-php-ext-install -j "$(nproc)" \
	bcmath \
	exif \
	gd \
	intl \
	mysqli \
	zip \
	; \
	# https://pecl.php.net/package/imagick
	pecl install imagick-3.6.0; \
	docker-php-ext-enable imagick; \
	rm -r /tmp/pear; \
	\
	# some misbehaving extensions end up outputting to stdout 🙈 (https://github.com/docker-library/wordpress/issues/669#issuecomment-993945967)
	out="$(php -r 'exit(0);')"; \
	[ -z "$out" ]; \
	err="$(php -r 'exit(0);' 3>&1 1>&2 2>&3)"; \
	[ -z "$err" ]; \
	\
	extDir="$(php -r 'echo ini_get("extension_dir");')"; \
	[ -d "$extDir" ]; \
	# reset apt-mark's "manual" list so that "purge --auto-remove" will remove all build dependencies
	apt-mark auto '.*' > /dev/null; \
	apt-mark manual $savedAptMark; \
	ldd "$extDir"/*.so \
	| awk '/=>/ { so = $(NF-1); if (index(so, "/usr/local/") == 1) { next }; gsub("^/(usr/)?", "", so); print so }' \
	| sort -u \
	| xargs -r dpkg-query --search \
	| cut -d: -f1 \
	| sort -u \
	| xargs -rt apt-mark manual; \
	\
	apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
	rm -rf /var/lib/apt/lists/*; \
	\
	! { ldd "$extDir"/*.so | grep 'not found'; }; \
	# check for output like "PHP Warning:  PHP Startup: Unable to load dynamic library 'foo' (tried: ...)
	err="$(php --version 3>&1 1>&2 2>&3)"; \
	[ -z "$err" ]

# set recommended PHP.ini settings
# see https://secure.php.net/manual/en/opcache.installation.php
RUN set -eux; \
	docker-php-ext-enable opcache; \
	{ \
	echo 'opcache.memory_consumption=128'; \
	echo 'opcache.interned_strings_buffer=8'; \
	echo 'opcache.max_accelerated_files=4000'; \
	echo 'opcache.revalidate_freq=2'; \
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
# The official WordPress Dockerfile END
################################################################################

# Change www-data user's UID and GID to 101 to match nginx user's UID and GID in the official nginx image.
# https://hub.docker.com/_/nginx
# https://stackoverflow.com/questions/36824222/how-to-change-the-nginx-process-user-of-the-official-docker-image-nginx
RUN usermod -u 101 -o www-data \
	&& groupmod -g 101 -o www-data

# Install extra package dependencies
RUN apt-get update \
	&& apt-get install --yes --no-install-recommends \
	git \
	unzip \
	&& apt-get clean \
	&& rm --recursive --force /var/lib/apt/lists/*

# Install PHP extra extension
RUN pecl install redis-5.3.7 \
	&& docker-php-ext-enable redis \
	&& rm -r /tmp/pear

# PHP custom configuration
RUN { \
	echo 'zend.exception_ignore_args = On'; \
	echo 'expose_php = Off'; \
	} > /usr/local/etc/php/conf.d/custom.ini

# Install Composer
RUN php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');" \
	&& php composer-setup.php --install-dir=/usr/local/bin --filename=composer \
	&& php -r "unlink('composer-setup.php');" \
	&& composer --version

# Install WP-CLI
RUN curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
	&& chmod +x wp-cli.phar \
	&& mv wp-cli.phar /usr/local/bin/wp \
	&& wp --info
