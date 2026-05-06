#!/usr/bin/env python3
"""
Web Crawler - Reconhecimento e Scanning
Uso: python main.py [url] [--threads N] [--timeout T] [--no-ssl-verify]
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

import urllib3

import config
from crawler import LinkCrawler
from logger_config import logger, setup_logger
from reporter import ReportGenerator
from scanner import DirectoryScanner, PortScanner
from session import get_session
from subdomain_enum import SubdomainEnumerator
from tech_detector import TechnologyDetector


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Web Crawler para Reconhecimento",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  python main.py https://exemplo.com
  python main.py https://exemplo.com --threads 20 --timeout 10
  python main.py https://exemplo.com --no-ssl-verify --output results/
        """,
    )

    parser.add_argument("url", nargs="?", default=config.TARGET, help=f"URL alvo (default: {config.TARGET})")
    parser.add_argument(
        "--threads",
        type=int,
        default=config.MAX_WORKERS,
        help=f"Numero de workers (default: {config.MAX_WORKERS})",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=config.TIMEOUT,
        help=f"Timeout em segundos (default: {config.TIMEOUT})",
    )
    parser.add_argument(
        "--rate-limit",
        type=int,
        default=config.RATE_LIMIT,
        help=f"Requests/seg (default: {config.RATE_LIMIT})",
    )
    parser.add_argument("--no-ssl-verify", action="store_true", help="Desabilitar verificacao SSL")
    parser.add_argument("--skip-subdomain", action="store_true", help="Saltar enumeracao de subdominios")
    parser.add_argument("--skip-crawl", action="store_true", help="Saltar crawling de links")
    parser.add_argument("--output", type=str, default=str(config.OUTPUT_DIR), help="Diretorio de output")

    return parser.parse_args()


def print_banner():
    """Mostra banner inicial."""
    banner = """
+------------------------------------------------------------+
|                         WEB CRAWLER                        |
|                    Reconhecimento & Scanning               |
|                                                            |
|        AVISO: Use apenas em ambientes autorizados!         |
|              Uso nao autorizado e ilegal!                  |
+------------------------------------------------------------+
    """
    print(banner)


def validate_url(url: str) -> bool:
    """Valida URL."""
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ["http", "https"]:
            logger.error(f"Scheme invalido: {parsed.scheme}. Use http:// ou https://")
            return False
        if not parsed.netloc:
            logger.error(f"URL invalida: {url}")
            return False
        return True
    except Exception as e:
        logger.error(f"Erro ao validar URL: {e}")
        return False


def main():
    """Funcao principal."""
    args = parse_arguments()
    print_banner()

    if not validate_url(args.url):
        sys.exit(1)

    config.MAX_WORKERS = args.threads
    config.TIMEOUT = args.timeout
    config.RATE_LIMIT = args.rate_limit
    config.SSL_VERIFY = not args.no_ssl_verify
    config.set_output_dir(Path(args.output))
    setup_logger("crawler", config.LOG_FILE)

    if not config.SSL_VERIFY:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    logger.info("=" * 60)
    logger.info(f"Alvo: {args.url}")
    logger.info(f"Config: {args.threads} workers, {args.timeout}s timeout, {args.rate_limit} req/s")
    logger.info(f"Hora: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("=" * 60)

    results = {
        "target": args.url,
        "timestamp": datetime.now().isoformat(),
        "open_ports": [],
        "directories": [],
        "links": [],
        "technologies": [],
        "subdomains": [],
        "waf_detected": None,
        "summary": {},
    }

    try:
        logger.info("\nFASE 1: Port Scanning")
        logger.info("-" * 60)
        host = urlparse(args.url).netloc.split(":")[0]
        port_scanner = PortScanner(host)
        results["open_ports"] = port_scanner.scan()

        if not args.skip_subdomain:
            logger.info("\nFASE 2: Enumeracao de Subdominios")
            logger.info("-" * 60)
            subdomain_enumerator = SubdomainEnumerator(host)
            results["subdomains"] = subdomain_enumerator.enumerate()

        if not args.skip_crawl:
            logger.info("\nFASE 3: Web Crawling")
            logger.info("-" * 60)
            link_crawler = LinkCrawler(args.url)
            results["links"] = list(link_crawler.crawl())

        logger.info("\nFASE 4: Directory Brute-Force")
        logger.info("-" * 60)
        dir_scanner = DirectoryScanner(args.url)
        results["directories"] = dir_scanner.scan()

        logger.info("\nFASE 5: Deteccao de Tecnologias")
        logger.info("-" * 60)
        tech_detector = TechnologyDetector(args.url)
        results["technologies"] = tech_detector.detect()

        session = get_session()
        if session.detected_waf:
            results["waf_detected"] = session.detected_waf

        results["summary"] = {
            "open_ports": len(results["open_ports"]),
            "subdomains_active": len(results["subdomains"]),
            "directories_found": len(results["directories"]),
            "technologies_detected": len(results["technologies"]),
            "links_crawled": len(results["links"]),
        }

        logger.info("\nFASE 6: Gerando Relatorios")
        logger.info("-" * 60)
        report_generator = ReportGenerator(results)

        json_file = report_generator.to_json()
        xml_file = report_generator.to_xml()
        html_file = report_generator.to_html()

        logger.info("\n" + "=" * 60)
        logger.info("SCAN COMPLETO")
        logger.info("=" * 60)
        logger.info("Resultados:")
        logger.info(f"   - Portas abertas: {results['summary']['open_ports']}")
        logger.info(f"   - Subdominios ativos: {results['summary']['subdomains_active']}")
        logger.info(f"   - Diretorios encontrados: {results['summary']['directories_found']}")
        logger.info(f"   - Tecnologias detectadas: {results['summary']['technologies_detected']}")
        logger.info(f"   - Links crawled: {results['summary']['links_crawled']}")
        if results.get("waf_detected"):
            logger.info(f"WAF detectado: {results['waf_detected']}")
        logger.info("\nRelatorios salvos em:")
        if json_file:
            logger.info(f"   - JSON: {json_file}")
        if xml_file:
            logger.info(f"   - XML: {xml_file}")
        if html_file:
            logger.info(f"   - HTML: {html_file}")
        logger.info("=" * 60)

    except KeyboardInterrupt:
        logger.warning("\nScan interrompido pelo utilizador")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Erro critico: {e}", exc_info=True)
        sys.exit(1)
    finally:
        session = get_session()
        if session:
            session.close()


if __name__ == "__main__":
    main()
