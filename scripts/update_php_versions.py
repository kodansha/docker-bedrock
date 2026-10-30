import re
import sys
from pathlib import Path

import requests

# Supported (non-EOSL) PHP versions
SUPPORTED_VERSIONS = ["8.2", "8.3", "8.4", "8.5"]

# Dockerfile directory suffix -> Docker Hub tag suffix
VARIANTS = {"": "apache", "-fpm": "fpm"}

PHP_RELEASES_URL = "https://www.php.net/releases/index.php"
DOCKER_HUB_TAG_URL = "https://hub.docker.com/v2/namespaces/library/repositories/php/tags/{tag}"

project_root = Path(__file__).parent.parent


def get_latest_php_release(major_minor):
    """Fetch the latest release of a PHP branch (e.g. 8.5 -> 8.5.12) from php.net"""
    response = requests.get(PHP_RELEASES_URL, params={"json": "", "version": major_minor}, timeout=30)
    response.raise_for_status()
    return response.json()["version"]


def docker_hub_tag_exists(tag):
    """Check whether a tag of the official php image exists on Docker Hub"""
    response = requests.get(DOCKER_HUB_TAG_URL.format(tag=tag), timeout=30)
    if response.status_code == 404:
        return False
    response.raise_for_status()
    return True


def parse_version(version):
    return tuple(int(part) for part in version.split("."))


def get_current_version(dockerfile_path):
    """Extract the PHP version from the FROM line in a Dockerfile"""
    match = re.search(r"^FROM php:([\d.]+)-", dockerfile_path.read_text(), flags=re.MULTILINE)
    return match.group(1) if match else None


def update_dockerfile(dockerfile_path, old_version, new_version):
    """Update the FROM line in a Dockerfile"""
    content = dockerfile_path.read_text()
    new_content = re.sub(
        rf"^FROM php:{re.escape(old_version)}-",
        f"FROM php:{new_version}-",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    if content == new_content:
        return False
    dockerfile_path.write_text(new_content)
    return True


def main():
    updates = []
    no_updates = []
    errors = []

    for major_minor in SUPPORTED_VERSIONS:
        try:
            latest = get_latest_php_release(major_minor)
        except (requests.RequestException, KeyError, ValueError) as e:
            errors.append(f"PHP {major_minor}: Failed to fetch the latest release from php.net ({e})")
            continue

        for dir_suffix, tag_suffix in VARIANTS.items():
            label = f"php{major_minor}{dir_suffix}"
            dockerfile_path = project_root / label / "Dockerfile"
            current = get_current_version(dockerfile_path)
            if current is None:
                errors.append(f"{label}: Could not read the PHP version from {dockerfile_path}")
                continue

            if parse_version(latest) <= parse_version(current):
                no_updates.append(f"{label}: Already at {current}")
                continue

            tag = f"{latest}-{tag_suffix}"
            try:
                exists = docker_hub_tag_exists(tag)
            except requests.RequestException as e:
                errors.append(f"{label}: Failed to check php:{tag} on Docker Hub ({e})")
                continue
            if not exists:
                no_updates.append(f"{label}: PHP {latest} released, but php:{tag} is not on Docker Hub yet")
                continue

            if update_dockerfile(dockerfile_path, current, latest):
                updates.append(f"{label}: {current} → {latest}")
            else:
                errors.append(f"{label}: Failed to update {dockerfile_path}")

    for title, messages in [("✅ Updated", updates), ("ℹ️  No updates needed", no_updates), ("❌ Errors", errors)]:
        if messages:
            print(f"{title}:")
            for message in messages:
                print(f"  {message}")
            print()

    print(f"Summary: {len(updates)} updated, {len(no_updates)} up-to-date, {len(errors)} errors")

    if errors:
        sys.exit(1)


if __name__ == "__main__":
    main()
