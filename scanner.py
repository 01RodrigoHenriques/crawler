"""
Port scanning e directory brute-force
"""

import socket
import threading
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Optional

import config
from logger_config import logger
from session import get_session


class PortScanner:
    """Scanner de portas TCP com threading."""

    def __init__(self, host: str):
        self.host = host
        self.open_ports: list[Dict[str, object]] = []
        self.lock = threading.Lock()

    def _scan_port(self, port: int) -> Optional[Dict]:
        """Escaneia uma porta individual."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(config.TIMEOUT)
                result = sock.connect_ex((self.host, port))

                if result == 0:
                    try:
                        service = socket.getservbyport(port)
                    except OSError:
                        service = "unknown"

                    banner = self._get_banner(self.host, port)
                    return {
                        "port": port,
                        "service": service,
                        "status": "open",
                        "banner": banner,
                    }
        except socket.timeout:
            pass
        except Exception as e:
            logger.debug(f"Erro ao escanear porta {port}: {e}")

        return None

    def _get_banner(self, host: str, port: int) -> str:
        """Tenta obter banner do servico."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect((host, port))

                if port in [80, 8000, 8008, 8080, 8888]:
                    request = f"HEAD / HTTP/1.0\r\nHost: {host}\r\n\r\n".encode("utf-8")
                    sock.send(request)
                else:
                    sock.send(b"\r\n")

                banner = sock.recv(1024).decode("utf-8", errors="ignore").strip()
                return banner[:200] if banner else ""
        except Exception:
            return ""

    def scan(self) -> List[Dict]:
        """Escaneia todas as portas configuradas."""
        logger.info(f"Port scanning em {self.host}...")

        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS_PORT_SCAN) as executor:
            futures = {executor.submit(self._scan_port, port): port for port in config.COMMON_PORTS}

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        with self.lock:
                            self.open_ports.append(result)
                            logger.info(f"  OK Porta {result['port']}/tcp aberta - {result['service']}")
                except Exception as e:
                    logger.error(f"Erro ao processar resultado: {e}")

        return sorted(self.open_ports, key=lambda x: x["port"])


class DirectoryScanner:
    """Directory brute-force com deteccao inteligente de 404s."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.session = get_session()
        self.found_dirs: list[Dict[str, object]] = []
        self.lock = threading.Lock()
        self.base_404_fingerprint: str | None = None
        self.base_root_fingerprint: str | None = None

    def _fingerprint(self, html: str) -> str:
        """Cria fingerprint normalizado do HTML para 404 detection."""
        if not html:
            return ""

        text = " ".join(html.lower().split())
        text = text.replace("<html>", "").replace("</html>", "")
        text = text.replace("<body>", "").replace("</body>", "")

        return text.strip()[:500]

    def _init_fingerprints(self):
        """Inicializa fingerprints da pagina root e 404."""
        if self.base_404_fingerprint is not None:
            return

        try:
            response = self.session.get(self.base_url, timeout=config.TIMEOUT)
            if response:
                self.base_root_fingerprint = self._fingerprint(response.text)

            random_path = f"/{uuid.uuid4()}_{uuid.uuid4()}"
            response = self.session.get(f"{self.base_url}{random_path}", timeout=config.TIMEOUT)
            if response:
                self.base_404_fingerprint = self._fingerprint(response.text)

            logger.debug("Fingerprints inicializados")
        except Exception as e:
            logger.error(f"Erro ao inicializar fingerprints: {e}")

    def _is_false_positive(self, url: str, status_code: int, html: str) -> bool:
        """Detecta false positives (servidor catch-all)."""
        normalized = self._fingerprint(html)

        if normalized == self.base_404_fingerprint or normalized == self.base_root_fingerprint:
            return True

        if status_code in [404, 403]:
            return False

        return False

    def _check_directory(self, directory: str) -> Optional[Dict]:
        """Verifica um diretorio."""
        url = f"{self.base_url}/{directory}"

        try:
            response = self.session.head(url, timeout=config.TIMEOUT)

            if not response:
                return None

            status_code = response.status_code

            if status_code in [200, 301, 302, 403]:
                response = self.session.get(url, timeout=config.TIMEOUT, allow_redirects=False)
                if response:
                    status_code = response.status_code
                    html = response.text

                    if not self._is_false_positive(url, status_code, html):
                        if status_code in [200, 301, 302, 403]:
                            return {
                                "path": url,
                                "status": status_code,
                                "size": len(html),
                            }

        except Exception as e:
            logger.debug(f"Erro ao verificar {directory}: {e}")

        return None

    def _load_wordlist(self) -> List[str]:
        """Carrega wordlist de diretorios."""
        directories = []

        try:
            with open(config.WORDLIST_DIRS, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        directories.append(line)
        except FileNotFoundError:
            logger.warning(f"Wordlist nao encontrado: {config.WORDLIST_DIRS}")

        if not directories:
            directories = [
                "admin",
                "api",
                "login",
                "logout",
                "register",
                "dashboard",
                "user",
                "users",
                "profile",
                "settings",
                "config",
                "backup",
                "download",
                "upload",
                "files",
                "images",
                "assets",
                "static",
                "media",
                "public",
                "private",
                "test",
                "dev",
                "development",
                "staging",
                "tmp",
                "cache",
                "temp",
                "logs",
                "bin",
                "lib",
                "robots.txt",
                "sitemap.xml",
                ".well-known",
                ".env",
                "wordpress",
                "wp-admin",
                "wp-login.php",
            ]
            logger.info(f"Usando {len(directories)} diretorios hardcoded")
        else:
            logger.info(f"Carregados {len(directories)} diretorios da wordlist")

        dirs_with_ext = []
        for base in directories:
            for ext in config.DIR_EXTENSIONS:
                dirs_with_ext.append(base + ext)

        return dirs_with_ext

    def scan(self) -> List[Dict]:
        """Escaneia diretorios."""
        logger.info(f"Brute-force de diretorios em {self.base_url}...")

        self._init_fingerprints()

        directories = self._load_wordlist()
        logger.info(f"  Testando {len(directories)} possiveis diretorios...")

        with ThreadPoolExecutor(max_workers=config.MAX_WORKERS) as executor:
            futures = {executor.submit(self._check_directory, directory): directory for directory in directories}

            for future in as_completed(futures):
                try:
                    result = future.result()
                    if result:
                        with self.lock:
                            self.found_dirs.append(result)
                            status_symbol = "OK" if result["status"] == 200 else "INFO"
                            logger.info(f"  {status_symbol} [{result['status']}] {result['path']}")
                except Exception as e:
                    logger.error(f"Erro ao processar resultado: {e}")

        logger.info(f"Encontrados {len(self.found_dirs)} diretorios")
        return self.found_dirs
