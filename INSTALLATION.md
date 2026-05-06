# Guia de Instalação

## Pré-requisitos

### Windows
- Python 3.8+ (https://www.python.org/downloads/)
- Git (opcional, para clonar repositório)
- Administrative access (para desenvolver)

### Linux/Mac
- Python 3.8+
- pip (gestor de pacotes Python)
- gcc (para compilação de extensions, se necessário)

## Instalação Passo-a-Passo

### 1. Verificar Python Instalado

```bash
# Verificar versão
python --version
python3 --version  # Se python não funcionar

# Verificar pip
pip --version
pip3 --version
```

Se Python não está instalado:
- **Windows**: https://www.python.org/downloads/ (marcar "Add Python to PATH")
- **Linux**: `sudo apt-get install python3 python3-pip`
- **Mac**: `brew install python3`

### 2. Clonar/Baixar Projeto

```bash
# Opção A: Clonar com Git
git clone https://github.com/01RodrigoHenriques/crawler.git
cd crawler

# Opção B: Download direto
# 1. Descarregar ZIP
# 2. Descomprimir
# 3. cd crawler/
```

### 3. Criar Virtual Environment (Optional mas Recomendado)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 4. Instalar Dependências

```bash
# Instalar tudo de uma vez
pip install -r requirements.txt

# Ou instalar individually (debugging)
pip install requests
pip install beautifulsoup4
pip install urllib3
pip install dnspython
pip install tqdm
pip install lxml
```

### 5. Verificar Instalação

```bash
# Executar testes
python -m pytest test_crawler.py -v

# Ou testar imports manualmente
python -c "import requests, bs4, urllib3; print('Todos os imports OK')"
```

### 6. Criação de Wordlists (Automática)

O projeto vem com wordlists inclusos em `wordlists/`:
- `directories.txt` (100+ diretórios comuns)
- `subdomains.txt` (150+ subdomínios comuns)

Se quiser usar wordlists customizadas:
```bash
# Editar directamente
nano wordlists/directories.txt
vim wordlists/subdomains.txt
```

### 7. Primeiro Teste

```bash
# Ver ajuda
python main.py --help

# Teste simples (httpbin.org is safe for testing)
python main.py https://httpbin.org

# Ou seu alvo real
python main.py https://exemplo.com
```

---

## Instalação Avançada

### Usando Poetry (Alternativa a pip)

```bash
# Instalar Poetry
pip install poetry

# Instalar dependências com poetry
poetry install

# Ativar ambiente
poetry shell

# Executar
poetry run python main.py https://exemplo.com
```

### Criar Executável com PyInstaller

```bash
# Instalar PyInstaller
pip install pyinstaller

# Gerar executável
pyinstaller --onefile main.py

# Executável em dist/main.exe (Windows) ou dist/main (Linux/Mac)
./dist/main https://exemplo.com
```

### Docker (Avançado)

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . /app

RUN pip install -r requirements.txt

ENTRYPOINT ["python", "main.py"]
```

Build e run:
```bash
docker build -t web-crawler .
docker run web-crawler https://exemplo.com
```

---

## Configuração Pós-Instalação

### 1. Editar config.py

```python
# config.py
TARGET = "https://seu-alvo.com"
MAX_WORKERS = 10  # Ajustar conforme CPU/Rede
TIMEOUT = 8
RATE_LIMIT = 50
```

### 2. Setup de Autenticação (se necessário)

```python
# config.py
AUTH_CONFIG = AuthConfig(
    enabled=True,
    auth_type="bearer",
    token="seu_token_aqui"
)
```

### 3. Setup de Proxy (se necessário)

```python
# config.py
PROXY_ENABLED = True
PROXIES = {
    "http": "http://proxy.company.com:8080",
    "https": "http://proxy.company.com:8080"
}
```

### 4. Criar Diretório de Output

```bash
mkdir -p results
chmod 755 results
```

---

## Instalação para Diferentes OS

### Windows 10/11

```batch
REM 1. Instalar Python 3.11+ de https://www.python.org
REM 2. Abrir cmd ou PowerShell

cd \Users\user\Documents\crawler
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

REM Testar
python main.py https://exemplo.com
```

### Ubuntu/Debian

```bash
# Atualizar
sudo apt update
sudo apt upgrade

# Instalar Python & dev tools
sudo apt install python3 python3-pip python3-venv

# Clonar e setup
git clone https://github.com/01RodrigoHenriques/crawler.git
cd crawler
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Testar
python main.py https://exemplo.com
```

### macOS

```bash
# Instalar Homebrew se não tiver
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Instalar Python
brew install python3

# Setup
git clone https://seu-repo.git crawler
cd crawler
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Testar
python main.py https://exemplo.com
```

---

## Troubleshooting de Instalação

### "Python não está definido" (Windows)

```bash
# Verificar instalação
py --version

# Ou adicionar ao PATH manualmente
# Control Panel > System > Environment Variables > Path > Add C:\Python311\
```

### "pip: command not found"

```bash
# Reinstalar pip
python -m ensurepip --upgrade

# Ou
python3 -m ensurepip --upgrade
```

### "Permission denied" (Linux/Mac)

```bash
# Dar permissões
chmod +x main.py

# Ou executar com python explícito
python3 main.py https://exemplo.com
```

### Problemas com SSL em instalação

```bash
# Verificar certificados
python -m certifi

# Se não existirem, instalar/atualizar
pip install --upgrade certifi

# Ou desabilitar verificação (temporário)
export PYTHONHTTPSVERIFY=0
```

---

## Verificação Completa

Após instalação, executar este script:

```python
# verify_install.py
import sys
print(f"Python: {sys.version}")
print(f"Path: {sys.executable}\n")

modules = ["requests", "bs4", "urllib3", "lxml"]
print("Verificando módulos:")
for mod in modules:
    try:
        __import__(mod)
        print(f"  OK {mod}")
    except ImportError:
        print(f"  ERRO {mod} - INSTALAR: pip install {mod}")

# Testar imports do crawler
print("\nVerificando crawler:")
try:
    import config
    import logger_config
    import session
    import crawler
    import scanner
    import tech_detector
    print("  Todos os módulos do crawler OK")
except ImportError as e:
    print(f"  Erro: {e}")
```

Executar:
```bash
python verify_install.py
```

---

## Suporte

Se encontrar problemas:
1. Consultar [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. Verificar logs: `cat results/crawler.log`
3. Testar componente individual em Python interactive: `python -i -c "import crawler; ..."`
