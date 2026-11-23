# Tasks: Avaliação mútua pós-viagem

**Feature**: 006-avaliacao-mutua; IDs oficiais locais, independentes do roadmap.
**Input**: [spec](spec.md), [plan](plan.md), [dados](data-model.md), [pesquisa](research.md), [contratos](contracts/web-routes.md), [quickstart](quickstart.md).
**Status**: T001/T002/T004 concluídas; T003/T005 incorporadas, T006 aberta. [Interface T029](evidence-t029.md). [Evidência](evidence-t028.md).
**Tests**: TDD constitucional, dados fictícios, venv e PostgreSQL. Teste/falha esperada → implementação → verde/regressão. SC da spec integram conclusão da tarefa.

## Phase 1: Setup — decisões

- [x] T001 Resolver D006-01/D006-02 em spec.md e data-model.md com critérios de término, janela, pares, comentário e cancelamento; conclusão: cenários temporais verificáveis e esquema de término definido. **Requisitos**: REQ-008, REQ-003, REQ-017; decisões. **Depende**: —. **Conclusão**: critérios citados aprovados com evidência; pendência mantém bloqueio. **Roadmap**: preparação.

## Phase 2: Foundational

Feature 004 para participantes; Feature 005 para estado cancelado. App reviews já criado e verificado pela T002; interface integrada na T004 unificada.
Modelagem canônica em data-model.md: tarefas de modelo implementam integralmente entidades/restrições citadas após fechar campos condicionais. Não recriar ambiente por conveniência.

## Phase 3: User Story 1 (P1)

**Objetivo**: Participante elegível avalia contraparte com nota de 1 a 5 e comentário opcional após término verificável.
**Teste independente**: SC-001: rejeitar notas 0/6/fracionárias, autor e alvo iguais, não participante e duplicata; aceitar 1 e 5 com comentário vazio.

- [x] T002 [US1] Implementar integralmente o núcleo de avaliação da T028 do roadmap, reunindo as antigas T002/T003: criar app reviews e registrá-lo no settings efetivo; implementar RideReview em reviews/models.py e reviews/migrations/; implementar a referência de término aprovada em rides/models.py e sua migração quando necessária, e ReviewService em reviews/services/review_service.py. Escrever e executar primeiro tests/test_reviews.py para rating inteiro 1..5, comentário, unicidade, autoavaliação, FKs preservadas, participação, cancelamento/no-show e bordas temporais aprovadas; confirmar falhas comportamentais esperadas antes da implementação, depois verde e regressão. Não assumir término na partida. Verificar migrações e constraints no PostgreSQL local e de testes, preservando dados legados. **Requisitos**: REQ-008, REQ-003, REQ-017; FR-001/FR-002/FR-004; SC-001/SC-002. **Depende**: T001; Feature 004/T002; Feature 005/T004. **Conclusão**: modelo, referência de término, serviço, integridade/transações, cenários e migrações aprovados com evidência; pendência de decisão mantém bloqueio. **Roadmap**: T028, correspondência única. Fonte canônica de campos em [data-model.md](data-model.md): `RideReview.offer`, `RideReview.reviewer`, `RideReview.reviewed_user`, `RideReview.rating`, `RideReview.comment`, `RideReview.created_at`. Campos condicionais somente após T001. Sem formulário, view, rota ou cálculo de reputação nesta tarefa.

**T003 — incorporada à T002 em 2026-11-23 por solicitação do usuário.** ID mantido como referência histórica, sem tarefa executável independente e sem conclusão fictícia de implementação.

## Phase 4: User Story 2 (P2)

**Objetivo**: Usuário autenticado envia formulário sem poder escolher avaliador ou adulterar elegibilidade.
**Teste independente**: SC-003: contraparte válida registra avaliação por POST com CSRF; adulteração, GET de escrita e comentário HTML não burlam autorização nem escape.

- [x] T004 [US2] Implementar a interface integral da T029, reunindo antigas T004/T005: RideReviewForm em reviews/forms.py, reviews/templates/reviews/submit_review.html, SubmitReviewView em reviews/views.py, reviews/urls.py e inclusão no URLconf raiz. Tests/test_reviews.py escritos/executados antes da produção cobrem nota/comentário/escape, GET somente leitura, elegibilidade antes de apresentar formulário, sessão, CSRF, autoria da sessão/alvo da URL, adulteração, prazo, redirecionamento fixo e duplicata concorrente. Reutilizar ReviewService, revalidando na gravação; consulta de elegibilidade compartilhada com o serviço sem duplicar regra temporal. Não exibir e-mail/placa ou dados de alvo inelegível. **Requisitos**: REQ-008, REQ-003, REQ-017; FR-001–FR-004; SC-001/SC-002/SC-003. **Depende**: T002. **Conclusão**: formulário/view/template/rotas e cenários HTTP/concorrência aprovados com evidência, TDD e regressão pertinente; preservar todos os contratos da T002. **Roadmap**: T029, correspondência única. Sem reputação, novas migrações ou nova interface de conclusão de oferta.

**T005 — incorporada à T004 em 2026-11-23 por autorização do usuário.** Referência histórica, sem tarefa executável independente e sem alegação de implementação antecipada.

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T006 Criar scripts/check-feature006-quality.ps1 e gerar coverage-feature006.json e test-results-feature006.xml após testes novos e regressão pertinente; sincronizar bloco identificado no README.md com métricas reais e validar quickstart.md. **Requisitos**: REQ-008, REQ-014–REQ-019; todos os SC. **Depende**: todas as tarefas locais anteriores. **Conclusão**: cenários, privacidade, migração e regressão aprovados, >=80% linhas/ramificações críticas, relatórios versionáveis e roteiro verificado; não concluir sem evidência ou decisão. **Roadmap**: suporte a T041–T043, sem concluí-las. Sem staging/commit.

## Dependencies & Execution Order

Dependências explícitas de cada tarefa são obrigatórias; número não permite ignorar ramo anterior. MVP local: US1 após decisões; entrega completa: US1+US2+T006. Implementação dependente de decisão permanece bloqueada.

## Correspondência com roadmap

| Roadmap | Requisito / objetivo detalhado na tarefa | IDs locais |
| --- | --- | --- |
| T028 | REQ-008; modelo, término e serviço de elegibilidade | T002 (inclui antiga T003) |
| T029 | REQ-008; formulário e fluxo HTTP de avaliação | T004 (inclui antiga T005) |
| Preparação/qualidade | Decisões e evidência | T001, T006 |

## Parallel Opportunities & Implementation Strategy

Sem [P]: estado e contratos compartilhados, com decisões condicionais. Revisão pode ocorrer em paralelo; execução dependente não. Uma tarefa por rodada revisável, preservando IDs, checkboxes e alterações de outras features. Aprovar documentação não confirma automaticamente valores de produto.

## Consolidação de tarefas — 2026-11-23

Usuário solicitou unir as tarefas locais que dividiam a T028. T002 absorve integralmente T003, preservando requisitos, critérios e dependências; T004 passa a depender de T002. T003 fica como referência histórica, não reutilizada nem marcada como implementada. T001 documental continua necessária para D006-01/D006-02 e não foi executada ou aprovada por esta reorganização. T004/T005/T006 mantêm IDs e escopo. Ordem: T001 → T002 → T004 → T005 → T006. Nenhum código ou migração criado, nenhum teste executado; somente consistência documental verificada.

## Consolidação da T029 — 2026-11-23

Usuário autorizou unificar e implementar T004/T005 como T004 local, sem renumerar T006. T005 incorporada; ordem executável atual T001 → T002 → T004 → T006. Consolidações anteriores permanecem históricas. T006 de qualidade final fora desta rodada.
