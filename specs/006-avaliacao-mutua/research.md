# Research: Avaliação mútua pós-viagem

## Fontes e estado observado

[constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Estado atual: accounts/rides, reservas/cancelamento e pacote rides/services implementados. reviews criado nesta T002; recorrência e penalidades permanecem futuras.

## Decisões técnicas propostas

**Decisão**: manter Django, PostgreSQL, templates e pytest. **Motivo**: stack constitucional e ambiente existente. **Alternativas rejeitadas**: frameworks novos, SQLite para provar concorrência, filas e fornecedores externos.

**Decisão**: preservar capacidade original, histórico e projeções reconstruíveis, com idempotência transacional. **Motivo**: evitar perda de auditoria e efeitos duplicados. **Alternativa rejeitada**: contadores sem fonte de verdade e validação apenas na view.

## Decisões homologadas de produto

- **D006-01 — CONFIRMADA em 2026-11-23**: motorista titular ativo registra completed_at pelo relógio do servidor, após partida (>= departure_at); repetição preserva primeiro término; canceladas não concluem e legado NULL não habilita avaliação.
- **D006-02 — CONFIRMADA em 2026-11-23**: janela [completed_at, completed_at+48h] inclusiva; somente motorista↔passageiro confirmado, ambos ativos/habilitados, excluídos cancelados/no-show. Nota inteira 1..5, comentário opcional <=500 caracteres, uma avaliação por direção/contraparte, sem edição.

Usuário homologou as decisões e autorizou T001 seguida de T002 unificada; aprovação registrada em docs/prompts.md.

## Homologação D006-01/D006-02 — 2026-11-23

Usuário aprovou as recomendações e autorizou T001 documental seguida da T002 unificada (antigas T002/T003). D006-01 CONFIRMADA: motorista titular ativo registra explicitamente conclusão após a partida (instante >= departure_at), relógio do servidor aware em UTC. RideOffer.completed_at opcional representa o término informado, não previsão de chegada nem detecção automática. Repetição autorizada preserva a primeira data. Oferta CANCELADA não pode ser concluída; ofertas legadas recebem NULL e não permitem avaliação sem conclusão registrada.

D006-02 CONFIRMADA: janela fechada [completed_at, completed_at+48h], ambos extremos inclusivos; bloquear antes e depois. Somente motorista↔passageiro com reserva CONFIRMADA na mesma oferta, ambos habilitados/com vínculo ativo; excluir cancelados e no-show. Uma avaliação por oferta/avaliador/avaliado, nota inteira 1..5, comentário opcional até 500 caracteres, sem edição. Sem passageiro↔passageiro, autoavaliação, reputação, penalidade ou interface nesta rodada.

Referências a decisões pendentes nas seções anteriores representam o estado histórico e são substituídas por esta homologação. T002 abrange domínio/migrações/serviços/testes; formulários e rotas permanecem T004/T005.
