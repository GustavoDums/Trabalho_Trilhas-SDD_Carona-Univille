# Feature Specification: Reserva de vagas sem overbooking

**Feature**: 004-reserva-sem-overbooking | **Created**: 2026-11-22
**Status**: rascunho preparado; decisões abaixo bloqueiam tarefas afetadas. Nenhuma implementação realizada.
**Input**: REQ-006 e solicitação de preparação documental.

## Contexto e rastreabilidade

Fontes: [constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Formato de referência: [Feature 003](../003-busca-rota-horario/spec.md).
Requisito principal REQ-006; transversais REQ-002, REQ-003, REQ-014–REQ-019. Correspondências oficiais em [tasks.md](tasks.md).
Propostas do roadmap não equivalem a decisões homologadas. Estes artefatos permitem revisar o escopo, sem decidir produto por suposição.

## Clarifications — decisões pendentes

- **D004-01 — PENDENTE**: Confirmar reserva instantânea versus aceite do motorista. CONFIRMADA/CANCELADA no roadmap pressupõe fluxo instantâneo; se houver aceite, rever estados, ocupação e critérios antes da implementação.
- **D004-02 — PENDENTE**: Confirmar coleta, finalidade e visibilidade do WhatsApp: não existe telefone na conta. E-mail nunca será divulgado. Definir também seleção/persistência de embarque e desembarque; não introduzir reutilização de vaga por trecho.

## User Scenarios & Testing

### US1 — Reservar sem exceder a capacidade (P1)

Passageiro ativo solicita uma vaga em oferta futura elegível; o servidor valida e confirma somente se houver disponibilidade.

**Teste independente**: SC-001: duas conexões PostgreSQL independentes disputam simultaneamente uma última vaga; exatamente uma confirma, outra recebe esgotamento, contagem confirmada=1 e disponibilidade=0 (após D004-01).

### US2 — Consultar minhas reservas com privacidade (P2)

Participante consulta suas reservas e dados autorizados da contraparte; terceiros não obtêm acesso por troca de ID.

**Teste independente**: SC-004: busca e consulta própria refletem disponibilidade atual sem N+1; GET não cria reserva.

## Functional Requirements

- FR-001 / REQ-006: quantidade de reservas CONFIRMADA nunca supera RideOffer.seats, inclusive sob concorrência; capacidade original permanece inalterada.
- FR-002 / REQ-002, REQ-006: impedir autorreserva, passageiro inelegível, oferta passada/fechada, duplicidade ativa e motorista sem vínculo ativo; revalidar no serviço.
- FR-003 / REQ-003: nome completo e placa somente à contraparte confirmada, sem e-mail em HTML, contexto público ou resposta de erro; contato depende de D004-02.
- FR-004 / REQ-006: disponibilidade exibida é capacidade menos reservas confirmadas; a confirmação sempre reconsulta o banco, sem confiar no cartão.
- FR-005 / REQ-006: uma solicitação rejeitada não grava reserva nem reduz capacidade. Fluxo de sucesso e mensagens finais dependem de D004-01.

## Fluxo e exceções

1. Identificar sessão e revalidar papel/vínculo no servidor.
2. Validar alvo, estado e política homologada antes de transição.
3. Executar operação completa ou preservar domínio em caso de recusa/rollback.
4. Apresentar resultado ao titular, sem dados privados de terceiros.
5. Verificar repetição e concorrência pelos critérios abaixo; dados do navegador nunca autorizam a ação.

## Dependencies & Scope

Features 001/002 implementadas; Feature 003/T001 (pacote de serviços) antes de criar módulos; Feature 003/T002–T004 antes da integração de disponibilidade na busca.

Não inclui bônus 010/011, staging, commits ou integrações externas. Critérios dependentes de decisão são condicionais até homologação. REQ-020 e T041–T045 orientam entrega geral, sem conclusão nesta preparação.

## Success Criteria

- SC-001: duas conexões PostgreSQL independentes disputam simultaneamente uma última vaga; exatamente uma confirma, outra recebe esgotamento, contagem confirmada=1 e disponibilidade=0 (após D004-01).
- SC-002: autorreserva, duplicidade e acesso indevido são recusados sem alteração de estado; rollback preserva a capacidade.
- SC-003: participante confirmado vê somente os dados liberados; estranho, visitante, pendente e participante cancelado não veem contato/placa; e-mail ausente em todos os casos.
- SC-004: busca e consulta própria refletem disponibilidade atual sem N+1; GET não cria reserva.

Todos os critérios exigem testes fictícios. Qualidade: >=80% de linhas e ramificações críticas, relatório versionável e métricas reais identificadas por feature no README; nenhuma métrica estimada nesta rodada.
