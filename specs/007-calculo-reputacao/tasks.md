# Tasks: Cálculo matemático de reputação

**Feature**: 007-calculo-reputacao; IDs oficiais locais, independentes do roadmap.
**Input**: [spec](spec.md), [plan](plan.md), [dados](data-model.md), [pesquisa](research.md), [contratos](contracts/web-routes.md), [quickstart](quickstart.md).
**Status**: T001, T002, T004 e T005 concluídas. T003 incorporada à T002. T006 aberta. [Evidência T030](evidence-t030.md) · [Recálculo T004](evidence-t004.md) · [Exibição T005](evidence-t005.md).
**Tests**: TDD constitucional, dados fictícios, venv e PostgreSQL. Teste/falha esperada → implementação → verde/regressão. SC da spec integram conclusão da tarefa.

## Phase 1: Setup — decisões

- [x] T001 Homologar D007-01/D007-02 em spec.md, research.md e data-model.md; converter exemplos contraditórios em fixtures de uma única fórmula com janela/unidade explícitas. **Requisitos**: REQ-009, REQ-003, REQ-017; decisões. **Depende**: —. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: preparação.

## Phase 2: Foundational

Feature 006 funcional (T002/T004 concluídas, T006 de qualidade própria ainda aberta); Feature 003 para integração na busca; Feature 001 para perfil. Penalidades serão integradas pela 008 sem duplicar mecanismo.
Modelagem canônica em data-model.md: tarefas de modelo implementam integralmente entidades/restrições citadas após fechar campos condicionais. Não recriar ambiente por conveniência.

## Phase 3: User Story 1 (P1)

**Objetivo**: Pontuação é calculada sobre conjunto elegível e regra transparente aprovada.
**Teste independente**: SC-001: após aprovação, novato e fixtures numéricas reproduzem regra exata; se média simples aprovada, [5,5,4,5,4]=4.60 e [5,5,5,1]=4.00.

- [x] T002 [US1] Implementar T030 integralmente, incorporando antiga T003: escrever/executar tests/test_reputation_calc.py antes da produção; criar ReputationProfile e migração em reviews/models.py e reviews/migrations/ conforme data-model.md; implementar calculate_score e ReputationService.rebuild em reviews/services/reputation_service.py. Cobrir novato, exemplos 4.60/4.00, precisão/arredondamento Decimal, janela de 20 avaliações, 21ª expulsando a mais antiga, empate por created_at/id, múltiplos passageiros da mesma viagem, referência temporal, sem expiração por dias, OneToOne/PROTECT/constraints, reconstrução/idempotência/rollback/cache ausente e dois rebuilds PostgreSQL independentes. Verificar migração local sem reset e regressão. **Requisitos**: REQ-009, REQ-003, REQ-017; FR-001/FR-002; SC-001/SC-002. **Depende**: T001; Feature 006/T002 (inclui antiga T003). **Conclusão**: modelo, seleção/cálculo/serviço e migração aprovados com evidência, vermelho/verde e meta documentada; sem signals ou exibição pública. **Roadmap**: T030, correspondência única. Campos canônicos: ReputationProfile.user, ReputationProfile.score, ReputationProfile.computed_at, em [data-model.md](data-model.md).

**T003 — incorporada à T002 em 2026-11-23 por autorização do usuário.** Referência histórica, sem tarefa independente ou conclusão fictícia.

## Phase 4: User Story 2 (P2)

**Objetivo**: Nova avaliação atualiza perfil e estrelas na busca sem expor detalhes privados.
**Teste independente**: SC-004: perfil e busca exibem nota atual sem campos privados nem N+1; ausência de perfil segue regra inicial homologada.

- [x] T004 [US2] Conectar signal em reviews/signals.py e reviews/apps.py ao serviço serializado; tests/test_reputation_integration.py comprova atualização, rollback, concorrência, cache ausente e reprocessamento idempotente. **Requisitos**: REQ-009, REQ-003, REQ-017; FR-003; SC-003. **Depende**: T002; Feature 006/T004 (inclui antiga T005). **Conclusão**: critérios citados aprovados na [evidência da T004](evidence-t004.md). **Roadmap**: T031.

- [x] T005 [US2] Integrar projeção no perfil de accounts e DTO/cartão em rides/services/matching_service.py e rides/templates/rides/_search_result.html; tests/test_reputation_integration.py cobre estrelas acessíveis, ausência de segredos e consultas sem N+1. **Requisitos**: REQ-009, REQ-003, REQ-017; FR-004; SC-004. **Depende**: T004; Feature 003/T004. **Conclusão**: critérios aprovados na [evidência](evidence-t005.md). **Roadmap**: T031.

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T006 Criar scripts/check-feature007-quality.ps1 e gerar coverage-feature007.json e test-results-feature007.xml após testes novos e regressão pertinente; sincronizar bloco identificado no README.md com métricas reais e validar quickstart.md. **Requisitos**: REQ-009, REQ-014–REQ-019; todos os SC. **Depende**: todas as tarefas locais anteriores. **Conclusão**: cenários, privacidade, migração e regressão aprovados, >=80% linhas/ramificações críticas, relatórios versionáveis e roteiro verificado; não concluir sem evidência ou decisão. **Roadmap**: suporte a T041–T043, sem concluí-las. Sem staging/commit.

## Dependencies & Execution Order

Dependências explícitas de cada tarefa são obrigatórias; número não permite ignorar ramo anterior. MVP local: US1 após decisões; entrega completa: US1+US2+T006. Implementação dependente de decisão permanece bloqueada.

## Correspondência com roadmap

| Roadmap | Requisito / objetivo detalhado na tarefa | IDs locais |
| --- | --- | --- |
| T030 | REQ-009; modelo, seleção e cálculo de reputação | T002 (inclui antiga T003) |
| T031 | REQ-009 | T004, T005 |
| Preparação/qualidade | Decisões e evidência | T001, T006 |

## Parallel Opportunities & Implementation Strategy

Sem [P]: estado e contratos compartilhados, com decisões condicionais. Revisão pode ocorrer em paralelo; execução dependente não. Uma tarefa por rodada revisável, preservando IDs, checkboxes e alterações de outras features. Aprovar documentação não confirma automaticamente valores de produto.

## Homologação e recorte — 2026-11-23

Usuário aprovou D007-01/D007-02 e autorizou T001 seguida da T002 unificada (antigas T002/T003, roadmap T030). D007-01: média aritmética simples das últimas 20 avaliações recebidas, cada avaliação com o mesmo peso mesmo na mesma viagem; sem janela de 30 dias. Selecionar created_at <= instante de referência e ordenar created_at DESC, id DESC, limit 20. A 21ª expulsa a mais antiga, não agrupar por oferta.

D007-02: novato 5.00 apenas quando conjunto vazio; base não entra como nota virtual. Calcular com Decimal e arredondar somente resultado final para duas casas com ROUND_HALF_UP, independente do contexto Decimal do chamador. [5,5,4,5,4]=4.60; [5,5,5,1]=4.00 (exatamente três notas 5 anteriores). Profile aceita 0.00..5.00; cálculo de notas 1..5 não gera zero, limite inferior prepara futura integração de penalidades da 008, não implementada agora.

ReputationProfile é projeção reconstruível sem substituir RideReview. Rebuild é serviço interno explícito, não endpoint; signals/atualização automática e exibição pública ficam T031. Referências anteriores a pendências/propostas divergentes são históricas e substituídas por esta homologação. Nenhuma aprovação de pesos, expiração por dias ou penalidades foi inferida.
IDs T004/T005/T006 preservados. Ordem atual T001 → T002 → T004 → T005 → T006; T003 incorporada. Dependências da Feature 006 remapeadas aos IDs sobreviventes T002/T004, sem concluir qualidade daquela feature.
