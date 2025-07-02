# セットアップガイド

## 環境別セットアップ手順

### Windows 11環境

#### 1. 前提条件
- Windows 11 PC
- インターネット接続
- 管理者権限でのコマンド実行が可能

#### 2. Python 3.7.16のインストール
1. [Python公式サイト](https://www.python.org/downloads/release/python-3716/)にアクセス
2. "Windows installer (64-bit)" をダウンロード
3. ダウンロードしたファイルを実行
4. インストール時に **"Add Python to PATH"** にチェックを入れる
5. "Install Now" をクリック

**インストール確認**
```cmd
python --version
```
`Python 3.7.16` と表示されることを確認

#### 3. Gitのインストール
1. [Git公式サイト](https://git-scm.com/download/win)からダウンロード
2. インストーラーを実行（デフォルト設定でOK）

**インストール確認**
```cmd
git --version
```

#### 4. アプリケーションのセットアップ
```cmd
# リポジトリクローン
git clone https://github.com/SB-Dev-Git/WebAppMigration.git
cd WebAppMigration

# ブランチ切り替え
git checkout devin/1750820022-kintai-app-migration

# 仮想環境作成・有効化
python -m venv venv
venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# アプリケーション起動
python app.py
```

#### 5. ブラウザアクセス
http://localhost:5000 にアクセス

### Linux (Ubuntu) 環境

#### 1. システム更新
```bash
sudo apt update && sudo apt upgrade -y
```

#### 2. Python 3.7.16のインストール
```bash
# Python 3.7のインストール
sudo apt install python3.7 python3.7-venv python3.7-dev -y

# pipのインストール
curl https://bootstrap.pypa.io/get-pip.py | python3.7
```

#### 3. 必要パッケージのインストール
```bash
sudo apt install git sqlite3 -y
```

#### 4. アプリケーションセットアップ
```bash
# リポジトリクローン
git clone https://github.com/SB-Dev-Git/WebAppMigration.git
cd WebAppMigration

# ブランチ切り替え
git checkout devin/1750820022-kintai-app-migration

# 仮想環境作成・有効化
python3.7 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# アプリケーション起動
python app.py
```

### AWS EC2 (Amazon Linux 2) 環境

#### 1. EC2インスタンス準備
- インスタンスタイプ: t2.micro以上
- セキュリティグループ: ポート5000を開放
- キーペア: SSH接続用

#### 2. SSH接続
```bash
ssh -i your-key.pem ec2-user@your-ec2-public-ip
```

#### 3. システム準備
```bash
# システム更新
sudo yum update -y

# 開発ツールインストール
sudo yum groupinstall "Development Tools" -y
sudo yum install git sqlite -y
```

#### 4. Python 3.7.16のインストール
```bash
# Python 3.7のビルドとインストール
cd /tmp
wget https://www.python.org/ftp/python/3.7.16/Python-3.7.16.tgz
tar xzf Python-3.7.16.tgz
cd Python-3.7.16
./configure --enable-optimizations
make altinstall
sudo make altinstall

# python3.7コマンドの確認
python3.7 --version
```

#### 5. アプリケーションセットアップ
```bash
# ホームディレクトリに移動
cd ~

# リポジトリクローン
git clone https://github.com/SB-Dev-Git/WebAppMigration.git
cd WebAppMigration

# ブランチ切り替え
git checkout devin/1750820022-kintai-app-migration

# 仮想環境作成・有効化
python3.7 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# アプリケーション起動（外部アクセス許可）
python app.py
```

#### 6. セキュリティグループ設定
AWS管理コンソールで以下を設定：
- インバウンドルール: TCP 5000番ポートを開放
- ソース: 0.0.0.0/0（全体）または特定IPアドレス

#### 7. アクセス確認
http://your-ec2-public-ip:5000 でアクセス

## 本番環境セットアップ

### Gunicorn + Nginx構成

#### 1. Gunicornのインストール
```bash
pip install gunicorn
```

#### 2. Gunicorn設定ファイル作成
```bash
# gunicorn.conf.py
bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
```

#### 3. systemdサービス作成
```bash
sudo nano /etc/systemd/system/kintai-app.service
```

```ini
[Unit]
Description=Kintai App
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/WebAppMigration
Environment=PATH=/home/ec2-user/WebAppMigration/venv/bin
ExecStart=/home/ec2-user/WebAppMigration/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

#### 4. サービス有効化
```bash
sudo systemctl daemon-reload
sudo systemctl enable kintai-app
sudo systemctl start kintai-app
sudo systemctl status kintai-app
```

#### 5. Nginxのインストールと設定
```bash
# Nginxインストール
sudo yum install nginx -y

# 設定ファイル作成
sudo nano /etc/nginx/conf.d/kintai-app.conf
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/ec2-user/WebAppMigration/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

#### 6. Nginx起動
```bash
sudo systemctl enable nginx
sudo systemctl start nginx
sudo systemctl status nginx
```

## SSL/HTTPS設定

### Let's Encryptを使用したSSL証明書設定

#### 1. Certbotのインストール
```bash
sudo yum install certbot python3-certbot-nginx -y
```

#### 2. SSL証明書取得
```bash
sudo certbot --nginx -d your-domain.com
```

#### 3. 自動更新設定
```bash
sudo crontab -e
```

```bash
0 12 * * * /usr/bin/certbot renew --quiet
```

## データベース設定

### SQLiteファイルの権限設定
```bash
# データベースファイルの権限設定
chmod 664 kintai.db
chown ec2-user:ec2-user kintai.db

# ディレクトリの権限設定
chmod 755 /home/ec2-user/WebAppMigration
```

### バックアップ設定
```bash
# バックアップスクリプト作成
nano backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/ec2-user/backups"
DB_FILE="/home/ec2-user/WebAppMigration/kintai.db"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR
cp $DB_FILE $BACKUP_DIR/kintai_backup_$DATE.db

# 30日以上古いバックアップを削除
find $BACKUP_DIR -name "kintai_backup_*.db" -mtime +30 -delete
```

```bash
# 実行権限付与
chmod +x backup_db.sh

# cron設定（毎日午前2時にバックアップ）
crontab -e
0 2 * * * /home/ec2-user/backup_db.sh
```

## 監視・ログ設定

### アプリケーションログ設定
```python
# app.py にログ設定を追加
import logging
from logging.handlers import RotatingFileHandler

if not app.debug:
    file_handler = RotatingFileHandler('logs/kintai.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Kintai app startup')
```

### システム監視
```bash
# ログディレクトリ作成
mkdir -p logs

# システムリソース監視スクリプト
nano monitor.sh
```

```bash
#!/bin/bash
LOG_FILE="/home/ec2-user/WebAppMigration/logs/system.log"
echo "$(date): CPU: $(top -bn1 | grep "Cpu(s)" | awk '{print $2}'), Memory: $(free -m | awk 'NR==2{printf "%.1f%%", $3*100/$2}')" >> $LOG_FILE
```

## 環境変数設定

### 本番環境用環境変数
```bash
# .env ファイル作成
nano .env
```

```bash
FLASK_ENV=production
SECRET_KEY=your-production-secret-key-here
DATABASE_URL=sqlite:///kintai.db
```

### 環境変数の読み込み
```python
# app.py に追加
import os
from dotenv import load_dotenv

load_dotenv()

app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')
```

## トラブルシューティング

よくある問題と解決方法については、[トラブルシューティング](Troubleshooting)ページを参照してください。

## 次のステップ

セットアップが完了したら、[使用方法](User-Guide)ページで機能の使い方を確認してください。
