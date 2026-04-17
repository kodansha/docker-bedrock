#!/usr/bin/env bats

load 'test_helper/bats-support/load'
load 'test_helper/bats-assert/load'

IMAGE="${IMAGE:-ghcr.io/kodansha/bedrock:php8.4}"

setup_file() {
  local container_id
  container_id=$(docker run -d --rm --pull=always "$IMAGE" sleep infinity)
  echo "$container_id" > "$BATS_FILE_TMPDIR/container_id"

  local php_ver composer_ver wpcli_ver
  php_ver=$(docker exec "$container_id" php -r 'echo PHP_VERSION;')
  composer_ver=$(docker exec "$container_id" composer --version 2>/dev/null | awk '/^Composer version/{print $3}')
  wpcli_ver=$(docker exec "$container_id" wp --info --allow-root 2>/dev/null | grep 'WP-CLI version' | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')

  printf '# \n' >&3
  printf '# ════════════════════════════════════════════\n' >&3
  printf '#   %s\n' "$IMAGE" >&3
  printf '# ════════════════════════════════════════════\n' >&3
  printf '#   PHP:      %s\n' "$php_ver" >&3
  printf '#   Composer: %s\n' "$composer_ver" >&3
  printf '#   WP-CLI:   %s\n' "$wpcli_ver" >&3
  printf '# \n' >&3
}

teardown_file() {
  docker stop "$(cat "$BATS_FILE_TMPDIR/container_id")" > /dev/null
}

dc() {
  docker exec "$(cat "$BATS_FILE_TMPDIR/container_id")" "$@"
}

# ---------------------------------------------------------------------------
# PHP
# ---------------------------------------------------------------------------

@test "PHP version is 8.4.x" {
  run dc php --version
  assert_success
  assert_output --partial "PHP 8.4"
}

@test "PHP extension: bcmath" {
  run dc php -m
  assert_success
  assert_output --partial "bcmath"
}

@test "PHP extension: exif" {
  run dc php -m
  assert_success
  assert_output --partial "exif"
}

@test "PHP extension: gd" {
  run dc php -m
  assert_success
  assert_output --partial "gd"
}

@test "PHP extension: intl" {
  run dc php -m
  assert_success
  assert_output --partial "intl"
}

@test "PHP extension: mysqli" {
  run dc php -m
  assert_success
  assert_output --partial "mysqli"
}

@test "PHP extension: zip" {
  run dc php -m
  assert_success
  assert_output --partial "zip"
}

@test "PHP extension: imagick" {
  run dc php -m
  assert_success
  assert_output --partial "imagick"
}

@test "PHP extension: opcache" {
  run dc php -m
  assert_success
  assert_output --partial "Zend OPcache"
}

@test "PHP ini: expose_php is Off" {
  run dc bash -c "php -i | grep '^expose_php'"
  assert_success
  assert_output --partial "Off"
}

@test "PHP ini: zend.exception_ignore_args is On" {
  run dc bash -c "php -i | grep 'zend.exception_ignore_args'"
  assert_success
  assert_output --partial "On"
}

# ---------------------------------------------------------------------------
# Tools
# ---------------------------------------------------------------------------

@test "composer is installed" {
  run dc composer --version
  assert_success
}

@test "wp-cli is installed" {
  run dc wp --info --allow-root
  assert_success
}

# ---------------------------------------------------------------------------
# System packages
# ---------------------------------------------------------------------------

@test "ghostscript is installed" {
  run dc gs --version
  assert_success
}

@test "git is installed" {
  run dc git --version
  assert_success
}

@test "unzip is installed" {
  run dc bash -c "command -v unzip"
  assert_success
}

# ---------------------------------------------------------------------------
# Apache modules
# ---------------------------------------------------------------------------

@test "Apache module: rewrite is enabled" {
  run dc a2query -m rewrite
  assert_success
}

@test "Apache module: expires is enabled" {
  run dc a2query -m expires
  assert_success
}

@test "Apache module: remoteip is enabled" {
  run dc a2query -m remoteip
  assert_success
}

# ---------------------------------------------------------------------------
# Environment variables
# ---------------------------------------------------------------------------

@test "COMPOSER_ALLOW_SUPERUSER is 1" {
  run dc bash -c 'echo "$COMPOSER_ALLOW_SUPERUSER"'
  assert_success
  assert_output "1"
}

@test "COMPOSER_NO_INTERACTION is 1" {
  run dc bash -c 'echo "$COMPOSER_NO_INTERACTION"'
  assert_success
  assert_output "1"
}

@test "APACHE_DOCUMENT_ROOT is /var/www/html/web" {
  run dc bash -c 'echo "$APACHE_DOCUMENT_ROOT"'
  assert_success
  assert_output "/var/www/html/web"
}
