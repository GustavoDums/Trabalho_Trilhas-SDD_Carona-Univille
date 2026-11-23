# Data Model: Reserva de vagas sem overbooking

**Status**: desenho proposto, não migração aplicada. Decisões da [spec](spec.md) bloqueiam campos dependentes.

## Entidades e restrições canônicas

RideBooking: id; offer FK PROTECT; passenger FK PROTECT; status CONFIRMADA/CANCELADA condicionado a D004-01; created_at e updated_at aware. UniqueConstraint condicional (offer, passenger) quando CONFIRMADA. Autorreserva exige validação cruzada no serviço. RideOffer.seats continua capacidade; available_seats é projeção calculada, nunca contador persistido. Embarque/desembarque dependem de D004-02.

## Persistência

PostgreSQL e timestamps aware. Relações históricas não desaparecem por exclusão de usuário/oferta. Constraints locais complementam serviço; regras entre linhas exigem transações e locks. Migrações tratam registros legados sem sobrescrevê-los; validar plano e aplicação no PostgreSQL local e banco isolado de testes, sem reset destrutivo.

## Fronteiras

Entidades/campos futuros, salvo os explicitamente existentes. [plan.md](plan.md) delimita componentes e [tasks.md](tasks.md) distribui implementação. Fechar decisões e atualizar contrato antes de criar campos condicionais, preservando IDs.

## Índice de campos canônicos

Os campos abaixo são os nomes exatos referidos pelas tarefas; tipos e restrições estão em Entidades e restrições canônicas. Campos condicionais mantêm bloqueio de produto.

- `RideBooking.offer`
- `RideBooking.passenger`
- `RideBooking.status`
- `RideBooking.created_at`
- `RideBooking.updated_at`
- `RideOffer.seats`
