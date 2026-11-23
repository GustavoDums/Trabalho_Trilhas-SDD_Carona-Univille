# Evidência — Feature 005 / T002–T003 locais / T024 e parcela da T025

Decisões confirmadas em 2026-11-22; implementação e medição encerradas em **2026-11-23**.
Requisitos: REQ-007, REQ-006, REQ-003 e REQ-017; governança REQ-014–REQ-019.

## Escopo confirmado

T024 corresponde a T002 local (política/auditoria). O usuário também confirmou executar T003 local, parcela de reserva da T025, para provar liberação de vaga.
D005-01: 2h passageiro, 4h motorista, saída da origem, comparação aware em UTC e borda inclusiva.
D005-02: tardio antes da partida é aceito/auditado, sem dedução numérica; partida ou posterior é recusado sem alterar estado. Repetição de reserva já cancelada é idempotente mesmo após a partida.

T001 documental atendida pela confirmação. Cancelamento de oferta T004, views/rotas T005/T006 e auditoria MVP T007 ficam fora desta rodada. Feature 004 está funcional; sua T007 de qualidade final não foi declarada concluída como pré-requisito.

## Implementação

CancellationPolicy.classify compara instantes completos normalizados para UTC. CancellationService.cancel_booking bloqueia oferta → usuários por PK → reserva, reconsulta o titular ativo, captura um único instante para nova transição e grava CANCELADA/cancelled_at/CancellationRecord no mesmo atomic. Sem contador: disponibilidade deriva de CONFIRMADA, sem alterar RideOffer.seats.

Auditoria tem ator, oferta, reserva opcional, instante e classificação TEMPESTIVO/TARDIO; FKs PROTECT, enum e unicidades parciais impedem eventos duplicados. NULL booking prepara esquema para futura oferta, não implementa cancel_offer. Reservas CANCELADA legadas mantêm data desconhecida None e não recebem evento inventado.

RideOffer.status/cancelled_at foram preparados conforme T002; BookingService recusa e MatchingService exclui CANCELADA. Nenhuma operação pública de cancelar oferta foi criada. Falha de auditoria após insert reverte também o estado/data da reserva.

## TDD e prazos

Antes da produção:
- **34 falhas** em test_cancellation_deadlines.py por serviço ausente.
- **8 falhas** em test_cancellation_flow.py por serviço/modelo/campos ausentes.
- Total vermelho válido: **42 falhas**, sem erros de fixture.

Após implementação: **42 aprovados**. Foi acrescentada verificação de esquema/vínculo da auditoria, enum SQL e unicidade de alvo nulo; conjunto final **43 aprovados** (35 prazos/modelo + 8 fluxo/concorrência).

| Ator | Antes do limite | Limite exato | Depois do limite, ainda antes da saída |
| --- | --- | --- | --- |
| Passageiro | 120min01s: TEMPESTIVO | 120min: TEMPESTIVO | 119min59s: TARDIO aceito |
| Motorista, política pura | 240min01s: TEMPESTIVO | 240min: TEMPESTIVO | 239min59s: TARDIO |

Teste de motorista valida a política; serviço de cancelamento da oferta permanece futuro.
Partida exata e 1s após: CancellationRefused, code departure_reached; reserva/datas/eventos/capacidade preservados.
Cobertos ainda meia-noite, offsets equivalentes, 1 microsegundo após borda, timestamps inválidos/naive, papel inválido, titularidade/estado atual da conta, IDs inválidos, captura única do clock, unicidade SQL e horários opcionais.

## Liberação, privacidade e concorrência

Após cancelamento aceito, saldo sobe de zero para um, repetição não o aumenta novamente e nova reserva usa essa vaga. Busca reflete saldo e consulta privada omite placa automaticamente. Não foi criada UI de cancelamento.
Falha sintética após inserir auditoria reverte reserva, timestamp e evento; nova tentativa funciona.

Duas threads PostgreSQL com conexões/transações distintas, barreira antes dos locks e timeouts, sem mocks de lock/sleeps. Propriedades do [JUnit](../../test-results-feature005-t024.xml):

| Corrida | Backend PIDs | TxIDs | Resultados observados | Confirmadas antes de nova tentativa | Eventos |
| --- | --- | --- | --- | --- | --- |
| Cancelar/reservar | 16668, 39368 | 23854, 23855 | cancelled / no_seats | 0 | 1 |
| Cancelar/cancelar | 36524, 6988 | 23886, 23887 | cancelled / cancelled | 0 | 1 |

Na corrida reservar/cancelar, ambas as ordens são válidas: se reserva chega primeiro, esgotamento é recusado e depois o cancelamento libera; a tentativa posterior é testada e confirma uma reserva, saldo zero. Se cancelamento chega primeiro, a reserva concorrente pode confirmar. Em todos os casos capacidade permanece 1 e confirmadas <=1. Repetição concorrente grava um evento só.

## Migração local

SQL e migrate --plan revisados antes da aplicação. **0004_cancellation_support aplicada no PostgreSQL local**:
- Campos antigos de contas, ofertas, reservas, pontos e paradas comparados por snapshots completos em memória: idênticos.
- Ofertas legadas recebem ABERTA; novas datas permanecem NULL; auditoria começa vazia.
- Migração registrada, 3 FKs e constraints de classificação/unicidade/estado verificadas por introspecção.
- Sem reset, exclusão ou rollback do banco local; showmigrations indica 0001–0004 aplicadas.
- manage.py check sem problemas; makemigrations --check --dry-run: No changes detected.

## Regressão e cobertura

~~~powershell
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature005-t024.json --junitxml=test-results-feature005-t024.xml
~~~

**598 aprovados; 0 falhas, 0 erros, 0 ignorados**: 43 novos da Feature 005 e 555 de regressão.
Cobertura rides: **563/564 linhas (99.822695035461%)**, **148/152 ramificações (97.36842105263158%)**, combinada **99.30167597765363%**.
cancellation_service: **51/52 linhas (98.07692307692308%)**, **19/20 ramificações (95%)**, combinada **97.22222222222223%**. Meta >=80% atendida em linhas/ramificações, sem alegar 100% ou cobertura global de accounts. A linha defensiva de reserva indisponível após reconsulta sob lock não foi exercitada.
Relatórios: [coverage-feature005-t024.json](../../coverage-feature005-t024.json) e [test-results-feature005-t024.xml](../../test-results-feature005-t024.xml). Relatórios anteriores preservados.
Editor sem diagnósticos; links/whitespace conferidos ao encerrar.

## Arquivos

- [models.py](../../rides/models.py), [0004_cancellation_support.py](../../rides/migrations/0004_cancellation_support.py), [cancellation_service.py](../../rides/services/cancellation_service.py).
- [booking_service.py](../../rides/services/booking_service.py) e [matching_service.py](../../rides/services/matching_service.py): checagem de status de oferta.
- [conftest.py](../../tests/conftest.py), [test_cancellation_deadlines.py](../../tests/test_cancellation_deadlines.py), [test_cancellation_flow.py](../../tests/test_cancellation_flow.py), [test_booking_flow.py](../../tests/test_booking_flow.py): último adaptado apenas à inclusão canônica de cancelled_at na whitelist do modelo.
- [spec.md](spec.md), [plan.md](plan.md), [tasks.md](tasks.md), [data-model.md](data-model.md), [research.md](research.md), [contracts/web-routes.md](contracts/web-routes.md), [quickstart.md](quickstart.md), este registro e [contrato do serviço da Feature 004](../004-reserva-sem-overbooking/contracts/web-routes.md).
- [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md), [README](../../README.md) e relatórios acima.

T001–T003 locais concluídas; T004–T007 abertas. T024 concluída, T025 parcial por faltar cancelamento de oferta. Sem UI, novas rotas, mensagens externas, penalidade numérica, staging ou commit. Constitution preservada; confirmação das regras é registrada nos artefatos da feature.
