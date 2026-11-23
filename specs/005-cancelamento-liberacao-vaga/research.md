# Research: Cancelamento e liberação de vaga

## Fontes e estado observado

[constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Aplicação atual contém accounts/rides e reservas/busca da Feature 004; pacote de serviços existe. Cancelamento de reserva implementado nas T002/T003; cancelamento de oferta implementado na T004 ([evidência](evidence-t025.md)); HTTP futuro. Qualidade final das features anteriores permanece em suas tarefas próprias.

## Decisões técnicas propostas

**Decisão**: manter Django, PostgreSQL, templates e pytest. **Motivo**: stack constitucional e ambiente existente. **Alternativas rejeitadas**: frameworks novos, SQLite para provar concorrência, filas e fornecedores externos.

**Decisão**: preservar capacidade original, histórico e projeções reconstruíveis, com idempotência transacional. **Motivo**: evitar perda de auditoria e efeitos duplicados. **Alternativa rejeitada**: contadores sem fonte de verdade e validação apenas na view.

## Decisões de produto confirmadas

- **D005-01 — CONFIRMADA em 2026-11-22**: passageiro 2h, motorista 4h, referência na saída da origem e borda inclusiva (antecedência >= prazo). Comparar instantes aware em UTC.
- **D005-02 — CONFIRMADA em 2026-11-22**: tardio antes da partida é aceito com evento auditável, sem dedução numérica nesta feature; na partida ou depois, recusar preservando estado. Penalidades futuras pertencem à 008.

Usuário confirmou regras e inclusão da T003 para liberação de vaga, após divergência de escopo. T001 documental atendida; sem cancelamento de oferta/HTTP ou penalidade numérica. Registro da confirmação em docs/prompts.md.
