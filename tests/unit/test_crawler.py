"""
Testes unitarios para o crawler
"""

import unittest
from unittest.mock import patch
from urllib.parse import urlparse

import config
from crawler import LinkCrawler
from reporter import ReportGenerator
from scanner import DirectoryScanner
from session import CrawlerSession, RateLimiter


class TestRateLimiter(unittest.TestCase):
    """Testes para RateLimiter."""

    def test_rate_limiter_initialization(self):
        limiter = RateLimiter(requests_per_second=10)
        self.assertEqual(limiter.requests_per_second, 10)
        self.assertEqual(limiter.min_interval, 0.1)
        self.assertEqual(limiter.consecutive_429s, 0)

    def test_rate_limiter_mark_rate_limited(self):
        limiter = RateLimiter(requests_per_second=10)
        limiter.mark_rate_limited()
        self.assertEqual(limiter.consecutive_429s, 1)

        limiter.mark_rate_limited()
        self.assertEqual(limiter.consecutive_429s, 2)

    def test_rate_limiter_reset(self):
        limiter = RateLimiter(requests_per_second=10)
        limiter.mark_rate_limited()
        limiter.reset_rate_limit_counter()
        self.assertEqual(limiter.consecutive_429s, 0)


class TestCrawlerSession(unittest.TestCase):
    """Testes para CrawlerSession."""

    def test_session_creation(self):
        session = CrawlerSession()
        self.assertIsNotNone(session.session)
        self.assertIsNotNone(session.rate_limiter)

    def test_session_headers(self):
        session = CrawlerSession()
        self.assertIn("User-Agent", session.session.headers)
        self.assertIn("Accept", session.session.headers)

    def test_session_respects_ssl_verify(self):
        session = CrawlerSession()
        self.assertEqual(session.session.verify, config.SSL_VERIFY)


class TestURLValidation(unittest.TestCase):
    """Testes para validacao de URLs."""

    def test_valid_http_url(self):
        url = "http://exemplo.com"
        parsed = urlparse(url)
        self.assertEqual(parsed.scheme, "http")
        self.assertIsNotNone(parsed.netloc)

    def test_valid_https_url(self):
        url = "https://exemplo.com"
        parsed = urlparse(url)
        self.assertEqual(parsed.scheme, "https")
        self.assertIsNotNone(parsed.netloc)

    def test_invalid_url(self):
        url = "not a valid url"
        parsed = urlparse(url)
        self.assertEqual(parsed.scheme, "")


class TestLinkCrawler(unittest.TestCase):
    """Testes para LinkCrawler."""

    def test_crawler_initialization(self):
        url = "https://exemplo.com"
        crawler = LinkCrawler(url)
        self.assertEqual(crawler.base_url, url)
        self.assertIn("exemplo.com", crawler.base_domain)
        self.assertEqual(crawler.site_root, "https://exemplo.com")

    @patch("crawler.get_session")
    def test_url_normalization(self, mock_session):
        crawler = LinkCrawler("https://exemplo.com")
        url = "https://exemplo.com/page#section"
        normalized = crawler._normalize_url(url)
        self.assertNotIn("#", normalized)

    def test_is_valid_url(self):
        crawler = LinkCrawler("https://exemplo.com")
        self.assertTrue(crawler._is_valid_url("https://exemplo.com/page"))
        self.assertFalse(crawler._is_valid_url("https://outro.com/page"))
        self.assertFalse(crawler._is_valid_url("ftp://exemplo.com/page"))


class TestDirectoryScanner(unittest.TestCase):
    """Testes para DirectoryScanner."""

    def test_scanner_initialization(self):
        scanner = DirectoryScanner("https://exemplo.com")
        self.assertEqual(scanner.base_url, "https://exemplo.com")

    def test_fingerprinting(self):
        scanner = DirectoryScanner("https://exemplo.com")
        html1 = "  <html> Hello  World  </html>  "
        html2 = "<html>Hello World</html>"
        self.assertEqual(scanner._fingerprint(html1), scanner._fingerprint(html2))

    def test_false_positive_detection(self):
        scanner = DirectoryScanner("https://exemplo.com")
        scanner.base_404_fingerprint = "404 not found page"
        scanner.base_root_fingerprint = "root page"
        self.assertTrue(scanner._is_false_positive("url", 200, "404 not found page"))
        self.assertFalse(scanner._is_false_positive("url", 200, "custom page"))


class TestConfig(unittest.TestCase):
    """Testes para configuracao."""

    def test_config_values(self):
        self.assertIsNotNone(config.TARGET)
        self.assertGreater(config.TIMEOUT, 0)
        self.assertGreater(config.MAX_WORKERS, 0)
        self.assertGreater(config.MAX_RETRIES, 0)


class TestReportGenerator(unittest.TestCase):
    """Testes para ReportGenerator."""

    def test_html_report_escapes_user_content(self):
        results: dict[str, object] = {
            "target": '<script>alert("x")</script>',
            "timestamp": "2026-03-25T12:00:00",
            "waf_detected": "<b>Cloudflare</b>",
            "open_ports": [],
            "directories": [{"path": '"/admin?<script>"', "status": 200}],
            "links": [],
            "technologies": [{"name": "<React>", "category": "Framework"}],
            "subdomains": [],
            "summary": {},
        }

        output_file = config.OUTPUT_DIR / "test_report_escape.html"
        report = ReportGenerator(results)
        report.to_html(output_file)
        content = output_file.read_text(encoding="utf-8")

        output_file.unlink(missing_ok=True)

        self.assertIn("&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;", content)
        self.assertNotIn('<script>alert("x")</script>', content)


if __name__ == "__main__":
    unittest.main()
