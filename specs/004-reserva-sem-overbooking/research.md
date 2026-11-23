# Research: Reserva de vagas sem overbooking

## Fontes e estado observado

[constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Aplicação atual contém accounts e rides; reservas, reviews, cancelamento e recorrência ainda não existem. A Feature 003 é documental: rides/services.py ainda depende da conversão em pacote pela T001 daquela feature.

## Decisões técnicas propostas

**Decisão**: manter Django, PostgreSQL, templates e pytest. **Motivo**: stack constitucional e ambiente existente. **Alternativas rejeitadas**: frameworks novos, SQLite para provar concorrência, filas e fornecedores externos.

**Decisão**: preservar capacidade original, histórico e projeções reconstruíveis, com idempotência transacional. **Motivo**: evitar perda de auditoria e efeitos duplicados. **Alternativa rejeitada**: contadores sem fonte de verdade e validação apenas na view.

## Questões não resolvidas por pesquisa técnica

- **D004-01 — PENDENTE**: Confirmar reserva instantânea versus aceite do motorista. CONFIRMADA/CANCELADA no roadmap pressupõe fluxo instantâneo; se houver aceite, rever estados, ocupação e critérios antes da implementação.
- **D004-02 — PENDENTE**: Confirmar coleta, finalidade e visibilidade do WhatsApp: não existe telefone na conta. E-mail nunca será divulgado. Definir também seleção/persistência de embarque e desembarque; não introduzir reutilização de vaga por trecho.

A instrução atual permite documentar partes seguras; o gate de implementação permanece pendente. Não alterar constitution/levantamento para simular consenso.
