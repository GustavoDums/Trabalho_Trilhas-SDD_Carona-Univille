# Evidência da Feature 011 / T002 local / T040 do roadmap

**Data** 2026-11-23 · **Requisitos** REQ-007, REQ-013 e REQ-017 · **Critérios** FR-003 e SC-003 · **Dependências** T024 e T039 concluídas.

O cancelamento individual repassa a vaga ao primeiro passageiro elegível dentro da transação que registra o cancelamento. A reserva resultante gera o aviso de confirmação já definido na Feature 010. A repetição do cancelamento conserva a mesma auditoria e reserva. Uma falha inesperada reverte cancelamento, auditoria, penalidade, avisos e repasse.

O painel consulta somente as entradas do passageiro da sessão e exibe posição, trecho e horário em ofertas abertas e futuras. A promoção remove a entrada atendida e a posição de quem espera é recalculada a partir da fila atual.

## Verificações no PostgreSQL 16.15

| Verificação | Resultado |
| --- | --- |
| TDD inicial | Três falhas esperadas pela ausência de posição e do gatilho integrado. O encerramento de oferta já deixava de produzir reservas. |
| Fluxo integrado | Quatro testes cobrem cancelamento HTTP e repetição, privacidade da posição e aviso, rollback e cancelamentos concorrentes em ofertas com filas cruzadas. |
| Suíte focada | 102 aprovados em fila, cancelamentos e notificações. |
| Suíte completa | 990 aprovados, incluindo quatro novos e 986 de regressão. Zero falhas, erros ou testes ignorados. |
| Cobertura consolidada | **98.95776193088317% em linhas** (1804/1823) e **96.41148325358851% em ramificações** (403/418). |
| Django | `check` sem problemas e `makemigrations --check --dry-run` sem alterações. |

[Cobertura JSON](../../coverage-feature011-t040.json) · [Resultados JUnit](../../test-results-feature011-t040.xml).

## Reprodução

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_waitlist_flow.py tests/test_waitlist.py tests/test_cancellation_flow.py tests/test_notifications.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=notifications --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature011-t040.json --junitxml=test-results-feature011-t040.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
~~~
