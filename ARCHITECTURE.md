# Architecture

This project is a flat Python application with a single CLI entry point and a set of focused modules.

## Runtime flow

1. `main.py` parses CLI arguments, applies runtime configuration, and coordinates the scan.
2. `session.py` builds the shared HTTP session with retry, rate limiting, proxy, and WAF detection.
3. `scanner.py`, `crawler.py`, `subdomain_enum.py`, and `tech_detector.py` gather data from the target.
4. `reporter.py` normalizes results and writes JSON, XML, and HTML reports.
5. `logger_config.py` configures console and file logging.

## Module responsibilities

- `config.py`: centralized defaults, paths, and shared constants.
- `main.py`: CLI orchestration only; it should not contain scan logic.
- `session.py`: reusable HTTP session and request policy.
- `crawler.py`: crawl same-domain links while respecting robots and sitemap hints.
- `scanner.py`: port scanning and directory discovery.
- `subdomain_enum.py`: subdomain enumeration and validation.
- `tech_detector.py`: technology fingerprinting.
- `reporter.py`: output rendering and escaping.

## Design choices

- A shared session reduces connection overhead and keeps request behavior consistent.
- Configuration is centralized so runtime flags can adjust behavior without editing code.
- Results are emitted in structured formats to support automation and manual review.
- The repository stays intentionally flat to keep the command-line entry point simple.

## Operational notes

- `results/` is treated as generated output and is not tracked by Git.
- Wordlists are resolved from the source tree during development and from installed data when packaged.
- CI runs linting, formatting checks, type checking, and tests on every push and pull request.
