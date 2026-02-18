import requests
import io
import sys
import socks
import socket

# Force UTF-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGET = "https://puskesjaten1.karanganyarkab.go.id"
PROXY_FILE = "proxies.txt"
GOOD_PROXY_FILE = "verified_proxies.txt"

def validate_proxies():
    print(f"[+] Validating Proxies against TARGET: {TARGET}")
    print("="*60)
    
    with open(PROXY_FILE, 'r') as f:
        proxies = [line.strip() for line in f if line.strip()]
    
    good_proxies = []
    
    for p in proxies:
        print(f"[*] Testing: {p:<30}", end="")
        
        # Parse Protocol
        if "://" in p:
            proto, address = p.split("://")
        else:
            proto = "http"
            address = p
            
        proxies_dict = {
            "http": p,
            "https": p
        }
        
        try:
            # Send Request
            if "socks" in proto:
                # Basic socks support via requests (needs requests[socks])
                proxies_dict = {"http": p, "https": p}
                
            r = requests.get(TARGET, proxies=proxies_dict, timeout=10, verify=False)
            
            if r.status_code == 200:
                print(f" -> [OK] {r.status_code}")
                good_proxies.append(p)
            elif r.status_code == 403:
                print(f" -> [BLOCKED] 403 (Nginx)")
                # Still might be useful if we bypass with headers later, but safer to skip for now?
                # Actually, if it connects, let's keep it. SQLMap handles 403.
                good_proxies.append(p) 
            else:
                 print(f" -> [FAIL] Code: {r.status_code}")
                 
        except requests.exceptions.SSLError:
            print(" -> [SSL ERROR]")
        except requests.exceptions.ConnectTimeout:
            print(" -> [TIMEOUT]")
        except requests.exceptions.ProxyError:
            print(" -> [PROXY ERROR]")
        except Exception as e:
            print(f" -> [ERROR] {e}")

    print("="*60)
    print(f"Total Proxies: {len(proxies)}")
    print(f"Working Proxies: {len(good_proxies)}")
    
    if good_proxies:
        with open(GOOD_PROXY_FILE, 'w') as f:
            for p in good_proxies:
                f.write(p + "\n")
        print(f"[+] Saved working proxies to '{GOOD_PROXY_FILE}'")
        print(f"[!] Please update PROXY_FILE in puskes_sqli.py to '{GOOD_PROXY_FILE}' or overwrite proxies.txt manually.")
    else:
        print("[!] No working proxies found! Try a different list.")

if __name__ == "__main__":
    # Suppress SSL warnings
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    validate_proxies()
