# Tasks: Busca por rota e horário

**Feature**: 003-busca-rota-horario. IDs abaixo são oficiais locais, independentes dos IDs do roadmap e de outras features.
**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contratos](contracts/web-routes.md), [quickstart.md](quickstart.md).
**Prerequisites**: identidade/middleware da Feature 001 e ofertas/catálogo da Feature 002 disponíveis. T007 de qualidade final da Feature 002 encerrada em 2026-11-23 por aceite final; ver [evidência](../002-oferta-caronas-paradas/evidence-t007.md).
**Tests**: exigidos pela constitution e REQ-017. Em cada tarefa de implementação: escrever/rodar testes antes, demonstrar falha esperada de comportamento, implementar e repetir. Refatoração preserva comportamento e comprova regressão sem fabricar falha de produto. Dados sintéticos, venv e PostgreSQL existentes. Atualização 2026-11-22: T001–T005 implementadas e verificadas; T005 encerrada em 2026-11-23 ([evidência](evidence-t005.md)). Evidências em [evidence-t018.md](evidence-t018.md) e [evidence-t019.md](evidence-t019.md).

## Phase 1: Setup

Não há novo app, dependência ou migração. Confirmar ambiente existente ao executar T001; não alterar `.env` ou métricas das features anteriores.

## Phase 2: Foundational — compatibilidade de publicação

- [x] T001 Transformar `rides/services.py` em pacote com `rides/services/offers.py` e `rides/services/__init__.py`, preservando corpo, assinatura, atomicidade e import público de publish_offer; adaptar somente imports relativos para `..models` e alvos de mocks realmente movidos. Adicionar teste de contrato do import em `tests/test_rides_offer.py` e executar toda a regressão desse módulo antes/depois, sem enfraquecer asserções. Não manter arquivo services.py e diretório services homônimos simultaneamente; não adicionar matching nesta tarefa. REQ-005 (preparação), REQ-004 (preservação); depende da implementação Feature 002; conclusão: imports antigos funcionam, publicação continua atômica, `manage.py check` e regressão aprovados. Preparação necessária à T002 local, não correspondência adicional funcional da T017.

## Phase 3: User Story 1 — Compatibilidade de rota (P1)

**Goal**: núcleo determinístico de busca compatível por rota e tempo, sem expor segredos.
**Independent Test**: matriz de pontos e horários executável diretamente no serviço sobre ofertas sintéticas, sem formulário ou endpoint.

- [x] T002 [US1] Escrever testes em `tests/test_matching.py` e implementar SearchQuery, SearchResult e MatchingService em `rides/services/matching_service.py`, com predicados e search segundo [contratos](contracts/web-routes.md). Fonte canônica [data-model.md](data-model.md): `SearchQuery.boarding_id`, `SearchQuery.alighting_id`, `SearchQuery.desired_at`; `SearchResult.offer_id`, `SearchResult.driver_display_name`, `SearchResult.itinerary`, `SearchResult.departure_at`, `SearchResult.seats`, `SearchResult.vehicle_model`, `SearchResult.vehicle_color`; fontes somente leitura `RoutePoint.id`, `RoutePoint.name`, `RideOffer.id`, `RideOffer.driver`, `RideOffer.origin`, `RideOffer.destination`, `RideOffer.departure_at`, `RideOffer.seats`, `RideOffer.created_at`, `RideOffer.vehicle_model`, `RideOffer.vehicle_color`, `Waypoint.offer`, `Waypoint.point`, `Waypoint.position`, `AcademicUser.id`, `AcademicUser.role`, `AcademicUser.academic_status`, `AcademicUser.is_active`, `AcademicUser.display_name`. Aplicar integralmente os contratos de validação, projeção, ordenação e elegibilidade, sem mudar campos persistidos. Cobrir todos os pares de posições, rota direta, inversão, iguais/ausentes, dado legado ambíguo, ±30min inclusivos, 1s fora, meia-noite, offsets equivalentes, saída passada/igual a now, motorista inelegível, ausência de duplicações, DTO sem segredos, autorização do passageiro, ausência de escrita e consultas sem N+1. Capturar now uma vez; sem ETA por parada. REQ-005, REQ-017, REQ-002, REQ-003; FR-001–FR-008, FR-010–FR-011; US1 e núcleo US2/US3; SC-001–SC-004; dependência T001. Conclusão: serviço validado no PostgreSQL e matriz temporal/rota aprovada. **Correspondência única: roadmap T017 → Feature 003/T002 local.** Sem formulário ou rota nesta tarefa.

## Phase 4: User Story 2 — Janela compreensível e filtros (P2)

**Goal**: traduzir consulta do passageiro e apresentar corretamente a referência temporal aprovada.
**Independent Test**: validar formulário e renderizar template com DTO sintético por RequestFactory, sem endpoint.

- [x] T003 [US2] Escrever testes de formulário/projeção/renderização em `tests/test_ride_search.py` e implementar RideSearchForm em `rides/forms.py`, `rides/templates/rides/search.html` e `rides/templates/rides/_search_result.html`. Seguir [contratos](contracts/web-routes.md), sem adicionar view/rota. Campos canônicos de [data-model.md](data-model.md): `SearchQuery.boarding_id`, `SearchQuery.alighting_id`, `SearchQuery.desired_at`, `SearchResult.offer_id`, `SearchResult.driver_display_name`, `SearchResult.itinerary`, `SearchResult.departure_at`, `SearchResult.seats`, `SearchResult.vehicle_model`, `SearchResult.vehicle_color`. ModelChoiceFields referem catálogo existente; horário convertido ao fuso indicado; erro específico para iguais/ausentes/inválidos. Janela fixa, sem campo de tolerância; aviso explícito de saída da origem e ausência de previsão por parada. Cartões só recebem DTO e escapam rótulos; sem placa/email/nome completo, nota ou botão de reserva em texto/atributos/JSON oculto. Diferenciar inicial/erro/vazio/resultados conforme searched; preservar filtros. REQ-005, REQ-003; FR-002, FR-005–FR-009; US2.4/2.5 e apresentação US3; dependência T002; conclusão: formulário e HTML sintéticos validados, sem endpoint antecipado. **Roadmap T018 → Feature 003/T003 local.**

## Phase 5: User Story 3 — Busca autorizada e resultados privados (P3)

**Goal**: passageiro ativo pesquisa via HTTP com consulta somente leitura.
**Independent Test**: GET real de `/caronas/buscar/` com ofertas de dois motoristas, filtros, resultados e todos os estados de acesso.

- [x] T004 [US3] Escrever testes HTTP em `tests/test_ride_search.py` e implementar ActivePassengerRequiredMixin/RideSearchView em `rides/views.py` e rota `rides:search` em `rides/urls.py`, conforme [contratos](contracts/web-routes.md). Converter formulário validado em SearchQuery e passar request.user ao serviço; fontes canônicas [data-model.md](data-model.md): `SearchQuery.boarding_id`, `SearchQuery.alighting_id`, `SearchQuery.desired_at`, `AcademicUser.id`, `AcademicUser.role`, `AcademicUser.academic_status`, `AcademicUser.is_active`. Só DTOs SearchResult definidos nesse documento compõem resultados do contexto. Testar visitante/pendente/motorista bloqueados, passageiro permitido, inicial distinto do vazio, erros sem chamada indevida ao matching, parâmetros extras sem alterar janela/permissões, ofertas ordenadas/únicas, exclusão de vínculos inativos e passadas, GET sem mudança de domínio e 405 em métodos de escrita. Preservar rotas de publicação, consulta própria e placeholder. REQ-005, REQ-002, REQ-003, REQ-017; FR-001–FR-011; US3; dependência T003; conclusão: busca integrada e restrita, com HTML privado e teste de regressão de rides. **Roadmap T019 → Feature 003/T004 local.**

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T005 Completar aceitação da busca em `tests/test_ride_search.py`, incluindo login/ativação reais e ofertas sintéticas publicadas pelas funcionalidades existentes, e criar `scripts/check-feature003-quality.ps1` para executar testes novos e regressão de `tests/test_rides_offer.py`, gerar `coverage-feature003.json` e `test-results-feature003.xml` e atualizar somente bloco Feature 003 do `README.md`. Medir conjunto técnico rides e módulo matching separadamente com meta >=80% em linhas e ramificações, identificando a contagem de testes novos versus regressão no JUnit. Executar também os seis módulos de accounts sem sobrescrever métricas anteriores. Validar [quickstart.md](quickstart.md), HTML e inspeção visual; registrar demo humana <=1 minuto, sem usar duração de suíte como comprovação. REQ-017, REQ-018, REQ-019, REQ-005, REQ-003; SC-001–SC-005; dependência T004; conclusão: cenários e regressões aprovados, relatórios reais e roteiro verificado. Não concluir se meta ou demo falhar; sem staging/commit automático.

## Dependencies & Execution Order

`Features 001/002 disponíveis → T001 → T002 → T003 → T004 → T005`.

- Fundação T001 é compatibilidade técnica, não nova modelagem de ofertas. Serviço T002 implementa núcleo de rota e tempo juntos para não existir matching incompleto por critério.
- US2 é verificável por formulário/renderização sem HTTP; US3 completa acesso integrado. Tarefas não antecipam dependentes silenciosamente.
- Escopo mínimo de matching: T001/T002; busca utilizável no navegador: T001–T004. T005 encerra aceitação/qualidade.

## Correspondência com roadmap

| Roadmap | Objetivo | ID local oficial |
| --- | --- | --- |
| T017 / REQ-005, REQ-017 | Matching de ordem e janela | **T002**, preparação técnica T001 |
| T018 / REQ-003, REQ-005 | Formulário e cartões | **T003** |
| T019 / REQ-005, REQ-017 | View e fluxo integrado | **T004** |
| Governança da entrega | Aceitação final e métricas | **T005** |

Sempre reportar os dois IDs para evitar confusão com features anteriores. T017 corresponde à T002 local e teve a preparação T001 como dependência já atendida. T001–T005 concluídas; ver [aceite final](evidence-t005.md). Ver [evidence-t018.md](evidence-t018.md) e [evidence-t019.md](evidence-t019.md).

## Parallel Opportunities & Examples

Sem [P] no fluxo: T001 altera fronteira de import, T002 fornece DTOs, T003 compartilha forms/templates e T004 usa esses contratos; T005 depende da entrega integrada. Não há trabalho de implementação independente que justifique execução paralela neste recorte. Após cada etapa, revisão dos critérios pode ocorrer junto à leitura dos relatórios: US1 matriz de pares e bordas; US2 inspeção de formulário e cartões; US3 auditoria de HTML e estado do banco. Não confundir revisão paralela com autorização para implementar outra tarefa.

## Implementation Strategy

Uma tarefa por rodada revisável. Testes antes das mudanças de comportamento, com falha real e evidência vermelho/verde; preparação/refatoração usa baseline e regressão comparáveis. Não criar reservas, reputação, horários por parada, tolerância ajustável ou novas migrações por conveniência. Manter os checkboxes abertos até execução e validação efetivas.

## Evidência parcial — T005 (2026-11-23)

[Registro](evidence-t005.md): sete testes de aceitação HTTP reais adicionados e aprovados, 668 testes aprovados na regressão (7 novos/661 anteriores), script e relatórios próprios gerados. rides: 99.83844911147011% linhas / 97.5609756097561% ramificações; matching 100% de ambas. Critério humano de busca <=1 minuto e inspeção visual ainda pendentes; T005 permanece aberta. Nenhuma aplicação de regra nova nem execução de T027.

## Aceite humano final — 2026-11-23

Após relato de que o teste funcionou, foi perguntado explicitamente se o usuário também realizou a busca, encontrou a oferta em até um minuto e conferiu a legibilidade da tela, em vez de apenas ativar o perfil. Resposta: “sim”. SC-005 e inspeção visual aprovados por confirmação humana, sem atribuir tempo exato em segundos ou usar duração de pytest. T005 concluída; registros parciais anteriores são históricos e substituídos por este aceite quanto às pendências.

Resultado técnico permanece 668 testes aprovados (7 novos/661 de regressão anterior), rides 99.83844911147011% linhas e 97.5609756097561% ramificações; matching 100% em ambas. Somente documentação atualizada nesta confirmação, sem repetir testes, staging ou commit. Feature 005/T007, correspondente à T027 do roadmap, ainda não executada.
