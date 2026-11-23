# Feature Specification: Penalidades por cancelamento tardio e no-show

**Feature**: 008-penalidades-conduta | **Created**: 2026-11-22
**Status**: D008-01 e D008-02 homologadas em 2026-11-23.
**Input**: REQ-010 e solicitação de preparação documental.

## Contexto e rastreabilidade

Fontes: [constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Formato de referência: [Feature 003](../003-busca-rota-horario/spec.md).
Requisito principal REQ-010; transversais REQ-002, REQ-003, REQ-014–REQ-019. Correspondências oficiais em [tasks.md](tasks.md).
Propostas do roadmap não equivalem a decisões homologadas. Estes artefatos permitem revisar o escopo, sem decidir produto por suposição.

## Clarifications — decisões homologadas em 2026-11-23

- **D008-01**: Três no-shows distintos em 30 dias geram 14 dias de suspensão. Tolerância de 10 minutos a partir do horário previsto de embarque e denúncia até 2 horas após a conclusão registrada da carona. Em parada sem horário previsto, a denúncia fica indisponível até existir referência de embarque.
- **D008-02**: Deduzir 0,20 por cancelamento tardio. No-show contribui com uma nota 1,0 na média e deduz 0,50 uma vez após o cálculo, com nota final entre 0,00 e 5,00. Somente a contraparte confirmada pode denunciar, com declaração vinculada à reserva e horário registrado. Contestação tem revisão administrativa. A suspensão bloqueia novas ofertas e reservas e mantém acesso à conta, ao extrato e ao cancelamento de compromissos existentes.
- **Complemento à D008-01**: O motorista titular pode registrar a conclusão pela interface. Para a denúncia de ausência do motorista sem conclusão registrada, a janela de 2 horas começa no fim dos 10 minutos de tolerância. A avaliação mútua continua condicionada à conclusão registrada.

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

A feature usa o evento auditável da 005, as avaliações da 006 e a reputação da 007. O estado disciplinar é separado do estado acadêmico da 001.

Não inclui bônus 010/011, staging, commits ou integrações externas. REQ-020 e T041–T045 orientam a entrega geral.

## Success Criteria

- SC-001: evento repetido e concorrente gera um registro e um efeito; rollback não altera reputação nem suspensão.
- SC-002: cancelamento tardio deduz 0,20 (4,80 → 4,60). No-show acrescenta uma nota 1,0 à média e deduz 0,50 uma vez.
- SC-003: testar tolerância e denúncia nos limites e um segundo fora, três ocorrências distintas em 30 dias e expiração da suspensão após 14 dias.
- SC-004: suspenso continua autenticável e lê próprio extrato, mas ações bloqueadas falham em view e serviço; expiração libera automaticamente sem mudar vínculo; terceiros não veem extrato.

Todos os critérios exigem testes fictícios. Qualidade: >=80% de linhas e ramificações críticas, relatório versionável e métricas reais identificadas por feature no README; nenhuma métrica estimada nesta rodada.
