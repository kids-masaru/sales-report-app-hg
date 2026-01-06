import sys
from unittest.mock import MagicMock

# Mock google.genai module
mock_google = MagicMock()
mock_genai = MagicMock()
mock_google.genai = mock_genai
sys.modules["google"] = mock_google
sys.modules["google.genai"] = mock_genai

from utils import get_extraction_prompt, NEXT_SALES_ACTIVITY_OPTIONS

with open("verification_result.txt", "w", encoding="utf-8") as f:
    prompt = get_extraction_prompt("2025-01-01")

    expected_phrases = [
        "敬称の厳格ルール",
        "「氏」は絶対に使用しないでください",
        "役職：名前様",
        "フォーマットと改行",
        "NEXT_SALES_ACTIVITY_OPTIONS" # Checking this implicitly by ensuring previous logic still holds, but let's check phrase
    ]

    missing = []
    for phrase in expected_phrases:
        if phrase not in prompt:
            missing.append(phrase)

    if missing:
        f.write(f"FAILED: Missing phrases in prompt: {missing}\n")
    else:
        f.write("SUCCESS: All expected phrases present in prompt.\n")
        
    f.write("\n--- Snippet from prompt ---\n")
    start_idx = prompt.find("### 8. 次回営業件名")
    f.write(prompt[start_idx:start_idx+500])
    
print("Verification complete. Check verification_result.txt")
