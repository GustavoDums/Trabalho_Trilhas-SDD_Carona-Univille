# Evidência — Feature 004 / T002 local / roadmap T020

Data local: 2026-11-22 (o cabeçalho gerado da migração usa UTC em 2026-11-23).
Requisitos: REQ-006, REQ-002, REQ-003 e REQ-017; governança REQ-014–REQ-019.

## Decisões e limite autorizado

Correspondência única: T020 do roadmap → T002 local, modelo RideBooking/migração.
Dependência documental T001 atendida por confirmação explícita do usuário: reserva instantânea CONFIRMADA/CANCELADA, uma vaga durante toda a oferta, persistência dos pontos escolhidos em ordem no itinerário e WhatsApp adiado (sem telefone). Confirmação registrada em [prompts](../../docs/prompts.md), [levantamento](../../docs/levantamento.md) e artefatos desta feature.

Modelo inclui offer, passenger, boarding_point, alighting_point, status e timestamps. Não altera RideOffer.seats.
PROTECT preserva relações históricas; enum/pontos distintos e índice único parcial em reserva CONFIRMADA estão no banco. Validações entre tabelas são Python/full_clean, repetidas futuramente pelo serviço sob lock.

**Não há operação suportada de reserva, controle de capacidade agregada ou comprovação de zero overbooking nesta tarefa.** Isso pertence à T003 local/T021; criação direta de modelo não substitui serviço transacional. bulk_create/update/SQL podem contornar clean; somente constraints SQL permanecem nesses caminhos.

## TDD

Testes escritos e executados antes do código de produção: **49 falhas**, todas LookupError por RideBooking ausente, sem erros de fixture.
Após modelo e migração: **49 aprovados** no PostgreSQL.

Casos: default CONFIRMADA, timestamps aware/atualização, autorreserva mesmo com papel alterado no banco, passageiro pendente/desabilitado/papel incorreto na criação, 16 pares do itinerário, ponto externo/inversão/igualdade, rota direta e dado legado ambíguo; relações obrigatórias/IDs inválidos/status inválido; unicidade ativa por passageiro/oferta inclusive trechos diferentes; restrições SQL via bulk/update; histórico CANCELADA permite nova CONFIRMADA; outra oferta/passageiro não é duplicata; FKs protegidas e esquema da migração introspectado.

## Migração no banco local previsto

Revisados manage.py migrate --plan e sqlmigrate rides 0003: única operação prevista rides.0003_ridebooking, criação de tabela/índices/FKs sem reescrever contas/ofertas/catálogo/paradas.

Aplicada por call_command('migrate', 'rides') no shell Django usando venv/configuração PostgreSQL existentes.
Comparados snapshots completos dos registros de AcademicUser, RideOffer, RoutePoint e Waypoint, apenas em memória e sem expor valores: **idênticos antes/depois**.
Confirmados: nova tabela vazia; registro da migração; 4 FKs, booking_active_passenger_unique, booking_status_valid e booking_points_distinct.
showmigrations rides: 0001, 0002 e **0003_ridebooking [X]**.
manage.py check: sem problemas; makemigrations --check --dry-run: No changes detected. Não houve reset, exclusão de registros ou rollback de esquema local.

## Regressão e medição

~~~powershell
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature004-t020.json --junitxml=test-results-feature004-t020.xml
~~~

**444 aprovados; 0 falhas, 0 erros e 0 ignorados**.
São 49 testes novos de modelo da Feature 004 e 395 de regressão (152 accounts, 115 ofertas e 128 busca).
Cobertura de rides: **351/351 linhas (100%)**, **89/92 ramificações (96.73913043478261%)**, combinada **99.32279909706546%**. RideBooking: 100% de linhas e ramificações no relatório. Meta >=80% atendida nesse conjunto, sem alegar cobertura global de accounts.
Relatórios versionáveis: [coverage-feature004-t020.json](../../coverage-feature004-t020.json) e [test-results-feature004-t020.xml](../../test-results-feature004-t020.xml). Medições anteriores preservadas.

Diagnósticos do editor: sem erros em modelo, migração e testes. Links/whitespace conferidos ao encerrar.

## Arquivos criados/alterados

- [rides/models.py](../../rides/models.py): RideBooking.
- [0003_ridebooking.py](../../rides/migrations/0003_ridebooking.py): tabela e constraints.
- [test_booking_flow.py](../../tests/test_booking_flow.py): somente casos de modelo nesta tarefa, sem HTTP antecipado.
- [spec.md](spec.md), [plan.md](plan.md), [tasks.md](tasks.md), [data-model.md](data-model.md), [research.md](research.md), [contracts/web-routes.md](contracts/web-routes.md), [quickstart.md](quickstart.md) e este registro.
- [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md), [README](../../README.md) e relatórios vinculados acima.

T001 documental e T002 concluídas somente após aprovação/evidência. T003–T007 locais continuam abertas. Sem serviço, view, rota, telefone, contador de vagas, staging ou commit. Alterações anteriores preservadas.
