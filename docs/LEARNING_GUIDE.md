# Guia de Aprendizado para File Integrity Guard

## Introdução

Este guia ajuda iniciantes a entender o File Integrity Guard, um monitor defensivo de integridade de arquivos.

## Conceitos Básicos

1. **Integridade de Arquivos**: Garantir que arquivos não foram alterados, adicionados ou excluídos sem autorização.
2. **Linha de Base**: Conjunto de hashes SHA-256 de arquivos autorizados.
3. **Relatório**: Lista de arquivos adicionados, modificados, excluídos ou inalterados.

## Como Funciona

1. **Inicialização**: Crie uma linha de base de arquivos locais autorizados.
2. **Verificação**: Compare o estado atual dos arquivos com a linha de base.
3. **Relatório**: Gere um relatório das alterações detectadas.

## Passo a Passo

1. **Instale o Python 3.10+**
2. **Clone o repositório**
3. **Instale as dependências**: `pip install -r requirements.txt`
4. **Configure o sistema**: Copie `config.example.yaml` para `config/config.yaml`
5. **Inicialize a linha de base**: `python -m src.cli init`
6. **Execute uma verificação**: `python -m src.cli check`
7. **Gere um relatório**: `python -m src.cli report`

## Recursos Adicionais

- **Documentação**: `docs/ARCHITECTURE.md`
- **Testes**: Execute `pytest` para verificar o funcionamento do sistema
- **Contribuição**: Leia `CONTRIBUTING.md` para saber como contribuir
