# Data Model: Avaliação mútua pós-viagem

**Status**: desenho proposto, não migração aplicada. Decisões da [spec](spec.md) bloqueiam campos dependentes.

## Entidades e restrições canônicas

RideReview: offer FK PROTECT, reviewer FK PROTECT, reviewed_user FK PROTECT, rating inteiro 1..5, comment opcional (max_length pendente D006-02), created_at aware. UniqueConstraint (offer, reviewer, reviewed_user), CheckConstraint rating e reviewer!=reviewed_user. Participação é validada no serviço. Referência de término e eventual campo/entidade adicional dependem de D006-01; não inventar completed_at nem arrival_at como já existentes.

## Persistência

PostgreSQL e timestamps aware. Relações históricas não desaparecem por exclusão de usuário/oferta. Constraints locais complementam serviço; regras entre linhas exigem transações e locks. Migrações tratam registros legados sem sobrescrevê-los; validar plano e aplicação no PostgreSQL local e banco isolado de testes, sem reset destrutivo.

## Fronteiras

Entidades/campos futuros, salvo os explicitamente existentes. [plan.md](plan.md) delimita componentes e [tasks.md](tasks.md) distribui implementação. Fechar decisões e atualizar contrato antes de criar campos condicionais, preservando IDs.

## Índice de campos canônicos

Os campos abaixo são os nomes exatos referidos pelas tarefas; tipos e restrições estão em Entidades e restrições canônicas. Campos condicionais mantêm bloqueio de produto.

- `RideReview.offer`
- `RideReview.reviewer`
- `RideReview.reviewed_user`
- `RideReview.rating`
- `RideReview.comment`
- `RideReview.created_at`
