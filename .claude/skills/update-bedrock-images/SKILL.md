---
name: update-bedrock-images
description: A skill for updating PHP versions in Bedrock Docker base images. Updates images for non-EOSL PHP versions (currently 8.2, 8.3, 8.4, 8.5) to the latest versions on Docker Hub and creates a PR.
---

# Update Bedrock Docker Images

## Overview

Update Bedrock Docker base images to the latest PHP versions.
Targets non-EOSL PHP versions (currently 8.2, 8.3, 8.4, 8.5).

## Prerequisites

- This skill must be run from the root directory of the `docker-bedrock` repository
- `mise` and `uv` must be available (Python 3.13 and dependencies are managed automatically)
- GitHub CLI (`gh`) must be available

## Steps

Execute the following steps in order.

### 0. Update the main branch to the latest

```bash
git checkout main
git pull origin main
```

### 1. Fetch the latest PHP versions from Docker Hub

Run `scripts/update_php_versions.py` to fetch the latest PHP versions published on Docker Hub.

```bash
mise run update-php-versions
```

**Note: This script fetches multiple pages from the Docker Hub API, so it takes about 2 minutes to complete.** Be mindful of timeouts.

This script does the following:

- Fetches the latest PHP tags from the Docker Hub API
- Automatically updates the Dockerfile and YAML files under `.github/workflows/` for each version
- Outputs a summary of the updates

### 2. Verify the updates

Check the script output to determine whether any updates occurred.
If the output shows "0 updated", everything is already up to date — inform the user and stop.

### 3. Create a topic branch and review the changes

If there are updates, create a topic branch from main.

```bash
git checkout -b update-YYYYMMDD
```

Replace `YYYYMMDD` in the branch name with today's date (e.g., `update-20260311`).

The script from step 1 will have automatically updated the following files:

- **`php8.X/Dockerfile`** - PHP version in the FROM line (e.g., `FROM php:8.4.15` → `FROM php:8.4.16`)
- **`php8.X-fpm/Dockerfile`** - PHP version in the FROM line (e.g., `FROM php:8.4.15-fpm` → `FROM php:8.4.16-fpm`)
- **`.github/workflows/php8.X.yml`** - Only the **Apache variant** image tags are automatically updated (e.g., `kodansha/bedrock:php8.4.15` → `kodansha/bedrock:php8.4.16`)

**Note: Due to regex limitations in the script, FPM variant tags (`php8.X.Y-fpm`) in the workflow YAML are NOT automatically updated.** Tags with the `-fpm` suffix must be updated manually:

- `kodansha/bedrock:php8.X.Y-fpm` → update to the new version
- `ghcr.io/kodansha/bedrock:php8.X.Y-fpm` → update to the new version

Use `git diff` to review the changes and verify the following:

1. Dockerfiles and workflow YAMLs for **all target versions** (8.2, 8.3, 8.4, 8.5) have been updated without omission
2. **FPM tags in workflow YAMLs** have been manually updated to the correct version (both `kodansha/bedrock:` and `ghcr.io/kodansha/bedrock:`)

**Important: Never reformat Dockerfiles.** This would introduce unnecessary diffs.

### 4. Check for WordPress official Dockerfile updates

Run `scripts/update_dockerfile.py` to check for any updates to the official Docker WordPress image.

```bash
mise run update-dockerfile
```

This script extracts the section from `# persistent dependencies` through the various settings in the official WordPress Dockerfile, and applies it to the local Dockerfile between `# The official WordPress Dockerfile START` and `# The official WordPress Dockerfile END`.

If there are updates, review the diff. **Never reformat Dockerfiles.**

### 5. Commit

Stage all changed files and commit.
List the updated PHP versions in the commit message, separated by commas.

Example: `PHP 8.2.28, 8.3.22, 8.4.16, 8.5.0`

If there are also WordPress Dockerfile updates, append that to the commit message.

Example: `PHP 8.3.22, 8.4.16 / WordPress Dockerfile updated`

### 6. Push to GitHub and create a PR

```bash
git push -u origin update-YYYYMMDD
```

Use the same text as the commit message for the PR title, and include details of the updated versions in the PR body.

After creating the PR, **ask the user whether to proceed with merging.**

### 7. Merge (if the user chooses to)

If the user chooses to merge:

1. Merge the PR into main
2. Delete the topic branch from both remote and local
3. Switch to the main branch and pull to get the latest

```bash
gh pr merge --merge
git checkout main
git pull origin main
git branch -d update-YYYYMMDD
```

If the user chooses not to merge, display the PR URL and stop.
