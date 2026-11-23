# Tasks: Avaliação mútua pós-viagem

**Feature**: 006-avaliacao-mutua; IDs oficiais locais, independentes do roadmap.
**Input**: [spec](spec.md), [plan](plan.md), [dados](data-model.md), [pesquisa](research.md), [contratos](contracts/web-routes.md), [quickstart](quickstart.md).
**Status**: todas abertas, nenhuma execução nesta preparação.
**Tests**: TDD constitucional, dados fictícios, venv e PostgreSQL. Teste/falha esperada → implementação → verde/regressão. SC da spec integram conclusão da tarefa.

## Phase 1: Setup — decisões

- [ ] T001 Resolver D006-01/D006-02 em spec.md e data-model.md com critérios de término, janela, pares, comentário e cancelamento; conclusão: cenários temporais verificáveis e esquema de término definido. **Requisitos**: REQ-008, REQ-003, REQ-017; decisões. **Depende**: —. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: preparação.

## Phase 2: Foundational

Feature 004 para participantes; Feature 005 para estado cancelado. Criar app reviews somente na execução das tarefas; não existe hoje.
Modelagem canônica em data-model.md: tarefas de modelo implementam integralmente entidades/restrições citadas após fechar campos condicionais. Não recriar ambiente por conveniência.

## Phase 3: User Story 1 (P1)

**Objetivo**: Participante elegível avalia contraparte com nota de 1 a 5 e comentário opcional após término verificável.
**Teste independente**: SC-001: rejeitar notas 0/6/fracionárias, autor e alvo iguais, não participante e duplicata; aceitar 1 e 5 com comentário vazio.

- [ ] T002 [US1] Criar app reviews, registrar configuração no módulo settings efetivo e testar/migrar RideReview de data-model.md em reviews/models.py e reviews/migrations/; tests/test_reviews.py cobre rating, unicidade, autoavaliação e FKs preservadas. **Requisitos**: REQ-008, REQ-003, REQ-017; FR-001/FR-004; SC-001. **Depende**: T001; Feature 004/T002. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T028. Fonte canônica de campos em [data-model.md](data-model.md): `RideReview.offer`, `RideReview.reviewer`, `RideReview.reviewed_user`, `RideReview.rating`, `RideReview.comment`, `RideReview.created_at`. Campos condicionais só após T001.

- [ ] T003 [US1] Implementar referência de término aprovada em rides/models.py e migração se necessária, e ReviewService em reviews/services/review_service.py; tests/test_reviews.py cobre participação, cancelamento/no-show e bordas de tempo sem assumir término na partida. **Requisitos**: REQ-008, REQ-003, REQ-017; FR-002/FR-004; SC-002. **Depende**: T002; Feature 005/T004. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T028. Fonte canônica de campos em [data-model.md](data-model.md): `RideReview.offer`, `RideReview.reviewer`, `RideReview.reviewed_user`, `RideReview.rating`, `RideReview.comment`, `RideReview.created_at`. Campos condicionais só após T001.

## Phase 4: User Story 2 (P2)

**Objetivo**: Usuário autenticado envia formulário sem poder escolher avaliador ou adulterar elegibilidade.
**Teste independente**: SC-003: contraparte válida registra avaliação por POST com CSRF; adulteração, GET de escrita e comentário HTML não burlam autorização nem escape.

- [ ] T004 [US2] Implementar RideReviewForm em reviews/forms.py e reviews/templates/reviews/submit_review.html; testes de formulário/renderização em tests/test_reviews.py cobrem campos, comentário opcional e escape. **Requisitos**: REQ-008, REQ-003, REQ-017; FR-001/FR-003; SC-001/SC-003. **Depende**: T003. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T029.

- [ ] T005 [US2] Implementar SubmitReviewView e rotas em reviews/views.py, reviews/urls.py e URLconf raiz efetiva; tests/test_reviews.py cobre sessão, CSRF, adulteração, redirecionamento e duplicata concorrente. **Requisitos**: REQ-008, REQ-003, REQ-017; FR-002/FR-003/FR-004; SC-003. **Depende**: T004. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: T029.

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T006 Criar scripts/check-feature006-quality.ps1 e gerar coverage-feature006.json e test-results-feature006.xml após testes novos e regressão pertinente; sincronizar bloco identificado no README.md com métricas reais e validar quickstart.md. **Requisitos**: REQ-008, REQ-014–REQ-019; todos os SC. **Depende**: todas as tarefas locais anteriores. **Conclusão**: cenários, privacidade, migração e regressão aprovados, >=80% linhas/ramificações críticas, relatórios versionáveis e roteiro verificado; não concluir sem evidência ou decisão. **Roadmap**: suporte a T041–T043, sem concluí-las. Sem staging/commit.

## Dependencies & Execution Order

Dependências explícitas de cada tarefa são obrigatórias; número não permite ignorar ramo anterior. MVP local: US1 após decisões; entrega completa: US1+US2+T006. Implementação dependente de decisão permanece bloqueada.

## Correspondência com roadmap

| Roadmap | Requisito / objetivo detalhado na tarefa | IDs locais |
| --- | --- | --- |
| T028 | REQ-008 | T002, T003 |
| T029 | REQ-008 | T004, T005 |
| Preparação/qualidade | Decisões e evidência | T001, T006 |

## Parallel Opportunities & Implementation Strategy

Sem [P]: estado e contratos compartilhados, com decisões condicionais. Revisão pode ocorrer em paralelo; execução dependente não. Uma tarefa por rodada revisável, preservando IDs, checkboxes e alterações de outras features. Aprovar documentação não confirma automaticamente valores de produto.
