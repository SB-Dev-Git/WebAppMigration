# 開発者向け情報

## コード構造

### プロジェクト構成
```
WebAppMigration/
├── app.py                 # メインアプリケーション
├── requirements.txt       # Python依存関係
├── kintai.db             # SQLiteデータベース
├── templates/            # Jinja2テンプレート
│   ├── base.html         # ベーステンプレート
│   ├── index.html        # ホーム画面
│   ├── input.html        # 勤怠入力画面
│   ├── display.html      # 勤怠一覧画面
│   └── import.html       # CSV取込画面
├── static/               # 静的ファイル
│   └── css/
│       └── style.css     # メインスタイルシート
├── logs/                 # ログファイル（本番環境）
├── backups/              # データベースバックアップ
└── README.md             # プロジェクト説明
```

### コード規約

#### PEP8準拠
- インデント: スペース4つ
- 行長: 最大79文字
- 関数名: snake_case
- クラス名: PascalCase
- 定数: UPPER_CASE

#### コメント規約
- 日本語でのコメント記述
- 関数の説明は docstring で記述
- 複雑なロジックには行コメント

```python
def calculate_work_hours(start_time, end_time, break_time):
    """
    実働時間を計算する
    
    Args:
        start_time (str): 出勤時間 (HH:MM形式)
        end_time (str): 退勤時間 (HH:MM形式)
        break_time (int): 休憩時間 (分単位)
    
    Returns:
        float: 実働時間 (時間単位、小数点2桁)
    """
    if not start_time or not end_time:
        return 0
    
    try:
        start = datetime.strptime(start_time, '%H:%M')
        end = datetime.strptime(end_time, '%H:%M')
        
        # 総勤務時間を分単位で計算
        diff_minutes = (end - start).total_seconds() / 60
        
        # 休憩時間を差し引いて実働時間を算出
        work_minutes = diff_minutes - break_time
        
        return round(work_minutes / 60, 2) if work_minutes > 0 else 0
    except ValueError:
        return 0
```

## 主要関数の詳細

### データベース関連

#### `init_db()`
データベースの初期化を行う関数

```python
def init_db():
    """
    SQLiteデータベースとテーブルを初期化
    アプリケーション起動時に自動実行
    """
    conn = sqlite3.connect('kintai.db')
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS attendance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            day_of_week TEXT NOT NULL,
            type TEXT NOT NULL,
            start_time TEXT,
            end_time TEXT,
            break_time INTEGER DEFAULT 0,
            work_hours REAL DEFAULT 0,
            comment TEXT
        )
    ''')
    
    conn.commit()
    conn.close()
```

### ユーティリティ関数

#### `get_day_of_week(date_str)`
日付文字列から曜日を取得

```python
def get_day_of_week(date_str):
    """
    日付文字列から日本語の曜日を取得
    
    Args:
        date_str (str): 日付文字列 (YYYY-MM-DD形式)
    
    Returns:
        str: 曜日 (月、火、水、木、金、土、日)
    """
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    days = ['月', '火', '水', '木', '金', '土', '日']
    return days[date_obj.weekday()]
```

#### `validate_time_input(start_time, end_time, break_time)`
入力データのバリデーション

```python
def validate_time_input(start_time, end_time, break_time):
    """
    時間入力のバリデーションを実行
    
    Args:
        start_time (str): 出勤時間
        end_time (str): 退勤時間
        break_time (int): 休憩時間
    
    Returns:
        list: エラーメッセージのリスト（エラーがない場合は空リスト）
    """
    errors = []
    
    if start_time and end_time:
        try:
            start = datetime.strptime(start_time, '%H:%M')
            end = datetime.strptime(end_time, '%H:%M')
            
            # 時間の論理チェック
            if end <= start:
                errors.append('退勤時間は出勤時間より後である必要があります')
                
            # 休憩時間の妥当性チェック
            total_minutes = (end - start).total_seconds() / 60
            if break_time >= total_minutes:
                errors.append('休憩時間は勤務時間より短い必要があります')
                
        except ValueError:
            errors.append('時間の形式が正しくありません（HH:MM形式で入力してください）')
    
    if break_time < 0:
        errors.append('休憩時間は0以上である必要があります')
    
    return errors
```

## ルート関数の詳細

### `index()`
ホーム画面の表示

```python
@app.route('/')
def index():
    """
    ホーム画面を表示
    アプリケーションの概要と機能一覧を提供
    """
    return render_template('index.html')
```

### `input_attendance()`
勤怠入力の処理

```python
@app.route('/input', methods=['GET', 'POST'])
def input_attendance():
    """
    勤怠入力画面の表示と勤怠データの保存
    
    GET: 入力フォームを表示
    POST: フォームデータを検証・保存
    """
    if request.method == 'POST':
        # フォームデータの取得
        date_str = request.form['date']
        attendance_type = request.form['type']
        start_time = request.form.get('start_time', '')
        end_time = request.form.get('end_time', '')
        break_time = int(request.form.get('break_time', 0))
        comment = request.form.get('comment', '')
        
        # バリデーション実行
        errors = validate_time_input(start_time, end_time, break_time)
        
        if errors:
            # エラーがある場合はフォームを再表示
            for error in errors:
                flash(error, 'error')
            return render_template('input.html', 
                                 date=date_str, 
                                 type=attendance_type,
                                 start_time=start_time,
                                 end_time=end_time,
                                 break_time=break_time,
                                 comment=comment)
        
        # データベースに保存
        day_of_week = get_day_of_week(date_str)
        work_hours = calculate_work_hours(start_time, end_time, break_time)
        
        conn = sqlite3.connect('kintai.db')
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO attendance 
                (date, day_of_week, type, start_time, end_time, break_time, work_hours, comment)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (date_str, day_of_week, attendance_type, start_time, end_time, break_time, work_hours, comment))
            
            conn.commit()
            flash('勤怠データを保存しました', 'success')
            
        except sqlite3.Error as e:
            flash(f'データベースエラー: {e}', 'error')
        finally:
            conn.close()
        
        return redirect(url_for('input_attendance'))
    
    # GET リクエストの場合
    today = date.today().strftime('%Y-%m-%d')
    return render_template('input.html', date=today)
```

## テンプレート構造

### ベーステンプレート (base.html)
```html
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}勤怠入力アプリケーション{% endblock %}</title>
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>
    <nav class="navbar">
        <!-- ナビゲーションメニュー -->
    </nav>
    
    <main class="container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### 個別テンプレートの継承
```html
{% extends "base.html" %}

{% block title %}勤怠入力 - 勤怠入力アプリケーション{% endblock %}

{% block content %}
<!-- ページ固有のコンテンツ -->
{% endblock %}
```

## CSS設計

### レスポンシブデザイン
```css
/* モバイルファースト設計 */
.container {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 15px;
}

/* タブレット対応 */
@media (min-width: 768px) {
    .container {
        padding: 0 30px;
    }
}

/* デスクトップ対応 */
@media (min-width: 1024px) {
    .container {
        padding: 0 50px;
    }
}
```

### カラーパレット
```css
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --danger-color: #dc3545;
    --warning-color: #ffc107;
    --info-color: #17a2b8;
    --light-color: #f8f9fa;
    --dark-color: #343a40;
}
```

## データベース設計の拡張

### 将来のテーブル追加

#### ユーザー管理テーブル
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT DEFAULT 'user',
    department_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (department_id) REFERENCES departments(id)
);
```

#### 部署管理テーブル
```sql
CREATE TABLE departments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    manager_id INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (manager_id) REFERENCES users(id)
);
```

#### 勤怠テーブルの拡張
```sql
ALTER TABLE attendance ADD COLUMN user_id INTEGER;
ALTER TABLE attendance ADD COLUMN approved_by INTEGER;
ALTER TABLE attendance ADD COLUMN approved_at DATETIME;
ALTER TABLE attendance ADD COLUMN status TEXT DEFAULT 'pending';
```

## テスト戦略

### 単体テスト
```python
import unittest
from app import calculate_work_hours, validate_time_input

class TestKintaiApp(unittest.TestCase):
    
    def test_calculate_work_hours(self):
        """実働時間計算のテスト"""
        # 正常ケース
        result = calculate_work_hours('09:00', '18:00', 60)
        self.assertEqual(result, 8.0)
        
        # 休憩時間なし
        result = calculate_work_hours('09:00', '17:00', 0)
        self.assertEqual(result, 8.0)
        
        # 異常ケース
        result = calculate_work_hours('', '', 0)
        self.assertEqual(result, 0)
    
    def test_validate_time_input(self):
        """入力バリデーションのテスト"""
        # 正常ケース
        errors = validate_time_input('09:00', '18:00', 60)
        self.assertEqual(len(errors), 0)
        
        # 時間順序エラー
        errors = validate_time_input('18:00', '09:00', 60)
        self.assertIn('退勤時間は出勤時間より後である必要があります', errors)

if __name__ == '__main__':
    unittest.main()
```

### 統合テスト
```python
import unittest
from app import app
import tempfile
import os

class TestKintaiAppIntegration(unittest.TestCase):
    
    def setUp(self):
        self.db_fd, app.config['DATABASE'] = tempfile.mkstemp()
        app.config['TESTING'] = True
        self.app = app.test_client()
        
    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(app.config['DATABASE'])
    
    def test_index_page(self):
        """ホーム画面のテスト"""
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('勤怠入力アプリケーション', rv.data.decode('utf-8'))
    
    def test_attendance_input(self):
        """勤怠入力のテスト"""
        rv = self.app.post('/input', data={
            'date': '2025-06-25',
            'type': 'フレックス',
            'start_time': '09:00',
            'end_time': '18:00',
            'break_time': '60',
            'comment': 'テストデータ'
        })
        self.assertEqual(rv.status_code, 302)  # リダイレクト
```

## デプロイメント

### 開発環境
```bash
# 仮想環境作成
python3.7 -m venv venv
source venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt

# 開発サーバー起動
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### 本番環境
```bash
# Gunicorn設定
cat > gunicorn.conf.py << EOF
bind = "127.0.0.1:5000"
workers = 2
worker_class = "sync"
worker_connections = 1000
timeout = 30
keepalive = 2
max_requests = 1000
max_requests_jitter = 100
preload_app = True
EOF

# systemdサービス設定
sudo tee /etc/systemd/system/kintai-app.service << EOF
[Unit]
Description=Kintai Attendance App
After=network.target

[Service]
User=ec2-user
Group=ec2-user
WorkingDirectory=/home/ec2-user/WebAppMigration
Environment=PATH=/home/ec2-user/WebAppMigration/venv/bin
ExecStart=/home/ec2-user/WebAppMigration/venv/bin/gunicorn -c gunicorn.conf.py app:app
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# サービス有効化
sudo systemctl daemon-reload
sudo systemctl enable kintai-app
sudo systemctl start kintai-app
```

## 監視・ログ

### アプリケーションログ
```python
import logging
from logging.handlers import RotatingFileHandler

# ログ設定
if not app.debug:
    if not os.path.exists('logs'):
        os.mkdir('logs')
    
    file_handler = RotatingFileHandler(
        'logs/kintai.log', 
        maxBytes=10240000,  # 10MB
        backupCount=10
    )
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Kintai app startup')
```

### パフォーマンス監視
```python
import time
from functools import wraps

def monitor_performance(f):
    """パフォーマンス監視デコレータ"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        start_time = time.time()
        result = f(*args, **kwargs)
        end_time = time.time()
        
        app.logger.info(f'{f.__name__} executed in {end_time - start_time:.2f}s')
        return result
    return decorated_function

@app.route('/display')
@monitor_performance
def display_attendance():
    # 既存の処理
    pass
```

## セキュリティ

### CSRF対策
```python
from flask_wtf.csrf import CSRFProtect

csrf = CSRFProtect(app)
```

### 入力サニタイゼーション
```python
from werkzeug.utils import secure_filename
import bleach

def sanitize_input(text):
    """入力テキストのサニタイゼーション"""
    if not text:
        return ''
    
    # HTMLタグの除去
    clean_text = bleach.clean(text, tags=[], strip=True)
    
    # 長さ制限
    return clean_text[:500]
```

## 今後の拡張計画

### 認証システム
- Flask-Login の導入
- パスワードハッシュ化
- セッション管理
- ロールベースアクセス制御

### API化
- Flask-RESTful の導入
- JSON レスポンス
- API認証（JWT）
- OpenAPI仕様書

### フロントエンド強化
- Vue.js / React の導入
- SPA化
- リアルタイム更新
- PWA対応

### データ分析機能
- 勤務時間統計
- グラフ表示
- レポート生成
- データエクスポート

## 貢献ガイドライン

### プルリクエスト
1. フィーチャーブランチを作成
2. コードを実装
3. テストを追加
4. ドキュメントを更新
5. プルリクエストを作成

### コードレビュー
- PEP8準拠の確認
- テストカバレッジの確認
- セキュリティチェック
- パフォーマンス影響の評価

### リリースプロセス
1. バージョンタグの作成
2. CHANGELOG.md の更新
3. 本番環境へのデプロイ
4. 動作確認
5. ロールバック手順の確認
