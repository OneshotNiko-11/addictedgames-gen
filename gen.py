import requests
import random
import string
import threading
import time
import os
from colorama import init, Fore

init()

def load_proxies():
    try:
        with open("data/proxies.txt", "r") as f:
            proxies = [line.strip() for line in f if line.strip()]
            if proxies:
                print(Fore.YELLOW + f"[*] Loaded {len(proxies)} proxies")
            return proxies
    except:
        return []

def get_proxy(proxies, index):
    if not proxies:
        return None
    return proxies[index % len(proxies)]

def setup_session_proxy(session, proxy_str, use_proxies):
    if use_proxies and proxy_str:
        try:
            session.proxies.update({
                'http': f'socks5://{proxy_str}',
                'https': f'socks5://{proxy_str}'
            })
        except:
            pass
    return session

def create_temp_inbox(session):
    try:
        url = 'https://api.internal.temp-mail.io/api/v3/email/new'
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        payload = {"min_name_length": 10, "max_name_length": 10}
        response = session.post(url, headers=headers, json=payload, timeout=15)

        if response.status_code != 200:
            return None

        data = response.json()
        email = data.get('email')

        if not email:
            return None

        return {'address': email}
    except:
        return None

def generate_username():
    chars = string.ascii_lowercase + string.digits
    return ''.join(random.choice(chars) for _ in range(10))

def generate_password():
    uppercase = random.choice(string.ascii_uppercase)
    symbol = random.choice('!@#$%^&*')
    number = random.choice(string.digits)
    lowercase = ''.join(random.choice(string.ascii_lowercase) for _ in range(8))

    password = uppercase + lowercase + symbol + number
    password_list = list(password)
    random.shuffle(password_list)
    return ''.join(password_list)

def create_account(proxies, target_accounts, accounts_created, lock, running, proxy_index_counter, use_proxies):
    while running[0]:
        with lock:
            if accounts_created[0] >= target_accounts:
                break
            proxy_index = proxy_index_counter[0]
            proxy_index_counter[0] += 1

        proxy = get_proxy(proxies, proxy_index) if use_proxies else None
        session = requests.Session()
        session = setup_session_proxy(session, proxy, use_proxies)

        try:
            temp_mail = create_temp_inbox(session)
            if not temp_mail or 'address' not in temp_mail:
                continue

            email = temp_mail['address']
            print(Fore.GREEN + "[*] (mail made) " + Fore.LIGHTMAGENTA_EX + f"({email})")
            username = generate_username()
            password = generate_password()

            url = 'https://addictinggames.com/user/register'
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Origin': 'https://addictinggames.com',
                'Referer': 'https://addictinggames.com/'
            }

            payload = {
                "name": [{"value": username}],
                "mail": [{"value": email}],
                "pass": [{"value": password}],
                "field_opt_in": [{"value": False}]
            }

            response = session.post(url, headers=headers, json=payload, timeout=15)

            if response.status_code == 200:
                with lock:
                    if accounts_created[0] < target_accounts:
                        accounts_created[0] += 1
                        with open("accs.txt", "a") as f:
                            f.write(f"{email}:{password}\n")
                        print(Fore.CYAN + "[+] (created) " + Fore.LIGHTMAGENTA_EX + f"({email}:{password})")
            else:
                print(Fore.RED + f"[-] (failed) {response.status_code}")

        except Exception as e:
            continue

def main():
    os.system('cls' if os.name == 'nt' else 'clear')

    print(Fore.LIGHTYELLOW_EX + "AddictingGames.com Generator")

    proxies = []
    use_proxies = False

    use_proxy_input = input(Fore.LIGHTCYAN_EX + "Use proxies? (y/n): " + Fore.WHITE).lower()
    if use_proxy_input == 'y':
        proxies = load_proxies()
        if not proxies:
            print(Fore.RED + "[!] No proxies found")
            return
        use_proxies = True
        print(Fore.GREEN + "[+] Using proxies")
    else:
        print(Fore.YELLOW + "[*] Running without proxies")

    try:
        target_accounts = int(input(Fore.LIGHTCYAN_EX + "Accounts to make: " + Fore.WHITE))
        threads_count = int(input(Fore.LIGHTCYAN_EX + "Threads: " + Fore.WHITE))
    except:
        return

    accounts_created = [0]
    running = [True]
    lock = threading.Lock()
    proxy_index_counter = [0]
    threads = []

    for i in range(threads_count):
        thread = threading.Thread(target=create_account, args=(proxies, target_accounts, accounts_created, lock, running, proxy_index_counter, use_proxies), daemon=True)
        threads.append(thread)
        thread.start()

    try:
        while any(t.is_alive() for t in threads):
            time.sleep(0.5)
            if accounts_created[0] >= target_accounts:
                running[0] = False
                break
    except KeyboardInterrupt:
        running[0] = False
        print(Fore.RED + "\n[!] Stopping...")

    print(Fore.LIGHTGREEN_EX + f"\nCreated {accounts_created[0]} accounts")
    print(Fore.LIGHTBLUE_EX + "[*] Saved to accs.txt")
    print(Fore.LIGHTBLUE_EX + "[*] Format: email:password")

if __name__ == "__main__":
    os.makedirs("output", exist_ok=True)
    os.makedirs("data", exist_ok=True)
    main()
