# Data Model: Caronas recorrentes

**Status**: desenho proposto, não migração aplicada. Decisões da [spec](spec.md) bloqueiam campos dependentes.

## Entidades e restrições canônicas

RecurringRideRule: driver FK PROTECT; origin/destination FK PROTECT; weekdays conjunto não vazio de dias válidos; local_time horário local; timezone conforme D009-01; seats e veículo com restrições herdadas da oferta; active boolean; created_at aware. Paradas ordenadas em entidade própria da regra conforme Waypoint. RecurringRideOccurrence: rule FK PROTECT, local_date date, offer OneToOne PROTECT; UniqueConstraint (rule, local_date). Manter vínculo inclusive após cancelamento; não inferir chave apenas por departure_at.

## Persistência

PostgreSQL e timestamps aware. Relações históricas não desaparecem por exclusão de usuário/oferta. Constraints locais complementam serviço; regras entre linhas exigem transações e locks. Migrações tratam registros legados sem sobrescrevê-los; validar plano e aplicação no PostgreSQL local e banco isolado de testes, sem reset destrutivo.

## Fronteiras

Entidades/campos futuros, salvo os explicitamente existentes. [plan.md](plan.md) delimita componentes e [tasks.md](tasks.md) distribui implementação. Fechar decisões e atualizar contrato antes de criar campos condicionais, preservando IDs.

## Índice de campos canônicos

Os campos abaixo são os nomes exatos referidos pelas tarefas; tipos e restrições estão em Entidades e restrições canônicas. Campos condicionais mantêm bloqueio de produto.

- `RecurringRideRule.driver`
- `RecurringRideRule.origin`
- `RecurringRideRule.destination`
- `RecurringRideRule.weekdays`
- `RecurringRideRule.local_time`
- `RecurringRideRule.timezone`
- `RecurringRideRule.seats`
- `RecurringRideRule.active`
- `RecurringRideRule.created_at`
- `RecurringRideOccurrence.rule`
- `RecurringRideOccurrence.local_date`
- `RecurringRideOccurrence.offer`
