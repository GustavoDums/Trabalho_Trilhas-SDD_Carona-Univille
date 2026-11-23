# Data Model: Penalidades por cancelamento tardio e no-show

**Status**: desenho da T002 conforme decisões homologadas na [spec](spec.md).

## Entidades e restrições canônicas

- `PenaltyRecord.subject`, `actor`, `offer`, `booking` e `cancellation` preservam referências com PROTECT. `source_key` é uma chave opaca única da origem.
- Cancelamento tardio usa origem de sistema (actor ausente), evento CancellationRecord tardio único, mesmo titular, oferta, reserva e instante do evento. A reserva pode estar ausente para cancelamento de oferta. Delta decimal de −0,20.
- No-show usa contraparte como actor, reserva e instante de registro da declaração (`reported_at`). Um usuário pode ter apenas um no-show por oferta. Delta decimal de −0,50 e nota automática 1 derivada do tipo. A integração da nota com a janela de reputação pertence à T003.
- `ConductProfile.user` é OneToOne com PROTECT. `suspended_until` é opcional, com fuso. A projeção considera 3 no-shows distintos na janela inclusiva de 30 dias. A suspensão expira no instante do fim dos 14 dias. A gravação da projeção pertence ao serviço.

## Persistência

PostgreSQL e timestamps aware. Relações históricas não desaparecem por exclusão de usuário/oferta. Constraints locais complementam serviço; regras entre linhas exigem transações e locks. Migrações tratam registros legados sem sobrescrevê-los; validar plano e aplicação no PostgreSQL local e banco isolado de testes, sem reset destrutivo.

## Fronteiras

O [plano](plan.md) delimita os componentes e as [tarefas](tasks.md) distribuem a implementação.

## Índice de campos canônicos

Os campos abaixo são os nomes exatos referidos pelas tarefas; tipos e restrições estão em Entidades e restrições canônicas.

- `PenaltyRecord.subject`
- `PenaltyRecord.actor`
- `PenaltyRecord.offer`
- `PenaltyRecord.booking`
- `PenaltyRecord.source_key`
- `PenaltyRecord.kind`
- `PenaltyRecord.occurred_at`
- `PenaltyRecord.delta`
- `PenaltyRecord.cancellation`
- `PenaltyRecord.reported_at`
- `ConductProfile.user`
- `ConductProfile.suspended_until`
