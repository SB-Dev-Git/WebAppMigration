# API仕様

## 概要

勤怠入力アプリケーションのWebエンドポイント仕様です。現在はHTML形式のレスポンスのみですが、将来的にはJSON APIの提供も予定しています。

## エンドポイント一覧

| エンドポイント | メソッド | 説明 | パラメータ |
|---------------|----------|------|------------|
| `/` | GET | ホーム画面 | なし |
| `/input` | GET/POST | 勤怠入力画面 | フォームデータ |
| `/display` | GET | 勤怠一覧画面 | なし |
| `/export_csv` | GET | CSV出力 | なし |
| `/import_csv` | GET/POST | CSV取込画面 | ファイルアップロード |

## 詳細仕様

### 1. ホーム画面
**エンドポイント**: `/`  
**メソッド**: GET  
**説明**: アプリケーションのホーム画面を表示

#### レスポンス
- **Content-Type**: text/html
- **テンプレート**: templates/index.html
- **ステータスコード**: 200

### 2. 勤怠入力
**エンドポイント**: `/input`  
**メソッド**: GET, POST

#### GET リクエスト
勤怠入力フォームを表示

**レスポンス**:
- **Content-Type**: text/html
- **テンプレート**: templates/input.html
- **デフォルト値**: 日付は今日の日付

#### POST リクエスト
勤怠データを保存

**リクエストパラメータ**:
```
date: 日付 (YYYY-MM-DD形式, 必須)
type: 勤怠種別 (必須)
start_time: 出勤時間 (HH:MM形式, 任意)
end_time: 退勤時間 (HH:MM形式, 任意)
break_time: 休憩時間 (分単位, 任意, デフォルト: 0)
comment: コメント (任意)
```

**バリデーション**:
- 出勤時間 < 退勤時間
- 休憩時間 < 総勤務時間
- 時間形式: HH:MM
- 休憩時間 >= 0

**レスポンス**:
- 成功時: リダイレクト (302) → `/input`
- エラー時: フォーム再表示 (200) + エラーメッセージ

### 3. 勤怠一覧表示
**エンドポイント**: `/display`  
**メソッド**: GET  
**説明**: 登録済み勤怠データを一覧表示

#### レスポンス
- **Content-Type**: text/html
- **テンプレート**: templates/display.html
- **データ**: 日付降順でソートされた勤怠レコード

#### データ構造
```python
records = [
    (date, day_of_week, type, start_time, end_time, break_time, work_hours, comment),
    ...
]
```

### 4. CSV出力
**エンドポイント**: `/export_csv`  
**メソッド**: GET  
**説明**: 勤怠データをCSV形式でダウンロード

#### レスポンス
- **Content-Type**: text/csv
- **Content-Disposition**: attachment; filename="kintai_YYYYMMDD.csv"
- **文字エンコード**: UTF-8 with BOM
- **データ順序**: 日付昇順

#### CSV形式
```csv
日付,曜日,種別,出勤時間,退勤時間,休憩時間,実働時間,コメント
2025-06-25,水,フレックス,09:00,18:00,60,8.0,テスト勤怠データ
```

### 5. CSV取込
**エンドポイント**: `/import_csv`  
**メソッド**: GET, POST

#### GET リクエスト
CSV取込画面を表示

**レスポンス**:
- **Content-Type**: text/html
- **テンプレート**: templates/import.html

#### POST リクエスト
CSVファイルから勤怠データを一括取込

**リクエストパラメータ**:
```
file: CSVファイル (multipart/form-data, 必須)
```

**ファイル要件**:
- 拡張子: .csv
- 文字エンコード: UTF-8
- ヘッダー行: 必須
- 最大ファイルサイズ: 制限なし（推奨: 10MB以下）

**処理フロー**:
1. ファイル形式検証
2. CSV解析
3. 行ごとのデータバリデーション
4. データベース保存（INSERT OR REPLACE）
5. 結果レポート

**レスポンス**:
- 成功時: リダイレクト (302) → `/import_csv` + 成功メッセージ
- エラー時: フォーム再表示 (200) + エラーメッセージ

## データベース操作

### SQLクエリ例

#### データ挿入・更新
```sql
INSERT OR REPLACE INTO attendance 
(date, day_of_week, type, start_time, end_time, break_time, work_hours, comment)
VALUES (?, ?, ?, ?, ?, ?, ?, ?);
```

#### データ取得（一覧表示用）
```sql
SELECT date, day_of_week, type, start_time, end_time, break_time, work_hours, comment
FROM attendance
ORDER BY date DESC;
```

#### データ取得（CSV出力用）
```sql
SELECT date, day_of_week, type, start_time, end_time, break_time, work_hours, comment
FROM attendance
ORDER BY date;
```

## エラーハンドリング

### バリデーションエラー
- **時間整合性エラー**: "退勤時間は出勤時間より後である必要があります"
- **休憩時間エラー**: "休憩時間は勤務時間より短い必要があります"
- **時間形式エラー**: "時間の形式が正しくありません（HH:MM形式で入力してください）"
- **数値範囲エラー**: "休憩時間は0以上である必要があります"

### ファイルアップロードエラー
- **ファイル未選択**: "ファイルが選択されていません"
- **ファイル形式エラー**: "CSVファイルを選択してください"
- **処理エラー**: "CSVファイルの処理中にエラーが発生しました: {詳細}"

### データベースエラー
- **DB接続エラー**: "データベースエラー: {詳細}"
- **制約違反**: 一意制約違反時の適切なエラーメッセージ

## セキュリティ

### 入力サニタイゼーション
- SQLインジェクション対策: パラメータ化クエリ使用
- ファイル名サニタイゼーション: `secure_filename()` 使用
- XSS対策: Jinja2テンプレートの自動エスケープ

### ファイルアップロード制限
- 許可拡張子: .csv のみ
- ファイルサイズ制限: 設定可能（現在は制限なし）
- ファイル内容検証: CSV形式チェック

## パフォーマンス

### レスポンス時間目標
- 画面表示: < 100ms
- CSV出力: < 1秒（1000件以下）
- CSV取込: < 5秒（1000件以下）

### 最適化ポイント
- データベース接続の適切な管理
- 大量データ処理時のメモリ使用量制御
- CSVストリーミング処理

## 将来のAPI拡張

### REST API計画
```
GET    /api/attendance          # 勤怠データ一覧取得
POST   /api/attendance          # 勤怠データ作成
GET    /api/attendance/{date}   # 特定日の勤怠データ取得
PUT    /api/attendance/{date}   # 特定日の勤怠データ更新
DELETE /api/attendance/{date}   # 特定日の勤怠データ削除
```

### JSON レスポンス例
```json
{
  "status": "success",
  "data": {
    "date": "2025-06-25",
    "day_of_week": "水",
    "type": "フレックス",
    "start_time": "09:00",
    "end_time": "18:00",
    "break_time": 60,
    "work_hours": 8.0,
    "comment": "テスト勤怠データ"
  }
}
```

### 認証API
```
POST /api/auth/login    # ログイン
POST /api/auth/logout   # ログアウト
GET  /api/auth/profile  # ユーザー情報取得
```

## 開発者向け情報

### ローカル開発
```bash
# 開発サーバー起動
python app.py

# デバッグモード
export FLASK_ENV=development
export FLASK_DEBUG=1
python app.py
```

### テスト用cURLコマンド

#### 勤怠データ投稿
```bash
curl -X POST http://localhost:5000/input \
  -F "date=2025-06-25" \
  -F "type=フレックス" \
  -F "start_time=09:00" \
  -F "end_time=18:00" \
  -F "break_time=60" \
  -F "comment=テストデータ"
```

#### CSV出力
```bash
curl -O http://localhost:5000/export_csv
```

#### CSV取込
```bash
curl -X POST http://localhost:5000/import_csv \
  -F "file=@test_data.csv"
```
