"""
Módulo de Scanning: Port scan e brute-force de diretórios
"""

import socket
import concurrent.futures
import requests
import time
from config import TIMEOUT, THREADS, COMMON_DIRS, COMMON_PORTS


def check_directory(base_url, directory):
    url = f"{base_url.rstrip('/')}/{directory}"
    try:
        time.sleep(0.1)  # Rate limiting para evitar bloqueios
        response = requests.get(url, timeout=TIMEOUT, verify=False, allow_redirects=False)
        if response.status_code in [200, 301, 302, 403]:
            return {"path": url, "status": response.status_code}
    except Exception:
        pass
    return None


def brute_force_dirs(base_url):
    print(f"\n[*] A fazer brute-force de diretórios em {base_url}...")
    found = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(check_directory, base_url, d): d for d in COMMON_DIRS}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                status = result["status"]
                symbol = "+" if status == 200 else "~"
                print(f"  [{symbol}] [{status}] {result['path']}")
                found.append(result)

    return found


def scan_port(host, port):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(TIMEOUT)
        result = sock.connect_ex((host, port))
        sock.close()
        if result == 0:
            try:
                service = socket.getservbyport(port)
            except Exception:
                service = "unknown"
            return {"port": port, "service": service}
    except Exception:
        pass
    return None


def port_scan(host):
    print(f"\n[*] A fazer port scan em {host}...")
    open_ports = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=THREADS) as executor:
        futures = {executor.submit(scan_port, host, p): p for p in COMMON_PORTS}
        for future in concurrent.futures.as_completed(futures):
            result = future.result()
            if result:
                print(f"  [+] Porta {result['port']}/tcp aberta - {result['service']}")
                open_ports.append(result)

    return sorted(open_ports, key=lambda x: x["port"])