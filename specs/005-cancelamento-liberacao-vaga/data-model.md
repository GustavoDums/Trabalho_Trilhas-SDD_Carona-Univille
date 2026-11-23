# Data Model: Cancelamento e liberação de vaga

**Status**: desenho proposto, não migração aplicada. Decisões da [spec](spec.md) bloqueiam campos dependentes.

## Entidades e restrições canônicas

RideOffer.status: ABERTA/CANCELADA, default ABERTA com migração dos registros atuais; cancelled_at aware nullable. RideBooking.cancelled_at aware nullable. CancellationRecord: actor FK PROTECT, offer FK PROTECT, booking FK PROTECT nullable (alvo oferta quando ausente), occurred_at aware, classification conforme política aprovada. Um evento por transição efetiva; repetição não cria evento novo. Estados e registros preservam autoria e histórico; capacity permanece RideOffer.seats.

## Persistência

PostgreSQL e timestamps aware. Relações históricas não desaparecem por exclusão de usuário/oferta. Constraints locais complementam serviço; regras entre linhas exigem transações e locks. Migrações tratam registros legados sem sobrescrevê-los; validar plano e aplicação no PostgreSQL local e banco isolado de testes, sem reset destrutivo.

## Fronteiras

Entidades/campos futuros, salvo os explicitamente existentes. [plan.md](plan.md) delimita componentes e [tasks.md](tasks.md) distribui implementação. Fechar decisões e atualizar contrato antes de criar campos condicionais, preservando IDs.

## Índice de campos canônicos

Os campos abaixo são os nomes exatos referidos pelas tarefas; tipos e restrições estão em Entidades e restrições canônicas. Campos condicionais mantêm bloqueio de produto.

- `RideOffer.status`
- `RideOffer.cancelled_at`
- `RideBooking.cancelled_at`
- `CancellationRecord.actor`
- `CancellationRecord.offer`
- `CancellationRecord.booking`
- `CancellationRecord.occurred_at`
- `CancellationRecord.classification`
