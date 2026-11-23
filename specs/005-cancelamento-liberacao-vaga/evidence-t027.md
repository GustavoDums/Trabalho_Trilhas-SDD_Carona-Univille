# Auditoria do MVP — Feature 005/T007 local / roadmap T027

Data: 2026-11-23. Requisitos auditados REQ-001–REQ-007, com REQ-014–REQ-019 de governança. Correspondência única pelo objetivo: auditoria MVP = T007 local. Dependências locais T001–T006 concluídas; Features 001–004 funcionais. Qualidade da Feature 002/T007 aceita pelo usuário (tempo humano aproximado, sem cronometragem exata) e Feature 003/T005 aceita por confirmação de busca <=1 minuto/legibilidade. Preservados os limites e evidências desses aceites.

## Rastreabilidade e critérios

| Requisito | Evidência automatizada | O que foi auditado |
| --- | --- | --- |
| REQ-001 | test_models.py, test_registration.py | Papéis fixos, nome, e-mail único, cadastro Motorista/Passageiro e estado inicial PENDENTE |
| REQ-002 | test_activation.py, test_access_control.py, jornadas de test_rides_offer.py/test_ride_search.py | Whitelist fictícia, aprovação/recusa, sessão e login reais, bloqueio de pendentes/inelegíveis |
| REQ-003 | test_privacy_lgpd.py, test_booking_flow.py, test_ride_search.py, test_cancellation_flow.py | Nome abreviado na busca, e-mail confidencial, dados privados somente à contraparte confirmada, revogação após cancelamento, CSRF e titularidade |
| REQ-004 | test_rides_offer.py | Catálogo, veículo/snapshot, zero/duas paradas ordenadas, autoria da sessão, publicação atômica, rollback, consulta própria |
| REQ-005 | test_matching.py, test_ride_search.py | i<j, ±30min inclusivos pela saída da origem, 1s fora, fuso/meia-noite, passageiro ativo, leitura sem mutação, sem N+1 |
| REQ-006 | test_booking_flow.py, test_concurrency_booking.py, disponibilidade em test_ride_search.py | Uma confirmação na última vaga, conexões/transações PostgreSQL independentes, capacidade preservada, duplicidade e rollback |
| REQ-007 | test_cancellation_deadlines.py, test_cancellation_flow.py | Prazos 2h/4h inclusivos, tardio pré-partida aceito/auditado, partida/depois recusado, lote de oferta, histórico, idempotência, concorrência e HTTP POST/CSRF |

SC-001: relógio controlado nos três instantes de ambos os prazos; SC-002: saldo derivado e cancelamento/reserva concorrentes; SC-003: cancelamento de oferta/lote e rollback; SC-004: titularidade, privacidade e exclusão/liberação imediata na busca; SC-005: execução integral, relatórios e metas consolidados abaixo.

REQ-014: cadeia spec/plan/tasks prévia respeitada. REQ-015: IDs locais/roadmap e sugestão de commit explícitos. REQ-016: prompts/decisões registrados. REQ-017: toda tests/ executada. REQ-018: JSON/JUnit e cobertura por módulo crítico. REQ-019: bloco MVP próprio no topo do README, sem atribuir contagem consolidada exclusivamente à Feature 005.

## Automação e reprodutibilidade

[check-mvp-quality.ps1](../../scripts/check-mvp-quality.ps1) usa venv existente, executa check/makemigrations --check --dry-run/migrate --check e toda tests/, com cobertura de accounts, rides e carona_univille e branches. Exige >=80% em linhas, ramificações e combinada, tanto consolidada como por arquivo crítico de models/forms/services/views/middleware. Exige testes aprovados e zero ignorados; erros deixam README sem alteração. Relatórios próprios [coverage-mvp.json](../../coverage-mvp.json) e [test-results-mvp.xml](../../test-results-mvp.xml), sem sobrescrever relatórios individuais.

Esta tarefa é auditoria/automação, sem mudança de comportamento da aplicação ou novo teste de produto: baseline anterior de 668 testes, repetido pelo script, sem fabricar falha de TDD. Scripts de qualidade anteriores serviram de referência. Nenhuma nova biblioteca ou migração. PostgreSQL real, fixtures sintéticas; nenhum reset ou modificação dos dados locais de desenvolvimento.

Migrações locais verificadas: accounts 0001/0002 e rides 0001/0002/0003/0004 aplicadas; migrate --plan sem operações, check sem problemas e makemigrations --check sem mudanças. Testes criam esquema no banco isolado. Pendências históricas da constitution (homologação docente, domínios adicionais) continuam registradas; a auditoria valida a PoC simulada aprovada, sem declarar homologação institucional real.

## Limites de escopo

Não encerrar T041–T045, bônus, penalidades, recorrência ou tarefas próprias de qualidade das outras features. Feature 004/T007 permanece em seu checklist; sua funcionalidade/concorrência e regressão são auditadas aqui, sem criar o script/relatórios próprios dessa tarefa. Nenhum staging/commit. O script mede código Python, não cobertura visual de HTML; demonstrações humanas das Features 002/003 constam em evidências próprias. Fluxos de cancelamento conferidos por testes HTTP Django, sem atribuir inspeção visual humana inexistente.

## Resultado final

**T007 local / T027 concluída.** Script executado integralmente: 668 testes aprovados, 0 falhas/ignorados, 87.04s. Nenhum teste de produto adicionado nesta auditoria; todos são regressão verificada.

| Escopo | Linhas | Ramificações | Combinada |
| --- | --- | --- | --- |
| accounts + rides + carona_univille | 905/920 (98.3695652173913%) | 208/216 (96.29629629629629%) | 97.97535211267606% |
| matching_service | 61/61 (100%) | 18/18 (100%) | 100% |
| booking_service | 51/51 (100%) | 20/20 (100%) | 100% |
| cancellation_service | 79/80 (98.75%) | 31/32 (96.875%) | 98.21428571428571% |

Todos os arquivos críticos de cadastro/validação/acesso/forms/views/models/services superaram 80% de linhas/ramificações/combinada pelo gate do script. Não ocultar lacunas: asgi.py e wsgi.py não foram exercitados (8 linhas totais de bootstrap), accounts/models.py possui 4 linhas não cobertas, accounts/views.py 2, e cancellation_service.py 1 linha defensiva de reconsulta; ramificações parciais preexistentes em accounts e rides. Esses arquivos continuam no denominador consolidado. Cobertura não promete 100% do produto ou de HTML.

Contagem por módulo: models 24; foundation 10; registration 35; activation 25; access_control 42; privacy_lgpd 16; rides_offer 115; matching 65; ride_search 77; booking_flow 120; concurrency_booking 33; cancellation_deadlines 35; cancellation_flow 71. Total 668.

### Concorrência real registrada nesta execução

JUnit contém conexões e transações distintas, com barreiras e timeout de lock. Seleção de evidências:

| Corrida | PIDs PostgreSQL | TxIDs | Resultado final |
| --- | --- | --- | --- |
| Última vaga / dois passageiros | 9276, 26888 | 43981, 43982 | confirmed/no_seats; 1 confirmada, saldo 0 |
| Última vaga / mesmo passageiro | 35584, 23272 | 44010, 44011 | already_booked/confirmed; 1 confirmada, saldo 0 |
| Cancelar reserva / reservar | 22520, 11488 | 43828, 43827 | cancelled/no_seats; 0 confirmadas antes de nova tentativa, 1 auditoria |
| Cancelar reserva / repetir | 11572, 17076 | 43859, 43860 | ambas cancelled; 0 confirmadas, 1 auditoria |
| Cancelar oferta / reservar | 35740, 21124 | 43890, 43891 | offer_cancelled/reserved; lote deixa 0 confirmadas, 1 auditoria de oferta |
| Cancelar oferta / cancelar reserva | 25528, 16836 | 43922, 43923 | ambas efetivadas/idempotentes; 0 confirmadas, 1 auditoria de oferta |
| Cancelar oferta / repetir | 38120, 36608 | 43953, 43954 | ambas offer_cancelled; 0 confirmadas, 1 auditoria de oferta |

No caso reservar/fechar oferta, reserva criada primeiro foi cancelada pelo lote. Saldo é derivado, capacidade não é incrementada. Metadados completos estão no JUnit; a regressão também verifica retries/idempotência/rollback.

### Quickstart e revisão de artefatos

Comandos de ambiente, migrações e testes do quickstart executados; fluxos de reserva/oferta canceladas, prazos e privacidade cobertos pelos testes de HTTP/serviço. Qualidade 002/003 validada pelas evidências de aceitação humana existentes; não há nova alegação de demo humana de cancelamento. Script salvo em UTF-8 com BOM para Windows PowerShell 5.1 ler corretamente acentos do bloco README, sem mudar configuração do sistema. Primeira saída com caracteres incorretos foi corrigida somente no novo bloco MVP; parser PowerShell final sem erros. Ajuste de codificação/documentação não exigiu repetição da suíte.

Métricas anteriores e dados locais preservados. git diff --check sem erros; nenhuma mudança de comportamento Python, staging ou commit. T041–T045 e Feature 004/T007 continuam abertas, conforme seu escopo próprio.

Arquivos criados/alterados: script, JSON/JUnit, [README](../../README.md), [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md), [spec](spec.md), [plan](plan.md), [tasks](tasks.md), [quickstart](quickstart.md) e esta evidência.

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-mvp-quality.ps1
~~~

Commit sugerido: chore(005/T007): auditar MVP e concluir T027 — REQ-001–REQ-007, REQ-014–REQ-019
