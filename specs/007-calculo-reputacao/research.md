# Research: Cálculo matemático de reputação

## Fontes e estado observado

[constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Aplicação atual contém accounts/rides/reviews, com reservas, avaliações, busca e cancelamento implementados; recorrência e penalidades futuras.

## Decisões técnicas propostas

**Decisão**: manter Django, PostgreSQL, templates e pytest. **Motivo**: stack constitucional e ambiente existente. **Alternativas rejeitadas**: frameworks novos, SQLite para provar concorrência, filas e fornecedores externos.

**Decisão**: preservar capacidade original, histórico e projeções reconstruíveis, com idempotência transacional. **Motivo**: evitar perda de auditoria e efeitos duplicados. **Alternativa rejeitada**: contadores sem fonte de verdade e validação apenas na view.

## Decisões de produto homologadas

- **D007-01 — CONFIRMADA em 2026-11-23**: últimas 20 avaliações recebidas, pesos iguais, sem corte de 30 dias ou agrupamento por carona; created_at/id decrescentes, até instante de referência inclusivo.
- **D007-02 — CONFIRMADA em 2026-11-23**: novato 5.00 sem nota virtual; Decimal, duas casas, ROUND_HALF_UP no final; armazenamento 0.00..5.00; exemplos 4.60 e 4.00 conforme fixtures; penalidades futuras.

D007-01/D007-02 aprovadas pelo usuário; recorte T001/T002 unificada autorizado.

## Homologação e recorte — 2026-11-23

Usuário aprovou D007-01/D007-02 e autorizou T001 seguida da T002 unificada (antigas T002/T003, roadmap T030). D007-01: média aritmética simples das últimas 20 avaliações recebidas, cada avaliação com o mesmo peso mesmo na mesma viagem; sem janela de 30 dias. Selecionar created_at <= instante de referência e ordenar created_at DESC, id DESC, limit 20. A 21ª expulsa a mais antiga, não agrupar por oferta.

D007-02: novato 5.00 apenas quando conjunto vazio; base não entra como nota virtual. Calcular com Decimal e arredondar somente resultado final para duas casas com ROUND_HALF_UP, independente do contexto Decimal do chamador. [5,5,4,5,4]=4.60; [5,5,5,1]=4.00 (exatamente três notas 5 anteriores). Profile aceita 0.00..5.00; cálculo de notas 1..5 não gera zero, limite inferior prepara futura integração de penalidades da 008, não implementada agora.

ReputationProfile é projeção reconstruível sem substituir RideReview. Rebuild é serviço interno explícito, não endpoint; signals/atualização automática e exibição pública ficam T031. Referências anteriores a pendências/propostas divergentes são históricas e substituídas por esta homologação. Nenhuma aprovação de pesos, expiração por dias ou penalidades foi inferida.
