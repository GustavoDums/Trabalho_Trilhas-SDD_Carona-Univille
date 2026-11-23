# Tasks: Oferta de caronas com paradas

**Feature**: 002-oferta-caronas-paradas. IDs abaixo são locais à Feature 002.
**Input**: [spec.md](spec.md), [plan.md](plan.md), [research.md](research.md), [data-model.md](data-model.md), [contratos](contracts/web-routes.md), [quickstart.md](quickstart.md).
**Prerequisites**: Feature 001 concluída; identidade e middleware disponíveis; PostgreSQL e venv existentes. Rodada de implementação autorizada: roadmap T013 corresponde a T002 local; preparação T001 e fundação T002 concluídas. T003 e T004 concluídas nos recortes da T014; T005 concluída em rodada T015; T006 concluída em rodada T016; T007 permanece aberta.
**Tests**: obrigatórios pela constitution, com dados sintéticos e TDD dentro de cada tarefa: escrever/rodar testes, registrar falha esperada, implementar, rodar novamente. Não aceitar erro de configuração como prova de comportamento.

## Phase 1: Setup

- [x] T001 Preparar app `rides/__init__.py` e `rides/apps.py`, registrá-lo em `carona_univille/settings.py` e criar o módulo `tests/test_rides_offer.py` com fixtures sintéticas locais (motorista ativo, motorista pendente e passageiro ativo), sem alterar autenticação ou esquema de accounts; validar `manage.py check` e teste de configuração do app. REQ-004, REQ-002; dependência Feature 001; conclusão: app registrado e ambiente PostgreSQL de testes utilizável.

## Phase 2: Foundational — correspondência principal da T013 do roadmap

- [x] T002 Implementar `RoutePoint`, `RideOffer` e `Waypoint` em `rides/models.py`, `rides/migrations/0001_initial.py` e `0002_seed_route_points.py`, com testes `test_model_*` em `tests/test_rides_offer.py`. Fonte canônica: [data-model.md](data-model.md), campos `RoutePoint.id`, `RoutePoint.code`, `RoutePoint.name`; `RideOffer.id`, `RideOffer.driver`, `RideOffer.origin`, `RideOffer.destination`, `RideOffer.departure_at`, `RideOffer.seats`, `RideOffer.vehicle_model`, `RideOffer.vehicle_color`, `RideOffer.vehicle_plate`, `RideOffer.created_at`; `Waypoint.id`, `Waypoint.offer`, `Waypoint.point`, `Waypoint.position`, incluindo relacionamentos, validações de inserção, normalização, constraints nomeadas e ordenações ali definidas. Sem duplicar ou ampliar essas restrições. Criar os quatro pontos de research.md por migração de dados histórica/reversível; testar FK PROTECT/CASCADE, constraints no PostgreSQL, criação por motorista ativo, rejeição dos demais, limites de horário em inserção sem invalidar histórico, sequência de paradas e snapshot. Registrar os limites de clean/save versus escritas em lote e contiguidade pelo futuro serviço, conforme o modelo de dados. Rodar testes vermelho/verde, `makemigrations --check --dry-run`, aplicar/verificar migrações no PostgreSQL local e de testes. REQ-004, REQ-002, REQ-003; FR-001, FR-003–FR-007; dependência T001; conclusão: modelos, catálogo, restrições e testes aprovados. **Correspondência oficial: roadmap T013 → Feature 002/T002**, com T001 como preparação.

**Checkpoint**: nenhum fluxo web antes da fundação. T002 não implementa formulário, publicação completa ou listagem.

## Phase 3: User Story 1 — Publicar oferta com itinerário (P1)

**Goal**: motorista ativo publica oferta íntegra usando veículo informado.
**Independent Test**: POST válido com zero/duas paradas e consulta pelo ORM preserva autoria, pontos e dados; anônimo/pendente/passageiro não publicam.

- [x] T003 [US1] Criar testes `test_publish_*` em `tests/test_rides_offer.py` antes de implementar `RideOfferForm`/formset em `rides/forms.py`, serviço `publish_offer` em `rides/services.py`, verificação de motorista ativo e `RideCreateView` em `rides/views.py`, `rides/urls.py`, integração em `carona_univille/urls.py`, `rides/templates/rides/offer_create.html` e `rides/static/rides/offer.js`, conforme [contratos](contracts/web-routes.md). Aplicar aos campos do formulário/serviço as definições de [data-model.md](data-model.md): `RideOffer.driver`, `RideOffer.origin`, `RideOffer.destination`, `RideOffer.departure_at`, `RideOffer.seats`, `RideOffer.vehicle_model`, `RideOffer.vehicle_color`, `RideOffer.vehicle_plate`, `Waypoint.offer`, `Waypoint.point`, `Waypoint.position`. O serviço usa conta da sessão reconsultada/bloqueada, valida itinerário completo e publica oferta/paradas numa transação; servidor gera posições da lista. Incluir veículo obrigatório já nesta etapa, sem aguardar T004 para tornar US1 válida. Testar acesso, autoria adulterada, CSRF, ordem, saída futura e rollback na falha de uma parada; conferir adicionar/remover linhas preservando ordem visível. Preservar `/caronas/`. REQ-004, REQ-002, REQ-003; FR-001–FR-008; US1.1–1.4; dependência T002; conclusão: publicação HTTP funciona com dados completos e sem publicação parcial. O 302 aponta à futura lista de T005; até lá testar destino sem segui-lo, verificando persistência por ORM.

## Phase 4: User Story 2 — Veículo e correção de erros (P2)

**Goal**: reutilização segura de veículo próprio e feedback consistente de entradas inválidas.
**Independent Test**: pré-preencher com última oferta própria, submeter erros e corrigir, mantendo snapshots anteriores intactos.

- [x] T004 [US2] Expandir testes `test_vehicle_*` e `test_invalid_*` em `tests/test_rides_offer.py` e completar tratamento de erros/reutilização em `rides/forms.py`, `rides/views.py`, `rides/services.py` e `rides/templates/rides/offer_create.html`, conforme [contratos](contracts/web-routes.md) e [data-model.md](data-model.md): `RideOffer.vehicle_model`, `RideOffer.vehicle_color`, `RideOffer.vehicle_plate`, `RideOffer.origin`, `RideOffer.destination`, `RideOffer.departure_at`, `RideOffer.seats`, `Waypoint.point`, `Waypoint.position`. Reutilizar somente snapshot da última oferta do próprio autor, copiar novos valores sem mutar a anterior; erros preservam dados não sensíveis e limpam placa. Cobrir campos ausentes/espaços, vagas fracionárias, horário exatamente agora/passado, catálogo desconhecido, pontos repetidos, management form inválido e falha intermediária sem gravação parcial. REQ-004, REQ-003; FR-004–FR-008; US2.1–2.3; dependência T003; conclusão: correção/reenvio e reutilização cumprem contrato, com testes aprovados.

## Phase 5: User Story 3 — Minhas ofertas (P3)

**Goal**: motorista consulta exclusivamente as próprias ofertas.
**Independent Test**: ofertas de dois motoristas em sessões distintas, ordenação determinística, ausência de e-mail/placa e estado vazio.

- [x] T005 [US3] Escrever testes `test_my_offers_*` em `tests/test_rides_offer.py` e implementar `MyOffersView` em `rides/views.py`, rota em `rides/urls.py` e `rides/templates/rides/my_offers.html`, segundo [contratos](contracts/web-routes.md). Consulta filtra autor da sessão, usa select_related/prefetch_related e as ordenações de [data-model.md](data-model.md): `RideOffer.driver`, `RideOffer.departure_at`, `RideOffer.created_at`, `RideOffer.id`, `Waypoint.position`. Mostrar itinerário, vagas e modelo/cor; omitir e-mail e placa inclusive de atributos ocultos; vazio com link de criação. Testar 403 para passageiro, bloqueios anônimo/pendente, query de autoria adulterada e 405 em métodos de escrita. Sem edição, exclusão, cancelamento ou contador de reservas. REQ-004, REQ-003, REQ-002; FR-001, FR-009–FR-011; US3.1–3.3; dependência T004; conclusão: consulta segura e redirecionamento da publicação agora pode ser seguido até HTTP 200.

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T006 Completar aceitação ponta a ponta em `tests/test_rides_offer.py` com cadastro/login manual/ativação da Feature 001 → oferta → consulta própria, trajeto direto e com paradas, dois autores, falhas sem publicação parcial e ausência de exposição de placa/e-mail; executar regressão dos seis arquivos existentes da Feature 001, sem enfraquecer seus testes. REQ-004, REQ-002, REQ-003, REQ-017; SC-001–SC-004; dependência T005; conclusão: cenários integrados e regressão aprovados no PostgreSQL.
- [ ] T007 Criar `scripts/check-feature002-quality.ps1` para executar `tests/test_rides_offer.py`, medir `rides` com pytest-cov/branch e meta 80% combinada e separada em linhas/ramificações, gerar `coverage-feature002.json` e `test-results-feature002.xml`, atualizar bloco Feature 002 próprio em `README.md`, registrar execução e validação de [quickstart.md](quickstart.md) sem misturar ou sobrescrever indicadores da Feature 001. Validar visualmente o formset e medir/registrar demo com duas paradas até 2 minutos, distinguindo resultado humano de duração de suíte; não concluir se critério falhar. REQ-018, REQ-019, REQ-004; SC-001–SC-005; dependência T006; conclusão: relatórios reais, regressão aprovada, roteiro validado e métricas >=80% versionáveis, sem staging/commit automático.

## Dependencies & Execution Order

`Feature 001 → T001 → T002 → T003 → T004 → T005 → T006 → T007`.

- Fundação T002 bloqueia todas as histórias. US2 e US3 integram com publicação, mas podem ser testadas isoladamente por dados sintéticos persistidos.
- Dentro de cada tarefa: testes → falha esperada → implementação → testes pertinentes → evidência. Não executar tarefa posterior para completar silenciosamente a selecionada.
- MVP funcional inicial: T001–T003 (publicação verificável por persistência); experiência completa de publicação/consulta: T001–T005. Qualidade final: T006–T007.

## Correspondência com roadmap

| Roadmap | Objetivo | IDs oficiais locais Feature 002 |
| --- | --- | --- |
| T013 / REQ-004 | Modelos, migrações, ordenação de paradas | **T002**, com preparação T001 |
| T014 / REQ-004 | Formulário e criação atômica | T003 (publicação), T004 (erros e reutilização) |
| T015 / REQ-004 | Consulta de ofertas próprias | T005 |
| T016 / REQ-004, REQ-017 | Aceitação integrada | T006 |
| Governança de entrega | Métricas e demo | T007 |

Se uma próxima solicitação usar T014 do roadmap, explicitar T003/T004 e pedir o recorte caso não esteja indicado; não confundir IDs com os da Feature 001. T013 tem uma correspondência principal inequívoca, T002; executar T001 primeiro se ainda pendente.

## Parallel Opportunities & Examples

Nenhuma tarefa marcada [P]: os passos compartilham `models.py`, `forms.py`, `views.py` ou o módulo de testes e possuem dependências reais. Em US1, inspeção visual do formulário pode ocorrer junto à revisão dos testes após T003; em US2, revisão de mensagens junto à auditoria de snapshot após T004; em US3, revisão de privacidade junto à checagem de ordenação após T005. São verificações independentes, não autorização para implementar tarefas futuras em paralelo.

## Implementation Strategy

Uma tarefa por rodada/commit revisável. Somente checkboxes com evidência de execução são marcados; T007 permanece aberta. Respeitar limites de validação do modelo de dados e nunca alegar garantias SQL de regras que dependem de serviço. Não alterar a constitution, as pendências de matching/cancelamento nem os comportamentos da Feature 001.

## Evidência — roadmap T013 / Feature 002 T002 local, preparação T001 (2026-11-22)

- Correspondência principal única por objetivo e requisito: modelos/migrações/sequência = T002 local. T001 executada primeiro como preparação expressamente exigida nesta dependência, informada ao usuário antes da edição. REQ-004, REQ-002, REQ-003; FR-001, FR-003–FR-007 no recorte de modelo.
- T001: teste de app ausente falhou antes do registro; após criar app/configuração e fixtures locais, teste passou e `manage.py check` não apontou problemas. Identidade e esquema de accounts preservados.
- TDD T002: 45 testes iniciais de modelo falharam pela ausência das entidades com Django/PostgreSQL configurados. Implementados RoutePoint, RideOffer, Waypoint, migração estrutural e catálogo histórico/reversível. Corrigida colisão de e-mails nas fixtures sintéticas; suíte final ampliada para 54 casos aprovados (inclui preparação).
- Cobertos: nomes/códigos, campos obrigatórios e comprimentos, motorista ativo e usuário desabilitado consultado do banco, origem/destino distintos, vagas positivas sem truncamento fracionário e limites técnicos, horário futuro/igual/passado/sem fuso e manutenção de histórico; snapshot de veículo, zero paradas, ordem de paradas, posição válida, UNIQUE/CHECK/FK SQL, PROTECT/CASCADE e funções de ida/volta do catálogo.
- Comando: `venv/Scripts/python.exe -m pytest tests/test_rides_offer.py --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature002.json --junitxml=test-results-feature002.xml`. Resultado: 54 aprovados; cobertura combinada 97,29729729729729%, linhas 112/112 (100%) e ramificações 32/36 (88,88888888888889%). Relatórios separados dos da Feature 001, README com bloco próprio da fundação.
- `manage.py migrate --plan` conferido; `migrate --noinput` aplicou `rides.0001_initial` e `0002_seed_route_points` no PostgreSQL local `carona_univille_db`. `showmigrations rides` confirmou ambas aplicadas; introspecção confirmou constraints nomeadas e quatro pontos do catálogo. pytest aplicou também as migrações no PostgreSQL de testes. Teste de reversão usa as funções da migração sem reverter banco local ou apagar seus dados.
- Regressão dos seis módulos existentes da Feature 001: 152 aprovados. Total das duas execuções: 206 casos aprovados, com métricas mantidas por feature. `manage.py check` sem problemas; `makemigrations --check --dry-run` sem diferenças; editor sem erros nos arquivos verificados; `git diff --check` sem erros.
- Limites preservados: escrita de publicação atômica, autoria da sessão e rechecagem sob bloqueio pertencem à T003. Contiguidade 1..N depende do serviço futuro, não de CHECK SQL; full_clean/save não são executados por bulk/update/SQL. Não foram criadas interfaces, rotas, formulários, serviços, frota, matching, reserva ou cancelamento.
- T001 e T002 locais e T013 do roadmap concluídas; T003–T007 e T014–T016 do roadmap não executadas. Alterações preexistentes preservadas; nenhum staging ou commit.

## Evidência — roadmap T014 parcial / Feature 002 T003 local (2026-11-22)

- Após identificar T003/T004 como correspondências da T014, usuário confirmou executar somente T003. Dependência T002 concluída. REQ-004, REQ-002 e REQ-003; FR-001–FR-008 no recorte de publicação. T004 continua aberta; não marcar T014 integralmente.
- TDD: 16 testes de publicação falharam inicialmente por ausência de rota/serviço. Implementados RideOfferForm e formset, serviço desacoplado publish_offer, mixin de motorista ativo, RideCreateView, rota de criação, template e JavaScript local; placeholder `/caronas/` preservado.
- Serviço reconsulta/bloqueia conta na transação e verifica vínculo/papel/flag técnica, ignora autoria do cliente, valida trajeto completo e gera posições 1..N. Falha na segunda parada reverte oferta e primeira parada. Veículo obrigatório e validações básicas dos modelos aplicadas desde esta etapa.
- Verificações: GET do formulário, trajeto direto/com duas paradas, autoria adulterada, visitante/pendente/passageiro em GET/POST, CSRF real, horário inválido, vagas fracionárias, placa obrigatória, repetição de extremo e rechecagem de motorista alterado no banco. Dados exclusivamente sintéticos.
- `venv/Scripts/python.exe -m pytest tests/test_rides_offer.py --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature002.json --junitxml=test-results-feature002.xml`: 70 aprovados (54 anteriores + 16 novos), PostgreSQL. Cobertura combinada 97,89915966386555%; linhas 191/192 e ramificações 42/46. Relatórios e bloco Feature 002 do README atualizados, sem sobrescrever os indicadores Feature 001.
- Regressão dos seis módulos existentes da Feature 001: 152 aprovados; total de 222 casos nas duas execuções. `manage.py check` sem problemas; `makemigrations --check --dry-run` sem diferenças; diagnósticos Python sem erros. Nenhuma mudança de esquema.
- Navegador: prévia HTML gerada pelo template real usando catálogo local, sem publicação no banco pela prévia. Adicionar três paradas, selecionar pontos e remover a do meio preservou ordem/valores, nomes e IDs consecutivos e TOTAL_FORMS=2. Persistência HTTP/CSRF verificada separadamente pelo cliente Django nos testes. Não se alega fluxo completo em servidor/navegador nem conclusão da demo final.
- Limites: 302 de sucesso para `/caronas/minhas-ofertas/`, cuja lista pertence à T005; destino testado sem segui-lo. Reutilização de veículo, limpeza de placa em reapresentação e bateria complementar de erros são T004 e não foram implementadas nesta rodada. T004–T007 e restante da T014 permanecem abertos. Sem staging ou commit; alteração preexistente do histórico preservada.

## Evidência — roadmap T014 / Feature 002 T004 local (2026-11-22)

- Ao solicitar T015, foi identificada dependência T004 local pendente. Usuário autorizou o caminho recomendado; escopo informado e executado: somente T004 local, encerrando a T014. T005 local/T015 não executada. Dependência T003 satisfeita; REQ-004, REQ-003; FR-004–FR-008 e US2.1–2.3.
- GET sugere apenas modelo/cor/placa da última oferta do motorista da sessão, por created_at/id decrescentes. Primeira oferta sem dados alheios; sem pré-preencher trajeto, horário ou vagas. POST cria novo snapshot e não altera registros anteriores.
- Em erro de campo, serviço ou paradas, placa é removida do formulário reapresentado; instrução pede nova digitação. Demais campos e seleções das paradas são mantidos. Management form ausente/não numérico, total negativo e initial incompatível são rejeitados sem escrita. Demais validações e rollback reutilizam modelos/serviço existentes, sem alteração de esquema.
- TDD: execução inicial selecionou 33 casos (24 novos e nove existentes), com 20 falhas e 13 aprovações. Quatro falhas eram comparação indevida de string HTTP com inteiro no teste de preservação de ponto; ajustada após inspeção. Lacunas reais de pré-preenchimento, placa e management form corrigidas; acrescentados três casos para extremos iguais, feedback de erro do serviço e catálogo inexistente no serviço.
- Resultado final: 97 testes da Feature 002 aprovados (27 novos nesta rodada), PostgreSQL. `venv/Scripts/python.exe -m pytest tests/test_rides_offer.py --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature002.json --junitxml=test-results-feature002.xml`.
- Regressão dos seis módulos da Feature 001: 152 aprovados, sem alterações em identidade/acesso. Total das duas execuções: 249 casos. Cobertura de rides: 98,83268482490273% combinada, linhas 205/205 (100%) e ramificações 49/52 (94,23076923076923%). Relatórios e README separados por feature.
- `manage.py check` sem problemas; `makemigrations --check --dry-run` sem diferenças; diagnósticos dos arquivos Python alterados sem erros; `git diff --check` sem erros. Sem novas migrações ou mudança no banco local.
- Critérios T004 atendidos e T014 do roadmap encerrada. T005/T015 agora pode ser executada em rodada própria; destino `/caronas/minhas-ofertas/` ainda não implementado nesta rodada. Nenhum staging ou commit; alterações preexistentes preservadas.

## Evidência — roadmap T015 / Feature 002 T005 local (2026-11-22)

- Correspondência única: consulta própria = T005 local; dependência T004 concluída. REQ-004, REQ-003 e REQ-002; FR-001, FR-009–FR-011; US3.1–3.3. Nenhuma decisão pendente afeta esta tarefa.
- Implementados MyOffersView, rota `rides:my-offers` em `/caronas/minhas-ofertas/` e template. Filtro obrigatório driver da sessão, independentemente dos parâmetros; ordenação por departure_at/created_at/id e paradas por posição. Select_related de extremos e Prefetch de paradas/pontos evitam consultas por linha; teste confirma duas consultas do queryset.
- Lista mostra itinerário, saída no fuso America/Sao_Paulo, vagas ofertadas, modelo e cor. Omite e-mail e placa, inclusive conteúdo oculto. Vazio apresenta mensagem e link de criação. Mixin exige motorista ativo; não implementa edição, exclusão, cancelamento ou contador de reservas. Rota de criação já existente preservada.
- TDD: 11 testes novos falharam antes por ausência de rota/view; após implementação, 108 testes de rides aprovados no PostgreSQL. Cobertos vazio, ordem e desempate, sequência das paradas, isolamento entre autores/query adulterada, privacidade, acesso anônimo/pendente/passageiro, quatro métodos de escrita rejeitados sem alteração, consultas otimizadas e redirecionamento após publicação seguido até HTTP 200 na lista.
- Comando: `venv/Scripts/python.exe -m pytest tests/test_rides_offer.py --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature002.json --junitxml=test-results-feature002.xml`. Cobertura combinada 98,86792452830188%; linhas 213/213 (100%) e ramificações 49/52 (94,23076923076923%). Relatórios e bloco próprio do README sincronizados.
- Regressão dos seis módulos Feature 001: 152 aprovados; total das duas execuções 260 casos. `manage.py check` sem problemas; `makemigrations --check --dry-run` sem diferenças; diagnósticos Python sem erros; `git diff --check` sem erros. Sem mudança de esquema.
- Template validado pela renderização HTTP em testes, sem afirmar inspeção visual manual. Aceitação abrangente T006 local/T016 do roadmap e qualidade final T007 local não executadas nesta rodada. T005 local e T015 do roadmap concluídas. Alterações preexistentes preservadas; nenhum staging ou commit.

## Evidência — roadmap T016 / Feature 002 T006 local (2026-11-22)

- Correspondência única por objetivo e requisito: aceitação integrada = T006 local. Dependência T005 satisfeita; REQ-004, REQ-002, REQ-003 e REQ-017; SC-001–SC-004. Nenhum artefato ou decisão pendente afeta o recorte.
- Acrescentados seis testes `test_acceptance_*` e fixture local `academic_journey` em `tests/test_rides_offer.py`. Cadastro, login manual e ativação HTTP reais, sem force_login/criação de conta via ORM; cliente exige CSRF e recebe o token de cada formulário, inclusive após rotação no login.
- Dois cenários de jornada completa (trajeto direto e com duas paradas) com dois motoristas em sessões separadas, autoria adulterada, ordem de paradas, persistência e consulta própria. Verificado que cada autor vê somente sua oferta e que nenhuma listagem contém placa ou e-mail dos envolvidos.
- Outros cenários: dado inválido sem escrita e reenvio corrigido; falha sintética na segunda parada pelo POST HTTP com rollback de oferta/primeira parada e ausência de sucesso; recusa acadêmica por registro inelegível e e-mail ausente, seguida de tentativa de publicação bloqueada. Dados exclusivamente sintéticos.
- Primeira execução dos seis cenários passou contra a aplicação existente. Por ser tarefa de aceitação, não foi criada falha artificial nem alterado código de produção. Nenhum defeito de produção foi demonstrado pelo novo recorte.
- Suíte Feature 002: 114 aprovados. Comando: `venv/Scripts/python.exe -m pytest tests/test_rides_offer.py --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature002.json --junitxml=test-results-feature002.xml`. Cobertura combinada 98,86792452830188%; linhas 213/213 (100%) e ramificações 49/52 (94,23076923076923%). Relatórios e bloco próprio do README sincronizados.
- Regressão dos seis módulos existentes de accounts: 152 aprovados no PostgreSQL; total das duas execuções 266 casos. Testes anteriores preservados. `manage.py check` sem problemas; editor sem diagnósticos no teste alterado; `git diff --check` sem erros.
- Validação integrada pelo cliente HTTP Django e PostgreSQL de testes, sem alegar automação completa em navegador ou medição de tempo humano. Qualidade, script e demonstração final da T007 local não executados. T006 local e T016 do roadmap concluídas. Alterações preexistentes preservadas; nenhum staging ou commit.
