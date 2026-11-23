# Feature Specification: Penalidades por cancelamento tardio e no-show

**Feature**: 008-penalidades-conduta | **Created**: 2026-11-22
**Status**: rascunho preparado; decisões abaixo bloqueiam tarefas afetadas. Nenhuma implementação realizada.
**Input**: REQ-010 e solicitação de preparação documental.

## Contexto e rastreabilidade

Fontes: [constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Formato de referência: [Feature 003](../003-busca-rota-horario/spec.md).
Requisito principal REQ-010; transversais REQ-002, REQ-003, REQ-014–REQ-019. Correspondências oficiais em [tasks.md](tasks.md).
Propostas do roadmap não equivalem a decisões homologadas. Estes artefatos permitem revisar o escopo, sem decidir produto por suposição.

## Clarifications — decisões pendentes

- **D008-01 — PENDENTE**: Resolver suspensão de 7 dias (roadmap) versus 14 dias (levantamento), limiar proposto de 3 faltas em 30 dias, tolerância proposta de 10min e denúncia até 2h; definir referência para paradas sem ETA.
- **D008-02 — PENDENTE**: Homologar deduções -0.20/-0.50, nota automática 1 e sua combinação sem dupla punição acidental; definir autor autorizado, evidência, contestação, limites da nota e ações bloqueadas durante suspensão.

## User Scenarios & Testing

### US1 — Registrar ocorrência uma única vez (P1)

Cancelamento tardio ou falta comprovada produz registro auditável e efeito segundo política aprovada.

**Teste independente**: SC-001: evento repetido e concorrente gera um registro e um efeito; rollback não altera reputação nem suspensão.

### US2 — Aplicar e consultar suspensão (P2)

Conta mantém identidade/vínculo e consulta extrato, com ações disciplinarmente restringidas até expiração.

**Teste independente**: SC-004: suspenso continua autenticável e lê próprio extrato, mas ações bloqueadas falham em view e serviço; expiração libera automaticamente sem mudar vínculo; terceiros não veem extrato.

## Functional Requirements

- FR-001 / REQ-010: somente ocorrência elegível e autorizada gera penalidade, com alvo, tipo, origem, autor e instante auditáveis; repetição não duplica efeito.
- FR-002 / REQ-009, REQ-010: recomputar reputação pela política aprovada, sem subtração repetida a cada leitura/signal.
- FR-003 / REQ-010: suspensão disciplinar é estado separado de academic_status e is_active; não transformar vínculo acadêmico em PENDENTE.
- FR-004 / REQ-002, REQ-003: usuário acessa apenas próprio extrato; login, ativação, saída e extrato continuam utilizáveis conforme matriz aprovada; bloquear ações definidas no servidor.
- FR-005 / REQ-010: ausência não é inferida automaticamente apenas pelo passar do tempo; denúncia e referência temporal dependem de D008-01/D008-02.

## Fluxo e exceções

1. Identificar sessão e revalidar papel/vínculo no servidor.
2. Validar alvo, estado e política homologada antes de transição.
3. Executar operação completa ou preservar domínio em caso de recusa/rollback.
4. Apresentar resultado ao titular, sem dados privados de terceiros.
5. Verificar repetição e concorrência pelos critérios abaixo; dados do navegador nunca autorizam a ação.

## Dependencies & Scope

Features 005 (evento auditável), 006 (avaliação) e 007 (reputação) concluídas; middleware da 001 preservado.

Não inclui bônus 010/011, staging, commits ou integrações externas. Critérios dependentes de decisão são condicionais até homologação. REQ-020 e T041–T045 orientam entrega geral, sem conclusão nesta preparação.

## Success Criteria

- SC-001: evento repetido e concorrente gera um registro e um efeito; rollback não altera reputação nem suspensão.
- SC-002: após homologação, dedução de cancelamento 4.80→4.60 se -0.20 aprovado; no-show testa separadamente dedução e eventual nota automática, sem efeitos extras.
- SC-003: testar tolerância/denúncia nos limites e 1s fora, três ocorrências distintas na janela proposta e expiração conforme duração finalmente aprovada.
- SC-004: suspenso continua autenticável e lê próprio extrato, mas ações bloqueadas falham em view e serviço; expiração libera automaticamente sem mudar vínculo; terceiros não veem extrato.

Todos os critérios exigem testes fictícios. Qualidade: >=80% de linhas e ramificações críticas, relatório versionável e métricas reais identificadas por feature no README; nenhuma métrica estimada nesta rodada.
