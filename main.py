#!/usr/bin/env python3
"""
Web Crawler de Reconhecimento
Funções: Directory brute-force, subdomain enumeration, port scan, tech detection
"""

import json
import datetime
from urllib.parse import urlparse
import urllib3

from config import TARGET, OUTPUT_FILE
from crawler import crawl_links
from scanner import port_scan, brute_force_dirs
from detector import detect_technologies


def main():
    print("=" * 60)
    print("  CRAWLER DE RECONHECIMENTO")
    print("  Uso apenas para fins educacionais e com permissão!")
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

    # Port scan
    results["open_ports"] = port_scan(host)

    # Brute-force de diretórios
    results["directories"] = brute_force_dirs(TARGET)

    # Deteção de tecnologias
    results["technologies"] = detect_technologies(TARGET)

    # Crawl de links
    print(f"\n[*] A extrair links de {TARGET}...")
    links = crawl_links(TARGET, max_depth=2)
    results["links"] = list(links)
    print(f"  [+] {len(links)} links encontrados")

    # Guardar resultados
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