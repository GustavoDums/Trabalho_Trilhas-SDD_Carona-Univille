# Evidência da Feature 009 / T005 e T006 locais / T036 do roadmap

**Data**: 2026-11-23. **Requisitos**: REQ-011, REQ-003, REQ-017; FR-001, FR-003, FR-005; SC-004 e SC-005. **Dependências**: [T035 e T004 local](evidence-t035.md), busca da Feature 003/T004 e reserva da Feature 004/T005.

Esta evidência registra a entrega original. A janela usada atualmente pelo formulário e pelo comando foi revisada na [Feature 009/T008 local](spec.md#clarifications--decisões-confirmadas).

Na T005, o motorista titular cria a regra em Minhas ofertas → Caronas recorrentes. O POST protegido por CSRF grava a regra, as paradas e as ofertas na mesma transação. A listagem apresenta somente as regras do titular e as datas da janela atual. Os testes verificam que o número de consultas não cresce ao acrescentar regras.

Na T006, o operador executa `generate_recurring_rides --all` diariamente no agendador do ambiente ou usa `--rule ID` para uma regra. O comando e o formulário usam o mesmo gerador. Uma execução diária adiciona as datas que passaram a integrar a janela de 16 dias. Se um lote falhar, suas escritas são revertidas, os lotes independentes podem concluir e a execução retorna erro. A saída contém somente IDs de regra, datas e estados genéricos. [Configuração da rotina diária](quickstart.md#acionamento-diário).

## Verificações no PostgreSQL 16.15

| Verificação | Resultado |
| --- | --- |
| TDD da T005 | 10 falhas esperadas antes de existir a rota e 2 testes de acesso já aprovados. Após a implementação, os 12 casos passaram. |
| TDD da T006 | 4 falhas esperadas pela ausência do comando. |
| Suíte focada | 54 testes aprovados. Inclui titularidade, CSRF, validação, rollback, listagem, execuções sucessivas, suspensão, equivalência das datas, busca e reserva. |
| Suíte completa | 959 aprovados, incluindo 21 novos e 938 de regressão. Zero falhas ou testes ignorados. |
| Cobertura consolidada | 99.08869987849332% em linhas (1631/1646) e 96.42857142857143% em ramificações (378/392). Comando e serviço de recorrência com 100% em ambas as medidas. |
| Comando em processo separado | Em um banco PostgreSQL temporário, duas execuções de `manage.py generate_recurring_rides --all` geraram sete datas na primeira e identificaram as mesmas sete como existentes na segunda. |
| Django | `check` sem problemas. `makemigrations --check --dry-run` sem alterações. A ajuda do comando reconhece as duas opções de seleção. |

[Cobertura JSON](../../coverage-feature009-t036.json) · [Resultados JUnit](../../test-results-feature009-t036.xml).

## Reprodução

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_recurring_flow.py tests/test_recurring_rides.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature009-t036.json --junitxml=test-results-feature009-t036.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py generate_recurring_rides --help
~~~
