# Tasks: Cancelamento e liberação de vaga

**Feature**: 005-cancelamento-liberacao-vaga; IDs oficiais locais, independentes do roadmap.
**Input**: [spec](spec.md), [plan](plan.md), [dados](data-model.md), [pesquisa](research.md), [contratos](contracts/web-routes.md), [quickstart](quickstart.md).
**Status**: T001–T004 concluídas; T005–T007 abertas. [Evidência T004](evidence-t025.md). [Evidência](evidence-t024.md).
**Tests**: TDD constitucional, dados fictícios, venv e PostgreSQL. Teste/falha esperada → implementação → verde/regressão. SC da spec integram conclusão da tarefa.

## Phase 1: Setup — decisões

- [x] T001 Homologar D005-01/D005-02 em spec.md, data-model.md e contracts/web-routes.md; registrar fronteiras e distribuição de responsabilidade com 008 antes de implementar prazos. **Requisitos**: REQ-007, REQ-003, REQ-017; decisões. **Depende**: —. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: preparação.

## Phase 2: Foundational

Feature 004 funcional, com T007 de qualidade final pendente; Feature 003 para disponibilidade na busca; auditoria MVP depende de todas as implementações T001–T026 do roadmap, não apenas destes documentos.
Modelagem canônica em data-model.md: tarefas de modelo implementam integralmente entidades/restrições citadas após fechar campos condicionais. Não recriar ambiente por conveniência.

## Phase 3: User Story 1 (P1)

**Objetivo**: Passageiro solicita cancelamento, recebe classificação temporal conforme política aprovada e libera vaga quando a transição for permitida.
**Teste independente**: SC-001: testar passageiro em 120min01s/120min/119min59s e motorista em 240min01s/240min/239min59s; os dois primeiros são tempestivos e o terceiro é tardio aceito antes da partida; na partida ou depois, recusar sem mutação.

- [x] T002 [US1] Escrever tests/test_cancellation_deadlines.py e implementar política/CancellationService em rides/services/cancellation_service.py; adicionar CancellationRecord e campos de cancelamento de data-model.md em rides/models.py e rides/migrations/; conclusão: matriz temporal aprovada, evento único e nenhuma dedução antecipada. **Requisitos**: REQ-007, REQ-003, REQ-017; FR-001/FR-005; SC-001. **Depende**: T001; Feature 004/T003. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T024. Fonte canônica de campos em [data-model.md](data-model.md): `RideOffer.status`, `RideOffer.cancelled_at`, `RideBooking.cancelled_at`, `CancellationRecord.id`, `CancellationRecord.actor`, `CancellationRecord.offer`, `CancellationRecord.booking`, `CancellationRecord.occurred_at`, `CancellationRecord.classification`. D005-01/D005-02 homologadas; campos/constraints de auditoria canônicos em data-model.md. Sem penalidade numérica.

- [x] T003 [US1] Implementar transição de reserva idempotente e disponibilidade derivada no serviço, atualizar BookingService/MatchingService para status de oferta e tests/test_cancellation_flow.py; conclusão: repetição e corrida reservar/cancelar respeitam capacidade sem modificar RideOffer.seats. **Requisitos**: REQ-007, REQ-003, REQ-017; FR-002; SC-002. **Depende**: T002; Feature 004/T006. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T025.

- [ ] T005 [US1] Implementar CancelBookingView, rota e confirmação em rides/views.py, rides/urls.py e rides/templates/rides/my_bookings.html; testar titularidade, CSRF, 405 e revogação de contato em tests/test_cancellation_flow.py. **Requisitos**: REQ-007, REQ-003, REQ-017; FR-001/FR-004; SC-004. **Depende**: T003; Feature 004/T005. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T026.

## Phase 4: User Story 2 (P1)

**Objetivo**: Motorista encerra oferta própria e cancela suas reservas vinculadas atomicamente.
**Teste independente**: SC-005: auditoria do MVP executa REQ-001–REQ-007 e versão real de relatório >=80% de linhas e ramificações críticas, sem encerrar marcos globais T041–T045.

- [x] T004 [US2] Implementar cancelamento atômico de oferta usando RideOffer.status/cancelled_at preparados na T002 conforme data-model.md; atuar em rides/services/cancellation_service.py e ajustar modelos/migrações somente se necessário; atualizar matching e reservas; testar rollback e disputa simultânea em tests/test_cancellation_flow.py. **Requisitos**: REQ-007, REQ-003, REQ-017; FR-003; SC-003/SC-004. **Depende**: T003. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T025.

- [ ] T006 [US2] Implementar CancelOfferView, rota e confirmação em rides/views.py, rides/urls.py e rides/templates/rides/my_offers.html; testes integrados de oferta e reservas em tests/test_cancellation_flow.py comprovam política aprovada e histórico preservado. **Requisitos**: REQ-007, REQ-003, REQ-017; FR-001/FR-003/FR-004; SC-003/SC-004. **Depende**: T004/T005. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T026.

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T007 Auditar MVP REQ-001–REQ-007 com toda a suíte tests/, após implementar/validar roadmap T001–T026; criar scripts/check-mvp-quality.ps1, coverage-mvp.json e test-results-mvp.xml; sincronizar bloco identificado no README.md com métricas reais e validar quickstart.md. **Requisitos**: REQ-007, REQ-014–REQ-019; todos os SC. **Depende**: todas as tarefas locais anteriores; Features 001–004 funcionais e qualidade pendente da 002/003 comprovada. **Conclusão**: cenários, privacidade, migração e regressão aprovados, >=80% linhas/ramificações críticas, relatórios versionáveis e roteiro verificado; não concluir sem evidência ou decisão. **Roadmap**: T027. Sem staging/commit.

## Dependencies & Execution Order

Dependências explícitas de cada tarefa são obrigatórias; número não permite ignorar ramo anterior. MVP local: US1 após decisões; entrega completa: US1+US2+T007. Implementação dependente de decisão permanece bloqueada.

## Correspondência com roadmap

| Roadmap | Requisito / objetivo detalhado na tarefa | IDs locais |
| --- | --- | --- |
| T024 | REQ-007 | T002 |
| T025 | REQ-007 | T003, T004 |
| T026 | REQ-007 | T005, T006 |
| T027 | REQ-014–REQ-019; auditoria MVP | T007 |
| Preparação/qualidade | Decisões e evidência | T001 |

## Parallel Opportunities & Implementation Strategy

Sem [P]: estado e contratos compartilhados, com decisões condicionais. Revisão pode ocorrer em paralelo; execução dependente não. Uma tarefa por rodada revisável, preservando IDs, checkboxes e alterações de outras features. Aprovar documentação não confirma automaticamente valores de produto.
