"""Integration tests against a local HTTP server."""

from contextlib import contextmanager
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from threading import Thread
from typing import Iterator
from urllib.parse import urlparse

import config
from crawler import LinkCrawler
from scanner import DirectoryScanner


def _build_handler(routes):
    default_headers = {"Content-Type": "text/html; charset=utf-8"}

    class Handler(BaseHTTPRequestHandler):
        def _respond(self, include_body: bool) -> None:
            path = urlparse(self.path).path or "/"
            status_code, headers, body = routes.get(
                path,
                (404, default_headers, "<html><body>Not Found</body></html>"),
            )

            self.send_response(status_code)

            response_headers = dict(default_headers)
            response_headers.update(headers)
            for header_name, header_value in response_headers.items():
                self.send_header(header_name, header_value)

            self.end_headers()

            if include_body and body:
                self.wfile.write(body.encode("utf-8"))

        def do_GET(self) -> None:  # noqa: N802 - interface name from BaseHTTPRequestHandler
            self._respond(True)

        def do_HEAD(self) -> None:  # noqa: N802 - interface name from BaseHTTPRequestHandler
            self._respond(False)

        def log_message(self, format: str, *args) -> None:  # noqa: A003 - stdlib signature
            return

    return Handler


@contextmanager
def local_http_server(routes) -> Iterator[str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), _build_handler(routes))
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()

    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=5)
        server.server_close()


def test_link_crawler_discovers_same_domain_links():
    routes = {
        "/": (
            200,
            {"Content-Type": "text/html; charset=utf-8"},
            """
            <html>
              <body>
                <a href="/about">About</a>
                <a href="/contact#team">Contact</a>
                <a href="https://example.org/external">External</a>
              </body>
            </html>
            """,
        ),
        "/about": (
            200,
            {"Content-Type": "text/html; charset=utf-8"},
            "<html><body>About</body></html>",
        ),
        "/contact": (
            200,
            {"Content-Type": "text/html; charset=utf-8"},
            "<html><body>Contact</body></html>",
        ),
    }

    with local_http_server(routes) as base_url:
        crawler = LinkCrawler(base_url)
        links = crawler.crawl(max_pages=5)

    assert f"{base_url}/about" in links
    assert f"{base_url}/contact" in links
    assert all("example.org" not in link for link in links)


def test_directory_scanner_detects_existing_directory(tmp_path, monkeypatch):
    routes = {
        "/": (200, {"Content-Type": "text/html; charset=utf-8"}, "<html><body>Home</body></html>"),
        "/admin": (
            200,
            {"Content-Type": "text/html; charset=utf-8"},
            "<html><body>Admin</body></html>",
        ),
    }

    wordlist_file = tmp_path / "directories.txt"
    wordlist_file.write_text("admin\nmissing\n", encoding="utf-8")

    monkeypatch.setattr(config, "WORDLIST_DIRS", wordlist_file)
    monkeypatch.setattr(config, "DIR_EXTENSIONS", [""])
    monkeypatch.setattr(config, "MAX_WORKERS", 2)
    monkeypatch.setattr(config, "TIMEOUT", 2)

    with local_http_server(routes) as base_url:
        scanner = DirectoryScanner(base_url)
        results = scanner.scan()

    assert any(result["path"].endswith("/admin") and result["status"] == 200 for result in results)
