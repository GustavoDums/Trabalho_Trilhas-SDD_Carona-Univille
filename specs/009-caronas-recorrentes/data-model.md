# Data Model: Caronas recorrentes

**Status**: modelo da T035 conforme decisões homologadas na [spec](spec.md).

## Entidades e restrições canônicas

- `RecurringRideRule` tem driver, origin e destination com PROTECT. `weekdays` contém dias distintos de 0 (segunda) a 6 (domingo), `local_time` é horário civil e `timezone` é America/Sao_Paulo. Capacidade e veículo seguem as restrições da oferta. `active` controla geração futura e `created_at` registra a criação.
- `RecurringRideStop` possui rule, point e position. As posições são positivas e únicas por regra. Os pontos são únicos por regra e distintos dos extremos.
- `RecurringRideOccurrence` possui rule FK PROTECT, local_date e offer OneToOne PROTECT. A unicidade é por (rule, local_date) e o vínculo persiste após cancelamento. Cada oferta recebe cópia dos dados da regra e das paradas na publicação.

## Persistência

PostgreSQL e timestamps aware. Relações históricas não desaparecem por exclusão de usuário/oferta. Constraints locais complementam serviço; regras entre linhas exigem transações e locks. Migrações tratam registros legados sem sobrescrevê-los; validar plano e aplicação no PostgreSQL local e banco isolado de testes, sem reset destrutivo.

## Fronteiras

[plan.md](plan.md) delimita componentes e [tasks.md](tasks.md) distribui a implementação.

## Índice de campos canônicos

Os campos abaixo compõem a regra e os vínculos com as ofertas geradas.

- `RecurringRideRule.driver`
- `RecurringRideRule.origin`
- `RecurringRideRule.destination`
- `RecurringRideRule.weekdays`
- `RecurringRideRule.local_time`
- `RecurringRideRule.timezone`
- `RecurringRideRule.seats`
- `RecurringRideRule.vehicle_model`
- `RecurringRideRule.vehicle_color`
- `RecurringRideRule.vehicle_plate`
- `RecurringRideRule.active`
- `RecurringRideRule.created_at`
- `RecurringRideStop.rule`
- `RecurringRideStop.point`
- `RecurringRideStop.position`
- `RecurringRideOccurrence.rule`
- `RecurringRideOccurrence.local_date`
- `RecurringRideOccurrence.offer`
