# Tasks: Reserva de vagas sem overbooking

**Feature**: 004-reserva-sem-overbooking; IDs oficiais locais, independentes do roadmap.
**Input**: [spec](spec.md), [plan](plan.md), [dados](data-model.md), [pesquisa](research.md), [contratos](contracts/web-routes.md), [quickstart](quickstart.md).
**Status**: T001–T003 concluídas; T004–T007 abertas. T006 autorizada pelo usuário para a próxima rodada, não executada aqui. [Modelo](evidence-t020.md) e [serviço/concorrência](evidence-t021.md).
**Tests**: TDD constitucional, dados fictícios, venv e PostgreSQL. Teste/falha esperada → implementação → verde/regressão. SC da spec integram conclusão da tarefa.

## Phase 1: Setup — decisões

- [x] T001 Fechar D004-01/D004-02 em spec.md e contracts/web-routes.md com aprovação da dupla; conclusão: estados, contato e pontos de embarque definidos, sem homologar propostas automaticamente. **Requisitos**: REQ-006, REQ-003, REQ-017; decisões. **Depende**: —. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: preparação.

## Phase 2: Foundational

Features 001/002 implementadas; Feature 003/T001 (pacote de serviços) antes de criar módulos; Feature 003/T002–T004 antes da integração de disponibilidade na busca.
Modelagem canônica em data-model.md: tarefas de modelo implementam integralmente entidades/restrições citadas após fechar campos condicionais. Não recriar ambiente por conveniência.

## Phase 3: User Story 1 (P1)

**Objetivo**: Passageiro ativo solicita uma vaga em oferta futura elegível; o servidor valida e confirma somente se houver disponibilidade.
**Teste independente**: SC-001: duas conexões PostgreSQL independentes disputam simultaneamente uma última vaga; exatamente uma confirma, outra recebe esgotamento, contagem confirmada=1 e disponibilidade=0 (após D004-01).

- [x] T002 [US1] Escrever testes do modelo em tests/test_booking_flow.py e adicionar RideBooking em rides/models.py e migração em rides/migrations/, conforme data-model.md (RideBooking e RideOffer.seats); testar autorreserva, passageiro elegível na criação, trecho ordenado/distinto e unicidade ativa, incluindo restrições de status/pontos/unicidade no PostgreSQL. Escopo de modelo de FR-006/SC-005; serviço de capacidade/concorrência permanece T003. **Requisitos**: REQ-006, REQ-003, REQ-017; FR-001/FR-002; SC-002. **Depende**: T001; Features 001/002. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T020. Fonte canônica de campos em [data-model.md](data-model.md): `RideBooking.id`, `RideBooking.offer`, `RideBooking.passenger`, `RideBooking.boarding_point`, `RideBooking.alighting_point`, `RideBooking.status`, `RideBooking.created_at`, `RideBooking.updated_at`, `RideOffer.seats`. D004-01/D004-02 homologadas; não adicionar telefone, contador de vagas ou serviço de reserva nesta tarefa.

- [x] T003 [US1] Implementar BookingService.create_booking em rides/services/booking_service.py após testes em tests/test_concurrency_booking.py com TransactionTestCase ou pytest transaction=True, duas conexões/threads e barreira antes da disputa (nunca após obter lock); conclusão: uma confirmação, uma rejeição, rollback e capacidade preservados no PostgreSQL. **Requisitos**: REQ-006, REQ-003, REQ-017; FR-001/FR-002/FR-005; SC-001/SC-002. **Depende**: T002; Feature 003/T001. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T021.

- [ ] T006 [US1] Integrar disponibilidade calculada em rides/services/matching_service.py e cartão de busca em rides/templates/rides/_search_result.html; testes em tests/test_ride_search.py comprovam vagas ocupadas e esgotamento sem alterar filtros nem expor segredos. **Requisitos**: REQ-006, REQ-003, REQ-017; FR-004; SC-004. **Depende**: T003; Feature 003/T004. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T021/T023.

## Phase 4: User Story 2 (P2)

**Objetivo**: Participante consulta suas reservas e dados autorizados da contraparte; terceiros não obtêm acesso por troca de ID.
**Teste independente**: SC-004: busca e consulta própria refletem disponibilidade atual sem N+1; GET não cria reserva.

- [ ] T004 [US2] Testar e implementar BookRideView e projeção privada de minhas reservas em rides/views.py e rides/templates/rides/my_bookings.html; verificar matriz de contrapartes e ausência de e-mail, conforme contracts/web-routes.md. **Requisitos**: REQ-006, REQ-003, REQ-017; FR-003; SC-003. **Depende**: T003. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T022.

- [ ] T005 [US2] Mapear rides:book e rides:my_bookings em rides/urls.py e completar fluxo HTTP em tests/test_booking_flow.py, incluindo CSRF, 405, repetição e IDs de terceiros; conclusão: reserva e consulta integradas conforme contrato. **Requisitos**: REQ-006, REQ-003, REQ-017; FR-002/FR-003/FR-005; SC-002/SC-003/SC-004. **Depende**: T004 e T006 (disponibilidade). **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T023.

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T007 Criar scripts/check-feature004-quality.ps1 e gerar coverage-feature004.json e test-results-feature004.xml após testes novos e regressão pertinente; sincronizar bloco identificado no README.md com métricas reais e validar quickstart.md. **Requisitos**: REQ-006, REQ-014–REQ-019; todos os SC. **Depende**: todas as tarefas locais anteriores. **Conclusão**: cenários, privacidade, migração e regressão aprovados, >=80% linhas/ramificações críticas, relatórios versionáveis e roteiro verificado; não concluir sem evidência ou decisão. **Roadmap**: suporte a T041–T043, sem concluí-las. Sem staging/commit.

## Dependencies & Execution Order

Dependências explícitas de cada tarefa são obrigatórias; número não permite ignorar ramo anterior. MVP local: US1 após decisões; entrega completa: US1+US2+T007. Implementação dependente de decisão permanece bloqueada.

## Correspondência com roadmap

| Roadmap | Requisito / objetivo detalhado na tarefa | IDs locais |
| --- | --- | --- |
| T020 | REQ-006 | T002 |
| T021 | REQ-006; núcleo de serviço/concorrência concluído | T003; T006 é integração em rodada própria |
| T022 | REQ-006 | T004 |
| T023 | REQ-006 | T005, T006 |
| Preparação/qualidade | Decisões e evidência | T001, T007 |

## Parallel Opportunities & Implementation Strategy

Sem [P]: estado e contratos compartilhados, com decisões condicionais. Revisão pode ocorrer em paralelo; execução dependente não. Uma tarefa por rodada revisável, preservando IDs, checkboxes e alterações de outras features. Aprovar documentação não confirma automaticamente valores de produto.
