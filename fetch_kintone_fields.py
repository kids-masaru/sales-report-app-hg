
import os
import requests
from dotenv import load_dotenv

load_dotenv()

KINTONE_SUBDOMAIN = os.getenv("KINTONE_SUBDOMAIN")
KINTONE_APP_ID = os.getenv("KINTONE_APP_ID")
KINTONE_API_TOKEN = os.getenv("KINTONE_API_TOKEN")

def get_field_options(field_code):
    if not all([KINTONE_SUBDOMAIN, KINTONE_APP_ID, KINTONE_API_TOKEN]):
        print("Error: Missing Kintone configuration.")
        return

    url = f"https://{KINTONE_SUBDOMAIN}.cybozu.com/k/v1/app/form/fields.json"
    headers = {"X-Cybozu-API-Token": KINTONE_API_TOKEN}
    params = {"app": KINTONE_APP_ID}

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        data = response.json()
        
        properties = data.get("properties", {})
        if field_code in properties:
             field_info = properties[field_code]
             options = field_info.get("options", {})
             sorted_options = sorted(options.items(), key=lambda x: int(x[1].get("index", 0)))
             print(f"--- Options for {field_code} ---")
             for label, details in sorted_options:
                 print(f"{label}")
        else:
            print(f"Field code '{field_code}' not found.")
            print("Available fields:", properties.keys())

    except Exception as e:
        print(f"Error fetching fields: {e}")
        if 'response' in locals():
            print(response.text)

if __name__ == "__main__":
    with open("kintone_options.txt", "w", encoding="utf-8") as f:
        # Redirect print to file
        import sys
        original_stdout = sys.stdout
        sys.stdout = f
        print("Fetching '新規営業件名' options...")
        get_field_options("新規営業件名")
        print("\nFetching '次回営業件名' options...")
        get_field_options("次回営業件名")
        sys.stdout = original_stdout
        print("Done writing to kintone_options.txt")
