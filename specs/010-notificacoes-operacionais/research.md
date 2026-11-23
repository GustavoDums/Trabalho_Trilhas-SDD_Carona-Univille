# Research: Notificações operacionais

- **Canal interno.** Escolhido por compatibilidade com o sino previsto na T038 e por não exigir contato, transporte ou configuração externa. E-mail simulado foi avaliado como alternativa do roadmap.
- **Destinatários.** Confirmação e cancelamento individual registram aviso para passageiro e motorista. O lote de cancelamento de oferta inclui motorista uma vez e passageiros das reservas efetivamente canceladas. Usar a seleção já protegida pelo lock da oferta evita incluir reservas antigas ou chamar uma operação por passageiro com a mesma origem.
- **Transação e repetição.** Chamadas explícitas após a criação da reserva ou evento de cancelamento preservam o fluxo existente. Um aviso obrigatório que falha reverte a transição. Constraints de origem e unicidade substituem deduplicação por texto ou horário. A consulta de contas mantém a ordem crescente de PK e locks compatíveis com as FKs de avisos concorrentes.
- **Lembretes.** O levantamento menciona lembretes no REQ-012, mas a T037 cobre confirmação e cancelamento. O horário e o acionamento de lembretes permanecem para decisão em rodada própria.
