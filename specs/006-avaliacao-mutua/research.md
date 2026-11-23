# Research: Avaliação mútua pós-viagem

## Fontes e estado observado

[constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Aplicação atual contém accounts e rides; reservas, reviews, cancelamento e recorrência ainda não existem. A Feature 003 é documental: rides/services.py ainda depende da conversão em pacote pela T001 daquela feature.

## Decisões técnicas propostas

**Decisão**: manter Django, PostgreSQL, templates e pytest. **Motivo**: stack constitucional e ambiente existente. **Alternativas rejeitadas**: frameworks novos, SQLite para provar concorrência, filas e fornecedores externos.

**Decisão**: preservar capacidade original, histórico e projeções reconstruíveis, com idempotência transacional. **Motivo**: evitar perda de auditoria e efeitos duplicados. **Alternativa rejeitada**: contadores sem fonte de verdade e validação apenas na view.

## Questões não resolvidas por pesquisa técnica

- **D006-01 — PENDENTE**: Definir término verificável da viagem: oferta contém somente departure_at. Levantamento fala em conclusão do horário previsto, mas não há chegada prevista. Não equiparar partida a término. Escolher referência e responsável pelo registro antes de alterar dados.
- **D006-02 — PENDENTE**: Confirmar janela proposta de 48h, bordas, elegibilidade de cancelados/no-show e pares permitidos (proposta: motorista↔passageiro, nunca passageiro↔passageiro); fixar limite do comentário e edição/revisão.

A instrução atual permite documentar partes seguras; o gate de implementação permanece pendente. Não alterar constitution/levantamento para simular consenso.
