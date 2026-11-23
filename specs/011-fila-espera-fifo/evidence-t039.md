# Evidência da Feature 011 / T001 local / T039 do roadmap

**Data** 2026-11-23 · **Requisitos** REQ-013, REQ-017, REQ-002 e REQ-003 · **Critérios** FR-001, FR-002, SC-001 e SC-002.

O ingresso pelo resultado lotado exige POST com CSRF, usa o titular da sessão e conserva o trecho em um novo envio. A oferta é o ponto de serialização entre ingresso, reserva e repasse. O serviço confirma uma reserva por chamada e remove a entrada na mesma transação. Os testes liberam uma vaga pelo fluxo existente e chamam o serviço diretamente. A conexão da chamada com o cancelamento é a T040.

## Resultados no PostgreSQL 16.15

| Verificação | Resultado |
| --- | --- |
| TDD inicial | Sete falhas esperadas após ajustar a fixture para cadastrar contas como pendentes e ativá-las em seguida. Faltavam serviço e rota. |
| Rollback em PostgreSQL | A primeira versão deixava um cursor de consulta aberto durante a reversão. O serviço passou a consultar a cabeça da fila a cada tentativa, o que permite reverter a reserva e eventuais remoções. |
| Filtro `test_fifo` | Oito aprovados, incluindo concorrência, inelegibilidade, alteração de trecho e rollback. |
| Suíte focada | 60 aprovados em espera, concorrência de reservas e notificações. |
| Suíte completa | 986 aprovados, incluindo 11 novos e 975 de regressão. Zero falhas, erros ou testes ignorados. |
| Cobertura consolidada | **98.95085588072888% em linhas** (1792/1811) e **96.3768115942029% em ramificações** (399/414). O serviço de fila alcançou 95.45454545454545% em linhas (42/44) e 92.85714285714286% em ramificações (13/14). |
| Migração | A migração `rides.0007_waitlist_entry` preservou duas contas, uma oferta, uma reserva e dois avisos sintéticos do esquema anterior. A tabela de espera começou vazia. |
| Django | `check` sem problemas e `makemigrations --check --dry-run` sem alterações. |

[Cobertura JSON](../../coverage-feature011-t039.json) · [Resultados JUnit](../../test-results-feature011-t039.xml).

## Reprodução

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_waitlist.py -k "test_fifo" -q --tb=short
.\venv\Scripts\python.exe -m pytest tests/test_waitlist.py tests/test_concurrency_booking.py tests/test_notifications.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=notifications --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature011-t039.json --junitxml=test-results-feature011-t039.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
~~~
