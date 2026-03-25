# Web Crawler de Reconhecimento

Este projeto é um crawler de reconhecimento web desenvolvido para fins educacionais em segurança da informação. Ele realiza brute-force de diretórios, varredura de portas, detecção de tecnologias e extração de links.

## Funcionalidades

- **Extração de Links**: Crawling recursivo de páginas web.
- **Brute-Force de Diretórios**: Testa caminhos comuns em busca de diretórios acessíveis.
- **Varredura de Portas**: Escaneia portas TCP comuns no host alvo.
- **Detecção de Tecnologias**: Identifica CMS, frameworks e servidores via headers e HTML.
- **Saída JSON**: Resultados salvos em arquivo JSON estruturado.

## Avisos Importantes

- **Uso Ético**: Use apenas em ambientes próprios ou com permissão explícita. Scans não autorizados podem ser ilegais.
- **Rate Limiting**: Inclui delays para evitar sobrecarga no alvo.
- **Educação**: Desenvolvido para aprendizado em estagio; não para uso malicioso.

## Estrutura do Projeto

- `config.py`: Configurações e constantes.
- `crawler.py`: Módulo de extração de links.
- `scanner.py`: Módulo de scanning (portas e diretórios).
- `detector.py`: Módulo de detecção de tecnologias.
- `main.py`: Script principal para executar o crawler.
- `crawler_single.py`: Versão única do código em um arquivo.
- `requirements.txt`: Dependências Python.

## Instalação

1. Clone ou baixe o repositório.
2. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

## Uso

### Versão Modular
Execute o script principal:
```
python main.py
```

### Versão Única
```
python crawler_single.py
```

### Personalização
Edite `config.py` para alterar o alvo, timeouts, threads, etc.

## Saída

Os resultados são salvos em `resultado_scan.json` com a seguinte estrutura:
```json
{
  "target": "https://exemplo.com",
  "timestamp": "2026-03-25T10:00:00",
  "open_ports": [{"port": 80, "service": "http"}],
  "directories": [{"path": "https://exemplo.com/admin", "status": 200}],
  "links": ["https://exemplo.com/page1"],
  "technologies": [{"type": "header", "name": "server", "value": "nginx"}]
}
```

## Dependências

- requests
- beautifulsoup4
- urllib3
- pyinstaller (opcional, para criar .exe)

## Criando Executável (.exe)

Para transformar em executável standalone:
```
pip install pyinstaller
pyinstaller --onefile main.py
```
O arquivo `main.exe` será criado na pasta `dist/`.

## Autor

Desenvolvido por Rodrigo Henriques, para BolinaTEC em ambito de estagio.