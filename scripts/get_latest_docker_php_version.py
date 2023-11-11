import requests
import re
import time

def get_latest_php_tags():
    base_url = "https://registry.hub.docker.com/v2/repositories/library/php/tags/"
    latest_versions = {}
    max_pages = 10  # 最大ページ数を10に設定

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
    while next_page_url and page_count < max_pages:
        next_page_url = process_page(next_page_url)
        page_count += 1
        time.sleep(3)  # APIリクエスト間に3秒の間隔を設ける

    return {k: v[0] for k, v in latest_versions.items()}

latest_tags = get_latest_php_tags()
for (version, tag_type), tag in latest_tags.items():
    print(f"Latest tag for PHP {version} {'FPM' if tag_type == 'fpm' else ''}: {tag}")
