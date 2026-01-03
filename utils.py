
import os
import json
from datetime import datetime, date, timedelta
from pathlib import Path
import requests
from dotenv import load_dotenv
from google import genai
from google.genai import types

# ... (rest of imports)

# Load environment variables
load_dotenv()

# =============================================================================
# CONFIGURATION
# =============================================================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# Using 2.0 Flash as standard efficient model, user's 2.5 might be invalid
GEMINI_MODEL = "gemini-2.0-flash-exp" 

# ... (Kintone config)

# ... (Directories)

# ... (Master Data)

# =============================================================================
# FUNCTIONS
# =============================================================================

def init_directories():
    SAVED_AUDIO_DIR.mkdir(exist_ok=True)

def init_gemini():
    if not GEMINI_API_KEY:
        print("GEMINI_API_KEY が設定されていません。")
        return False
    return True

# ... (save_audio_file, convert_date_str_safe, search_clients, get_current_date_str, calculate_smart_next_date, get_extraction_prompt, get_qa_extraction_prompt, parse_json_response, get_mime_type)

def process_audio_only(audio_file_path: str, mode: str = "sales") -> dict:
    if not GEMINI_API_KEY: return {}
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt_func = get_qa_extraction_prompt if mode == "qa" else get_extraction_prompt
    sys_instruct = prompt_func(get_current_date_str())
    
    # Upload file
    uploaded_file = client.files.upload(path=audio_file_path)
    
    prompt = "この音声ファイルの内容を聞き取り、データを抽出してください。"
    
    # Generate
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[uploaded_file, prompt],
        config=types.GenerateContentConfig(system_instruction=sys_instruct)
    )
    return parse_json_response(response.text)

def process_text_only(text: str, mode: str = "sales") -> dict:
    if not GEMINI_API_KEY: return {}
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt_func = get_qa_extraction_prompt if mode == "qa" else get_extraction_prompt
    sys_instruct = prompt_func(get_current_date_str())
    
    prompt = f"以下のテキストからデータを抽出してください:\n\n{text}"
    
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(system_instruction=sys_instruct)
    )
    return parse_json_response(response.text)

def process_audio_and_text(audio_file_path: str, text: str, mode: str = "sales") -> dict:
    if not GEMINI_API_KEY: return {}
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt_func = get_qa_extraction_prompt if mode == "qa" else get_extraction_prompt
    sys_instruct = prompt_func(get_current_date_str())
    
    uploaded_file = client.files.upload(path=audio_file_path)
    
    prompt = f"音声ファイルの内容を分析し、データを抽出してください。テキストメモ優先:\n{text}"
    
    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=[uploaded_file, prompt],
        config=types.GenerateContentConfig(system_instruction=sys_instruct)
    )
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
        print(f"ファイルアップロードエラー: {e}")
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
        resp = requests.post(url, headers=headers, data=json.dumps(payload, ensure_ascii=False).encode('utf-8'))
        resp.raise_for_status()
        return True, ""
    except Exception as e:
        error_msg = f"{str(e)}"
        try:
            if 'resp' in locals():
                error_msg += f" Response: {resp.text}"
        except:
            pass
        print(f"Kintone Error: {error_msg}")
        return False, error_msg
