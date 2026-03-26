# Guia de Troubleshooting

## Problemas Comuns e Soluções

### 1. "ModuleNotFoundError: No module named 'requests'"

**Causa**: Dependências não instaladas

**Solução**:
```bash
# Verificar se está no ambiente correto
python --version

# Instalar dependências
pip install -r requirements.txt

# Ou específica
pip install requests beautifulsoup4 urllib3
```

### 2. "ConnectionError: ('Connection aborted.')"

**Causa**: Firewall, bloqueio de acesso, ou alvo offline

**Solução**:
```bash
# 1. Testar conectividade
ping exemplo.com

# 2. Testar com curl
curl -v https://exemplo.com

# 3. Aumentar timeout
python main.py https://exemplo.com --timeout 15

# 4. Usar proxy
# Editar config.py:
PROXY_ENABLED = True
PROXIES = {"http": "...", "https": "..."}
```

### 3. "Too many open files" ou "Resource temporarily unavailable"

**Causa**: Limite de file descriptors do sistema superado

**Solução**:
```bash
# Linux/Mac: Aumentar limite
ulimit -n 10000

# Ou em Python - reduzir threads
python main.py https://exemplo.com --threads 5
```

Em `config.py`:
```python
MAX_WORKERS = 5         # Em vez de 10
MAX_WORKERS_PORT_SCAN = 10  # Em vez de 20
```

### 4. "429 Too Many Requests - Rate Limited"

**Causa**: Alvo bloqueou por muitas requisições

**Solução**:
```bash
# Reduzir rate limit
python main.py https://exemplo.com --rate-limit 5

# Aumentar delay
# config.py:
MIN_DELAY = 0.5  # Em vez de 0.1
MAX_DELAY = 10.0  # Em vez de 5.0
```

### 5. "SSL: CERTIFICATE_VERIFY_FAILED"

**Causa**: Certificado SSL inválido ou auto-assinado

**Solução**:
```bash
# Desabilitar verificação SSL (use com cuidado!)
python main.py https://self-signed.com --no-ssl-verify

# Ou manter padrão (já é default)
```

### 6. "requests.exceptions.Timeout"

**Causa**: Servidor lento ou não responde

**Solução**:
```bash
# Aumentar timeout
python main.py https://exemplo.com --timeout 15

# Reduzir threads (menos requisições simultâneas)
python main.py https://exemplo.com --threads 5
```

### 7. Detectado WAF - "WAF Detectado: CloudFlare"

**Observação**: Não é um erro, mas aviso importante

**O que fazer**:
- Reduzir rate limit significativamente
- Usar proxies rotativos
- Aumentar delays entre requisições
- Considerar usar-se de outras técnicas de reconhecimento

```python
# config.py
RATE_LIMIT = 5
MIN_DELAY = 1.0
```

### 8. Nenhum resultado (0 portas, 0 diretórios, etc.)

**Causa Possível**: 
- Alvo não acessível
- Wordlist vazia
- Timeout muito baixo

**Solução**:
```bash
# Testar conectividade primeira
curl -v https://exemplo.com

# Verificar logs
tail -f results/crawler.log

# Aumentar timeout
python main.py https://exemplo.com --timeout 20

# Verificar se wordlists existem
ls -la wordlists/
```

### 9. "UnicodeDecodeError" em HTML parsing

**Causa**: Conteúdo HTML com encoding não-UTF8

**Solução**: 
Já está tratado automaticamente no código (errors='ignore'), mas se persistir:

```python
# Em crawler.py, adicionar:
response.encoding = 'utf-8'
soup = BeautifulSoup(response.text, "html.parser")
```

### 10. Pouca Performance / Muito Lento

**Causa**: Config subótima

**Solução - Modo Agressivo**:
```bash
python main.py https://exemplo.com --threads 50 --rate-limit 200

# config.py:
MAX_WORKERS = 50
MAX_WORKERS_PORT_SCAN = 50
RATE_LIMIT = 200
```

**Solução - Modo Balanceado**:
```bash
python main.py https://exemplo.com --threads 15 --rate-limit 30

# config.py:
MAX_WORKERS = 15
MAX_WORKERS_PORT_SCAN = 15
RATE_LIMIT = 30
```

### 11. Relatórios não gerados

**Causa**: Permissões de escrita

**Solução**:
```bash
# Verificar permissões
ls -la results/

# Criar diretório se não existir
mkdir -p results/

# Dar permissões
chmod 755 results/
```

### 12. "ConnectionRefusedError: [Errno 111] Connection refused"

**Causa**: Porta específica não está aberta/escutando

**Solução**:
```bash
# Só afeta port scanning. Verificar alvo:
nmap -p 80,443 exemplo.com

# Ou usar netstat
netstat -an | grep exemplo.com
```

---

## Debug Avançado

### Ativar Logging Detalhado

Em `config.py`:
```python
LOG_LEVEL = "DEBUG"  # Em vez de "INFO"
```

Então:
```bash
python main.py https://exemplo.com 2>&1 | tee debug.log
```

### Testar Componentes Individuais

```python
# Testar Session
from session import get_session
session = get_session()
resp = session.get("https://exemplo.com")
print(resp.status_code)

# Testar Port Scanner
from scanner import PortScanner
scanner = PortScanner("exemplo.com")
ports = scanner.scan()
print(ports)

# Testar Subdomain Enum
from subdomain_enum import SubdomainEnumerator
enum = SubdomainEnumerator("exemplo.com")
subs = enum.enumerate()
print(subs)
```

### Monitorar Requisições HTTP

```bash
# Linux/Mac: tcpdump
sudo tcpdump -i any -A 'tcp port 80 or tcp port 443'

# Ou Wireshark GUI
wireshark
```

### Profile de Performance

```python
# test_profile.py
import cProfile
import pstats
from main import main

profiler = cProfile.Profile()
profiler.enable()

main()

profiler.disable()
stats = pstats.Stats(profiler)
stats.sort_stats('cumulative')
stats.print_stats(20)  # Top 20 funções
```

---

## Checklist de Diagnóstico

- [ ] Python 3.8+ instalado? `python --version`
- [ ] Dependências instaladas? `pip list | grep -E 'requests|beautifulsoup'`
- [ ] URL válida? `curl https://your-url.com`
- [ ] Conectividade? `ping your-domain.com`
- [ ] Permissões de escrita? `touch results/test.txt`
- [ ] Wordlists existem? `ls wordlists/`
- [ ] Configuração padrão OK? `python main.py --help`
- [ ] Sem firewalls bloqueando? `netstat -an | grep :443`

---

## Contato & Suporte

Se o problema persiste:
1. Verificar logs em `results/crawler.log`
2. Aumentar verbosidade com `--debug`
3. Testar com URL simples primeiro (ex: httpbin.org)
4. Consultar a documentação em README.md
