# Docker Image for Bedrock

This is a configured PHP Docker image as a base environment for
[Bedrock](https://roots.io/bedrock/) WordPress boilerplate.

## Package

https://github.com/orgs/kodansha/packages/container/package/bedrock

## Dev Container Features

The Docker Image for Bedrock is designed to be used in both production and
development environments. However, in development, there may be situations where
additional customization is needed, such as installing Xdebug.

To address this, we provide typical development configurations as a Dev Container
Feature. For more details, please refer to https://github.com/kodansha/docker-bedrock/tree/main/features/src/bedrock-extra.

## Testing

Tests are written with [bats-core](https://bats-core.readthedocs.io/) and run locally against images already published to the GitHub Container Registry. Run tests **after** a new image has been pushed.

### Prerequisites

bats-core and its helper libraries are managed as Git submodules. After cloning this repository, initialize them with:

```bash
git submodule update --init
```

### Running tests

Each test file pulls the latest image from the registry automatically before running, and removes the container when finished.

Use `tests/run.sh` to run tests. It suppresses passing test output, and always prints the image name and tool versions (PHP, Composer, WP-CLI, etc.) at the start of each file's results. Only failures are shown in detail.

```bash
# Run a single version
tests/run.sh tests/php8.5.bats
tests/run.sh tests/php8.5-fpm.bats

# Run all versions at once
tests/run.sh tests/
```

To test a specific tag, set the `IMAGE` environment variable:

```bash
IMAGE=ghcr.io/kodansha/bedrock:php8.5.3 tests/run.sh tests/php8.5.bats
```

You can also invoke bats directly if you prefer the full test-by-test output:

```bash
tests/bats/bin/bats tests/php8.5.bats
```
