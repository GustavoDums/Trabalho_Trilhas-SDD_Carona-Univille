# Feature Specification: Avaliação mútua pós-viagem

**Feature**: 006-avaliacao-mutua | **Created**: 2026-11-22
**Status**: rascunho preparado; decisões abaixo bloqueiam tarefas afetadas. Nenhuma implementação realizada.
**Input**: REQ-008 e solicitação de preparação documental.

## Contexto e rastreabilidade

Fontes: [constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Formato de referência: [Feature 003](../003-busca-rota-horario/spec.md).
Requisito principal REQ-008; transversais REQ-002, REQ-003, REQ-014–REQ-019. Correspondências oficiais em [tasks.md](tasks.md).
Propostas do roadmap não equivalem a decisões homologadas. Estes artefatos permitem revisar o escopo, sem decidir produto por suposição.

## Clarifications — decisões pendentes

- **D006-01 — PENDENTE**: Definir término verificável da viagem: oferta contém somente departure_at. Levantamento fala em conclusão do horário previsto, mas não há chegada prevista. Não equiparar partida a término. Escolher referência e responsável pelo registro antes de alterar dados.
- **D006-02 — PENDENTE**: Confirmar janela proposta de 48h, bordas, elegibilidade de cancelados/no-show e pares permitidos (proposta: motorista↔passageiro, nunca passageiro↔passageiro); fixar limite do comentário e edição/revisão.

## User Scenarios & Testing

### US1 — Avaliar contraparte após viagem (P1)

Participante elegível avalia contraparte com nota de 1 a 5 e comentário opcional após término verificável.

**Teste independente**: SC-001: rejeitar notas 0/6/fracionárias, autor e alvo iguais, não participante e duplicata; aceitar 1 e 5 com comentário vazio.

### US2 — Enviar avaliação pela interface (P2)

Usuário autenticado envia formulário sem poder escolher avaliador ou adulterar elegibilidade.

**Teste independente**: SC-003: contraparte válida registra avaliação por POST com CSRF; adulteração, GET de escrita e comentário HTML não burlam autorização nem escape.

## Functional Requirements

- FR-001 / REQ-008: nota inteira entre 1 e 5 e comentário opcional; sem autoavaliação, sem duplicidade por oferta/avaliador/avaliado.
- FR-002 / REQ-008: autorização exige participação elegível e término comprovável; janela e cancelamentos seguem D006-01/D006-02.
- FR-003 / REQ-002, REQ-003: identidade do avaliador vem da sessão; IDs enviados não permitem avaliar terceiro não participante; comentário escapado e sem divulgação de e-mail/placa.
- FR-004 / REQ-008: validação no serviço e banco para nota/unicidade; rejeição não grava avaliação. Não calcular reputação nesta feature.

## Fluxo e exceções

1. Identificar sessão e revalidar papel/vínculo no servidor.
2. Validar alvo, estado e política homologada antes de transição.
3. Executar operação completa ou preservar domínio em caso de recusa/rollback.
4. Apresentar resultado ao titular, sem dados privados de terceiros.
5. Verificar repetição e concorrência pelos critérios abaixo; dados do navegador nunca autorizam a ação.

## Dependencies & Scope

Feature 004 para participantes; Feature 005 para estado cancelado. Criar app reviews somente na execução das tarefas; não existe hoje.

Não inclui bônus 010/011, staging, commits ou integrações externas. Critérios dependentes de decisão são condicionais até homologação. REQ-020 e T041–T045 orientam entrega geral, sem conclusão nesta preparação.

## Success Criteria

- SC-001: rejeitar notas 0/6/fracionárias, autor e alvo iguais, não participante e duplicata; aceitar 1 e 5 com comentário vazio.
- SC-002: bloquear antes do término; após homologar referência e janela, testar instante de término, limite exato e 1s fora; cancelados/no-show seguem decisão explícita.
- SC-003: contraparte válida registra avaliação por POST com CSRF; adulteração, GET de escrita e comentário HTML não burlam autorização nem escape.

Todos os critérios exigem testes fictícios. Qualidade: >=80% de linhas e ramificações críticas, relatório versionável e métricas reais identificadas por feature no README; nenhuma métrica estimada nesta rodada.
