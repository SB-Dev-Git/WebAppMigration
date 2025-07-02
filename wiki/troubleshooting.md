# トラブルシューティング

## よくある問題と解決方法

### インストール・セットアップ関連

#### Python バージョンエラー
**問題**: `Python 3.7.16 が見つからない`
```
python: command not found
```

**解決方法**:
```bash
# Windows
# Python公式サイトから3.7.16をダウンロード・インストール
# インストール時に "Add Python to PATH" にチェック

# Linux (Ubuntu)
sudo apt update
sudo apt install python3.7 python3.7-venv python3.7-dev

# 確認
python3.7 --version
```

#### pip インストールエラー
**問題**: `pip install -r requirements.txt` でエラー
```
ERROR: Could not find a version that satisfies the requirement Flask==2.2.5
```

**解決方法**:
```bash
# pipのアップグレード
python -m pip install --upgrade pip

# 仮想環境の再作成
rm -rf venv
python3.7 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 依存関係の再インストール
pip install -r requirements.txt
```

#### Git関連エラー
**問題**: `git clone` でアクセス拒否
```
Permission denied (publickey)
```

**解決方法**:
```bash
# HTTPS URLを使用
git clone https://github.com/SB-Dev-Git/WebAppMigration.git

# SSH鍵の設定（必要に応じて）
ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
```

### アプリケーション起動関連

#### ポート使用中エラー
**問題**: `Address already in use`
```
OSError: [Errno 98] Address already in use
```

**解決方法**:
```bash
# 使用中のプロセスを確認
# Linux/Mac
lsof -i :5000
netstat -tulpn | grep :5000

# Windows
netstat -ano | findstr :5000

# プロセス終了
kill -9 <PID>  # Linux/Mac
taskkill /PID <PID> /F  # Windows

# または別のポートを使用
python app.py --port 5001
```

#### データベースエラー
**問題**: `sqlite3.OperationalError: database is locked`

**解決方法**:
```bash
# データベースファイルの権限確認
ls -la kintai.db

# 権限修正
chmod 664 kintai.db

# データベースファイル再作成（データ消失注意）
rm kintai.db
python app.py  # 自動的に再作成される
```

#### モジュールインポートエラー
**問題**: `ModuleNotFoundError: No module named 'flask'`

**解決方法**:
```bash
# 仮想環境が有効化されているか確認
which python  # Linux/Mac
where python  # Windows

# 仮想環境の有効化
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Flaskの再インストール
pip install Flask==2.2.5
```

### ブラウザアクセス関連

#### ページが表示されない
**問題**: `このサイトにアクセスできません`

**解決方法**:
1. **URLの確認**
   ```
   正: http://localhost:5000
   誤: https://localhost:5000 (HTTPSではない)
   ```

2. **アプリケーションの起動確認**
   ```bash
   # ログを確認
   * Running on http://127.0.0.1:5000
   * Running on http://0.0.0.0:5000
   ```

3. **ファイアウォール設定**
   ```bash
   # Windows Defender ファイアウォール
   # 「アクセスを許可する」を選択
   
   # Linux iptables
   sudo iptables -A INPUT -p tcp --dport 5000 -j ACCEPT
   ```

#### EC2でアクセスできない
**問題**: EC2のパブリックIPでアクセスできない

**解決方法**:
1. **セキュリティグループ設定**
   - インバウンドルール追加
   - タイプ: カスタムTCP
   - ポート: 5000
   - ソース: 0.0.0.0/0 または特定IP

2. **アプリケーション設定確認**
   ```python
   # app.py の最終行を確認
   app.run(debug=True, host='0.0.0.0', port=5000)
   # host='127.0.0.1' だと外部アクセス不可
   ```

3. **パブリックIP確認**
   ```bash
   curl http://checkip.amazonaws.com/
   ```

### 機能別トラブル

#### 勤怠入力エラー
**問題**: 「退勤時間は出勤時間より後である必要があります」

**解決方法**:
- 時間形式を確認: HH:MM（例: 09:00, 18:00）
- 24時間制で入力
- 出勤時間 < 退勤時間になっているか確認

**問題**: 「休憩時間は勤務時間より短い必要があります」

**解決方法**:
```
例: 出勤09:00, 退勤18:00 (9時間) の場合
休憩時間は540分未満である必要がある
```

#### CSV出力エラー
**問題**: CSVファイルが文字化けする

**解決方法**:
1. **Excelでの正しい開き方**
   - 「データ」タブ → 「テキストまたはCSVから」
   - 文字エンコード: UTF-8を選択
   - 区切り文字: カンマを選択

2. **テキストエディタで確認**
   - UTF-8対応エディタ（VS Code, Notepad++等）で開く

#### CSV取込エラー
**問題**: 「CSVファイルの処理中にエラーが発生しました」

**解決方法**:
1. **ファイル形式確認**
   ```csv
   日付,曜日,種別,出勤時間,退勤時間,休憩時間,実働時間,コメント
   2025-06-25,水,フレックス,09:00,18:00,60,8.0,テストデータ
   ```

2. **文字エンコード確認**
   - UTF-8で保存されているか確認
   - BOM付きUTF-8でも可

3. **データ形式確認**
   - 日付: YYYY-MM-DD形式
   - 時間: HH:MM形式
   - 休憩時間: 数値（分単位）
   - 実働時間: 数値（時間単位）

### パフォーマンス問題

#### 動作が重い
**問題**: 画面表示やCSV処理が遅い

**解決方法**:
1. **データベースサイズ確認**
   ```bash
   ls -lh kintai.db
   ```

2. **古いデータの削除**
   ```sql
   -- 1年以上前のデータを削除
   DELETE FROM attendance WHERE date < '2024-01-01';
   ```

3. **システムリソース確認**
   ```bash
   # メモリ使用量
   free -m
   
   # CPU使用率
   top
   ```

#### メモリ不足
**問題**: 大量データ処理時のメモリエラー

**解決方法**:
```python
# CSV処理の最適化
def process_large_csv():
    # ストリーミング処理を実装
    # バッチサイズを制限
    batch_size = 1000
    # メモリ使用量を監視
```

### セキュリティ関連

#### 不正アクセス対策
**問題**: 外部からの不正アクセス

**解決方法**:
1. **アクセス制限**
   ```bash
   # 特定IPのみ許可
   # セキュリティグループで制限
   ```

2. **認証機能の追加**（将来実装）
   ```python
   # ログイン機能
   # セッション管理
   # CSRF対策
   ```

### 本番環境関連

#### Gunicorn起動エラー
**問題**: `gunicorn: command not found`

**解決方法**:
```bash
# Gunicornのインストール
pip install gunicorn

# 設定ファイル作成
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
timeout = 30
EOF

# 起動
gunicorn -c gunicorn.conf.py app:app
```

#### Nginx設定エラー
**問題**: `502 Bad Gateway`

**解決方法**:
1. **Gunicornの起動確認**
   ```bash
   ps aux | grep gunicorn
   ```

2. **Nginx設定確認**
   ```bash
   sudo nginx -t
   sudo systemctl reload nginx
   ```

3. **ログ確認**
   ```bash
   sudo tail -f /var/log/nginx/error.log
   ```

### ログ・デバッグ

#### デバッグ情報の有効化
```python
# app.py にデバッグログ追加
import logging
logging.basicConfig(level=logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
```

#### ログファイルの確認
```bash
# アプリケーションログ
tail -f logs/kintai.log

# システムログ
sudo tail -f /var/log/syslog

# Nginxログ
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

## 緊急時対応

### データベース破損
```bash
# バックアップからの復旧
cp kintai_backup_YYYYMMDD.db kintai.db

# データベース整合性チェック
sqlite3 kintai.db "PRAGMA integrity_check;"
```

### アプリケーション停止
```bash
# プロセス強制終了
pkill -f "python app.py"
pkill -f gunicorn

# サービス再起動
sudo systemctl restart kintai-app
sudo systemctl restart nginx
```

### 緊急メンテナンス
```bash
# メンテナンスページ表示
sudo mv /var/www/html/index.html /var/www/html/index.html.bak
echo "メンテナンス中です" > /var/www/html/index.html

# メンテナンス終了
sudo mv /var/www/html/index.html.bak /var/www/html/index.html
```

## サポート連絡先

### 技術サポート
- GitHub Issues: https://github.com/SB-Dev-Git/WebAppMigration/issues
- メール: support@ditgroup.jp

### 報告時の必要情報
1. エラーメッセージの全文
2. 実行環境（OS、Pythonバージョン）
3. 実行したコマンド
4. ログファイルの内容
5. 再現手順

### よくある質問への回答
詳細は[使用方法](User-Guide)ページのFAQセクションを参照してください。
