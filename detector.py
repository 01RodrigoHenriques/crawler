"""
Módulo de Detecção de Tecnologias
"""

import requests
from config import TIMEOUT


def detect_technologies(url):
    print(f"\n[*] A detetar tecnologias em {url}...")
    techs = []

    try:
        response = requests.get(url, timeout=TIMEOUT, verify=False)
        headers = response.headers
        html = response.text.lower()

        # Headers relevantes
        interesting_headers = ["server", "x-powered-by", "x-generator", "x-drupal-cache",
                                "x-wp-super-cache", "cf-ray"]
        for header in interesting_headers:
            if header in headers:
                value = headers[header]
                print(f"  [+] Header: {header} = {value}")
                techs.append({"type": "header", "name": header, "value": value})

        # Detecção por HTML
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