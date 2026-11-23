# Tasks: Caronas recorrentes

**Feature**: 009-caronas-recorrentes; IDs oficiais locais, independentes do roadmap.
**Input**: [spec](spec.md), [plan](plan.md), [dados](data-model.md), [pesquisa](research.md), [contratos](contracts/web-routes.md), [quickstart](quickstart.md).
**Status**: T001 homologada e T002–T006 concluídas. [Evidência da T035](evidence-t035.md) · [Evidência da T036](evidence-t036.md).
**Tests**: TDD constitucional, dados fictícios, venv e PostgreSQL. Teste/falha esperada → implementação → verde/regressão. SC da spec integram conclusão da tarefa.

## Phase 1: Setup — decisões

- [x] T001 Homologar D009-01/D009-02 em spec.md, data-model.md e contracts/web-routes.md. **Requisitos**: REQ-011, REQ-003, REQ-017; decisões. **Depende**: —. **Conclusão**: regras de calendário e geração automática confirmadas pelo usuário em 2026-11-23. **Roadmap**: preparação.

## Phase 2: Foundational

Feature 002 para publicação atômica; Feature 003/T001 para pacote de serviços e busca para integração; Feature 005 para comprovar independência no cancelamento.
Modelagem canônica em data-model.md: tarefas de modelo implementam integralmente entidades/restrições citadas após fechar campos condicionais. Não recriar ambiente por conveniência.

## Phase 3: User Story 1 (P1)

**Objetivo**: Motorista ativo configura regra e materializa ofertas futuras válidas sem duplicar ocorrências.
**Teste independente**: SC-001: regra em dias selecionados gera exatamente as datas aprovadas do horizonte, com paradas na ordem e snapshots íntegros.

- [x] T002 [US1] Testar e implementar RecurringRideRule, paradas e RecurringRideOccurrence de data-model.md em rides/models.py e rides/migrations/; tests/test_recurring_rides.py cobre unicidade regra/data, snapshot e proteção do histórico. **Requisitos**: REQ-011, REQ-003, REQ-017; FR-001/FR-002; SC-001/SC-002. **Depende**: T001; Feature 002 implementada. **Conclusão**: critérios aprovados na [evidência da T035](evidence-t035.md). **Roadmap**: T035. Fonte canônica de campos em [data-model.md](data-model.md): `RecurringRideRule.driver`, `RecurringRideRule.origin`, `RecurringRideRule.destination`, `RecurringRideRule.weekdays`, `RecurringRideRule.local_time`, `RecurringRideRule.timezone`, `RecurringRideRule.seats`, `RecurringRideRule.active`, `RecurringRideRule.created_at`, `RecurringRideOccurrence.rule`, `RecurringRideOccurrence.local_date`, `RecurringRideOccurrence.offer`.

- [x] T003 [US1] Implementar RecurringRideService em rides/services/recurring_ride_service.py usando publish_offer; tests/test_recurring_rides.py cobre calendário aprovado, transação de lote, duas conexões, repetição, motorista inelegível e datas passadas. **Requisitos**: REQ-011, REQ-003, REQ-017; FR-001/FR-002/FR-003; SC-001/SC-002/SC-004. **Depende**: T002; Feature 003/T001. **Conclusão**: critérios aprovados na [evidência da T035](evidence-t035.md). **Roadmap**: T035. Fonte canônica de campos em [data-model.md](data-model.md): `RecurringRideRule.driver`, `RecurringRideRule.origin`, `RecurringRideRule.destination`, `RecurringRideRule.weekdays`, `RecurringRideRule.local_time`, `RecurringRideRule.timezone`, `RecurringRideRule.seats`, `RecurringRideRule.active`, `RecurringRideRule.created_at`, `RecurringRideOccurrence.rule`, `RecurringRideOccurrence.local_date`, `RecurringRideOccurrence.offer`.

- [x] T004 [US1] Verificar cancelamento de ocorrência via CancellationService sem mudar série em tests/test_recurring_rides.py e ajustar somente vínculo do gerador se necessário; conclusão: reexecução não recria ocorrência cancelada. **Requisitos**: REQ-011, REQ-003, REQ-017; FR-002/FR-004; SC-003. **Depende**: T003; Feature 005/T006. **Conclusão**: critérios aprovados na [evidência da T035](evidence-t035.md). **Roadmap**: T035. Fonte canônica de campos em [data-model.md](data-model.md): `RecurringRideRule.driver`, `RecurringRideRule.origin`, `RecurringRideRule.destination`, `RecurringRideRule.weekdays`, `RecurringRideRule.local_time`, `RecurringRideRule.timezone`, `RecurringRideRule.seats`, `RecurringRideRule.active`, `RecurringRideRule.created_at`, `RecurringRideOccurrence.rule`, `RecurringRideOccurrence.local_date`, `RecurringRideOccurrence.offer`.

## Phase 4: User Story 2 (P2)

**Objetivo**: Formulário autorizado e comando compartilham gerador; resultado mostra datas criadas e já existentes.
**Teste independente**: SC-005: formulário e comando produzem mesmo conjunto de datas; ofertas geradas aparecem na busca da 003 e podem ser reservadas pelo fluxo da 004.

- [x] T005 [US2] Implementar RecurringRideForm, view/rotas e rides/templates/rides/recurring_offers.html em rides/forms.py, rides/views.py e rides/urls.py; tests/test_recurring_flow.py cobre titularidade, CSRF, validação e datas exibidas. **Requisitos**: REQ-011, REQ-003, REQ-017; FR-003/FR-005; SC-004/SC-005. **Depende**: T004. **Conclusão**: critérios aprovados na [evidência da T036](evidence-t036.md). **Roadmap**: T036.

- [x] T006 [US2] Implementar rides/management/commands/generate_recurring_rides.py conforme contrato aprovado; tests/test_recurring_flow.py compara CLI/formulário, erro/rollback e integração de busca/reserva sem imprimir dados privados. **Requisitos**: REQ-011, REQ-003, REQ-017; FR-001/FR-003/FR-005; SC-005. **Depende**: T005; Feature 003/T004; Feature 004/T005. **Conclusão**: critérios aprovados na [evidência da T036](evidence-t036.md). **Roadmap**: T036.

## Phase 5: Polish & Cross-Cutting Concerns

- [ ] T007 Criar scripts/check-feature009-quality.ps1 e gerar coverage-feature009.json e test-results-feature009.xml após testes novos e regressão pertinente; sincronizar bloco identificado no README.md com métricas reais e validar quickstart.md. **Requisitos**: REQ-011, REQ-014–REQ-019; todos os SC. **Depende**: todas as tarefas locais anteriores. **Conclusão**: cenários, privacidade, migração e regressão aprovados, >=80% linhas/ramificações críticas, relatórios versionáveis e roteiro verificado; não concluir sem evidência ou decisão. **Roadmap**: suporte a T041–T043, sem concluí-las. Sem staging/commit.

## Revisão da janela de recorrência

- [x] T008 Atualizar D009-01 para 15 dias úteis com o calendário da BrasilAPI e compartilhar o cálculo entre formulário, consulta e rotina diária. **Requisitos** REQ-011, REQ-003, REQ-014, REQ-017–REQ-019; FR-003, SC-001/SC-004–SC-006. **Depende de** T003, T005 e T006. **Conclusão** testes de calendário e indisponibilidade aprovados, histórico preservado e relatório consolidado sincronizado. [Evidência de conclusão](evidence-t008.md).

## Dependencies & Execution Order

Dependências explícitas de cada tarefa são obrigatórias; número não permite ignorar ramo anterior. MVP local: US1 após decisões; entrega completa: US1+US2+T007. Implementação dependente de decisão permanece bloqueada.

## Correspondência com roadmap

| Roadmap | Requisito / objetivo detalhado na tarefa | IDs locais |
| --- | --- | --- |
| T035 | REQ-011 | T002, T003, T004 |
| T036 | REQ-011 | T005, T006 |
| Atualização de calendário | REQ-011, REQ-003, REQ-014, REQ-017–REQ-019 | T008 |
| Preparação/qualidade | Decisões e evidência | T001, T007 |

## Parallel Opportunities & Implementation Strategy

Sem [P]: estado e contratos compartilhados, com decisões condicionais. Revisão pode ocorrer em paralelo; execução dependente não. Uma tarefa por rodada revisável, preservando IDs, checkboxes e alterações de outras features. Aprovar documentação não confirma automaticamente valores de produto.
