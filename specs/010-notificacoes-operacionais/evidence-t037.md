# Evidência da Feature 010 / T001 local / T037 do roadmap

**Data**: 2026-11-23. **Requisitos**: REQ-012, REQ-003, REQ-017 e SC-001 a SC-003 no recorte de registro. As dependências de identidade, reserva e cancelamento já estavam concluídas.

A confirmação e o cancelamento individual registram um aviso para a pessoa titular da reserva e outro para o motorista. O cancelamento coletivo registra um aviso para o motorista e para cada passageiro cuja reserva confirmada foi cancelada. Cada aviso guarda apenas destinatário, tipo, origem e instantes de criação e leitura. A T038 trata de consulta e leitura.

O aviso é gravado junto com a operação original. Reprocessamento conserva o aviso existente e seu estado de leitura. A unicidade no PostgreSQL é por destinatário e reserva criada ou registro de cancelamento. O cancelamento coletivo reutiliza a lista de reservas já protegida pelo lock.

## Verificações no PostgreSQL 16.15

| Verificação | Resultado |
| --- | --- |
| TDD inicial | 12 falhas esperadas por ausência do app de notificações. |
| Concorrência | O primeiro teste integrado reproduziu timeout ao validar a FK do destinatário com outra reserva em andamento. A reserva passou a usar FOR NO KEY UPDATE nas contas, compatível com a verificação da FK. |
| Suíte focada | 116 aprovados, incluindo os testes de avisos, reservas concorrentes e cancelamentos. |
| Suíte completa | 971 aprovados, incluindo 12 novos e 959 de regressão. Zero falhas ou testes ignorados. |
| Cobertura consolidada | 99.11452184179457% em linhas (1679/1694) e 96.44670050761421% em ramificações (380/394). O pacote notifications atingiu 100% em ambas as medidas. |
| Migração | notifications.0001_initial aplicada em PostgreSQL temporário com dados fictícios anteriores. A comparação preservou 2 contas, 4 pontos, 1 oferta, 1 reserva e 1 cancelamento. A nova tabela foi criada vazia. |
| Django | `check` sem problemas, `makemigrations --check --dry-run` sem alterações e `migrate --plan` vazio após a aplicação. |

[Cobertura JSON](../../coverage-feature010-t037.json) · [Resultados JUnit](../../test-results-feature010-t037.xml).

## Reprodução

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_notifications.py tests/test_concurrency_booking.py tests/test_cancellation_flow.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=notifications --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature010-t037.json --junitxml=test-results-feature010-t037.xml
.\venv\Scripts\python.exe manage.py sqlmigrate notifications 0001
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
~~~
