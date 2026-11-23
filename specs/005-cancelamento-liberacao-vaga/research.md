# Research: Cancelamento e liberação de vaga

## Fontes e estado observado

[constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Aplicação atual contém accounts e rides; reservas, reviews, cancelamento e recorrência ainda não existem. A Feature 003 é documental: rides/services.py ainda depende da conversão em pacote pela T001 daquela feature.

## Decisões técnicas propostas

**Decisão**: manter Django, PostgreSQL, templates e pytest. **Motivo**: stack constitucional e ambiente existente. **Alternativas rejeitadas**: frameworks novos, SQLite para provar concorrência, filas e fornecedores externos.

**Decisão**: preservar capacidade original, histórico e projeções reconstruíveis, com idempotência transacional. **Motivo**: evitar perda de auditoria e efeitos duplicados. **Alternativa rejeitada**: contadores sem fonte de verdade e validação apenas na view.

## Questões não resolvidas por pesquisa técnica

- **D005-01 — PENDENTE**: Confirmar 2h para passageiro, 4h para motorista, referência na saída da origem e borda inclusiva. São propostas, não critérios aprovados.
- **D005-02 — PENDENTE**: Definir se cancelamento tardio é aceito com sanção ou recusado, e comportamento após partida. T024 pede penalidade computada, cuja fórmula pertence à 008; aqui haverá somente evento auditável até a integração aprovada.

A instrução atual permite documentar partes seguras; o gate de implementação permanece pendente. Não alterar constitution/levantamento para simular consenso.
