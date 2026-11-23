# Evidência — Feature 005 / T004 local / roadmap T025

Data: 2026-11-23. Requisitos REQ-007, REQ-003, REQ-017; FR-003; SC-003/SC-004. Dependência T003 concluída. Usuário autorizou somente T004 após identificação das duas correspondências T003/T004. Notificações pertencem a T037–T038; interface permanece T005/T006 local.

## Comportamento e verificação

CancellationService.cancel_offer valida motorista titular ativo no banco, bloqueia oferta → usuários por PK → reservas confirmadas por PK. Captura relógio uma vez, aplica prazo inclusivo de 4h pela saída da origem, aceita tardio anterior à partida com auditoria, recusa na partida/depois sem mutação. Oferta e reservas confirmadas são canceladas atomicamente; capacidade e histórico anterior preservados. Um evento de oferta (booking=None) representa o lote, sem imputar cancelamento aos passageiros. Repetição não altera datas/eventos, inclusive legado sem auditoria.

- TDD vermelho: 23 novos testes falharam por AttributeError: CancellationService.cancel_offer ausente; 8 anteriores passaram.
- Verde focado: 66 testes de cancelamento aprovados (43 anteriores + 23 novos).
- Regressão: 621 aprovados, 0 falhas/ignorados, 83.26s; 598 anteriores preservados.
- Cenários: 4h01s/4h/3h59min59s; partida/pós-partida; ator anônimo, passageiro, terceiro motorista, pendente, desabilitado e removido; IDs inválidos/ausentes; lote com várias reservas e histórico anterior; oferta sem confirmadas; rollback após inserção de auditoria; idempotência e legado.
- Busca exclui oferta encerrada; nova reserva é rejeitada; projeção privada revoga placa após cancelamento.
- PostgreSQL, conexões e transações independentes, barreira de sincronização e lock_timeout de 10s; sem sleep ou mocks de locks. Metadados no JUnit:

| Corrida | Backend PIDs | TxIDs | Resultados | Confirmadas finais / eventos de oferta |
| --- | --- | --- | --- | --- |
| oferta / reservar | 37848, 38892 | 27015, 27016 | offer_cancelled, reserved | 0 / 1 |
| oferta / reserva cancelada | 4124, 29004 | 27047, 27048 | offer_cancelled, booking_cancelled | 0 / 1 |
| oferta / oferta | 2560, 26060 | 27078, 27079 | offer_cancelled, offer_cancelled | 0 / 1 |

Na primeira corrida a reserva foi criada antes do fechamento e cancelada pelo lote. Todas as interleavings válidas terminam sem confirmadas na oferta cancelada.

## Qualidade e reprodução

[JSON de cobertura](../../coverage-feature005-t025.json), [JUnit](../../test-results-feature005-t025.xml).

- rides/: 591/592 linhas (99.83108108108108%), 160/164 ramificações (97.5609756097561%); combinada 99.33862433862434%.
- cancellation_service: 79/80 linhas (98.75%), 31/32 ramificações (96.875%). Única linha não coberta: defesa preexistente da reserva ausente após reconsulta; três outras ramificações preexistentes em models. Meta de 80% atendida.
- manage.py check: nenhum problema; makemigrations --check --dry-run: sem alterações; migrate --plan: nenhuma operação; conexão local vendor=postgresql e zero migrações pendentes. Esquema 0004 existente suficiente; nenhum dado local alterado.
- Diagnósticos do editor: nenhum erro nos dois arquivos Python alterados. git diff --check sem erros.

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_cancellation_deadlines.py tests/test_cancellation_flow.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature005-t025.json --junitxml=test-results-feature005-t025.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
~~~

Quickstart conferido para API e verificações acima; fluxo HTTP/GUI ainda não disponível nesta tarefa. T004 e T025 concluídas; T005–T007 abertas. Sem staging, commit, notificações, penalidade ou auditoria global do MVP.

Arquivos: serviço e tests/test_cancellation_flow.py; README; relatórios JSON/JUnit; docs/prompts.md e roadmap; spec/plan/tasks/data-model/research/contracts/quickstart desta feature e esta evidência. Relatórios anteriores preservados.
