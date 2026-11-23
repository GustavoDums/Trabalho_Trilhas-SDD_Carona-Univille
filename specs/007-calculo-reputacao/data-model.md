# Data Model: Cálculo matemático de reputação

**Status**: desenho proposto, não migração aplicada. Decisões da [spec](spec.md) bloqueiam campos dependentes.

## Entidades e restrições canônicas

ReputationProfile: user OneToOne PROTECT, score Decimal (precisão, default e intervalo pendentes D007-02), computed_at aware. Fonte: RideReview da 006 e posteriormente PenaltyRecord da 008. Não persistir contador sem definir unidade de janela. Ordenação determinística por referência temporal aprovada e PK. Profile é projeção reconstruível; não substituir histórico de avaliações.

## Persistência

PostgreSQL e timestamps aware. Relações históricas não desaparecem por exclusão de usuário/oferta. Constraints locais complementam serviço; regras entre linhas exigem transações e locks. Migrações tratam registros legados sem sobrescrevê-los; validar plano e aplicação no PostgreSQL local e banco isolado de testes, sem reset destrutivo.

## Fronteiras

Entidades/campos futuros, salvo os explicitamente existentes. [plan.md](plan.md) delimita componentes e [tasks.md](tasks.md) distribui implementação. Fechar decisões e atualizar contrato antes de criar campos condicionais, preservando IDs.

## Índice de campos canônicos

Os campos abaixo são os nomes exatos referidos pelas tarefas; tipos e restrições estão em Entidades e restrições canônicas. Campos condicionais mantêm bloqueio de produto.

- `ReputationProfile.user`
- `ReputationProfile.score`
- `ReputationProfile.computed_at`
