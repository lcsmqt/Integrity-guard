# Como contribuir

Obrigado pelo interesse em melhorar o **File Integrity Guard**. Este projeto é um laboratório defensivo de cibersegurança: monitore apenas arquivos locais autorizados.

## Princípios

- Código e identificadores em inglês; documentação em português.
- Sem APIs pagas, sem segredos e sem ataques a sistemas de terceiros.
- Mudanças pequenas e testáveis. Prefira um PR focado a um PR gigante.
- Não envie arquivos `.env`, bancos SQLite reais nem relatórios com dados pessoais.

## Ambiente local

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy config\config.example.yaml config\config.yaml
```

## Verificações antes do PR

```bash
ruff check src tests
pytest
```

## Padrões de código

- Type hints em funções públicas.
- `argparse` para a CLI; `logging` para mensagens operacionais.
- Testes com `tmp_path`; não dependa de caminhos da máquina do autor.
- Não adicione dependências pagas ou que exijam chave de API.

## Relato de issues

Inclua: sistema operacional, versão do Python, comando executado, trecho de log e se o caminho monitorado é local.

## Licença

Ao contribuir, você concorda em licenciar o trabalho sob a licença MIT deste repositório.
