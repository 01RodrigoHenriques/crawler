"""
Módulo de Crawling de Links
"""

import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup
from config import TIMEOUT


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