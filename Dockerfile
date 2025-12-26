# Python 3.9を使用
FROM python:3.9-slim

# 作業ディレクトリを設定
WORKDIR /app

# 依存関係ファイルをコピーしてインストール
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# アプリケーションのコードを全てコピー
COPY . .

# Streamlitのポート（8501）を公開
EXPOSE 7860

# アプリ起動コマンド（Hugging Faceはポート7860をリッスンする必要があるため設定変更）
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=7860"]
