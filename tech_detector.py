"""
Detecção de tecnologias, frameworks e CMS
"""

from collections.abc import Mapping
from typing import Dict, List

import config
from logger_config import logger
from session import get_session


class TechnologyDetector:
    """Detecta tecnologias, frameworks e CMS"""

    def __init__(self, url: str):
        self.url = url
        self.session = get_session()
        self.detected_techs: list[Dict[str, str]] = []

    def _detect_from_headers(
        self,
        headers: Mapping[str, str],
    ) -> List[tuple[str, str, str]]:
        """Detecta tecnologias via headers HTTP"""
        techs = []

        important_headers = [
            "server",
            "x-powered-by",
            "x-generator",
            "x-drupal-cache",
            "x-wp-super-cache",
            "cf-ray",
            "x-aspnet-version",
            "x-iis-version",
            "x-ua-compatible",
            "strict-transport-security",
        ]

        for header, value in headers.items():
            header_lower = header.lower()

            if header_lower in important_headers:
                # Detectar CMS/Framework específicos
                value_lower = value.lower()

                if "wordpress" in value_lower or "wp" in value_lower:
                    techs.append(("WordPress", "CMS", value))
                elif "joomla" in value_lower:
                    techs.append(("Joomla", "CMS", value))
                elif "drupal" in value_lower:
                    techs.append(("Drupal", "CMS", value))
                elif "express" in value_lower:
                    techs.append(("Express.js", "Framework", value))
                elif "nginx" in value_lower:
                    techs.append(("Nginx", "Web Server", value))
                elif "apache" in value_lower:
                    techs.append(("Apache", "Web Server", value))
                elif "iis" in value_lower or "asp.net" in value_lower:
                    techs.append(("IIS / ASP.NET", "Web Server", value))
                elif "php" in value_lower:
                    techs.append(("PHP", "Language", value))
                elif "cloudflare" in value_lower:
                    techs.append(("Cloudflare", "CDN", value))
                elif "akamai" in value_lower:
                    techs.append(("Akamai", "CDN", value))
                else:
                    # Generic tech
                    techs.append((value, "Unknown", header))

        return techs

    def _detect_from_html(self, html: str) -> List[tuple[str, str, str]]:
        """Detecta tecnologias via conteúdo HTML"""
        techs = []
        html_lower = html.lower()

        for tech_name, signatures in config.TECH_SIGNATURES.items():
            # Check HTML signatures
            html_sigs = signatures.get("html", [])
            if any(sig.lower() in html_lower for sig in html_sigs):
                techs.append((tech_name, "Framework/CMS/Library", "HTML analysis"))
                continue

            # Check for specific files
            files_sigs = signatures.get("files", [])
            for file_sig in files_sigs:
                if file_sig.lower() in html_lower:
                    techs.append((tech_name, "Framework/CMS", f"File: {file_sig}"))
                    break

        return techs

    def _check_specific_endpoints(self) -> List[tuple[str, str, str]]:
        """Verifica endpoints específicos para detecção de CMS"""
        techs = []

        endpoints = {
            "/wp-admin/": "WordPress",
            "/wp-login.php": "WordPress",
            "/administrator/": "Joomla",
            "/admin/": "Multiple",
            "/sites/default/": "Drupal",
            "/sites/all/": "Drupal",
            "/modules/": "Drupal",
            "/.env": "Generic (Exposed config)",
            "/.git": "Git Repository",
            "/.well-known/": "Standard config",
        }

        for endpoint, tech in endpoints.items():
            try:
                response = self.session.head(f"{self.url.rstrip('/')}{endpoint}", timeout=3)
                if response and response.status_code in [200, 301, 302, 403]:
                    techs.append((tech, "Endpoint", endpoint))
                    logger.debug(f"    Endpoint encontrado: {tech} ({endpoint})")
            except Exception:
                pass

        return techs

    def detect(self) -> List[Dict]:
        """
        Detecta todas as tecnologias

        Returns:
            Lista de dicts com tecnologias detectadas
        """
        logger.info(f"Detectando tecnologias em {self.url}...")

        try:
            response = self.session.get(self.url, timeout=config.TIMEOUT)

            if not response:
                logger.warning("Não foi possível obter resposta para detecção de tecnologias")
                return []

            techs_detected = set()  # Usar set para evitar duplicatas

            # 1. Detectar via headers
            logger.debug("  Analisando headers...")
            for tech, category, _ in self._detect_from_headers(response.headers):
                techs_detected.add((tech, category))
                logger.debug(f"    OK {tech} ({category})")

            # 2. Detectar via HTML
            logger.debug("  Analisando HTML...")
            for tech, category, _ in self._detect_from_html(response.text):
                techs_detected.add((tech, category))
                logger.debug(f"    OK {tech} ({category})")

            # 3. Verificar endpoints específicos
            logger.debug("  Verificando endpoints específicos...")
            for tech, category, _ in self._check_specific_endpoints():
                techs_detected.add((tech, category))

            # Converter para list of dicts
            result = []
            for tech, category in sorted(techs_detected):
                result.append({"name": tech, "category": category})
                self.detected_techs.append({"name": tech, "category": category})

            logger.info(f"Detectadas {len(result)} tecnologias")
            return result

        except Exception as e:
            logger.error(f"Erro ao detectar tecnologias: {e}")
            return []
