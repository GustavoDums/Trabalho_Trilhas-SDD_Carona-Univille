# Evidência — Feature 004 / T006 local / integração T021–T023

Data: 2026-11-22. Requisitos: REQ-006, REQ-003, REQ-017; FR-004 e recorte de busca de SC-004. Governança REQ-018/REQ-019.

## Escopo e dependências

T006 é o ID oficial local, vinculado à integração de disponibilidade dos itens T021/T023 do roadmap. Usuário autorizou esta rodada após conclusão de T003 e reforçou exigência de TDD, regressão e mensagem de commit.
Dependências atendidas: serviço de reserva T003 e busca HTTP Feature 003/T004. Somente matching/cartão e seus testes/contratos são alterados; sem implementar BookRideView, minhas reservas ou rotas de reserva.

## Serviços e apresentação

MatchingService agrega Count distinto das bookings CONFIRMADA por oferta na consulta SQL. CANCELADA não ocupa vaga; todas as confirmações da oferta contam independentemente do trecho. O prefetch de paradas permanece separado. Não há consultas por cartão nem contador persistido.

SearchResult.seats preserva capacidade original; novo campo obrigatório available_seats calcula max(0, seats-confirmadas). Cartão passa a usar available_seats, com singular/plural e Vagas esgotadas para zero, além de informar que a disponibilidade pode mudar até a confirmação.

Filtros de rota, ±30min, futuro, vínculo/papel/habilitação e ordenação permanecem. Oferta compatível esgotada continua visível com saldo zero; não foi criado filtro por saldo. Nenhum novo campo pessoal, contato ou botão de reserva.

BookingService e seu protocolo transacional permanecem **sem alteração**: cartão antigo não substitui checagem sob lock. A regressão de concorrência da T003 continua comprovando uma confirmação, uma recusa e saldo zero no PostgreSQL.

## TDD

Antes da produção: **7 falhas**, todas AttributeError de SearchResult.available_seats ausente; 63 casos anteriores não selecionados nessa execução vermelha.

Após implementação: **70 testes aprovados** em tests/test_ride_search.py (63 anteriores + 7 novos). Testes antigos adaptados apenas à extensão explícita do DTO e ao rótulo de disponibilidade: helper sintético passa available_seats, whitelist inclui o novo campo público e asserção antiga de capacidade é preservada com verificação adicional de saldo.

Casos novos:
1. Confirmações reais pelo BookingService levam saldo 3→2→1→0, com cartão correto; capacidade e ordenação permanecem.
2. CANCELADA não entra na contagem; outra oferta não sofre redução indevida.
3. Reservas em trechos distintos consomem vagas da oferta inteira, sem reutilização por trecho.
4. Rollback da reserva não reduz disponibilidade.
5. Cartão antigo com uma vaga não permite reservar depois de outro passageiro ocupá-la; serviço recusa e nova consulta mostra zero.
6. Snapshot de contas, ofertas, paradas, catálogo e reservas não muda pelo GET; privacidade, filtros e ordenação mantidos.
7. Aumento de duas para seis ofertas com paradas e histórico mantém quantidade de consultas constante, sem duplicar resultados ou contagens.

## Regressão, métricas e verificações

~~~powershell
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature004-t006.json --junitxml=test-results-feature004-t006.xml
~~~

**484 aprovados; 0 falhas, 0 erros, 0 ignorados.**
São 7 novos desta tarefa; 49 modelo + 33 serviço da Feature 004 e 395 de regressão anterior (152 accounts, 115 ofertas, 128 busca).
Feature 004 acumula 89 casos; os 70 do módulo de busca não são todos novos nem exclusivos desta feature.

Cobertura rides: **403/403 linhas (100%)**, **109/112 ramificações (97.32142857142857%)**, combinada **99.41747572815534%**. MatchingService: 61/61 linhas e 18/18 ramificações; booking_service: 51/51 linhas e 20/20 ramificações (100%). Meta >=80% atendida no conjunto, sem atribuir essa cobertura a accounts.
Relatórios: [coverage-feature004-t006.json](../../coverage-feature004-t006.json) e [test-results-feature004-t006.xml](../../test-results-feature004-t006.xml). Relatórios anteriores preservados.

Django check: sem problemas. makemigrations --check --dry-run: No changes detected. Sem diagnósticos do editor nos arquivos alterados. Links e whitespace conferidos ao encerrar. Coverage não mede templates; singular/plural, esgotamento, privacidade e escape são verificados no HTML renderizado.

## Arquivos criados/alterados

Produção/testes:
- [matching_service.py](../../rides/services/matching_service.py).
- [_search_result.html](../../rides/templates/rides/_search_result.html).
- [test_ride_search.py](../../tests/test_ride_search.py).
- [test_matching.py](../../tests/test_matching.py).

Contratos compartilhados da busca:
- [spec da Feature 003](../003-busca-rota-horario/spec.md), [plano](../003-busca-rota-horario/plan.md), [DTO canônico](../003-busca-rota-horario/data-model.md) e [contrato de cartões](../003-busca-rota-horario/contracts/web-routes.md), com evolução explicitamente atribuída à Feature 004/T006; sem alterar IDs/checkboxes da 003.

Rastreabilidade desta feature:
- [spec.md](spec.md), [plan.md](plan.md), [tasks.md](tasks.md), [data-model.md](data-model.md), [research.md](research.md), [contracts/web-routes.md](contracts/web-routes.md), [quickstart.md](quickstart.md) e este registro.
- [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md), [README](../../README.md) e relatórios acima.

## Limites

T006 concluída. T004/T005 de interface/fluxo de reserva e T007 de qualidade final continuam abertas; o item T023 do roadmap permanece aberto por depender desses componentes. Consulta própria de reservas e liberação privada de dados não foram antecipadas.

Sem mudança em modelos, migrações, BookingService, publicação, middleware, formulários, views ou rotas. Sem staging ou commit. Roteiros humanos/demonstração final continuam pendentes nas tarefas próprias.
