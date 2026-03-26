"""
Sessao HTTP com retry inteligente, rate limiting e proxy support
"""
import random
import threading
import time
from typing import Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

import config
from logger_config import logger


class RateLimiter:
    """Rate limiter adaptativo com jitter para evitar bloqueio por padroes."""

    def __init__(self, requests_per_second: float = config.RATE_LIMIT):
        self.requests_per_second = requests_per_second
        self.min_interval = 0 if requests_per_second <= 0 else 1.0 / requests_per_second
        self.last_request_time = 0.0
        self.consecutive_429s = 0
        self.lock = threading.Lock()

    def wait(self):
        """Aguarda e aplica rate limiting."""
        with self.lock:
            now = time.time()
            elapsed = now - self.last_request_time

            if self.consecutive_429s > 0:
                delay = min(config.MAX_DELAY, self.min_interval * (2 ** self.consecutive_429s))
            else:
                delay = self.min_interval

            jitter = random.uniform(0, 0.1 * delay) if delay > 0 else 0
            delay += jitter

            if elapsed < delay:
                time.sleep(delay - elapsed)

            self.last_request_time = time.time()

    def mark_rate_limited(self):
        """Marca que recebemos 429 (Too Many Requests)."""
        with self.lock:
            self.consecutive_429s += 1
            current_count = self.consecutive_429s
        logger.warning(f"Rate limited (429). Consecutive count: {current_count}")

    def reset_rate_limit_counter(self):
        """Reseta contador de 429s."""
        with self.lock:
            self.consecutive_429s = 0


class CrawlerSession:
    """Sessao HTTP thread-safe com retry, rate limiting e WAF detection."""

    def __init__(self):
        self.session = self._create_session()
        self.rate_limiter = RateLimiter(config.RATE_LIMIT)
        self.detected_waf = None
        self.waf_lock = threading.Lock()

    def _create_session(self) -> requests.Session:
        """Cria sessao com retry strategy e headers customizados."""
        session = requests.Session()

        retry_strategy = Retry(
            total=config.MAX_RETRIES,
            backoff_factor=config.BACKOFF_FACTOR,
            status_forcelist=list(config.RETRY_STATUS_CODES),
            allowed_methods=["GET", "HEAD", "OPTIONS"],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        session.headers.update(
            {
                "User-Agent": random.choice(config.USER_AGENTS),
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
                "Accept-Encoding": "gzip, deflate, br",
                "DNT": "1",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
            }
        )

        session.verify = config.SSL_VERIFY

        if config.PROXY_ENABLED and config.PROXIES:
            session.proxies.update(config.PROXIES)

        if config.AUTH_CONFIG.enabled:
            if config.AUTH_CONFIG.auth_type == "basic":
                session.auth = (config.AUTH_CONFIG.username, config.AUTH_CONFIG.password)
            elif config.AUTH_CONFIG.auth_type == "bearer":
                session.headers["Authorization"] = f"Bearer {config.AUTH_CONFIG.token}"

        return session

    def get(self, url: str, **kwargs) -> Optional[requests.Response]:
        """GET request com rate limiting e tratamento de erros."""
        return self._request("GET", url, **kwargs)

    def head(self, url: str, **kwargs) -> Optional[requests.Response]:
        """HEAD request com rate limiting e tratamento de erros."""
        return self._request("HEAD", url, **kwargs)

    def _request(self, method: str, url: str, **kwargs) -> Optional[requests.Response]:
        """Request generico com rate limiting, retry e WAF detection."""
        timeout = kwargs.pop("timeout", config.TIMEOUT)
        allow_redirects = kwargs.pop("allow_redirects", True)

        self.rate_limiter.wait()

        headers = dict(kwargs.pop("headers", {}))
        headers["User-Agent"] = random.choice(config.USER_AGENTS)

        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=timeout,
                allow_redirects=allow_redirects,
                headers=headers,
                **kwargs,
            )

            self._check_waf(response)

            if response.status_code == 429:
                self.rate_limiter.mark_rate_limited()
            else:
                self.rate_limiter.reset_rate_limit_counter()

            return response

        except requests.exceptions.Timeout:
            logger.warning(f"Timeout: {url}")
            return None
        except requests.exceptions.ConnectionError as e:
            logger.debug(f"Connection error for {url}: {e}")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error for {url}: {e}")
            return None

    def _check_waf(self, response: requests.Response):
        """Detecta WAF baseado em headers e respostas."""
        with self.waf_lock:
            if self.detected_waf:
                return

            headers = {k.lower(): v.lower() for k, v in response.headers.items()}

            for waf_name, signatures in config.WAF_SIGNATURES.items():
                for sig in signatures:
                    if any(sig.lower() in header for header in headers.values()):
                        self.detected_waf = waf_name
                        logger.warning(f"WAF detectado: {waf_name}")
                        return

    def close(self):
        """Fecha sessao."""
        self.session.close()
        logger.debug("Session closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


_session = None
_session_lock = threading.Lock()


def get_session() -> CrawlerSession:
    """Retorna sessao global (thread-safe para multiplas chamadas)."""
    global _session
    if _session is None:
        with _session_lock:
            if _session is None:
                _session = CrawlerSession()
    return _session
