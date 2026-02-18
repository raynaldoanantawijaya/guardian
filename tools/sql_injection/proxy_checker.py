import requests
import concurrent.futures
import time

TARGET_URL = "https://puskesjaten1.karanganyarkab.go.id"
TEST_URL = "https://www.google.co.id"
PROXY_FILE = "proxies.txt"

def check_proxy(proxy):
    proxies = {
        "http": proxy,
        "https": proxy
    }
    
    start = time.time()
    result = {
        "proxy": proxy,
        "google": False,
        "target": False,
        "latency": 999
    }
    
    # 1. Test Google (Is it alive?)
    try:
        r = requests.get(TEST_URL, proxies=proxies, timeout=5)
        if r.status_code == 200:
            result["google"] = True
            result["latency"] = round(time.time() - start, 2)
    except:
        return result

    # 2. Test Target (Is it blocked?)
    if result["google"]:
        try:
            r = requests.get(TARGET_URL, proxies=proxies, timeout=5, verify=False)
            if r.status_code == 200 or r.status_code == 403: # 403 means we reached the server at least
                result["target"] = True
        except:
            pass
            
    return result

def main():
    print(f"[*] Testing proxies from {PROXY_FILE}...")
    
    with open(PROXY_FILE, "r") as f:
        proxy_list = [line.strip() for line in f if line.strip()]

    valid_proxies = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        future_to_proxy = {executor.submit(check_proxy, p): p for p in proxy_list}
        
        for future in concurrent.futures.as_completed(future_to_proxy):
            data = future.result()
            if data["google"]:
                print(f"[+] ALIVE (Google): {data['proxy']} - {data['latency']}s")
                if data["target"]:
                    print(f"    [!!!] TARGET REACHABLE: {data['proxy']}")
                    valid_proxies.append(data)
                else:
                    print(f"    [-] Target Unreachable/Slow")

    print("\n--- Summary ---")
    if valid_proxies:
        best = min(valid_proxies, key=lambda x: x['latency'])
        print(f"BEST PROXY: {best['proxy']} ({best['latency']}s)")
        # Update run command hint
        print(f"SUGGESTION: Update puskes_sqli.py to use: {best['proxy']}")
    else:
        print("No proxies could reach the target from this environment.")

if __name__ == "__main__":
    main()
