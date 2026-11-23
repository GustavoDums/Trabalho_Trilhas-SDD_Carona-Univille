# T043 — Medição consolidada da entrega

**Requisitos** REQ-017, REQ-018 e REQ-019 · **Princípio** III · **Data** 2026-11-23.

As dependências T001–T040 estão concluídas. A execução mede as Features 001–011 entregues, incluindo notificações e fila de espera. [Roadmap](roadmap-implementacao.md) · [Levantamento](levantamento.md) · [Constitution](../.specify/memory/constitution.md).

## Execução

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-quality-metrics.ps1 -Consolidado
~~~

Usar o ambiente virtual com as dependências do projeto e PostgreSQL. A opção `-PythonPath` permite indicar outro ambiente Python com a mesma stack. O script da T012 executa todos os testes em `tests/`, mede `accounts`, `rides`, `reviews`, `notifications` e `carona_univille` e gera `coverage.json` e `test-results-t043.xml`. O relatório original da T012 foi preservado em [coverage-feature001-t012.json](../coverage-feature001-t012.json), junto ao [JUnit histórico](../test-results.xml).

O script exige 80% de linhas, ramificações e cobertura combinada na medição global e nos módulos de negócio. A verificação por módulo inclui o código executável dos quatro apps, além de `carona_univille/views.py`. Migrações e módulos de inicialização do projeto também entram no total global. O README recebe os percentuais do JSON e a contagem de casos aprovados no JUnit após a validação.

## Resultado

A medição consolidada incorpora a remoção de ofertas do painel e a janela de recorrência de 15 dias úteis. [Feature 005/T008 local](../specs/005-cancelamento-liberacao-vaga/evidence-t008.md) · [Feature 009/T008 local](../specs/009-caronas-recorrentes/evidence-t008.md).

| Verificação | Resultado |
| --- | --- |
| Suíte completa | 1005 aprovados, 0 falhas, 0 erros e 0 ignorados no PostgreSQL 16.15. |
| Cobertura combinada | **98.55564995751912%** |
| Linhas | **99.01041666666667%** (1901/1920) |
| Ramificações | **96.54377880184332%** (419/434) |
| Módulos críticos | 38 módulos atingiram a meta em linhas, ramificações e cobertura combinada. |
| Arquivos abaixo de 80% | `carona_univille/asgi.py` e `carona_univille/wsgi.py` ficaram com 0% de linhas e de cobertura combinada. Ambos entram no total global como inicializadores de implantação. |
| Validação da meta | Um relatório sintético confirmou a rejeição de ramificações globais e de linhas de um módulo crítico abaixo de 80%. |
| Consistência dos artefatos | Contagem do JUnit e percentuais do JSON conferidos no topo do README. O JSON histórico da T012 está idêntico à versão anterior no Git. |
| Django e Git | `manage.py check`, `makemigrations --check --dry-run` e `git diff --check` passaram. |

[Cobertura JSON](../coverage.json) · [Execução JUnit](../test-results-t043.xml) · [Indicadores no README](../README.md).
