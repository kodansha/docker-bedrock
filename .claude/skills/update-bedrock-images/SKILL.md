---
name: update-bedrock-images
description: Bedrock の Docker ベースイメージの PHP バージョンをアップデートするスキル。EOSL になっていない PHP バージョン (現在は 8.2, 8.3, 8.4, 8.5) のイメージを Docker Hub の最新バージョンに更新し、PR を作成する。
---

# Update Bedrock Docker Images

## 概要

Bedrock の Docker ベースイメージを最新の PHP バージョンにアップデートする。
対象は EOSL になっていない PHP バージョン (現在は 8.2, 8.3, 8.4, 8.5)。

## 前提条件

- このスキルは `docker-bedrock` リポジトリのルートディレクトリで実行すること
- Python の仮想環境が `.venv/` に存在し、`requests` パッケージがインストール済みであること
- GitHub CLI (`gh`) が使用可能であること

## 手順

以下の手順を順番に実行する。

### 0. main ブランチを最新に更新

```bash
git checkout main
git pull origin main
```

### 1. Docker Hub から最新の PHP バージョンを取得

`scripts/get_latest_docker_php_version.py` を実行して、Docker Hub で公開されている最新の PHP バージョンを取得する。

```bash
.venv/bin/python scripts/get_latest_docker_php_version.py
```

**注意: このスクリプトは Docker Hub API を複数ページにわたってフェッチするため、実行完了まで2分程度かかる。** タイムアウトに注意すること。

このスクリプトは以下を行う:

- Docker Hub API から最新の PHP タグを取得
- 各バージョンの Dockerfile と `.github/workflows/` 以下の YAML ファイルを自動更新
- 更新結果のサマリーを出力

### 2. 更新の確認

スクリプトの出力を確認し、更新が発生したかどうかを判断する。
「0 updated」の場合はすべて最新であり、ユーザーにその旨を伝えて終了する。

### 3. トピックブランチの作成と変更内容の確認

更新がある場合、main ブランチからトピックブランチを作成する。

```bash
git checkout -b update-YYYYMMDD
```

ブランチ名の `YYYYMMDD` は当日の日付にする (例: `update-20260311`)。

手順1のスクリプトにより、以下のファイルが自動的に更新されている:

- **`php8.X/Dockerfile`** - FROM 行の PHP バージョン (例: `FROM php:8.4.15` → `FROM php:8.4.16`)
- **`php8.X-fpm/Dockerfile`** - FROM 行の PHP バージョン (例: `FROM php:8.4.15-fpm` → `FROM php:8.4.16-fpm`)
- **`.github/workflows/php8.X.yml`** - Docker イメージタグのうち **Apache 版のみ** 自動更新される (例: `kodansha/bedrock:php8.4.15` → `kodansha/bedrock:php8.4.16`)

**注意: スクリプトの正規表現の制約により、workflow YAML 内の FPM 版タグ (`php8.X.Y-fpm`) は自動更新されない。** `-fpm` サフィックス付きタグは手動で更新する必要がある:

- `kodansha/bedrock:php8.X.Y-fpm` → 新しいバージョンに更新
- `ghcr.io/kodansha/bedrock:php8.X.Y-fpm` → 新しいバージョンに更新

`git diff` で変更内容を確認し、以下の点をチェックすること:

1. **すべての対象バージョン** (8.2, 8.3, 8.4, 8.5) の Dockerfile と workflow YAML が漏れなく更新されているか
2. **workflow YAML 内の FPM タグ** を手動で正しいバージョンに更新したか (`kodansha/bedrock:` と `ghcr.io/kodansha/bedrock:` の両方)

**重要: Dockerfile のフォーマットは絶対にしないこと。** 不要な差分が発生するため。

### 4. WordPress 公式 Dockerfile の更新確認

`scripts/update_dockerfile.py` を実行し、Docker 公式 WordPress イメージの更新がないかを確認する。

**注意: このスクリプトは相対パスで Dockerfile を参照するため、`scripts/` ディレクトリから実行する必要がある。**

```bash
cd scripts && ../.venv/bin/python update_dockerfile.py && cd ..
```

このスクリプトは WordPress 公式 Dockerfile から `# persistent dependencies` から各種設定までの部分を抽出し、ローカルの Dockerfile の `# The official WordPress Dockerfile START` ~ `# The official WordPress Dockerfile END` の間に反映する。

更新があった場合、差分を確認する。**Dockerfile のフォーマットは絶対にしないこと。**

### 5. コミット

変更されたファイルをすべてステージングしてコミットする。
コミットメッセージには、更新された PHP バージョンをカンマ区切りで列挙する。

例: `PHP 8.2.28, 8.3.22, 8.4.16, 8.5.0`

WordPress Dockerfile の更新もあった場合はコミットメッセージに追記する。

例: `PHP 8.3.22, 8.4.16 / WordPress Dockerfile 更新`

### 6. GitHub に push して PR を作成

```bash
git push -u origin update-YYYYMMDD
```

PR のタイトルはコミットメッセージと同じにし、本文には更新されたバージョンの詳細を記載する。

PR 作成後、**マージまで実行するかどうかをユーザーに尋ねること。**

### 7. マージ (ユーザーが選択した場合)

ユーザーがマージを選択した場合:

1. PR を main にマージする
2. トピックブランチをリモートとローカルで削除する
3. main ブランチに切り替え、pull して最新にする

```bash
gh pr merge --merge
git checkout main
git pull origin main
git branch -d update-YYYYMMDD
```

ユーザーがマージを選択しなかった場合は、PR の URL を表示して終了する。
