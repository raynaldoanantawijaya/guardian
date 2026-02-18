import os
import requests
import json
import sys

def test_api():
    print("Testing OpenRouter API Connection...")
    
    # Get key from env
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        print("[ERROR] OPENROUTER_API_KEY environment variable is NOT set.")
        return
    
    masked = f"{api_key[:10]}...{api_key[-4:]}" if len(api_key) > 10 else "***"
    print(f"Using Key: {masked}")
    
    # 1. Test Models Endpoint (Cheapest/Fastest check)
    print("\n[1] Check '/models' endpoint...")
    try:
        resp = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": f"Bearer {api_key}"},
            timeout=10
        )
        if resp.status_code == 200:
            print("[PASS] API Key is valid! (Models list retrieved)")
        else:
            print(f"[FAIL] Models check failed: {resp.status_code} - {resp.text}")
            return
    except Exception as e:
        print(f"[ERROR] Connection failed: {e}")
        return

    # 2. Test Chat Generation (Gemini Flash)
    print("\n[2] Testing Chat Generation (google/gemini-2.0-flash-001)...")
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://guardian.test",
        "X-Title": "Guardian Debug"
    }
    data = {
        "model": "google/gemini-2.0-flash-001",
        "messages": [{"role": "user", "content": "Say 'Hello Guardian'"}],
        "max_tokens": 10
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=10)
        if resp.status_code == 200:
            print(f"[PASS] Generation successful!\nResponse: {resp.json()['choices'][0]['message']['content']}")
        else:
            print(f"[FAIL] Generation failed: {resp.status_code} - {resp.text}")
            
    except Exception as e:
        print(f"[ERROR] Chat request error: {e}")

if __name__ == "__main__":
    test_api()
