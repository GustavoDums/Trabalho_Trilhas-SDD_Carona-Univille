# Feature Specification: Caronas recorrentes

**Feature**: 009-caronas-recorrentes | **Created**: 2026-11-22
**Status**: D009-01 e D009-02 homologadas em 2026-11-23.
**Input**: REQ-011 e solicitação de preparação documental.

## Contexto e rastreabilidade

Fontes: [constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Formato de referência: [Feature 003](../003-busca-rota-horario/spec.md).
Requisito principal REQ-011; transversais REQ-002, REQ-003, REQ-014–REQ-019. Correspondências oficiais em [tasks.md](tasks.md).
Propostas do roadmap não equivalem a decisões homologadas. Estes artefatos permitem revisar o escopo, sem decidir produto por suposição.

## Clarifications — decisões homologadas em 2026-11-23

- **D009-01**: Horizonte de 16 dias corridos, contando a data local de referência até essa data + 15, inclusive, em `America/Sao_Paulo`. Gerar nos dias da semana selecionados, incluindo fins de semana e feriados quando selecionados. Partidas devem ser estritamente futuras em relação ao instante de referência.
- **D009-02**: Gerar automaticamente ao criar uma regra e completar o horizonte diariamente. O comando interno agendado revalida o vínculo e a elegibilidade do motorista a cada execução. Edição e desativação só afetam gerações futuras e preservam todas as ofertas existentes.

## User Scenarios & Testing

### US1 — Gerar instâncias independentes (P1)

Motorista ativo configura regra e materializa ofertas futuras válidas sem duplicar ocorrências.

**Teste independente**: SC-001: regra em dias selecionados gera exatamente as datas aprovadas do horizonte, com paradas na ordem e snapshots íntegros.

### US2 — Gerenciar geração pela interface e CLI (P2)

Formulário autorizado e comando compartilham gerador; resultado mostra datas criadas e já existentes.

**Teste independente**: SC-005: formulário e comando produzem mesmo conjunto de datas; ofertas geradas aparecem na busca da 003 e podem ser reservadas pelo fluxo da 004.

## Functional Requirements

- FR-001 / REQ-011: cada ocorrência é RideOffer independente, com snapshot de trajeto, paradas, capacidade e veículo validado como na publicação.
- FR-002 / REQ-011: reexecutar ou executar simultaneamente não cria duas ofertas para a mesma regra/data local; cancelamento de uma ocorrência não a recria.
- FR-003 / REQ-004, REQ-011: somente motorista ativo gera, incluindo revalidação no comando; não criar oferta passada; período e dias seguem D009-01.
- FR-004 / REQ-007, REQ-011: cancelar uma instância não muda regra, demais datas, reservas ou avaliações das outras instâncias.
- FR-005 / REQ-003: formulário/lista só exibem regras do titular; CLI não imprime contato ou segredos; sem dependência de notificações ou fila.

## Fluxo e exceções

1. Identificar sessão e revalidar papel/vínculo no servidor.
2. Validar alvo, estado e política homologada antes de transição.
3. Executar operação completa ou preservar domínio em caso de recusa/rollback.
4. Apresentar resultado ao titular, sem dados privados de terceiros.
5. Verificar repetição e concorrência pelos critérios abaixo; dados do navegador nunca autorizam a ação.

## Dependencies & Scope

Feature 002 para publicação atômica; Feature 003/T001 para pacote de serviços e busca para integração; Feature 005 para comprovar independência no cancelamento.

Não inclui bônus 010/011, staging, commits ou integrações externas. A T035 entrega modelos, gerador e independência do cancelamento. Os pontos de entrada que acionam o gerador automaticamente pertencem à T036. REQ-020 e T041–T045 orientam a entrega geral.

## Success Criteria

- SC-001: regra em dias selecionados gera exatamente as datas aprovadas do horizonte, com paradas na ordem e snapshots íntegros.
- SC-002: duas gerações simultâneas e repetição posterior mantêm uma ocorrência por regra/data; falha intermediária faz rollback do lote e permite repetição segura.
- SC-003: cancelar uma ocorrência mantém as demais inalteradas e reexecutar gerador não repõe a cancelada.
- SC-004: conta inelegível, terceiro e horário passado não geram; testar bordas de horizonte, mudança de mês e fuso conforme política.
- SC-005: formulário e comando produzem mesmo conjunto de datas; ofertas geradas aparecem na busca da 003 e podem ser reservadas pelo fluxo da 004.

Todos os critérios exigem testes fictícios. Qualidade: >=80% de linhas e ramificações críticas, relatório versionável e métricas reais identificadas por feature no README; nenhuma métrica estimada nesta rodada.
