# Feature Specification: Reserva de vagas sem overbooking

**Feature**: 004-reserva-sem-overbooking | **Created**: 2026-11-22
**Status**: decisões/modelo T001/T002, serviço T003, disponibilidade T006 e apresentação T004 concluídos; T005 de rotas/fluxo HTTP também concluída; somente T007 aberta. [Fluxo HTTP](evidence-t023.md). [Apresentação](evidence-t022.md). [Disponibilidade](evidence-t006.md). [Modelo](evidence-t020.md) e [concorrência](evidence-t021.md).
**Input**: REQ-006 e solicitação de preparação documental.

## Contexto e rastreabilidade

Fontes: [constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro histórico de preparação](../../docs/preparacao-features-004-009.md). Formato de referência: [Feature 003](../003-busca-rota-horario/spec.md).
Requisito principal REQ-006; transversais REQ-002, REQ-003, REQ-014–REQ-019. Correspondências oficiais em [tasks.md](tasks.md).
D004-01/D004-02 confirmadas pelo usuário após recomendação explícita; registro em docs/prompts.md. Outras propostas do roadmap não se tornam decisões por essa confirmação.

## Clarifications — decisões confirmadas

- **D004-01 — CONFIRMADA em 2026-11-22**: reserva instantânea, sem aceite do motorista; estados CONFIRMADA/CANCELADA. Uma confirmação ocupa uma vaga durante toda a oferta, sem reutilização por trecho.
- **D004-02 — CONFIRMADA em 2026-11-22**: persistir boarding_point/alighting_point do catálogo no registro de reserva, respeitando ordem do itinerário e pontos distintos. WhatsApp adiado; não coletar telefone nesta tarefa. E-mail nunca divulgado. Nas tarefas de apresentação, nome completo/placa somente à contraparte confirmada; eventual adoção futura de WhatsApp exige definição própria.

## User Scenarios & Testing

### US1 — Reservar sem exceder a capacidade (P1)

Passageiro ativo solicita uma vaga em oferta futura elegível; o servidor valida e confirma somente se houver disponibilidade.

**Teste independente**: SC-001: duas conexões PostgreSQL independentes disputam simultaneamente uma última vaga; exatamente uma confirma, outra recebe esgotamento, contagem confirmada=1 e disponibilidade=0 (confirmação instantânea homologada).

### US2 — Consultar minhas reservas com privacidade (P2)

Participante consulta suas reservas e dados autorizados da contraparte; terceiros não obtêm acesso por troca de ID.

**Teste independente**: SC-004: busca e consulta própria refletem disponibilidade atual sem N+1; GET não cria reserva.

## Functional Requirements

- FR-001 / REQ-006: quantidade de reservas CONFIRMADA nunca supera RideOffer.seats, inclusive sob concorrência; capacidade original permanece inalterada.
- FR-002 / REQ-002, REQ-006: impedir autorreserva, passageiro inelegível, oferta passada/fechada, duplicidade ativa e motorista sem vínculo ativo; revalidar no serviço.
- FR-003 / REQ-003: nome completo e placa somente à contraparte confirmada, sem e-mail em HTML, contexto público ou resposta de erro; WhatsApp adiado conforme D004-02, sem coleta de telefone.
- FR-004 / REQ-006: disponibilidade exibida é capacidade menos reservas confirmadas; a confirmação sempre reconsulta o banco, sem confiar no cartão. Preservar filtros/ordenação; ofertas compatíveis esgotadas permanecem visíveis com saldo zero e indicação de esgotamento.
- FR-005 / REQ-006: uma solicitação rejeitada não grava reserva nem reduz capacidade. Confirmação é instantânea conforme D004-01; interface pertence às tarefas posteriores.

- FR-006 / REQ-005, REQ-006: persistir embarque/desembarque do catálogo na reserva; devem constar no itinerário da oferta, em ordem estrita anterior/posterior e sem ambiguidade. Pontos não permitem reutilização de vaga entre trechos.

## Fluxo e exceções

1. Identificar sessão e revalidar papel/vínculo no servidor.
2. Validar alvo, estado e política homologada antes de transição.
3. Executar operação completa ou preservar domínio em caso de recusa/rollback.
4. Apresentar resultado ao titular, sem dados privados de terceiros.
5. Verificar repetição e concorrência pelos critérios abaixo; dados do navegador nunca autorizam a ação.

## Dependencies & Scope

Features 001/002 implementadas; Feature 003/T001 (pacote de serviços) antes de criar módulos; Feature 003/T002–T004 antes da integração de disponibilidade na busca.

Não inclui bônus 010/011, staging, commits ou integrações externas. D004-01/D004-02 homologadas; não há coleta de WhatsApp nesta feature enquanto não houver nova decisão explícita. REQ-020 e T041–T045 orientam entrega geral, sem conclusão nesta preparação.

## Success Criteria

- SC-001: duas conexões PostgreSQL independentes disputam simultaneamente uma última vaga; exatamente uma confirma, outra recebe esgotamento, contagem confirmada=1 e disponibilidade=0 (confirmação instantânea homologada).
- SC-002: autorreserva, duplicidade e acesso indevido são recusados sem alteração de estado; rollback preserva a capacidade.
- SC-003: participante confirmado vê somente os dados liberados; estranho, visitante, pendente e participante cancelado não veem contato/placa; e-mail ausente em todos os casos.
- SC-004: busca e consulta própria refletem disponibilidade atual sem N+1; GET não cria reserva.

- SC-005: modelo rejeita autorreserva, passageiro inelegível na criação, trecho igual/invertido/ausente/ambíguo e duplicidade CONFIRMADA; reserva CANCELADA preserva histórico e permite nova CONFIRMADA; constraints SQL de status, pontos distintos e unicidade ativa verificadas no PostgreSQL.

Todos os critérios exigem testes fictícios. Qualidade: >=80% de linhas e ramificações críticas, relatório versionável e métricas reais identificadas por feature no README; nenhuma métrica estimada nesta rodada.
