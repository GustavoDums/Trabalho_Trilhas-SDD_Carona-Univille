# Tasks: Cálculo matemático de reputação

**Feature**: 007-calculo-reputacao; IDs oficiais locais, independentes do roadmap.
**Input**: [spec](spec.md), [plan](plan.md), [dados](data-model.md), [pesquisa](research.md), [contratos](contracts/web-routes.md), [quickstart](quickstart.md).
**Status**: todas abertas, nenhuma execução nesta preparação.
**Tests**: TDD constitucional, dados fictícios, venv e PostgreSQL. Teste/falha esperada → implementação → verde/regressão. SC da spec integram conclusão da tarefa.

## Phase 1: Setup — decisões

- [ ] T001 Homologar D007-01/D007-02 em spec.md, research.md e data-model.md; converter exemplos contraditórios em fixtures de uma única fórmula com janela/unidade explícitas. **Requisitos**: REQ-009, REQ-003, REQ-017; decisões. **Depende**: —. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: preparação.

## Phase 2: Foundational

Feature 006 concluída; Feature 003 para integração na busca; Feature 001 para perfil. Penalidades serão integradas pela 008 sem duplicar mecanismo.
Modelagem canônica em data-model.md: tarefas de modelo implementam integralmente entidades/restrições citadas após fechar campos condicionais. Não recriar ambiente por conveniência.

## Phase 3: User Story 1 (P1)

**Objetivo**: Pontuação é calculada sobre conjunto elegível e regra transparente aprovada.
**Teste independente**: SC-001: após aprovação, novato e fixtures numéricas reproduzem regra exata; se média simples aprovada, [5,5,4,5,4]=4.60 e [5,5,5,1]=4.00.

- [ ] T002 [US1] Escrever tests/test_reputation_calc.py e implementar ReputationProfile e migração em reviews/models.py e reviews/migrations/ conforme data-model.md; testar base aprovada, OneToOne e precisão Decimal. **Requisitos**: REQ-009, REQ-003, REQ-017; FR-001/FR-002; SC-001. **Depende**: T001; Feature 006/T003. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T030. Fonte canônica de campos em [data-model.md](data-model.md): `ReputationProfile.user`, `ReputationProfile.score`, `ReputationProfile.computed_at`. Campos condicionais só após T001.

- [ ] T003 [US1] Implementar cálculo e seleção de janela em reviews/services/reputation_service.py; tests/test_reputation_calc.py cobre exemplos aprovados, expiração, empate, unidade por carona/avaliação, arredondamento e reconstrução. **Requisitos**: REQ-009, REQ-003, REQ-017; FR-001/FR-002; SC-001/SC-002. **Depende**: T002. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T030. Fonte canônica de campos em [data-model.md](data-model.md): `ReputationProfile.user`, `ReputationProfile.score`, `ReputationProfile.computed_at`. Campos condicionais só após T001.

## Phase 4: User Story 2 (P2)

**Objetivo**: Nova avaliação atualiza perfil e estrelas na busca sem expor detalhes privados.
**Teste independente**: SC-004: perfil e busca exibem nota atual sem campos privados nem N+1; ausência de perfil segue regra inicial homologada.

- [ ] T004 [US2] Conectar signal em reviews/signals.py e reviews/apps.py ao serviço serializado; tests/test_reputation_integration.py comprova atualização, rollback, concorrência, cache ausente e reprocessamento idempotente. **Requisitos**: REQ-009, REQ-003, REQ-017; FR-003; SC-003. **Depende**: T003; Feature 006/T005. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T031.

- [ ] T005 [US2] Integrar projeção no perfil de accounts e DTO/cartão em rides/services/matching_service.py e rides/templates/rides/_search_result.html; tests/test_reputation_integration.py cobre estrelas acessíveis, ausência de segredos e consultas sem N+1. **Requisitos**: REQ-009, REQ-003, REQ-017; FR-004; SC-004. **Depende**: T004; Feature 003/T004. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T031.

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T006 Criar scripts/check-feature007-quality.ps1 e gerar coverage-feature007.json e test-results-feature007.xml após testes novos e regressão pertinente; sincronizar bloco identificado no README.md com métricas reais e validar quickstart.md. **Requisitos**: REQ-009, REQ-014–REQ-019; todos os SC. **Depende**: todas as tarefas locais anteriores. **Conclusão**: cenários, privacidade, migração e regressão aprovados, >=80% linhas/ramificações críticas, relatórios versionáveis e roteiro verificado; não concluir sem evidência ou decisão. **Roadmap**: suporte a T041–T043, sem concluí-las. Sem staging/commit.

## Dependencies & Execution Order

Dependências explícitas de cada tarefa são obrigatórias; número não permite ignorar ramo anterior. MVP local: US1 após decisões; entrega completa: US1+US2+T006. Implementação dependente de decisão permanece bloqueada.

## Correspondência com roadmap

| Roadmap | Requisito / objetivo detalhado na tarefa | IDs locais |
| --- | --- | --- |
| T030 | REQ-009 | T002, T003 |
| T031 | REQ-009 | T004, T005 |
| Preparação/qualidade | Decisões e evidência | T001, T006 |

## Parallel Opportunities & Implementation Strategy

Sem [P]: estado e contratos compartilhados, com decisões condicionais. Revisão pode ocorrer em paralelo; execução dependente não. Uma tarefa por rodada revisável, preservando IDs, checkboxes e alterações de outras features. Aprovar documentação não confirma automaticamente valores de produto.
