
import os
import json
from datetime import datetime, date, timedelta
from pathlib import Path
import requests
from dotenv import load_dotenv
import google.generativeai as genai
import streamlit as st

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = "gemini-2.5-flash"

# Kintone API Configuration
KINTONE_SUBDOMAIN = os.getenv("KINTONE_SUBDOMAIN")
KINTONE_APP_ID = os.getenv("KINTONE_APP_ID")
KINTONE_API_TOKEN = os.getenv("KINTONE_API_TOKEN")
KINTONE_CLIENT_APP_ID = os.getenv("KINTONE_CLIENT_APP_ID")
KINTONE_CLIENT_API_TOKEN = os.getenv("KINTONE_CLIENT_API_TOKEN")

SAVED_AUDIO_DIR = Path("./saved_audio")

# =============================================================================
# MASTER DATA
# =============================================================================

SALES_ACTIVITY_OPTIONS = [
    "架電、メール", "アポ架電（担当者通電）", "初回訪問", "提案（担当者訪問）", 
    "提案（見積書提出）", "提案（決裁者訪問・プレゼン）", "合意後訪問（商談）", 
    "訪問（公示前）", "公示対応（提案書提出）", "公示対応（プレゼン参加）", 
    "公示対応（入札・開封）", "合意後訪問（公示）",
]

STAFF_OPTIONS = [
    "水野 邦彦", "杉山 拓真", "一條 祐輔", "堀越 隆太郎", "矢部 昌子", 
    "鈴木 沙耶佳", "井﨑 優", "鈴木 智朗", "中村 紀夫",
]

STAFF_CODE_MAP = {
    "水野 邦彦": "mizuno.k@kids-21.co.jp",
    "杉山 拓真": "sugiyama.t@kids-21.co.jp",
    "一條 祐輔": "ichijo.y@kids-21.co.jp",
    "堀越 隆太郎": "horikoshi.r@kids-21.co.jp",
    "矢部 昌子": "yabe.m@kids-21.co.jp",
    "鈴木 沙耶佳": "suzuki.sayaka@kids-21.co.jp",
    "井﨑 優": "izaki.m@kids-21.co.jp",
    "鈴木 智朗": "suzuki.tomoaki@kids-21.co.jp",
    "中村 紀夫": "nakamura.norio@kids-21.co.jp",
}

# =============================================================================
# FUNCTIONS
# =============================================================================

def init_directories():
    SAVED_AUDIO_DIR.mkdir(exist_ok=True)

def init_gemini():
    if not GEMINI_API_KEY:
        st.error("GEMINI_API_KEY が設定されていません。")
        return False
    genai.configure(api_key=GEMINI_API_KEY)
    return True

def save_audio_file(uploaded_file) -> str:
    init_directories()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    original_name = Path(uploaded_file.name).stem
    extension = Path(uploaded_file.name).suffix
    filename = f"{timestamp}_{original_name}{extension}"
    file_path = SAVED_AUDIO_DIR / filename
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getvalue())
    return str(file_path)

def convert_date_str_safe(date_str: str, default_func=None) -> date:
    try:
        if not date_str: raise ValueError
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return default_func() if default_func else date.today()

def search_clients(keyword: str) -> list:
    if not KINTONE_CLIENT_APP_ID or not KINTONE_CLIENT_API_TOKEN:
        st.error("取引先アプリの設定が不足しています。")
        return []
    url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/records.json"
    headers = {"X-Cybozu-API-Token": KINTONE_CLIENT_API_TOKEN}
    params = {"app": KINTONE_CLIENT_APP_ID, "query": f'取引先名 like "{keyword}" limit 20'}
    try:
        response = requests.get(url, headers=headers, params=params)
        if response.status_code != 200: return []
        records = response.json().get("records", [])
        return [{
            "id": rec.get("取引先ID", {}).get("value", rec["$id"]["value"]),
            "record_id": rec["$id"]["value"],
            "name": rec.get("取引先名", {}).get("value", "不明")
        } for rec in records]
    except: return []

def get_current_date_str():
    return datetime.now().strftime("%Y-%m-%d")

def get_extraction_prompt(current_date_str: str):
    # f-stringでのJSON出力には {{ }} でのエスケープが必要です
    return f"""
あなたは営業報告書作成のエキスパートAIです。
入力された商談の文字起こしやメモ情報から、以下のフィールドを厳密なJSON形式で抽出してください。

## 前提条件
- **現在日時**: {current_date_str}
- **自社名**: 株式会社キッズコーポレーション（通称：キッズ、キッズさん 等）
- 自社の情報は「競合情報」には含めず、必要な場合のみ「商談内容」に含めてください。
- 入力テキストには誤字・脱字の可能性があります。文脈から補完してください。

## フィールド抽出ルール

### 1. 新規営業件名 (sales_activity_type)
**重要: 訪問か架電かの判定ロジック**
- **音声データがある場合**: 原則として「**訪問**」系（初回訪問、提案、合意後訪問など）とみなしてください。
- **テキストのみの場合**: 文脈から判断してください。
    - 「伺いました」「訪問し」「対面で」「名刺交換」「オフィスの様子」等の記述 -> **訪問**
    - 「お電話にて」「架電」「不在」等の記述 -> **架電、メール**
    - 明確なキーワードがない場合も、商談の深さ（見積提示など）から推測してください。

[選択肢]: "架電、メール", "アポ架電（担当者通電）", "初回訪問", "提案（担当者訪問）", "提案（見積書提出）", "提案（決裁者訪問・プレゼン）", "合意後訪問（商談）", "訪問（公示前）", "公示対応（提案書提出）", "公示対応（プレゼン参加）", "公示対応（入札・開封）", "合意後訪問（公示）"

### 2. 対応日 (action_date)
活動日付 (YYYY-MM-DD)。不明時は本日({current_date_str})。

### 3. 現在の課題・問題点 (current_issues)
**文体指定: 常体（〜だ、〜である）で統一。「〜しました」「〜です」は禁止。**
- 内容: クライアントの悩み、困りごと。(100〜200文字)
- **抽出対象例**:
  - 園児が集まらない、利用率が低い
  - 保育士の反発、採用難、退職
  - 委託会社と連絡が取れない、対応が悪い
  - 予算超過、コスト高、運営の手間
  - 制度への理解不足、監査対応の負担

### 4. 競合・マーケット情報 (competitor_market_info)
**文体指定: 常体（〜だ、〜である）で統一。「〜しました」「〜です」は禁止。**
- 内容: 競合他社の動向やマーケット情報。(100〜200文字)
- **注意**: 自社の情報は含めないこと。
- **抽出対象例**: 他社の値上げ、訪問頻度、単価、見積額、撤退の噂、採用状況など。
- **競合他社例**: アンフィニ、IQキッズ、OZcompany、スクルド、アピカル、トットメイト、ニチイキッズ、ピジョンハーツ、ライクキッズ、アイグラン、テノ、ポピンズなど。

### 5. 商談内容 (meeting_summary)
**文体指定: 常体（〜だ、〜である）で統一。「〜しました」「〜です」は禁止。**
**重要: 重複排除ルール**
- **「現在の課題」「競合・マーケット情報」に記載した内容は、ここには絶対に記載しないでください。**
- 上記2項目に含まれない、その他の会話内容、実施した具体的なアクション、相手の反応、事実関係のみを記載してください。
- **構成**:
  1. **訪問種類の明記**:（例：初回訪問を実施した、等）
  2. **実施内容と反応**: 何を説明し、どういう反応だったか事実のみ。
  3. **園の基本情報**: 園児数、先生人数、駐車場契約、園種別などがあれば必ず記載。
- 記述例: 「初回飛び込み訪問を実施した。園児数は0歳1名...（※課題や競合の話はここには書かない）」

### 6. 次回提案内容 (next_proposal)
- 次に行うべき「具体的なアクション」を簡潔に。(50文字以内)
- 抽象的な表現（「関係構築に努める」等）は避け、行動ベースで記載してください。
- **記述例**:
  - 定期的に連絡を行う
  - 不在だったため、日時を改めて架電する
  - 見積書を作成し、アポイント取得の連絡をする
  - ○月○日に再訪問する

### 7. 次回提案予定日 (next_proposal_date)
次回提案予定日 (YYYY-MM-DD)。不明時は空欄。

### 8. 次回営業件名 (next_sales_activity_type)
次回提案内容に合致する選択肢。不明時は空欄。
[選択肢]: "架電、メール", "アポ架電（担当者通電）", "初回訪問", "提案（担当者訪問）", "提案（見積書提出）", "提案（決裁者訪問・プレゼン）", "合意後訪問（商談）", "訪問（公示前）", "公示対応（提案書提出）", "公示対応（プレゼン参加）", "公示対応（入札・開封）", "合意後訪問（公示）"

## 出力形式
```json
{{
    "新規営業件名": "選択肢から選択",
    "対応日": "YYYY-MM-DD",
    "商談内容": "...",
    "現在の課題・問題点": "...",
    "競合・マーケット情報": "...",
    "次回提案内容": "...",
    "次回提案予定日": "YYYY-MM-DD",
    "次回営業件名": "選択肢から選択"
}}
```
"""

def parse_json_response(response_text: str) -> dict:
    try:
        if "```json" in response_text: json_str = response_text.split("```json")[1].split("```")[0].strip()
        elif "```" in response_text: json_str = response_text.split("```")[1].split("```")[0].strip()
        else: json_str = response_text.strip()
        import re
        json_str = re.sub(r':\s*"([^"]*)"', lambda m: ': "' + m.group(1).replace('\n', '\\n').replace('\r', '') + '"', json_str)
        return json.loads(json_str)
    except: return None

def get_mime_type(file_path: str) -> str:
    ext = Path(file_path).suffix.lower()
    if ext == ".mp3": return "audio/mp3"
    elif ext == ".wav": return "audio/wav"
    elif ext == ".m4a": return "audio/mp4" # Gemini usually treats m4a as mp4 audio or just audio/m4a if supported, generally audio/mp4 is safe standard or audio/mpeg
    elif ext == ".webm": return "audio/webm"
    elif ext == ".aac": return "audio/aac"
    elif ext == ".flac": return "audio/flac"
    elif ext == ".ogg": return "audio/ogg"
    else: return "audio/mp3" # Fallback

def process_audio_only(audio_file_path: str) -> dict:
    model = genai.GenerativeModel(model_name=GEMINI_MODEL, system_instruction=get_extraction_prompt(get_current_date_str()))
    uploaded_file = genai.upload_file(audio_file_path, mime_type=get_mime_type(audio_file_path))
    prompt = "この音声ファイルの内容を聞き取り、営業報告データを抽出してください。"
    response = model.generate_content([uploaded_file, prompt])
    return parse_json_response(response.text)

def process_text_only(text: str) -> dict:
    model = genai.GenerativeModel(model_name=GEMINI_MODEL, system_instruction=get_extraction_prompt(get_current_date_str()))
    prompt = f"以下のテキストから営業報告データを抽出してください:\n\n{text}"
    response = model.generate_content(prompt)
    return parse_json_response(response.text)

def process_audio_and_text(audio_file_path: str, text: str) -> dict:
    model = genai.GenerativeModel(model_name=GEMINI_MODEL, system_instruction=get_extraction_prompt(get_current_date_str()))
    uploaded_file = genai.upload_file(audio_file_path, mime_type=get_mime_type(audio_file_path))
    prompt = f"音声ファイルの内容を分析し、営業報告データを抽出してください。テキストメモ優先:\n{text}"
    response = model.generate_content([uploaded_file, prompt])
    return parse_json_response(response.text)

def sanitize_text(text: str) -> str:
    if not text: return ""
    import re
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', str(text)).strip()

def upload_file_to_kintone(file_path: str, file_name: str) -> str:
    if not all([KINTONE_SUBDOMAIN, KINTONE_API_TOKEN]): return ""
    url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/file.json"
    headers = {"X-Cybozu-API-Token": KINTONE_API_TOKEN}
    try:
        with open(file_path, "rb") as f:
            files = {"file": (file_name, f)}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
            return response.json().get("fileKey", "")
    except Exception as e:
        st.warning(f"ファイルアップロードエラー: {e}")
        return ""

def upload_to_kintone(data: dict, file_keys: list = None) -> bool:
    if not all([KINTONE_SUBDOMAIN, KINTONE_APP_ID, KINTONE_API_TOKEN]): return False
    url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/record.json"
    combined_token = KINTONE_API_TOKEN
    if KINTONE_CLIENT_API_TOKEN: combined_token = f"{KINTONE_API_TOKEN},{KINTONE_CLIENT_API_TOKEN}"
    headers = {"X-Cybozu-API-Token": combined_token, "Content-Type": "application/json; charset=utf-8"}
    
    staff_name = data.get("対応者", "")
    staff_code = STAFF_CODE_MAP.get(staff_name, "")
    
    record = {
        "取引先ID": {"value": str(data.get("取引先ID", ""))},
        "新規営業件名": {"value": sanitize_text(data.get("新規営業件名", ""))},
        "対応日": {"value": sanitize_text(data.get("対応日", ""))},
        "対応者": {"value": [{"code": staff_code}] if staff_code else []},
        "商談内容": {"value": sanitize_text(data.get("商談内容", ""))},
        "現在の課題・問題点": {"value": sanitize_text(data.get("現在の課題・問題点", ""))},
        "競合・マーケット情報": {"value": sanitize_text(data.get("競合・マーケット情報", ""))},
        "次回提案内容": {"value": sanitize_text(data.get("次回提案内容", ""))},
        "次回提案予定日": {"value": sanitize_text(data.get("次回提案予定日", ""))},
        "次回営業件名": {"value": sanitize_text(data.get("次回営業件名", ""))},
    }
    if file_keys: record["添付ファイル_0"] = {"value": [{"fileKey": fk} for fk in file_keys]}
    
    payload = {"app": int(KINTONE_APP_ID), "record": record}
    try:
        requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8')).raise_for_status()
        return True
    except Exception as e:
        st.error(f"Error: {e}")
        return False
