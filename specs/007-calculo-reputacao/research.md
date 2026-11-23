# Research: Cálculo matemático de reputação

## Fontes e estado observado

[constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Aplicação atual contém accounts e rides; reservas, reviews, cancelamento e recorrência ainda não existem. A Feature 003 é documental: rides/services.py ainda depende da conversão em pacote pela T001 daquela feature.

## Decisões técnicas propostas

**Decisão**: manter Django, PostgreSQL, templates e pytest. **Motivo**: stack constitucional e ambiente existente. **Alternativas rejeitadas**: frameworks novos, SQLite para provar concorrência, filas e fornecedores externos.

**Decisão**: preservar capacidade original, histórico e projeções reconstruíveis, com idempotência transacional. **Motivo**: evitar perda de auditoria e efeitos duplicados. **Alternativa rejeitada**: contadores sem fonte de verdade e validação apenas na view.

## Questões não resolvidas por pesquisa técnica

- **D007-01 — PENDENTE**: Resolver média simples versus ponderada (pesos ausentes), janela de 30 dias versus 20 caronas versus 20 avaliações; definir agregação por viagem com múltiplos passageiros e ordenação de desempate.
- **D007-02 — PENDENTE**: Homologar nota inicial 5.00, limites da pontuação, precisão/arredondamento e os exemplos numéricos do roadmap. Exemplo 4.00 pressupõe exatamente três notas 5 anteriores, não qualquer usuário com média 5.

A instrução atual permite documentar partes seguras; o gate de implementação permanece pendente. Não alterar constitution/levantamento para simular consenso.
