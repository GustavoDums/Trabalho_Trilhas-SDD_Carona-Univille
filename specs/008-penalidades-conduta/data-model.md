# Data Model: Penalidades por cancelamento tardio e no-show

**Status**: desenho proposto, não migração aplicada. Decisões da [spec](spec.md) bloqueiam campos dependentes.

## Entidades e restrições canônicas

PenaltyRecord: subject FK PROTECT, actor FK PROTECT ou origem de sistema explicitamente homologada, offer FK PROTECT, booking FK PROTECT nullable, source_key única, kind CANCELAMENTO_TARDIO/NO_SHOW, occurred_at aware, delta Decimal conforme política aprovada. Suspensão: suspended_until aware nullable em entidade de conduta separada (proposta ConductProfile OneToOne user); definir campos definitivos após D008-02. Fonte de cancelamento liga CancellationRecord para deduplicação. Nunca armazenar alegação como fato comprovado sem política.

## Persistência

PostgreSQL e timestamps aware. Relações históricas não desaparecem por exclusão de usuário/oferta. Constraints locais complementam serviço; regras entre linhas exigem transações e locks. Migrações tratam registros legados sem sobrescrevê-los; validar plano e aplicação no PostgreSQL local e banco isolado de testes, sem reset destrutivo.

## Fronteiras

Entidades/campos futuros, salvo os explicitamente existentes. [plan.md](plan.md) delimita componentes e [tasks.md](tasks.md) distribui implementação. Fechar decisões e atualizar contrato antes de criar campos condicionais, preservando IDs.

## Índice de campos canônicos

Os campos abaixo são os nomes exatos referidos pelas tarefas; tipos e restrições estão em Entidades e restrições canônicas. Campos condicionais mantêm bloqueio de produto.

- `PenaltyRecord.subject`
- `PenaltyRecord.actor`
- `PenaltyRecord.offer`
- `PenaltyRecord.booking`
- `PenaltyRecord.source_key`
- `PenaltyRecord.kind`
- `PenaltyRecord.occurred_at`
- `PenaltyRecord.delta`
- `ConductProfile.suspended_until`
