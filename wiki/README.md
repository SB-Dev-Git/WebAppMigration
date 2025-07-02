# 勤怠入力アプリケーション Wiki

## 概要

Flask + SQLiteを使用した勤怠管理Webアプリケーションです。社員が日ごとの勤怠情報を入力・一覧表示・CSV入出力できる簡易Webアプリケーションとして設計されています。

### 主な特徴
- **シンプルな操作性**: 直感的なWebインターフェース
- **完全日本語対応**: UI、メッセージ、ドキュメント全て日本語
- **データ検証機能**: 時間整合性チェック、入力バリデーション
- **CSV連携**: データのインポート・エクスポート機能
- **レスポンシブデザイン**: PC・モバイル対応

### 対象環境
- **開発環境**: Windows 11, Linux (Ubuntu)
- **本番環境**: AWS EC2 (Amazon Linux 2)
- **Python**: 3.7.16対応
- **ブラウザ**: Chrome, Edge, Firefox等のモダンブラウザ

## Wiki目次

1. **[概要](README.md)** - このページ
2. **[アーキテクチャ](architecture.md)** - システム構成と技術スタック
3. **[データベース設計](database-design.md)** - E-R図とテーブル設計
4. **[画面設計](screen-design.md)** - UI仕様と画面遷移図
5. **[セットアップガイド](setup-guide.md)** - 環境別インストール手順
6. **[使用方法](user-guide.md)** - 機能別操作マニュアル
7. **[API仕様](api-reference.md)** - エンドポイント詳細
8. **[トラブルシューティング](troubleshooting.md)** - よくある問題と解決方法
9. **[開発者向け情報](developer-guide.md)** - コード構造と拡張方法

## クイックスタート

### 1. 環境準備
```bash
# リポジトリクローン
git clone https://github.com/SB-Dev-Git/WebAppMigration.git
cd WebAppMigration

# ブランチ切り替え
git checkout devin/1750820022-kintai-app-migration
```

### 2. 依存関係インストール
```bash
# 仮想環境作成
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# パッケージインストール
pip install -r requirements.txt
```

### 3. アプリケーション起動
```bash
python app.py
```

### 4. ブラウザアクセス
http://localhost:5000 にアクセスして勤怠アプリケーションを使用開始

## 主要機能

### 勤怠入力
- 日付選択（土日自動判定）
- 種別選択（フレックス、在宅勤務、休暇等）
- 出退勤時間入力
- 休憩時間設定
- コメント記録

### 勤怠管理
- 一覧表示（表形式）
- 実働時間自動計算
- データ検索・フィルタリング

### データ連携
- CSV出力（kintai_YYYYMMDD.csv形式）
- CSV一括インポート
- データバリデーション

## 技術仕様

| 項目 | 内容 |
|------|------|
| 言語 | Python 3.7.16 |
| フレームワーク | Flask 2.2.5 |
| データベース | SQLite |
| フロントエンド | HTML5, CSS3, JavaScript |
| 文字エンコーディング | UTF-8 |
| コーディング規約 | PEP8準拠 |

## サポート

問題が発生した場合は、[トラブルシューティング](troubleshooting.md)ページを参照するか、GitHubのIssueで報告してください。

---

**最終更新**: 2025年6月30日  
**バージョン**: 1.0.0  
**メンテナー**: DIT Group
