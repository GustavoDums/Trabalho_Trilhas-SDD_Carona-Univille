# Research: Reserva de vagas sem overbooking

## Fontes e estado observado

[constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro histórico de preparação](../../docs/preparacao-features-004-009.md). Aplicação atual contém accounts e rides e, após T020, o modelo RideBooking. Serviço transacional de reserva T003 implementado/verificado; HTTP, reviews, cancelamento e recorrência permanecem futuros. Feature 003/T001–T004 implementadas: pacote de serviços e busca disponíveis; qualidade final daquela feature permanece fora deste recorte.

## Decisões técnicas propostas

**Decisão**: manter Django, PostgreSQL, templates e pytest. **Motivo**: stack constitucional e ambiente existente. **Alternativas rejeitadas**: frameworks novos, SQLite para provar concorrência, filas e fornecedores externos.

**Decisão**: preservar capacidade original, histórico e projeções reconstruíveis, com idempotência transacional. **Motivo**: evitar perda de auditoria e efeitos duplicados. **Alternativa rejeitada**: contadores sem fonte de verdade e validação apenas na view.

## Decisões de produto confirmadas

- **D004-01 — CONFIRMADA em 2026-11-22**: reserva instantânea, sem aceite do motorista; estados CONFIRMADA/CANCELADA. Uma confirmação ocupa uma vaga durante toda a oferta, sem reutilização por trecho.
- **D004-02 — CONFIRMADA em 2026-11-22**: persistir boarding_point/alighting_point do catálogo no registro de reserva, respeitando ordem do itinerário e pontos distintos. WhatsApp adiado; não coletar telefone nesta tarefa. E-mail nunca divulgado. Nas tarefas de apresentação, nome completo/placa somente à contraparte confirmada; eventual adoção futura de WhatsApp exige definição própria.

Confirmação explícita do usuário registrada em docs/prompts.md; gate de decisões da T001 atendido. Após T020/T002, o usuário confirmou T021/T003 nesta rodada e autorizou integração T006 para a próxima. Serviço concorrente concluído conforme evidence-t021.md. Na rodada seguinte, T006 foi executada conforme evidence-t006.md; interface de reserva permanece futura.
