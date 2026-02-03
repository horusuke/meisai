# Streamlit アプリケーション

Streamlitを使用した基本的なWebアプリケーションの雛形です。

## セットアップ

1. 仮想環境を作成（推奨）:
```bash
python -m venv venv
source venv/bin/activate  # macOS/Linux
# または
venv\Scripts\activate  # Windows
```

2. 依存関係をインストール:
```bash
pip install -r requirements.txt
```

## 実行方法

```bash
streamlit run app.py
```

ブラウザで `http://localhost:8501` が自動的に開きます。

## 機能

- サイドバーでの設定
- カラムレイアウト
- データ表示
- チャート表示

## カスタマイズ

`app.py` を編集して、アプリケーションをカスタマイズしてください。
