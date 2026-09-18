# Guia de Entrevista — File Integrity Guard

## 1. O que o projeto faz

Cria uma linha de base de hashes SHA-256 de arquivos/diretórios autorizados e depois compara o estado atual contra essa linha de base, reportando arquivos adicionados, modificados, excluídos e inalterados — o conceito de FIM (File Integrity Monitoring) usado em SOC e auditorias de compliance.

## 2. Por que foi criado

Para demonstrar segurança defensiva de forma prática e legal: nenhum ataque a terceiros, apenas detecção de alteração em arquivos que o próprio operador escolheu monitorar.

## 3. Arquitetura

`scanner` varre os caminhos configurados → `hashing` calcula SHA-256 e metadados → `store` (SQLite) persiste a linha de base → `compare` confronta a varredura atual com a linha de base salva → `reporting` gera relatórios em JSON e Markdown → `cli` expõe os comandos `init`, `check` e `report`.

## 4. Tecnologias principais

Python 3.10+, `hashlib` (SHA-256), SQLite (armazenamento local da linha de base), YAML (configuração), pytest.

## 5. Decisões técnicas

- SQLite em vez de um arquivo JSON de baseline: permite consultas e evita reescrever o arquivo inteiro a cada verificação.
- Hash SHA-256 em vez de MD5/SHA-1: resistente a colisões, padrão atual para integridade.
- Globs de include/exclude configuráveis: evita falso positivo em diretórios ruidosos (`.git`, `__pycache__`, `node_modules`).

## 6. Banco de dados

Não há SGBD servidor — SQLite local guarda `path`, `hash`, `size`, `mtime` e `status` de cada arquivo monitorado. Ver `src/store.py` e `src/models.py`.

## 7. Segurança

Ferramenta puramente defensiva e local: só lê caminhos explicitamente autorizados pelo operador, nunca acessa rede ou sistemas de terceiros, e a linha de base fica no disco do próprio host — nunca é enviada para fora.

## 8. Problema mais difícil

Evitar falsos positivos causados por arquivos temporários/gerados (cache, logs, `.venv`) sem exigir que o usuário liste manualmente cada exceção.

## 9. Como foi resolvido

Padrões de `exclude` no YAML de configuração cobrindo os diretórios ruidosos mais comuns, testados com fixtures que criam e removem arquivos temporários (`tests/test_scanner.py`, `tests/test_compare.py`).

## 10–11. 20 perguntas e respostas sugeridas

### 1. Como o File Integrity Guard detecta alterações em arquivos?

Compara o hash SHA-256 atual de cada arquivo com o hash gravado na linha de base; qualquer diferença de conteúdo muda o hash.

### 2. Qual algoritmo de hash é usado e por que?

SHA-256: rápido o suficiente para arquivos locais e sem colisões conhecidas, ao contrário de MD5/SHA-1.

### 3. Como o sistema lida com arquivos grandes?

Lê em blocos (`hashlib` com `update()` incremental) em vez de carregar o arquivo inteiro na memória de uma vez.

### 4. Qual é a diferença entre uma linha de base e um relatório?

A linha de base é o estado "confiável" salvo no SQLite; o relatório é o resultado de comparar o estado atual contra essa linha de base.

### 5. Como o sistema trata arquivos excluídos (removidos do disco)?

Um caminho que está na linha de base mas não aparece na varredura atual é marcado como `excluído` no relatório.

### 6. Qual é o propósito do arquivo de configuração?

Definir quais caminhos monitorar e quais padrões incluir/excluir, sem precisar alterar código para mudar o alvo do monitoramento.

### 7. Como o sistema lida com symlinks?

Não segue links simbólicos por padrão (evita loops e monitorar conteúdo fora do escopo autorizado); comportamento documentado no roadmap como configurável.

### 8. Qual é a diferença entre os relatórios JSON e Markdown?

JSON é para consumo por outras ferramentas/scripts; Markdown é para leitura humana e pode ser colado direto em um ticket ou PR.

### 9. Como o sistema lida com erros de leitura de arquivo (permissão negada, arquivo apagado no meio da varredura)?

Captura a exceção por arquivo, registra em log e continua a varredura dos demais — um arquivo problemático não derruba a execução inteira.

### 10. Qual é o propósito do `.gitignore` no projeto?

Evitar versionar artefatos locais (`__pycache__`, bancos SQLite gerados, ambientes virtuais) que não fazem parte do código-fonte.

### 11. O File Integrity Guard pode ser usado para monitorar sistemas remotos?

Não hoje — é local por design; monitorar um host remoto exigiria um agente rodando lá e um canal seguro para transmitir os hashes, o que fica no roadmap.

### 12. Como o sistema protege contra vazamento de dados?

Ele não transmite nada: hashes e metadados ficam apenas no SQLite local, sem rede envolvida.

### 13. O sistema usa alguma forma de criptografia?

Não além do próprio SHA-256 (que é hashing, não criptografia). Não há necessidade de cifrar a linha de base, pois ela não guarda conteúdo, só hashes.

### 14. Como o sistema lida com arquivos que contêm dados sensíveis?

Ele nunca lê o conteúdo além do necessário para calcular o hash, e o relatório traz apenas caminho/hash/status — nunca o conteúdo do arquivo.

### 15. O sistema usa alguma forma de autenticação?

Não é necessário: é uma ferramenta de linha de comando que roda com as permissões do próprio usuário do sistema operacional.

### 16. Como um usuário inicializa a linha de base?

`python -m src.cli init`, depois de configurar `config/config.yaml` com os caminhos desejados.

### 17. Como um usuário executa uma verificação?

`python -m src.cli check`, que compara o estado atual com a linha de base e imprime um resumo.

### 18. Como um usuário gera um relatório?

`python -m src.cli report`, que roda a verificação e grava os arquivos em `reports/` (JSON e Markdown).

### 19. Como um usuário configura o sistema para monitorar novos diretórios?

Edita `paths` em `config/config.yaml` e roda `init` novamente para recriar a linha de base incluindo o novo caminho.

### 20. Como um usuário lida com falsos positivos (por exemplo, um log que muda o tempo todo)?

Adiciona o caminho/padrão à lista `exclude` da configuração e recria a linha de base.

## 12. Alterações de live-coding que um entrevistador pode pedir

- Adicionar um modo `--follow-symlinks` opcional ao scanner.
- Fazer o `check` retornar código de saída diferente de zero quando houver alterações (para uso em CI).
- Adicionar um limite de tamanho de arquivo, pulando arquivos maiores que N MB.
- Gravar o histórico de todas as verificações (não só a linha de base atual) no SQLite.
- Adicionar suporte a notificação por webhook quando uma violação for detectada.
