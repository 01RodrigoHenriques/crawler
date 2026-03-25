"""
Configurações para o Web Crawler de Reconhecimento
"""

# Alvo principal
TARGET = "https://bolinatec.com"

# Configurações gerais
TIMEOUT = 5
THREADS = 20
OUTPUT_FILE = "resultado_scan.json"

# Dicionário de diretórios comuns
COMMON_DIRS = [
    "admin", "login", "dashboard", "api", "backup", "config",
    "uploads", "images", "files", "test", "dev", "staging",
    "wp-admin", "wp-content", "phpmyadmin", "robots.txt",
    ".git", ".env", "server-status", "readme.txt", "cgi-bin", "bank", "bank/login", "bank/queryxpath.aspx",
    "search.aspx", "signin.aspx", "logout.aspx"
]

# Portas comuns
COMMON_PORTS = [21, 22, 23, 25, 53, 80, 443, 3306, 3389, 5432, 6379, 8080, 8443, 8888]