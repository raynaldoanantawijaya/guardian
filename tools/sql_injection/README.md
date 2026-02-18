# sqlmapauto: Advanced Automated Wrapper for SQLMap & Site Hunter

**sqlmapauto** is now a comprehensive vulnerability suite. It includes the classic SQLMap automation wrapper and a new specialized tool, **Surakarta Hunter CLI**, for detecting complex web misconfigurations (WAF Bypass, Laravel .env exposure, ISPConfig detection).

## 🚀 Features

### 1. sqlmapauto (SQL Injection)
*   **Smart WAF Bypass**: Automatically loads effective tamper scripts.
*   **Auto Proxy Rotation**: Randomly selects a high-anonymity SOCKS5/HTTP proxy.
*   **One-Command-Run**: Optimized settings for maximum efficiency.

### 2. Surakarta Hunter CLI (Web & Misconfiguration)
*   **Laravel Evasion**: Bypasses WAF blocks on `.env` files using techniques like semicolon truncation (`/.env;`) and path traversal.
*   **Admin Panel Detection**: Scans for ISPConfig (`:8080`), phpMyAdmin, and other admin portals.
*   **MySQL Probing**: Checks for external database access via proxy.

## 📋 Requirements
*   **Python 3.x**
*   **Dependencies**: `requests`, `pysocks`
    ```bash
    pip install requests pysocks
    ```

## 🛠️ Installation

```bash
git clone https://github.com/raynaldoanantawijaya/sqlmapauto.git
cd sqlmapauto
```

## 💻 Usage

### A. SQL Injection Scanning (sqlmapauto)
Use this for specific URL targets with parameters (e.g., `?id=1`).

```bash
python sqlmapauto.py <TARGET_URL>
```
*Example:*
```bash
python sqlmapauto.py "http://surakarta.go.id/news.php?id=12"
```

### B. Full Site Vulnerability Scan (Surakarta Hunter)
Use this to scan the domain for admin panels, config leaks, and open ports.

```bash
python surakarta_hunter.py
```
*The tool will automatically:*
1.  Check for **ISPConfig** on port 8080.
2.  Attempt to bypass WAF to read **Laravel .env** files.
3.  Probe for **MySQL** (Port 3306) access.
4.  Ask if you want to run `sqlmapauto` on a specific URL found.

## ⚠️ Disclaimer
This tool is for educational purposes and authorized penetration testing only. Do not use this tool on targets you do not have permission to audit. code authentication.
