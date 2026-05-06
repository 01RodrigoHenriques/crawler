"""
Enumeração de subdomínios com DNS resolution
"""

import socket
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional, Tuple

import config
from logger_config import logger
from session import get_session


class SubdomainEnumerator:
    """Enumera subdomínios com validação de DNS e HTTP"""

    def __init__(self, domain: str):
        self.domain = domain
        self.subdomains_found: list[Dict[str, object]] = []
        self.session = get_session()
        self.lock = threading.Lock()

    def _load_wordlist(self) -> List[str]:
        """Carrega wordlist de subdomínios"""
        subdomains = []

        # Tentar carregar wordlist externo
        try:
            with open(config.WORDLIST_SUBDOMAINS, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip().lower()
                    if line and not line.startswith("#"):
                        subdomains.append(line)
        except FileNotFoundError:
            logger.warning(f"Wordlist não encontrado: {config.WORDLIST_SUBDOMAINS}")

        # Hardcoded fallback
        if not subdomains:
            subdomains = [
                "www",
                "mail",
                "ftp",
                "admin",
                "api",
                "dev",
                "test",
                "staging",
                "blog",
                "shop",
                "app",
                "mobile",
                "secure",
                "portal",
                "webmail",
                "remote",
                "vpn",
                "cloud",
                "backup",
                "git",
                "svn",
                "jenkins",
                "ci",
                "db",
                "database",
                "mysql",
                "postgres",
                "redis",
                "rabbitmq",
                "monitor",
                "monitoring",
                "status",
                "health",
                "swagger",
                "docs",
                "cdn",
                "static",
                "media",
                "assets",
                "image",
                "images",
                "video",
                "download",
                "upload",
                "files",
                "drive",
                "box",
                "dropbox",
                "mail",
                "email",
                "smtp",
                "pop",
                "imap",
                "calendar",
                "contacts",
                "chat",
                "slack",
                "teams",
                "zoom",
                "meet",
                "call",
                "voice",
                "pay",
                "payment",
                "billing",
                "invoice",
                "receipt",
                "order",
                "analytics",
                "metrics",
                "stats",
                "logs",
                "syslog",
                "debug",
                "internal",
                "intranet",
                "corporate",
                "office",
                "hr",
                "employee",
                "dashboard",
                "admin-panel",
                "cpanel",
                "whm",
                "phpmyadmin",
            ]
            logger.info(f"Usando {len(subdomains)} subdomínios hardcoded")
        else:
            logger.info(f"Carregados {len(subdomains)} subdomínios da wordlist")

        return subdomains

    def _resolve_dns(self, subdomain: str) -> Tuple[str, Optional[str]]:
        """
        Resolve subdomain via DNS

        Returns:
            (full_domain, ip_address or None)
        """
        full_domain = f"{subdomain}.{self.domain}"

        try:
            ip = socket.gethostbyname(full_domain)
            return full_domain, ip
        except socket.gaierror:
            return full_domain, None
        except Exception as e:
            logger.debug(f"Erro ao resolver {full_domain}: {e}")
            return full_domain, None

    def _check_http(self, full_domain: str) -> Tuple[bool, Optional[int], str]:
        """
        Verifica se subdomínio está ativo via HTTP/HTTPS

        Returns:
            (is_active, status_code, error_message)
        """
        for scheme in ["https", "http"]:
            try:
                url = f"{scheme}://{full_domain}"
                response = self.session.get(url, timeout=5, allow_redirects=True)

                if response:
                    # Qualquer resposta que não seja 5xx ou timeout é ativa
                    if response.status_code < 500:
                        return True, response.status_code, ""
            except Exception as e:
                logger.debug(f"Erro ao verificar {scheme}://{full_domain}: {str(e)[:100]}")

        return False, None, "Sem resposta HTTP/HTTPS"

    def _enumerate_subdomain(self, subdomain: str) -> Optional[Dict]:
        """Enumera um subdomínio individual"""
        full_domain, ip = self._resolve_dns(subdomain)

        if not ip:
            return None  # DNS não resolveu

        # Verificar se está ativo via HTTP
        is_active, status_code, error = self._check_http(full_domain)

        result = {
            "subdomain": full_domain,
            "ip": ip,
            "active": is_active,
            "status_code": status_code,
        }

        if not is_active and error:
            result["error"] = error

        return result

    def enumerate(self) -> List[Dict]:
        """Enumera todos os subdomínios"""
        logger.info(f"Enumerando subdomínios para {self.domain}...")

        subdomains = self._load_wordlist()
        found_count = 0

        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            futures = {executor.submit(self._enumerate_subdomain, sub): sub for sub in subdomains}

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        is_active = result.get("active", False)

                        # Apenas log para ativos
                        if is_active:
                            with self.lock:
                                self.subdomains_found.append(result)
                                found_count += 1
                                logger.info(f"  OK {result['subdomain']} -> {result['ip']} (Status: {result['status_code']})")
                        else:
                            logger.debug(f"  Inativo: {result['subdomain']} -> {result['ip']}")

                except Exception as e:
                    logger.error(f"Erro ao processar resultado: {e}")

        logger.info(f"Encontrados {found_count} subdomínios ativos")
        return sorted(self.subdomains_found, key=lambda x: x["subdomain"])
