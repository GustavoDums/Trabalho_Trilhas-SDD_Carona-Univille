# Feature Specification: Notificações operacionais

**Feature**: 010-notificacoes-operacionais  
**Data**: 2026-11-23  
**Requisitos de origem**: [REQ-012 e REQ-017](../../docs/levantamento.md), com REQ-002 e REQ-003 transversais. [Roadmap](../../docs/roadmap-implementacao.md).

**Status**: bônus incluído no recorte de T037 e T038 por solicitação do usuário.

## User Scenarios & Testing

### US1 — Receber aviso de reserva ou cancelamento (P1)

Como participante de uma carona, quero que a confirmação ou o cancelamento gere um aviso interno para que eu possa consultar o que aconteceu.

1. Confirmar uma reserva registra um aviso para o passageiro titular e outro para o motorista.
2. Cancelar uma reserva registra um aviso para o passageiro titular e outro para o motorista, em qualquer classificação de cancelamento aceita.
3. Cancelar uma oferta registra um aviso para o motorista titular e um para cada passageiro cuja reserva confirmada foi cancelada nessa operação. Uma oferta sem reservas gera apenas o aviso do motorista.
4. Repetir um evento conserva os avisos existentes. Operação recusada, reserva sem vaga e transação revertida não produzem aviso.

### US2 — Consultar os próprios avisos (P2, T038)

O titular com vínculo ativo consulta os avisos, vê quantos estão pendentes e pode marcar um aviso próprio como lido. Essa entrega tem critérios próprios no checklist.

### Edge Cases

- Reserva cancelada antes do cancelamento da oferta fica fora dos destinatários da operação posterior.
- Uma nova reserva feita após cancelar outra gera um evento de confirmação distinto, mesmo para a mesma carona.
- Dois pedidos de cancelamento da mesma reserva geram um único conjunto de avisos.

## Requirements

### Functional Requirements

- **FR-001 / REQ-012**. Registrar avisos internos de confirmação de reserva, cancelamento de reserva e cancelamento de oferta nos destinatários definidos em US1.
- **FR-002 / REQ-012, REQ-017**. A gravação dos avisos acompanha a transição confirmada. Cada combinação de destinatário e evento gera no máximo um aviso, inclusive em reprocessamento ou concorrência.
- **FR-003 / REQ-002, REQ-003**. Cada aviso é privado ao titular. O registro contém somente a identificação do evento, do titular e os instantes necessários à entrega e leitura. Contato, placa e texto informado pelos participantes ficam fora do conteúdo dos avisos.
- **FR-004 / REQ-012, REQ-003**. A T038 entrega consulta, contador e leitura pelo titular com vínculo ativo.

### Key Entities

- **Aviso**. Relaciona um destinatário a uma confirmação de reserva ou a um evento de cancelamento e guarda o estado de leitura.
- **Evento de origem**. Confirmação identificada pela reserva criada ou cancelamento identificado pelo registro de auditoria.

## Success Criteria

### Measurable Outcomes

- **SC-001**. Os três eventos de US1 produzem exatamente um aviso por destinatário elegível ao evento e nenhum para terceiros.
- **SC-002**. Repetição e concorrência preservam a contagem e identidade dos avisos. Recusa e rollback não deixam eventos ou avisos parciais.
- **SC-003**. O conteúdo registrado não contém e-mail, placa nem texto livre. Na T038, tentativa de consultar ou marcar como lido aviso de terceiro é recusada.

## Assumptions

O canal é interno. A T037 entrega o registro dos avisos das transições acima. A solicitação da T038 inclui no escopo a consulta, o contador e a leitura. Lembretes de partida fazem parte do REQ-012 e precisam de política própria de horário e acionamento.
