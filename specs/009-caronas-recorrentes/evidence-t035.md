# Evidência da Feature 009 / T002 a T004 locais / T035 do roadmap

**Data**: 2026-11-23. **Requisitos**: REQ-011, REQ-003 e REQ-017. **Dependências**: [decisões D009-01/D009-02](spec.md), publicação da Feature 002, pacote de serviços da Feature 003/T001 e cancelamento da Feature 005/T006.

| Tarefa | Evidência |
| --- | --- |
| T002 | Regra, paradas ordenadas e vínculo único entre regra, data local e oferta. A migração criou três tabelas e protege os vínculos históricos. |
| T003 | O gerador usa 16 dias corridos em America/Sao_Paulo, incluindo a data local de referência. Partidas estritamente futuras são publicadas pelo serviço existente, com validação do motorista, bloqueio PostgreSQL e rollback do lote. Edições e desativação preservam os dados das ocorrências anteriores. |
| T004 | Um cancelamento real via CancellationService alterou apenas a oferta e a reserva daquela ocorrência. Os snapshots das outras ofertas e reservas e a regra permaneceram iguais. A reexecução conservou o ID da oferta cancelada e o vínculo original. |

A criação pela interface e o acionamento diário do gerador pertencem à T036.

## Verificações no PostgreSQL 16.15

| Verificação | Resultado |
| --- | --- |
| TDD dos modelos | 17 falhas esperadas pela ausência dos modelos, seguidas de 17 aprovações. |
| TDD do serviço | 12 falhas esperadas pela ausência do gerador, seguidas de 29 aprovações no módulo. |
| Suíte focada | 33 aprovados. Cobre cancelamento e reexecução, duas conexões concorrentes, rollback intermediário, limites de calendário, fuso, suspensão, autorização e snapshots. Inclui dois casos adicionais para oferta inexistente e oferta de outro motorista. |
| Suíte completa | 938 aprovados, incluindo 33 novos e 905 de regressão. Zero falhas ou testes ignorados. |
| Cobertura consolidada | 99.03969270166453% em linhas (1547/1562) e 96.03174603174604% em ramificações (363/378). Modelos de recorrência com 100% em linhas (67/67) e 83,33% em ramificações (20/24). Gerador com 100% em ambas as medidas. |
| Migração | rides.0006_recurring_ride aplicada em PostgreSQL temporário sobre 2 contas, 4 pontos, 1 oferta, 1 parada e 1 reserva fictícias. A comparação confirmou que todos os registros permaneceram iguais. As três novas tabelas foram criadas vazias. |
| Django | `check` sem problemas, `makemigrations --check --dry-run` sem alterações e `migrate --plan` vazio após a aplicação. |

[Cobertura JSON](../../coverage-feature009-t035.json) · [Resultados JUnit](../../test-results-feature009-t035.xml).

## Reprodução

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_recurring_rides.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature009-t035.json --junitxml=test-results-feature009-t035.xml
.\venv\Scripts\python.exe manage.py sqlmigrate rides 0006
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
~~~
