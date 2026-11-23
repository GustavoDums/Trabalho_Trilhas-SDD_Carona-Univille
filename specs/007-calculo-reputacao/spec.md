# Feature Specification: Cálculo matemático de reputação

**Feature**: 007-calculo-reputacao | **Created**: 2026-11-22
**Status**: T001 homologada; T002 unificada concluída ([evidência](evidence-t030.md)); sinais/exibição futuros.
**Input**: REQ-009 e solicitação de preparação documental.

## Contexto e rastreabilidade

Fontes: [constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Formato de referência: [Feature 003](../003-busca-rota-horario/spec.md).
Requisito principal REQ-009; transversais REQ-002, REQ-003, REQ-014–REQ-019. Correspondências oficiais em [tasks.md](tasks.md).
Propostas do roadmap não equivalem a decisões homologadas. Estes artefatos permitem revisar o escopo, sem decidir produto por suposição.

## Clarifications — decisões homologadas

- **D007-01 — CONFIRMADA em 2026-11-23**: últimas 20 avaliações recebidas, pesos iguais, sem corte de 30 dias ou agrupamento por carona; created_at/id decrescentes, até instante de referência inclusivo.
- **D007-02 — CONFIRMADA em 2026-11-23**: novato 5.00 sem nota virtual; Decimal, duas casas, ROUND_HALF_UP no final; armazenamento 0.00..5.00; exemplos 4.60 e 4.00 conforme fixtures; penalidades futuras.

## User Scenarios & Testing

### US1 — Obter reputação determinística (P1)

Pontuação é calculada sobre conjunto elegível e regra transparente aprovada.

**Teste independente**: SC-001: após aprovação, novato e fixtures numéricas reproduzem regra exata; se média simples aprovada, [5,5,4,5,4]=4.60 e [5,5,5,1]=4.00.

### US2 — Ver reputação atualizada (P2)

Nova avaliação atualiza perfil e estrelas na busca sem expor detalhes privados.

**Teste independente**: SC-004: perfil e busca exibem nota atual sem campos privados nem N+1; ausência de perfil segue regra inicial homologada.

## Functional Requirements

- FR-001 / REQ-009: função de cálculo determinística, usando Decimal e política explícita; mesma entrada e instante de referência produzem mesmo resultado.
- FR-002 / REQ-009: janela, pesos, base, limites e arredondamento seguem D007-01/D007-02; exemplos conflitantes não são aceites simultâneos.
- FR-003 / REQ-009: atualizar reputação ao persistir avaliação; reprocessamento não soma novamente eventos. Cache deve ser reconstruível das fontes.
- FR-004 / REQ-003: exibir somente nota pública e nome já permitido, sem avaliações individuais, e-mail ou placa na busca; perfil próprio não cria acesso público por ID.

## Fluxo e exceções

1. Identificar sessão e revalidar papel/vínculo no servidor.
2. Validar alvo, estado e política homologada antes de transição.
3. Executar operação completa ou preservar domínio em caso de recusa/rollback.
4. Apresentar resultado ao titular, sem dados privados de terceiros.
5. Verificar repetição e concorrência pelos critérios abaixo; dados do navegador nunca autorizam a ação.

## Dependencies & Scope

Feature 006 funcional (T002/T004 concluídas, qualidade T006 própria ainda aberta); Feature 003 para integração na busca; Feature 001 para perfil. Penalidades serão integradas pela 008 sem duplicar mecanismo.

Não inclui bônus 010/011, staging, commits ou integrações externas. Critérios dependentes de decisão são condicionais até homologação. REQ-020 e T041–T045 orientam entrega geral, sem conclusão nesta preparação.

## Success Criteria

- SC-001: após aprovação, novato e fixtures numéricas reproduzem regra exata; se média simples aprovada, [5,5,4,5,4]=4.60 e [5,5,5,1]=4.00.
- SC-002: testar expulsão do elemento mais antigo conforme unidade aprovada, empate temporal, múltiplas avaliações da mesma viagem e limite de arredondamento.
- SC-003: nova avaliação atualiza nota; repetição/rebuild e gravações concorrentes geram mesmo valor final, sem dupla soma.
- SC-004: perfil e busca exibem nota atual sem campos privados nem N+1; ausência de perfil segue regra inicial homologada.

Todos os critérios exigem testes fictícios. Qualidade: >=80% de linhas e ramificações críticas, relatório versionável e métricas reais identificadas por feature no README; nenhuma métrica estimada nesta rodada.

## Homologação e recorte — 2026-11-23

Usuário aprovou D007-01/D007-02 e autorizou T001 seguida da T002 unificada (antigas T002/T003, roadmap T030). D007-01: média aritmética simples das últimas 20 avaliações recebidas, cada avaliação com o mesmo peso mesmo na mesma viagem; sem janela de 30 dias. Selecionar created_at <= instante de referência e ordenar created_at DESC, id DESC, limit 20. A 21ª expulsa a mais antiga, não agrupar por oferta.

D007-02: novato 5.00 apenas quando conjunto vazio; base não entra como nota virtual. Calcular com Decimal e arredondar somente resultado final para duas casas com ROUND_HALF_UP, independente do contexto Decimal do chamador. [5,5,4,5,4]=4.60; [5,5,5,1]=4.00 (exatamente três notas 5 anteriores). Profile aceita 0.00..5.00; cálculo de notas 1..5 não gera zero, limite inferior prepara futura integração de penalidades da 008, não implementada agora.

ReputationProfile é projeção reconstruível sem substituir RideReview. Rebuild é serviço interno explícito, não endpoint; signals/atualização automática e exibição pública ficam T031. Referências anteriores a pendências/propostas divergentes são históricas e substituídas por esta homologação. Nenhuma aprovação de pesos, expiração por dias ou penalidades foi inferida.
