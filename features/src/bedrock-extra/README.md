# Bedrock (Modern WordPress Boilerplate) Extra Features

This feature enhances the developer experience by adding some additional tools and configurations to the [Docker Image for Bedrock
](https://github.com/kodansha/docker-bedrock) devcontainer.

## Main Features

- Install and configure locale package
- Install and configure [Xdebug](https://xdebug.org)
- Set the environment variable `WP_CLI_ALLOW_ROOT` to `1` to avoid spamming `--allow-root` every time you run WP CLI commands

## Options

| Options Id | Description | Type | Default Value | Example |
|-----|-----|-----|-----|-----|
| locale | Install and configure the specified locale | string | none | ja_JP.UTF-8 |
| xdebug | Whether to install Xdebug | boolean | false | true |
| xdebugVersion | Xdebug version to install (effective only if `xdebug` is true) | string | latest | 3.3.0 |
| xdebugClientHost | Xdebug client host (effective only if `xdebug` is true) | string | localhost | host.docker.internal |
| xdebugClientPort | Xdebug client port (effective only if `xdebug` is true) | string | 9003 | 9000 |

## Example Usage

```jsonc
{
    // ... other devcontainer.json settings

    "image": "ghcr.io/kodansha/bedrock:php8.3-fpm",
    "features": {
        "ghcr.io/kodansha/docker-bedrock/bedrock-extra:1": {
            "locale": "ja_JP.UTF-8",
            "xdebug": true,
            "xdebugVersion": "3.3.0",
            "xdebugClientHost": "host.docker.internal",
            "xdebugClientPort": "9000"
        }
    },
    "containerEnv": {
        // Set the configured locale to the container environment variable: LANG
        "LANG": "ja_JP.UTF-8"
    }

    // ... other devcontainer.json settings
}
```

## OS Support

This Feature is intended to work only on [Docker Image for Bedrock
](https://github.com/kodansha/docker-bedrock).
