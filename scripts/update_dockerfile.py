import requests
import os

# 設定辞書
configurations = {
    "8.4": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.4/apache/Dockerfile",
        "end_phrase": "find /etc/apache2 -type f -name '*.conf' -exec sed -ri 's/([[:space:]]*LogFormat[[:space:]]+\"[^\"]*)%h([^\"]*\")/\\1%a\\2/g' '{}' +",
        "dockerfile_path": "../php8.4/Dockerfile"
    },
    "8.4-fpm": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.4/fpm/Dockerfile",
        "end_phrase": "} > /usr/local/etc/php/conf.d/error-logging.ini",
        "dockerfile_path": "../php8.4-fpm/Dockerfile"
    },
    "8.3": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.3/apache/Dockerfile",
        "end_phrase": "find /etc/apache2 -type f -name '*.conf' -exec sed -ri 's/([[:space:]]*LogFormat[[:space:]]+\"[^\"]*)%h([^\"]*\")/\\1%a\\2/g' '{}' +",
        "dockerfile_path": "../php8.3/Dockerfile"
    },
    "8.3-fpm": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.3/fpm/Dockerfile",
        "end_phrase": "} > /usr/local/etc/php/conf.d/error-logging.ini",
        "dockerfile_path": "../php8.3-fpm/Dockerfile"
    },
    "8.2": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.2/apache/Dockerfile",
        "end_phrase": "find /etc/apache2 -type f -name '*.conf' -exec sed -ri 's/([[:space:]]*LogFormat[[:space:]]+\"[^\"]*)%h([^\"]*\")/\\1%a\\2/g' '{}' +",
        "dockerfile_path": "../php8.2/Dockerfile"
    },
    "8.2-fpm": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.2/fpm/Dockerfile",
        "end_phrase": "} > /usr/local/etc/php/conf.d/error-logging.ini",
        "dockerfile_path": "../php8.2-fpm/Dockerfile"
    },
    "8.1": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.1/apache/Dockerfile",
        "end_phrase": "find /etc/apache2 -type f -name '*.conf' -exec sed -ri 's/([[:space:]]*LogFormat[[:space:]]+\"[^\"]*)%h([^\"]*\")/\\1%a\\2/g' '{}' +",
        "dockerfile_path": "../php8.1/Dockerfile"
    },
    "8.1-fpm": {
        "download_url": "https://raw.githubusercontent.com/docker-library/wordpress/master/latest/php8.1/fpm/Dockerfile",
        "end_phrase": "} > /usr/local/etc/php/conf.d/error-logging.ini",
        "dockerfile_path": "../php8.1-fpm/Dockerfile"
    }
}

# 各バージョンの Dockerfile を処理
for version, config in configurations.items():
    print(f"バージョン {version} の処理を開始します。")

    # ダウンロードしてテキストを取得
    response = requests.get(config["download_url"])
    lines = response.text.split('\n')

    # 抽出する範囲を特定
    start_phrase = "# persistent dependencies"
    end_phrase = config["end_phrase"]
    start_index = end_index = None

    for i, line in enumerate(lines):
        if start_phrase in line:
            start_index = i
        elif end_phrase in line and start_index is not None:
            end_index = i
            break

    # .temp.txt に必要な部分を保存
    temp_file = ".temp.txt"
    if start_index is not None and end_index is not None:
        with open(temp_file, 'w') as file:
            for line in lines[start_index:end_index + 1]:
                file.write(line + '\n')

        print(f"抽出が完了し、{temp_file} に保存されました。")

        # Dockerfile のパス
        dockerfile_path = config["dockerfile_path"]

        # 置き換える範囲の開始と終了のマーカー
        start_marker = "# The official WordPress Dockerfile START\n"
        end_marker = "# The official WordPress Dockerfile END\n"

        # Dockerfile を読み込む
        with open(dockerfile_path, 'r') as file:
            dockerfile_contents = file.readlines()

        # 置き換える範囲を見つける
        start_index = end_index = None
        for i, line in enumerate(dockerfile_contents):
            if line.strip() == start_marker.strip():
                start_index = i
            elif line.strip() == end_marker.strip() and start_index is not None:
                end_index = i
                break

        # 範囲を置き換える
        if start_index is not None and end_index is not None:
            with open(temp_file, 'r') as file:
                replacement_content = file.readlines()

            dockerfile_contents[start_index:end_index + 1] = [start_marker] + replacement_content + [end_marker]

            # 変更を保存する
            with open(dockerfile_path, 'w') as file:
                file.writelines(dockerfile_contents)

            print(f"Dockerfile ({dockerfile_path}) の置き換えが完了しました。")
        else:
            print("指定された範囲が Dockerfile で見つかりませんでした。")

        # .temp.txt を削除
        os.remove(temp_file)
        print(f"{temp_file} が削除されました。")
    else:
        print("指定された範囲が元のファイルで見つかりませんでした。")
