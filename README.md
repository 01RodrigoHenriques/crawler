# Web Crawler

Crawler em Python para reconhecimento web com port scanning, enumeração de subdomínios, descoberta de links, brute-force de diretórios e geração de relatórios.

O projeto está preparado para manutenção de equipa: packaging moderno, CI, linting, type checking, testes unitários e integração local.

## O que faz


- Port scanning das portas comuns configuradas em `config.py`
- Enumeração de subdomínios com validação DNS e verificação HTTP
- Crawl de links do mesmo domínio com suporte a `robots.txt` e `sitemap.xml`
- Brute-force de diretórios com fingerprinting para reduzir falsos positivos
- Detecção básica de tecnologias e WAF
- Relatórios em JSON, XML e HTML


## Requisitos

- Python 3.10+
- Instalação via `pyproject.toml`

Instalação detalhada: [INSTALLATION.md](INSTALLATION.md)

## Quick Start

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m main https://exemplo.com
```

Também podes usar o entry point instalado:

```bash
crawler https://exemplo.com
```

## Uso

```bash
python -m main https://exemplo.com
python -m main https://exemplo.com --threads 20 --timeout 10
python -m main https://exemplo.com --skip-subdomain --skip-crawl
python -m main https://exemplo.com --output results_custom/
python -m main https://self-signed.local --no-ssl-verify
python -m main --help
```

## Opções principais

- `url`: alvo a analisar
- `--threads`: número de workers
- `--timeout`: timeout por request
- `--rate-limit`: limite de requests por segundo
- `--skip-subdomain`: salta enumeração de subdomínios
- `--skip-crawl`: salta crawling de links
- `--output`: muda o diretório de output
- `--no-ssl-verify`: desativa verificação SSL para certificados inválidos ou self-signed

## Output

Os ficheiros são gravados em `results/` por defeito:

- `report.json`
- `report.xml`
- `report.html`
- `crawler.log`

## Estrutura do projeto

```text
crawler/
|-- main.py
|-- config.py
|-- logger_config.py
|-- session.py
|-- crawler.py
|-- scanner.py
|-- subdomain_enum.py
|-- tech_detector.py
|-- reporter.py
|-- tests/
|   |-- unit/
|   `-- integration/
|-- wordlists/
|-- pyproject.toml
|-- CONTRIBUTING.md
|-- ARCHITECTURE.md
|-- INSTALLATION.md
|-- TROUBLESHOOTING.md
`-- results/
```

## Estado atual

- CLI empacotada com entry point `crawler`
- Sessão HTTP partilhada com retry e rate limiting
- HTML report com escape de conteúdo antes de renderizar
- Fingerprinting e banner grabbing corrigidos
- Testes unitários e de integração local
- CI a validar lint, formatação e type checking

## Testes

```bash
pytest -q
python -m ruff format --check .
python -m ruff check .
python -m mypy .
```

## Segurança

Usa este projeto apenas em ambientes teus ou com autorização explícita. Não uses o crawler para reconhecimento ativo em alvos públicos sem permissão.

## Documentação complementar

- Instalação: [INSTALLATION.md](INSTALLATION.md)
- Troubleshooting: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Arquitetura: [ARCHITECTURE.md](ARCHITECTURE.md)
- Contribuição: [CONTRIBUTING.md](CONTRIBUTING.md)

## Qualidade

- Lint: `ruff check .`
- Formatação: `ruff format .`
- Type checking: `mypy .`
- Testes: `pytest -q`

## Garantia de execução limpa

```bash
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m main --help
python -m ruff check .
python -m mypy .
pytest -q --cov=. --cov-report=term-missing --cov-fail-under=50
```
