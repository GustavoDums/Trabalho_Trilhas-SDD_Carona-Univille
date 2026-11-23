# Feature Specification: Cancelamento e liberação de vaga

**Feature**: 005-cancelamento-liberacao-vaga | **Created**: 2026-11-22
**Status**: decisões homologadas e T001–T003 concluídas; T004–T007 abertas. [Evidência](evidence-t024.md).
**Input**: REQ-007 e solicitação de preparação documental.

## Contexto e rastreabilidade

Fontes: [constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro histórico de preparação](../../docs/preparacao-features-004-009.md). Formato de referência: [Feature 003](../003-busca-rota-horario/spec.md).
Requisito principal REQ-007; transversais REQ-002, REQ-003, REQ-014–REQ-019. Correspondências oficiais em [tasks.md](tasks.md).
Propostas do roadmap não equivalem a decisões homologadas. Estes artefatos permitem revisar o escopo, sem decidir produto por suposição.

## Clarifications — decisões confirmadas

- **D005-01 — CONFIRMADA em 2026-11-22**: passageiro 2h, motorista 4h, referência na saída da origem e borda inclusiva (antecedência >= prazo). Comparar instantes aware em UTC.
- **D005-02 — CONFIRMADA em 2026-11-22**: tardio antes da partida é aceito com evento auditável, sem dedução numérica nesta feature; na partida ou depois, recusar preservando estado. Penalidades futuras pertencem à 008.

## User Scenarios & Testing

### US1 — Cancelar minha reserva (P1)

Passageiro solicita cancelamento, recebe classificação temporal conforme política aprovada e libera vaga quando a transição for permitida.

**Teste independente**: SC-001: testar passageiro em 120min01s/120min/119min59s e motorista em 240min01s/240min/239min59s; os dois primeiros são tempestivos e o terceiro é tardio aceito antes da partida; na partida/depois, recusar sem mutação.

### US2 — Cancelar minha oferta (P1)

Motorista encerra oferta própria e cancela suas reservas vinculadas atomicamente.

**Teste independente**: SC-005: auditoria do MVP executa REQ-001–REQ-007 e versão real de relatório >=80% de linhas e ramificações críticas, sem encerrar marcos globais T041–T045.

## Functional Requirements

- FR-001 / REQ-007: somente titular cancela reserva ou oferta; avaliar relógio aware capturado uma vez dentro da transação conforme D005-01/D005-02.
- FR-002 / REQ-006: CONFIRMADA→CANCELADA libera exatamente uma vaga derivada; repetição é idempotente. Nunca incrementar RideOffer.seats.
- FR-003 / REQ-007: cancelamento de oferta impede novas reservas e cancela todas as confirmadas no mesmo commit; preservar histórico.
- FR-004 / REQ-003: revogar acesso a contato/placa após cancelamento, mantendo resumo próprio sem segredos; não disparar mensagens externas.
- FR-005 / REQ-007, REQ-010: registrar autor, instante, alvo e classificação temporal; dedução numérica pertence à Feature 008.

## Fluxo e exceções

1. Identificar sessão e revalidar papel/vínculo no servidor.
2. Validar alvo, estado e política homologada antes de transição.
3. Executar operação completa ou preservar domínio em caso de recusa/rollback.
4. Apresentar resultado ao titular, sem dados privados de terceiros.
5. Verificar repetição e concorrência pelos critérios abaixo; dados do navegador nunca autorizam a ação.

## Dependencies & Scope

Feature 004 funcional (T001–T006 implementadas; T007 de qualidade final ainda pendente); Feature 003 para disponibilidade na busca; auditoria MVP depende de todas as implementações T001–T026 do roadmap, não apenas destes documentos.

Não inclui bônus 010/011, staging, commits ou integrações externas. D005-01/D005-02 homologadas; T003 local incluída explicitamente nesta rodada para provar liberação de vaga. T004/T005/T006/T007 permanecem futuras. REQ-020 e T041–T045 orientam entrega geral, sem conclusão nesta preparação.

## Success Criteria

- SC-001: testar passageiro em 120min01s/120min/119min59s e motorista em 240min01s/240min/239min59s; os dois primeiros são tempestivos e o terceiro é tardio aceito antes da partida; na partida/depois, recusar sem mutação.
- SC-002: cancelar reserva aumenta disponibilidade derivada em um; repetir não altera contagem. Cancelamento concorrente com reserva nunca excede capacidade.
- SC-003: cancelar oferta com várias reservas fecha oferta e cancela todas, ou rollback não altera nenhuma; nova reserva é rejeitada.
- SC-004: terceiro não cancela nem lê contato; busca reflete cancelamento imediatamente após commit.
- SC-005: auditoria do MVP executa REQ-001–REQ-007 e versão real de relatório >=80% de linhas e ramificações críticas, sem encerrar marcos globais T041–T045.

Todos os critérios exigem testes fictícios. Qualidade: >=80% de linhas e ramificações críticas, relatório versionável e métricas reais identificadas por feature no README; nenhuma métrica estimada nesta rodada.
