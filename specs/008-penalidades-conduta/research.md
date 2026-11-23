# Research: Penalidades por cancelamento tardio e no-show

## Fontes e estado observado

[constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Aplicação atual contém accounts e rides; reservas, reviews, cancelamento e recorrência ainda não existem. A Feature 003 é documental: rides/services.py ainda depende da conversão em pacote pela T001 daquela feature.

## Decisões técnicas propostas

**Decisão**: manter Django, PostgreSQL, templates e pytest. **Motivo**: stack constitucional e ambiente existente. **Alternativas rejeitadas**: frameworks novos, SQLite para provar concorrência, filas e fornecedores externos.

**Decisão**: preservar capacidade original, histórico e projeções reconstruíveis, com idempotência transacional. **Motivo**: evitar perda de auditoria e efeitos duplicados. **Alternativa rejeitada**: contadores sem fonte de verdade e validação apenas na view.

## Questões não resolvidas por pesquisa técnica

- **D008-01 — PENDENTE**: Resolver suspensão de 7 dias (roadmap) versus 14 dias (levantamento), limiar proposto de 3 faltas em 30 dias, tolerância proposta de 10min e denúncia até 2h; definir referência para paradas sem ETA.
- **D008-02 — PENDENTE**: Homologar deduções -0.20/-0.50, nota automática 1 e sua combinação sem dupla punição acidental; definir autor autorizado, evidência, contestação, limites da nota e ações bloqueadas durante suspensão.

A instrução atual permite documentar partes seguras; o gate de implementação permanece pendente. Não alterar constitution/levantamento para simular consenso.
