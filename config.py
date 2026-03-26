"""
Configuração centralizada do crawler
"""
from dataclasses import dataclass
from typing import List
from pathlib import Path

# ─────────────────────────────────────────────
# PATHS
# ─────────────────────────────────────────────
PROJECT_DIR = Path(__file__).parent
WORDLIST_DIR = PROJECT_DIR / "wordlists"
WORDLIST_DIRS = WORDLIST_DIR / "directories.txt"
WORDLIST_SUBDOMAINS = WORDLIST_DIR / "subdomains.txt"
OUTPUT_DIR = PROJECT_DIR / "results"
OUTPUT_JSON = OUTPUT_DIR / "report.json"
OUTPUT_XML = OUTPUT_DIR / "report.xml"
OUTPUT_HTML = OUTPUT_DIR / "report.html"


def set_output_dir(path_like: Path | str) -> None:
    """Atualiza diretório e arquivos de output em runtime."""
    global OUTPUT_DIR, OUTPUT_JSON, OUTPUT_XML, OUTPUT_HTML, LOG_FILE

    output_dir = Path(path_like).expanduser()
    if not output_dir.is_absolute():
        output_dir = (PROJECT_DIR / output_dir).resolve()

    output_dir.mkdir(parents=True, exist_ok=True)

    OUTPUT_DIR = output_dir
    OUTPUT_JSON = OUTPUT_DIR / "report.json"
    OUTPUT_XML = OUTPUT_DIR / "report.xml"
    OUTPUT_HTML = OUTPUT_DIR / "report.html"
    LOG_FILE = OUTPUT_DIR / "crawler.log"


LOG_FILE = OUTPUT_DIR / "crawler.log"

OUTPUT_DIR.mkdir(exist_ok=True)
WORDLIST_DIR.mkdir(exist_ok=True)

# ─────────────────────────────────────────────
# TARGET
# ─────────────────────────────────────────────
TARGET = "https://exemple.com"

# ─────────────────────────────────────────────
# TIMEOUT & RETRY
# ─────────────────────────────────────────────
TIMEOUT = 8
MAX_RETRIES = 3
BACKOFF_FACTOR = 1.5  # exponential: 1s, 1.5s, 2.25s
RETRY_STATUS_CODES = {408, 429, 500, 502, 503, 504}  # Retry on these
SSL_VERIFY = True

# ─────────────────────────────────────────────
# RATE LIMITING
# ─────────────────────────────────────────────
RATE_LIMIT = 50  # requests per second (adaptive)
MIN_DELAY = 0.1  # minimum delay between requests
MAX_DELAY = 5.0  # maximum delay (on 429 Too Many Requests)

# ─────────────────────────────────────────────
# THREADING
# ─────────────────────────────────────────────
MAX_WORKERS = 10  # threads
MAX_WORKERS_PORT_SCAN = 20

# ─────────────────────────────────────────────
# SCANNING
# ─────────────────────────────────────────────
COMMON_PORTS = [
    21, 22, 23, 25, 53, 80, 110, 143, 443,
    465, 587, 993, 995, 3306, 3389, 5432, 5984,
    6379, 8000, 8008, 8080, 8443, 8888, 9200, 27017
]

# Extensions to test for directories
DIR_EXTENSIONS = ["", ".php", ".asp", ".aspx", ".html", ".xml", ".json", ".jsp", ".do"]

# ─────────────────────────────────────────────
# SUBDOMAIN ENUMERATION
# ─────────────────────────────────────────────
DNS_TIMEOUT = 5
DNS_NAMESERVERS = ["8.8.8.8", "8.8.4.4", "1.1.1.1"]  # Google, Cloudflare

# ─────────────────────────────────────────────
# CRAWLING
# ─────────────────────────────────────────────
MAX_CRAWL_DEPTH = 3
MAX_PAGES_PER_SCAN = 500
ROBOTS_TXT_CHECK = True
SITEMAP_CHECK = True

# ─────────────────────────────────────────────
# AUTHENTICATION (optional)
# ─────────────────────────────────────────────
@dataclass
class AuthConfig:
    """Configuração de autenticação (Basic Auth, Bearer Token, etc)"""
    enabled: bool = False
    auth_type: str = "basic"  # 'basic', 'bearer', 'api_key'
    username: str = ""
    password: str = ""
    token: str = ""
    headers: dict = None

    def __post_init__(self):
        if self.headers is None:
            self.headers = {}

AUTH_CONFIG = AuthConfig(enabled=False)

# ─────────────────────────────────────────────
# PROXY CONFIGURATION
# ─────────────────────────────────────────────
PROXY_ENABLED = False
PROXIES = {
    # "http": "http://proxy.example.com:8080",
    # "https": "http://proxy.example.com:8080",
}

# ─────────────────────────────────────────────
# USER AGENTS (rotação automática)
# ─────────────────────────────────────────────
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
]

# ─────────────────────────────────────────────
# WAF DETECTION
# ─────────────────────────────────────────────
WAF_SIGNATURES = {
    "CloudFlare": ["cf-ray", "cloudflare"],
    "AWS WAF": ["x-amzn-waf", "x-amzn-requestid"],
    "ModSecurity": ["mod-security", "modsecurity"],
    "Imperva": ["x-iinfo", "x-originating-ip"],
    "Akamai": ["akamai-origin", "x-akamai"],
    "Fortinet": ["fortigate", "x-fortiweb"],
}

# ─────────────────────────────────────────────
# TECHNOLOGY DETECTION SIGNATURES
# ─────────────────────────────────────────────
TECH_SIGNATURES = {
    "WordPress": {
        "html": ["wp-content", "wp-includes", "wp-emoji"],
        "headers": ["x-wp-super-cache"],
        "files": ["/wp-admin/", "/wp-login.php"]
    },
    "Joomla": {
        "html": ["joomla", "/components/com_", "com_content"],
        "files": ["/administrator/", "/templates/"]
    },
    "Drupal": {
        "html": ["drupal", "/sites/default/", "drupal.js"],
        "files": ["/sites/", "/modules/"]
    },
    "Django": {
        "headers": ["server:"],  # Django often reveals itself in headers
        "html": ["django", "csrfmiddlewaretoken"]
    },
    "Flask": {
        "headers": ["werkzeug"],
        "html": ["flask"]
    },
    "Laravel": {
        "html": ["laravel", "laravel_session"],
        "files": ["/artisan"]
    },
    "Angular": {
        "html": ["angular.js", "ng-", "__angular"],
    },
    "React": {
        "html": ["react", "__react", "_react"],
    },
    "Vue": {
        "html": ["vue.js", "__vue__", "v-app"],
    },
    "jQuery": {
        "html": ["jquery"],
    },
    "Bootstrap": {
        "html": ["bootstrap"],
    },
    "PHP": {
        "html": ["<?php", "phpversion"],
        "files": [".php"],
        "headers": ["x-powered-by"]
    },
    "ASP.NET": {
        "html": ["__viewstate", "__eventtarget"],
        "headers": ["x-aspnet-version", "x-powered-by"]
    },
    "Node.js": {
        "headers": ["express", "hapi"],
        "html": ["node.js"]
    },
}

# ─────────────────────────────────────────────
# LOGGING
# ─────────────────────────────────────────────
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = OUTPUT_DIR / "crawler.log"

# ─────────────────────────────────────────────
# OUTPUT FORMATS
# ─────────────────────────────────────────────
OUTPUT_JSON = OUTPUT_DIR / "report.json"
OUTPUT_XML = OUTPUT_DIR / "report.xml"
OUTPUT_HTML = OUTPUT_DIR / "report.html"
