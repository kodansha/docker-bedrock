import requests
import re
import time
import os
from pathlib import Path

def get_latest_php_tags():
    """Docker Hub APIから最新のPHPタグを取得"""
    base_url = "https://registry.hub.docker.com/v2/repositories/library/php/tags/"
    latest_versions = {}
    max_pages = 60  # 最大ページ数を60に設定

    def process_page(url):
        response = requests.get(url)
        data = response.json()
        tags = data['results']

        for tag in tags:
            tag_name = tag['name']
            # 8.x.x および 8.x.x-fpm のパターンに対応
            match = re.match(r'^(\d+\.\d+)(\.(\d+))?(?:-fpm)?$', tag_name)
            if match:
                major_minor = match.group(1)
                patch = int(match.group(3)) if match.group(3) else 0
                tag_type = 'fpm' if '-fpm' in tag_name else 'regular'
                key = (major_minor, tag_type)

                if key not in latest_versions or patch > latest_versions[key][1]:
                    latest_versions[key] = (tag_name, patch)

        return data.get('next')

    next_page_url = base_url
    page_count = 0
    print("Fetching latest PHP versions from Docker Hub", end='', flush=True)
    while next_page_url and page_count < max_pages:
        next_page_url = process_page(next_page_url)
        page_count += 1
        time.sleep(2)  # APIリクエスト間に2秒の間隔を設ける
        print('.', end='', flush=True)

    print(' Done!\n')

    return {k: v[0] for k, v in latest_versions.items()}


def get_current_version_from_dockerfile(dockerfile_path):
    """DockerfileからFROM行のPHPバージョンを抽出"""
    if not os.path.exists(dockerfile_path):
        return None

    with open(dockerfile_path, 'r') as f:
        first_line = f.readline().strip()
        match = re.match(r'^FROM php:([\d.]+)(?:-(.+))?$', first_line)
        if match:
            return match.group(1)
    return None


def update_dockerfile(dockerfile_path, old_version, new_version):
    """DockerfileのFROM行を更新"""
    if not os.path.exists(dockerfile_path):
        return False

    with open(dockerfile_path, 'r') as f:
        content = f.read()

    # FROM行を更新
    new_content = re.sub(
        rf'^FROM php:{re.escape(old_version)}(-[a-z]+)?$',
        rf'FROM php:{new_version}\1',
        content,
        count=1,
        flags=re.MULTILINE
    )

    if content != new_content:
        with open(dockerfile_path, 'w') as f:
            f.write(new_content)
        return True
    return False


def update_workflow_yaml(yaml_path, old_version, new_version):
    """GitHub Actions WorkflowのYAMLファイルを更新"""
    if not os.path.exists(yaml_path):
        return False

    with open(yaml_path, 'r') as f:
        content = f.read()

    # タグ内のバージョンを更新
    new_content = re.sub(
        rf'(bedrock:(?:php)?){re.escape(old_version)}(?=\s|$)',
        rf'\g<1>{new_version}',
        content
    )

    if content != new_content:
        with open(yaml_path, 'w') as f:
            f.write(new_content)
        return True
    return False


def process_version_updates(latest_tags):
    """バージョンごとにファイルを更新"""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    updates = []
    no_updates = []
    errors = []

    # PHPバージョンごとに処理
    versions_to_check = {}

    # latest_tagsから取得した情報を整理
    for (major_minor, tag_type), full_tag in latest_tags.items():
        # 正規表現でバージョンを抽出
        match = re.match(r'^([\d.]+)(?:-(.+))?$', full_tag)
        if match:
            version = match.group(1)
            suffix = match.group(2) or ''

            if major_minor not in versions_to_check:
                versions_to_check[major_minor] = {}
            versions_to_check[major_minor][tag_type] = version

    # バージョンごとに確認・更新
    for major_minor in sorted(versions_to_check.keys()):
        version_info = versions_to_check[major_minor]

        # 整数部分を取得 (例: "8.5" -> "8", "5")
        major, minor = major_minor.split('.')
        dir_prefix = f"php{major}.{minor}"

        # Apache版の処理
        if 'regular' in version_info:
            new_version = version_info['regular']
            apache_dir = project_root / dir_prefix
            dockerfile_path = apache_dir / "Dockerfile"

            if dockerfile_path.exists():
                current_version = get_current_version_from_dockerfile(dockerfile_path)
                if current_version and current_version != new_version:
                    # Dockerfileを更新
                    if update_dockerfile(dockerfile_path, current_version, new_version):
                        # Workflow YAMLも更新
                        yaml_path = project_root / ".github" / "workflows" / f"{dir_prefix}.yml"
                        yaml_updated = update_workflow_yaml(yaml_path, current_version, new_version)

                        updates.append({
                            'version': major_minor,
                            'type': 'Apache',
                            'old': current_version,
                            'new': new_version,
                            'files': [str(dockerfile_path.relative_to(project_root))] +
                                   ([str(yaml_path.relative_to(project_root))] if yaml_updated else [])
                        })
                    else:
                        errors.append(f"{dir_prefix} (Apache): Failed to update Dockerfile")
                elif current_version == new_version:
                    no_updates.append(f"{dir_prefix} (Apache): Already at {new_version}")

        # FPM版の処理
        if 'fpm' in version_info:
            new_version = version_info['fpm']
            fpm_dir = project_root / f"{dir_prefix}-fpm"
            dockerfile_path = fpm_dir / "Dockerfile"

            if dockerfile_path.exists():
                current_version = get_current_version_from_dockerfile(dockerfile_path)
                if current_version and current_version != new_version:
                    # Dockerfileを更新
                    if update_dockerfile(dockerfile_path, current_version, new_version):
                        # Workflow YAMLも更新
                        yaml_path = project_root / ".github" / "workflows" / f"{dir_prefix}.yml"
                        yaml_updated = update_workflow_yaml(yaml_path, current_version, new_version)

                        updates.append({
                            'version': major_minor,
                            'type': 'FPM',
                            'old': current_version,
                            'new': new_version,
                            'files': [str(dockerfile_path.relative_to(project_root))] +
                                   ([str(yaml_path.relative_to(project_root))] if yaml_updated else [])
                        })
                    else:
                        errors.append(f"{dir_prefix}-fpm: Failed to update Dockerfile")
                elif current_version == new_version:
                    no_updates.append(f"{dir_prefix} (FPM): Already at {new_version}")

    return updates, no_updates, errors


def main():
    print("=" * 70)
    print("PHP Docker Image Version Updater")
    print("=" * 70)
    print()

    # 最新バージョンを取得
    latest_tags = get_latest_php_tags()

    # ファイルを更新
    updates, no_updates, errors = process_version_updates(latest_tags)

    # 結果を表示
    if updates:
        print("✅ Updated versions:")
        print("-" * 70)
        for update in updates:
            print(f"  PHP {update['version']} ({update['type']}): {update['old']} → {update['new']}")
            for file in update['files']:
                print(f"    - {file}")
        print()

    if no_updates:
        print("ℹ️  No updates needed:")
        print("-" * 70)
        for msg in no_updates:
            print(f"  {msg}")
        print()

    if errors:
        print("❌ Errors:")
        print("-" * 70)
        for error in errors:
            print(f"  {error}")
        print()

    print("=" * 70)
    print(f"Summary: {len(updates)} updated, {len(no_updates)} up-to-date, {len(errors)} errors")
    print("=" * 70)


if __name__ == "__main__":
    main()
