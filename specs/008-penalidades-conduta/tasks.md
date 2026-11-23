# Tasks: Penalidades por cancelamento tardio e no-show

**Feature**: 008-penalidades-conduta; IDs oficiais locais, independentes do roadmap.
**Input**: [spec](spec.md), [plan](plan.md), [dados](data-model.md), [pesquisa](research.md), [contratos](contracts/web-routes.md), [quickstart](quickstart.md).
**Status**: todas abertas, nenhuma execução nesta preparação.
**Tests**: TDD constitucional, dados fictícios, venv e PostgreSQL. Teste/falha esperada → implementação → verde/regressão. SC da spec integram conclusão da tarefa.

## Phase 1: Setup — decisões

- [ ] T001 Resolver D008-01/D008-02 em spec.md, data-model.md e contracts/web-routes.md, incluindo fonte de prova, contestação, janela, sanção e suspensão; conclusão: nenhuma divergência 7/14 dias remanescente como regra executável. **Requisitos**: REQ-010, REQ-003, REQ-017; decisões. **Depende**: —. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: preparação.

## Phase 2: Foundational

Features 005 (evento auditável), 006 (avaliação) e 007 (reputação) concluídas; middleware da 001 preservado.
Modelagem canônica em data-model.md: tarefas de modelo implementam integralmente entidades/restrições citadas após fechar campos condicionais. Não recriar ambiente por conveniência.

## Phase 3: User Story 1 (P1)

**Objetivo**: Cancelamento tardio ou falta comprovada produz registro auditável e efeito segundo política aprovada.
**Teste independente**: SC-001: evento repetido e concorrente gera um registro e um efeito; rollback não altera reputação nem suspensão.

- [ ] T002 [US1] Testar e implementar PenaltyRecord e entidade de conduta aprovada de data-model.md em reviews/models.py e reviews/migrations/; tests/test_penalties.py cobre origem única, deltas aprovados e histórico preservado. **Requisitos**: REQ-010, REQ-003, REQ-017; FR-001/FR-002/FR-003; SC-001/SC-002. **Depende**: T001; Feature 007/T003. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T032. Fonte canônica de campos em [data-model.md](data-model.md): `PenaltyRecord.subject`, `PenaltyRecord.actor`, `PenaltyRecord.offer`, `PenaltyRecord.booking`, `PenaltyRecord.source_key`, `PenaltyRecord.kind`, `PenaltyRecord.occurred_at`, `PenaltyRecord.delta`, `ConductProfile.suspended_until`. Campos condicionais só após T001.

- [ ] T003 [US1] Implementar PenaltyService em reviews/services/penalty_service.py consumindo CancellationRecord da 005; tests/test_penalties.py cobre deduplicação, concorrência, rollback e recomputação determinística com ReputationService. **Requisitos**: REQ-010, REQ-003, REQ-017; FR-001/FR-002; SC-001/SC-002. **Depende**: T002; Feature 005/T002; Feature 007/T004. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T033.

- [ ] T004 [US1] Implementar fluxo autorizado de no-show em reviews/services/penalty_service.py, reviews/views.py e reviews/urls.py após contrato aprovado; tests/test_penalties.py e tests/test_penalties_flow.py cobrem denúncia, evidência, limites, elegibilidade e efeito único. **Requisitos**: REQ-010, REQ-003, REQ-017; FR-001/FR-005; SC-003. **Depende**: T003; Feature 006/T005. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T033.

## Phase 4: User Story 2 (P2)

**Objetivo**: Conta mantém identidade/vínculo e consulta extrato, com ações disciplinarmente restringidas até expiração.
**Teste independente**: SC-004: suspenso continua autenticável e lê próprio extrato, mas ações bloqueadas falham em view e serviço; expiração libera automaticamente sem mudar vínculo; terceiros não veem extrato.

- [ ] T005 [US2] Integrar suspensão separada em accounts/middleware.py e checagens dos serviços de domínio; tests/test_penalties_flow.py cobre matriz de ações, início/expiração e preservação de academic_status/is_active. **Requisitos**: REQ-010, REQ-003, REQ-017; FR-003/FR-004; SC-004. **Depende**: T004. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T034.

- [ ] T006 [US2] Adicionar extrato próprio em accounts/views.py, accounts/urls.py e accounts/templates/accounts/penalties_history.html; tests/test_penalties_flow.py cobre acesso do suspenso, terceiros, dados privados e apresentação de motivo/prazo. **Requisitos**: REQ-010, REQ-003, REQ-017; FR-004; SC-004. **Depende**: T005. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T034.

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T007 Criar scripts/check-feature008-quality.ps1 e gerar coverage-feature008.json e test-results-feature008.xml após testes novos e regressão pertinente; sincronizar bloco identificado no README.md com métricas reais e validar quickstart.md. **Requisitos**: REQ-010, REQ-014–REQ-019; todos os SC. **Depende**: todas as tarefas locais anteriores. **Conclusão**: cenários, privacidade, migração e regressão aprovados, >=80% linhas/ramificações críticas, relatórios versionáveis e roteiro verificado; não concluir sem evidência ou decisão. **Roadmap**: suporte a T041–T043, sem concluí-las. Sem staging/commit.

## Dependencies & Execution Order

Dependências explícitas de cada tarefa são obrigatórias; número não permite ignorar ramo anterior. MVP local: US1 após decisões; entrega completa: US1+US2+T007. Implementação dependente de decisão permanece bloqueada.

## Correspondência com roadmap

| Roadmap | Requisito / objetivo detalhado na tarefa | IDs locais |
| --- | --- | --- |
| T032 | REQ-010 | T002 |
| T033 | REQ-010 | T003, T004 |
| T034 | REQ-010 | T005, T006 |
| Preparação/qualidade | Decisões e evidência | T001, T007 |

## Parallel Opportunities & Implementation Strategy

Sem [P]: estado e contratos compartilhados, com decisões condicionais. Revisão pode ocorrer em paralelo; execução dependente não. Uma tarefa por rodada revisável, preservando IDs, checkboxes e alterações de outras features. Aprovar documentação não confirma automaticamente valores de produto.
