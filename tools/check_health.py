#!/usr/bin/env python3
import shutil
import sys
import os
import yaml
from pathlib import Path

# Color codes
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"
BOLD = "\033[1m"

TOOLS = {
    "Network": ["nmap", "masscan"],
    "Web Recon": ["httpx", "whatweb", "wafw00f"],
    "Subdomain": ["subfinder", "amass", "dnsrecon"],
    "Vulnerability": ["nuclei", "nikto", "sqlmap", "wpscan"],
    "SSL/TLS": ["testssl", "sslyze"], # testssl might be a script
    "Content": ["gobuster", "ffuf", "arjun"],
    "Analysis": ["xsstrike", "gitleaks", "cmseek"]
}

def check_tool(tool_name):
    # Special handling for tools that might be aliased or scripts
    if tool_name == "testssl":
        # Check standard path or alias
        if shutil.which("testssl") or shutil.which("testssl.sh"):
            return True
        return False
        
    return shutil.which(tool_name) is not None

def check_python_env():
    print(f"\n{BOLD}[*] Checking Python Environment...{RESET}")
    print(f"Python Version: {sys.version.split()[0]}")
    if sys.version_info < (3, 11):
        print(f"{RED}[FAIL] Python 3.11+ required!{RESET}")
    else:
        print(f"{GREEN}[PASS] Python version ok{RESET}")

    # Check imports
    try:
        import cli.main
        print(f"{GREEN}[PASS] Guardian CLI package found{RESET}")
    except ImportError:
        print(f"{RED}[FAIL] Guardian CLI package NOT installed (run 'pip install -e .'){RESET}")

def check_config():
    print(f"\n{BOLD}[*] Checking Configuration...{RESET}")
    config_path = Path("config/guardian.yaml")
    if not config_path.exists():
        print(f"{RED}[FAIL] config/guardian.yaml NOT found!{RESET}")
        return

    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
        
        provider = config.get("ai", {}).get("provider", "unknown")
        print(f"Active Provider: {BOLD}{provider}{RESET}")
        
        # Check API Key
        api_key = config.get("ai", {}).get(provider, {}).get("api_key")
        env_var = f"{provider.upper()}_API_KEY"
        
        if api_key:
            print(f"{GREEN}[PASS] API Key configured in yaml{RESET}")
        elif os.environ.get(env_var):
            print(f"{GREEN}[PASS] API Key configured in ENV ({env_var}){RESET}")
        else:
            print(f"{RED}[FAIL] No API Key found for {provider}!{RESET}")
            
    except Exception as e:
        print(f"{RED}[FAIL] Error reading config: {e}{RESET}")

def main():
    print(f"{BOLD}🛡️  Guardian System Health Check 🛡️{RESET}")
    print("=" * 40)
    
    check_python_env()
    check_config()
    
    print(f"\n{BOLD}[*] Checking External Tools (19/19)...{RESET}")
    
    missing_tools = []
    
    for category, tool_list in TOOLS.items():
        print(f"\n{BOLD}:: {category} ::{RESET}")
        for tool in tool_list:
            if check_tool(tool):
                print(f"{GREEN} [✔] {tool:<15} INSTALLED{RESET}")
            else:
                print(f"{RED} [✘] {tool:<15} MISSING{RESET}")
                missing_tools.append(tool)

    print("\n" + "=" * 40)
    if not missing_tools:
        print(f"{GREEN}{BOLD}🎉 ALL SYSTEMS GO! Guardian is fully armed.{RESET}")
    else:
        print(f"{YELLOW}{BOLD}⚠️  {len(missing_tools)} Tools Missing.{RESET}")
        print("To install missing tools:")
        print(f"sudo apt install {' '.join([t for t in missing_tools if t not in ['httpx', 'subfinder', 'nuclei']])}")
        print("(Go tools like httpx/nuclei need 'go install ...')")

if __name__ == "__main__":
    main()
