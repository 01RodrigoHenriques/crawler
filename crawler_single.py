#!/usr/bin/env python3
"""
Web Crawler de Reconhecimento
Funções: Directory brute-force, subdomain enumeration, port scan, tech detection
"""

import requests
import socket
import concurrent.futures
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
import json
import datetime
import time
import urllib3

# ─────────────────────────────────────────────
# CONFIGURAÇÃO
# ─────────────────────────────────────────────
TARGET = "https://bolinatec.com"
TIMEOUT = 5
THREADS = 20
OUTPUT_FILE = "resultado_scan.json"

COMMON_DIRS = [
    "admin", "login", "dashboard", "api", "backup", "config",
    "uploads", "images", "files", "test", "dev", "staging",
    "wp-admin", "wp-content", "phpmyadmin", "robots.txt",
    ".git", ".env", "server-status", "readme.txt", "cgi-bin", "bank", "bank/login", "bank/queryxpath.aspx",
    "search.aspx", "signin.aspx", "logout.aspx"
]

COMMON_PORTS = [21, 22, 23, 25, 53, 80, 443, 3306, 3389, 5432, 6379, 8080, 8443, 8888]


# ─────────────────────────────────────────────
# 1. EXTRAÇÃO DE LINKS (Page Crawler)
# ─────────────────────────────────────────────
def crawl_links(url, max_depth=2, visited=None):
    if visited is None:
        visited = set()
    if url in visited or max_depth == 0:
        return visited

    visited.add(url)
    print(f"  [+] A visitar: {url}")

    try:
        response = requests.get(url, timeout=TIMEOUT, verify=False)
        soup = BeautifulSoup(response.text, "html.parser")
        base_domain = urlparse(url).netloc

        for tag in soup.find_all("a", href=True):
            link = urljoin(url, tag["href"])
            parsed = urlparse(link)
            if parsed.netloc == base_domain and link not in visited:
                crawl_links(link, max_depth - 1, visited)

    except Exception as e:
        print(f"  [-] Erro em {url}: {e}")

    return visited


# ─────────────────────────────────────────────
# 2. DIRECTORY BRUTE-FORCE
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# 3. PORT SCANNER
# ─────────────────────────────────────────────
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


# ─────────────────────────────────────────────
# 4. DETECÇÃO DE TECNOLOGIAS
# ─────────────────────────────────────────────
def detect_technologies(url):
    print(f"\n[*] A detetar tecnologias em {url}...")
    techs = []

    try:
        response = requests.get(url, timeout=TIMEOUT, verify=False)
        headers = response.headers
        html = response.text.lower()

        interesting_headers = ["server", "x-powered-by", "x-generator", "x-drupal-cache",
                                "x-wp-super-cache", "cf-ray"]
        for header in interesting_headers:
            if header in headers:
                value = headers[header]
                print(f"  [+] Header: {header} = {value}")
                techs.append({"type": "header", "name": header, "value": value})

        tech_signatures = {
            "WordPress": ["wp-content", "wp-includes"],
            "Joomla": ["joomla", "/components/com_"],
            "Drupal": ["drupal", "/sites/default/"],
            "jQuery": ["jquery.min.js", "jquery.js"],
            "Bootstrap": ["bootstrap.min.css", "bootstrap.css"],
            "React": ["react.min.js", "__react"],
            "PHP": [".php", "phpsessid"],
            "ASP.NET": ["__viewstate", "asp.net"],
        }

        for tech, signatures in tech_signatures.items():
            if any(sig in html for sig in signatures):
                print(f"  [+] Tecnologia detetada: {tech}")
                techs.append({"type": "cms_or_framework", "name": tech})

    except Exception as e:
        print(f"  [-] Erro: {e}")

    return techs


# ─────────────────────────────────────────────
# 5. MAIN - JUNTA TUDO
# ─────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  CRAWLER DE RECONHECIMENTO")
    print("  AVISO: Use apenas para fins educacionais e com permissão!")
    print("=" * 60)
    print(f"  Alvo   : {TARGET}")
    print(f"  Hora   : {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    parsed = urlparse(TARGET)
    host = parsed.netloc or TARGET

    results = {
        "target": TARGET,
        "timestamp": datetime.datetime.now().isoformat(),
        "open_ports": [],
        "directories": [],
        "links": [],
        "technologies": []
    }

    results["open_ports"] = port_scan(host)
    results["directories"] = brute_force_dirs(TARGET)
    results["technologies"] = detect_technologies(TARGET)

    print(f"\n[*] A extrair links de {TARGET}...")
    links = crawl_links(TARGET, max_depth=2)
    results["links"] = list(links)
    print(f"  [+] {len(links)} links encontrados")

    with open(OUTPUT_FILE, "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n[✓] Scan completo. Resultados guardados em: {OUTPUT_FILE}")
    print(f"    Portas abertas : {len(results['open_ports'])}")
    print(f"    Diretórios     : {len(results['directories'])}")
    print(f"    Tecnologias    : {len(results['technologies'])}")
    print(f"    Links          : {len(results['links'])}")


if __name__ == "__main__":
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()