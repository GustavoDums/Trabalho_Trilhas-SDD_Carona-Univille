# Feature Specification: Fila de Espera Automática com Repasse FIFO

**Feature** 011-fila-espera-fifo · **Data** 2026-11-23

## User Scenarios & Testing

### US1 — Entrar na fila e receber a primeira vaga (P1, T039)

O passageiro com vínculo ativo pode entrar na fila de uma carona lotada usando o trecho escolhido na busca. Um novo envio para a mesma carona conserva sua posição e seu trecho original. Ao processar uma vaga disponível, o sistema confirma a reserva imediatamente para a primeira pessoa elegível.

### US2 — Receber a vaga após um cancelamento (P2, T040)

O cancelamento chama o repasse e o passageiro acompanha sua posição no painel. A reserva confirmada gera aviso interno. Esse fluxo tem verificação própria na T040.

### Edge Cases

- Carona com vagas, encerrada ou já iniciada, trecho inválido e passageiro com reserva confirmada recusam o ingresso.
- No repasse, entradas de quem perdeu a elegibilidade ou já tem reserva confirmada são removidas. O próximo elegível mantém sua precedência sobre quem entrou depois.
- Dois repasses concorrentes para uma única vaga confirmam somente uma reserva. Uma falha inesperada reverte o repasse e mantém a fila.

## Requirements

### Functional Requirements

- **FR-001 / REQ-013, REQ-002, REQ-003**. Somente o passageiro elegível pode entrar na fila em seu próprio nome. A fila guarda apenas oferta, titular, trecho e ordem de ingresso.
- **FR-002 / REQ-013**. Uma vaga disponível é atribuída ao primeiro passageiro elegível no momento do repasse. A remoção da entrada e a reserva devem concluir juntas.
- **FR-003 / REQ-013, REQ-007**. A T040 conecta o cancelamento ao repasse, exibe posição ao titular e verifica a notificação.

### Key Entities

- Entrada da fila. Relaciona um passageiro, uma carona e seu trecho até o repasse ou a perda de elegibilidade.

## Success Criteria

### Measurable Outcomes

- **SC-001 / REQ-017**. Em oferta lotada, dois ingressos válidos reproduzem a ordem de chegada. Sessão indevida, duplicidade, trecho inválido e carona indisponível preservam fila e capacidade.
- **SC-002 / REQ-017**. Uma vaga libera exatamente uma confirmação imediata, respeitando FIFO; a próxima vaga atende a próxima entrada elegível. Concorrência, repetição, inelegibilidade e rollback têm resultados verificáveis.
- **SC-003 / REQ-017**. A T040 comprova o fluxo iniciado pelo cancelamento e a exposição privada da posição.

## Assumptions

O usuário autorizou preparar a Feature 011 e executar a T039. Adota-se o repasse imediato proposto no roadmap e reaplica-se a elegibilidade da reserva no momento do repasse. A T039 verifica o serviço diretamente após a liberação de capacidade. A T040 é responsável por chamá-lo no cancelamento.
