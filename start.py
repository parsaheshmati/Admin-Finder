#!/usr/bin/env python3

import os
import sys
import time
import signal
import requests
from urllib.parse import urljoin
from datetime import datetime

HEADERS = {"User-Agent": "NetroxAdminFinder/2.0"}
TIMEOUT = 8.0
DELAY_BETWEEN = 0.03
WORDLIST_FILENAME = "wordlist.txt"
FOUND_FILENAME = "found.txt"
LOG_DIR = "netrox_logs"

try:
    from colorama import init as _colorama_init, Fore, Style
    _colorama_init()
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    BLUE = Fore.CYAN
    MAGENTA = Fore.MAGENTA
    RESET = Style.RESET_ALL
    CYAN = Fore.CYAN
except Exception:
    GREEN = "\033[92m"
    RED = "\033[91m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    RESET = "\033[0m"

DEFAULT_WORDLIST = ["admin/", "admin/login.php", "wp-admin/", "wp-login.php", "administrator/", "login/", "cpanel/"]

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")

def banner():
    art = """
NNNNNNNN        NNNNNNNN                             tttt
N:::::::N       N::::::N                          ttt:::t
N::::::::N      N::::::N                          t:::::t
N:::::::::N     N::::::N                          t:::::t
N::::::::::N    N::::::N    eeeeeeeeeeee    ttttttt:::::ttttttt   rrrrr   rrrrrrrrr      ooooooooooo xxxxxxx      xxxxxxx
N:::::::::::N   N::::::N  ee::::::::::::ee  t:::::::::::::::::t   r::::rrr:::::::::r   oo:::::::::::oox:::::x    x:::::x 
N:::::::N::::N  N::::::N e::::::eeeee:::::eet:::::::::::::::::t   r:::::::::::::::::r o:::::::::::::::ox:::::x  x:::::x  
N::::::N N::::N N::::::Ne::::::e     e:::::etttttt:::::::tttttt   rr::::::rrrrr::::::ro:::::ooooo:::::o x:::::xx:::::x   
N::::::N  N::::N:::::::Ne:::::::eeeee::::::e      t:::::t          r:::::r     r:::::ro::::o     o::::o  x::::::::::x    
N::::::N   N:::::::::::Ne:::::::::::::::::e       t:::::t          r:::::r     rrrrrrro::::o     o::::o   x::::::::x     
N::::::N    N::::::::::Ne::::::eeeeeeeeeee        t:::::t          r:::::r            o::::o     o::::o   x::::::::x     
N::::::N     N:::::::::Ne:::::::e                 t:::::t    ttttttr:::::r            o::::o     o::::o  x::::::::::x    
N::::::N      N::::::::Ne::::::::e                t::::::tttt:::::tr:::::r            o:::::ooooo:::::o x:::::xx:::::x   
N::::::N       N:::::::N e::::::::eeeeeeee        tt::::::::::::::tr:::::r            o:::::::::::::::ox:::::x  x:::::x  
N::::::N        N::::::N  ee:::::::::::::e          tt:::::::::::ttr:::::r             oo:::::::::::oox:::::x    x:::::x 
NNNNNNNN         NNNNNNN    eeeeeeeeeeeeee            ttttttttttt  rrrrrrr               ooooooooooo xxxxxxx      xxxxxxx
"""
    print(GREEN + art + RESET)

def progress_bar(current, total, width=30):
    pct = float(current) / float(total) if total else 0.0
    filled = int(round(width * pct))
    bar = "#" * filled + "-" * (width - filled)
    return f"[{bar}] {int(pct*100):3d}%"

def human_time(seconds):
    if seconds is None or seconds < 0:
        return "--:--"
    m = int(seconds // 60)
    s = int(seconds % 60)
    return f"{m:02d}:{s:02d}"

def load_wordlist():
    if os.path.exists(WORDLIST_FILENAME):
        with open(WORDLIST_FILENAME, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    else:
        with open(WORDLIST_FILENAME, "w", encoding="utf-8") as f:
            for p in DEFAULT_WORDLIST:
                f.write(p + "\n")
        return DEFAULT_WORDLIST

def scan_admin_pages():
    clear_console()
    banner()
    print(f"{YELLOW}--- Admin Page Scanner ---{RESET}\n")

    #print("Do you have permission to scan this target? (yes/no): ").strip().lower()
    

    target = input("Target URL (example: https://example.com): ").strip()
    if not target.startswith("http"):
        target = "https://" + target

    print(YELLOW + "If it gets stuck, press Enter to continue..." + RESET)

    paths = load_wordlist()
    total = len(paths)
    print(f"\n{BLUE}[+] Scanning {total} paths on {target}{RESET}\n")

    session = requests.Session()
    found = []
    start_time = time.monotonic()

    for idx, path in enumerate(paths, start=1):
        url = urljoin(target, path)
        try:
            resp = session.get(url, headers=HEADERS, timeout=TIMEOUT, allow_redirects=True)
            status = resp.status_code
        except requests.RequestException:
            status = "ERR"

        elapsed = time.monotonic() - start_time
        avg = elapsed / idx
        remaining = (total - idx) * avg
        eta = human_time(remaining)
        bar = progress_bar(idx, total)

        if status == 200:
            print(f"{GREEN}[{idx}/{total}] {bar} ETA:{eta} -> 200 OK FOUND: {url}{RESET}")
            found.append(url)
        else:
            print(f"{BLUE}[{idx}/{total}] {bar} ETA:{eta} -> {status} {url}{RESET}")

        time.sleep(DELAY_BETWEEN)

    print(f"\n{YELLOW}--- Scan Finished ---{RESET}")
    if found:
        print(f"{GREEN}[+] {len(found)} pages found:{RESET}")
        for u in found:
            print("  ->", u)
        with open(FOUND_FILENAME, "w", encoding="utf-8") as f:
            for u in found:
                f.write(u + "\n")
        print(f"{YELLOW}[i] Results saved to {FOUND_FILENAME}{RESET}")
    else:
        print(f"{RED}[!] No admin pages found.{RESET}")

    input("\nPress Enter to return to menu...")

def show_help():
    clear_console()
    banner()
    print(f"{YELLOW}--- Help / README ---{RESET}\n")
    print("1. Place your wordlist of admin/login paths in 'wordlist.txt'.")
    print("2. Run the tool and select option [1] to start scanning.")
    print("3. Enter the target URL (e.g., https://example.com).")
    print("4. Discovered admin pages with status 200 will be printed and saved to 'found.txt'.")
    print("\nNOTE: Use this tool ONLY on systems you are authorized to test!")
    input("\nPress Enter to return to menu...")

def show_about():
    clear_console()
    banner()
    print(f"{YELLOW}--- About ---{RESET}\n")
    print(f"{RED} Netrox Admin Finder {RESET}  {GREEN} v2.0  {RESET}")
    print("Developer: Netrox Security")
    print(f"{BLUE}GitHub:{RESET} {YELLOW} https://github.com/parsaheshmati {RESET}")
    print("\nLegal Disclaimer: For authorized security testing only.")
    input("\nPress Enter to return to menu...")

def menu():
    while True:
        clear_console()
        banner()
        print(f"{YELLOW}{'='*50}{RESET}")
        print(f"{MAGENTA}            === Main Menu ==={RESET}")
        print(f"{YELLOW}{'='*50}{RESET}\n")
        
        print(f"{GREEN}1){RESET} {BLUE}Scan for admin pages{RESET}")
        print(f"{GREEN}2){RESET} {CYAN}Help / README{RESET}")
        print(f"{GREEN}3){RESET} {MAGENTA}About{RESET}")
        print(f"{RED}0){RESET} {YELLOW}Exit{RESET}\n")
        
        choice = input(f"{RED}Select an option: {RESET}").strip()

        if choice == "1":
            scan_admin_pages()
        elif choice == "2":
            show_help()
        elif choice == "3":
            show_about()
        elif choice == "0":
            print(f"{RED}Exiting...{RESET}")
            sys.exit(0)
        else:
            print(f"{RED}Invalid choice!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    menu()
