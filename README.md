# Web Crawler 

Crawler em Python para reconhecimento web com port scanning, enumeração de subdomínios, descoberta de links, brute-force de diretórios e geração de relatórios.

## O que faz

- Port scanning das portas comuns configuradas em `config.py`
- Enumeração de subdomínios com validação DNS e verificação HTTP
- Crawl de links do mesmo domínio com suporte a `robots.txt` e `sitemap.xml`
- Brute-force de diretórios com fingerprinting para reduzir falsos positivos
- Detecção básica de tecnologias e WAF
- Relatórios em JSON, XML e HTML

## Requisitos

- Python 3.8+
- Dependências em `requirements.txt`

Instalação detalhada: [INSTALLATION.md](INSTALLATION.md)

## Quick Start

```bash
pip install -r requirements.txt
python main.py https://exemplo.com
```

## Uso

```bash
python main.py https://exemplo.com
python main.py https://exemplo.com --threads 20 --timeout 10
python main.py https://exemplo.com --skip-subdomain --skip-crawl
python main.py https://exemplo.com --output results_custom/
python main.py https://self-signed.local --no-ssl-verify
python main.py --help
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
|-- test_crawler.py
|-- wordlists/
|-- INSTALLATION.md
|-- TROUBLESHOOTING.md
`-- results/
```

## Estado atual

- CLI alinhado com o comportamento real de SSL e output
- Sessão HTTP com controlo de concorrência melhorado
- HTML report com escape de conteúdo antes de renderizar
- Fingerprinting e banner grabbing corrigidos
- Testes locais atualizados

## Testes

```bash
python -m unittest -v
```

## Segurança

Usa este projeto apenas em ambientes teus ou com autorização explícita. Não uses o crawler para reconhecimento ativo em alvos públicos sem permissão.

## Documentação complementar

- Instalação: [INSTALLATION.md](INSTALLATION.md)
- Troubleshooting: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
