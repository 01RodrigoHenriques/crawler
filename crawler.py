"""
Crawler de links com suporte a robots.txt e sitemap
"""
import re
from typing import List, Set
from urllib.parse import urljoin, urlparse, urlunparse

from bs4 import BeautifulSoup

import config
from logger_config import logger
from session import get_session


class LinkCrawler:
    """Crawler para extracao de links no mesmo dominio."""

    def __init__(self, base_url: str):
        self.base_url = base_url
        parsed = urlparse(base_url)
        self.base_domain = parsed.netloc
        self.site_root = f"{parsed.scheme}://{parsed.netloc}"
        self.visited = set()
        self.to_visit = {base_url}
        self.session = get_session()
        self.links_found = set()

    def _normalize_url(self, url: str) -> str:
        """Normaliza URL para evitar variacoes do mesmo link."""
        try:
            parsed = urlparse(url)
            return urlunparse((parsed.scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, ""))
        except Exception:
            return url

    def _is_valid_url(self, url: str) -> bool:
        """Verifica se URL e valida e do mesmo dominio."""
        try:
            parsed = urlparse(url)

            if parsed.scheme not in ["http", "https"]:
                return False

            if parsed.netloc != self.base_domain:
                return False

            if any(path in parsed.path.lower() for path in [".jpg", ".png", ".gif", ".pdf", ".zip", ".exe"]):
                return False

            return True
        except Exception:
            return False

    def _parse_robots_txt(self) -> Set[str]:
        """Parse robots.txt para descobrir paths permitidos."""
        if not config.ROBOTS_TXT_CHECK:
            return set()

        try:
            robots_url = f"{self.site_root.rstrip('/')}/robots.txt"
            response = self.session.get(robots_url, timeout=5)

            if response and response.status_code == 200:
                logger.info("robots.txt encontrado")

                sitemaps = re.findall(r"Sitemap:\s*(.+)", response.text, re.IGNORECASE)
                for sitemap_url in sitemaps:
                    logger.debug(f"  Sitemap encontrado: {sitemap_url.strip()}")

                allowed_paths = set()
                for line in response.text.splitlines():
                    if line.startswith("Allow:"):
                        path = line.split(":", 1)[1].strip()
                        if path:
                            allowed_paths.add(path)

                return allowed_paths
        except Exception as e:
            logger.debug(f"Erro ao parse robots.txt: {e}")

        return set()

    def _parse_sitemap(self) -> Set[str]:
        """Parse sitemap.xml para descobrir URLs."""
        if not config.SITEMAP_CHECK:
            return set()

        urls = set()
        sitemap_urls = [
            f"{self.site_root.rstrip('/')}/sitemap.xml",
            f"{self.site_root.rstrip('/')}/sitemap_index.xml",
        ]

        for sitemap_url in sitemap_urls:
            try:
                response = self.session.get(sitemap_url, timeout=5)
                if response and response.status_code == 200:
                    logger.debug(f"Sitemap encontrado: {sitemap_url}")

                    matches = re.findall(r"<loc>(.+?)</loc>", response.text)
                    for match in matches:
                        url = match.strip()
                        if self._is_valid_url(url):
                            urls.add(url)

                    logger.debug(f"  {len(matches)} URLs extraidas do sitemap")
            except Exception as e:
                logger.debug(f"Erro ao parse sitemap: {e}")

        return urls

    def _extract_links_from_page(self, url: str) -> List[str]:
        """Extrai links de uma pagina HTML."""
        try:
            response = self.session.get(url, timeout=config.TIMEOUT)

            if not response:
                return []

            if response.status_code != 200:
                logger.debug(f"Status {response.status_code}: {url}")
                return []

            if "text/html" not in response.headers.get("Content-Type", "").lower():
                return []

            soup = BeautifulSoup(response.text, "html.parser")
            links = []

            for tag in soup.find_all("a", href=True):
                link = self._normalize_url(urljoin(url, tag["href"]))
                if self._is_valid_url(link):
                    links.append(link)

            for tag in soup.find_all(["script", "link"]):
                src = tag.get("src") or tag.get("href")
                if src:
                    link = self._normalize_url(urljoin(url, src))
                    if self._is_valid_url(link):
                        links.append(link)

            logger.debug(f"  Extraidos {len(links)} links de {url}")
            return links
        except Exception as e:
            logger.debug(f"Erro ao extrair links de {url}: {e}")
            return []

    def crawl(self, max_pages: int = config.MAX_PAGES_PER_SCAN) -> Set[str]:
        """
        Crawl recursivo com limite de paginas.

        Args:
            max_pages: Maximo de paginas a crawlear

        Returns:
            Set de links encontrados
        """
        logger.info(f"Iniciando crawl de {self.base_url}")

        extra_urls = self._parse_robots_txt()
        extra_urls.update(self._parse_sitemap())

        if extra_urls:
            logger.info(f"{len(extra_urls)} URLs adicionais descobertas via robots.txt/sitemap")
            for url in extra_urls:
                url_full = urljoin(self.base_url, url)
                if self._is_valid_url(url_full):
                    self.to_visit.add(self._normalize_url(url_full))

        while self.to_visit and len(self.visited) < max_pages:
            url = self.to_visit.pop()

            if url in self.visited:
                continue

            self.visited.add(url)
            logger.debug(f"  [{len(self.visited)}/{max_pages}] {url}")

            new_links = self._extract_links_from_page(url)
            for link in new_links:
                if link not in self.visited and len(self.to_visit) < max_pages:
                    self.to_visit.add(link)
                    self.links_found.add(link)

        logger.info(f"Crawl concluido: {len(self.visited)} paginas visitadas")
        return self.links_found
