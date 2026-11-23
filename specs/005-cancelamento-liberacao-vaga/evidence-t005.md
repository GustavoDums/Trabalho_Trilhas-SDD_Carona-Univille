# Evidência — Feature 005 / T005 local / parcela da T026

Data: 2026-11-23. Requisitos REQ-007, REQ-003, REQ-017; FR-001/FR-004; SC-004. Dependências T003 desta feature e T005 da Feature 004 concluídas. T026 corresponde a T005/T006; usuário confirmou somente T005, após esclarecimento. T006 e T007 seguem abertas, assim como T026 do roadmap.

## Entrega

CancelBookingView e rota nomeada rides:cancel_booking (POST /caronas/reservas/<booking_id>/cancelar/). Formulário de confirmação em details/summary acessível na lista de reservas, apenas para passageiro com reserva confirmada. Texto explica 2h inclusivas pela saída da origem, tardio anterior à partida aceito e recusa na partida/depois. Sem JavaScript obrigatório.

A view usa ator da sessão e reserva da URL, delega ao serviço transacional existente e não confia em IDs/next enviados no corpo. Sucesso/repetição redireciona ao endereço fixo da lista própria e informa estado cancelado; recusa temporal retorna 400 com alerta e outros erros de validação têm texto genérico. Terceiros recebem 403; demais restrições de sessão/vínculo seguem middleware existente. Métodos não POST retornam 405 para ator elegível; CSRF obrigatório.

Projeção existente de reservas remove placa e nome completo da contraparte após CANCELADA. Busca mostra imediatamente a disponibilidade derivada; capacidade não alterada. Serviços/modelos/migrações não precisaram de alterações. Não implementados cancelamento de oferta pela interface, notificações ou penalidades.

## TDD e regressão

- Antes da produção: 20 casos novos executados; 17 falhas por rota/CSRF/confirmação ausentes, 3 aprovados por controles já existentes.
- Depois: 86 testes de cancelamento aprovados (66 anteriores + 20 novos).
- Regressão completa no PostgreSQL: 641 aprovados, 0 ignorados/falhas, 80.07s; 621 anteriores preservados, incluindo concorrência real dos serviços.
- Novos testes: rota nomeada e visibilidade da confirmação; CSRF válido/ausente/inválido; GET/HEAD/PUT/PATCH/DELETE/OPTIONS 405; ator anônimo, pendente, desabilitado, terceiro e motorista; corpo com IDs/next forjados; limites 120min01s/120min/119min59s, partida/pós-partida; estado preservado em recusa; idempotência; liberação na busca e revogação dos dados privados. Relógio controlado e dados sintéticos.
- rides/: 605/606 linhas (99.83498349834983%), 160/164 ramificações (97.5609756097561%), combinada 99.35064935064935%. rides/views.py: 111/111 linhas, 12/12 ramificações, ambas 100%. Meta >=80% atendida.
- Django check sem problemas; makemigrations --check --dry-run sem alterações; migrate --plan sem operações. Banco local confirmado postgresql. Não houve escrita no banco local de desenvolvimento; testes usam banco de testes.
- Diagnósticos do editor sem erros nos três arquivos Python alterados. git diff --check sem erros. Pré-requisitos Spec Kit atendidos; sem hooks/checklists adicionais. Ponteiro de feature preservado. Git inicialmente limpo, sem staging/commit.

[JSON](../../coverage-feature005-t005.json) e [JUnit](../../test-results-feature005-t005.xml). Relatórios anteriores preservados.

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_cancellation_flow.py -k booking_cancel_ -q --tb=short
.\venv\Scripts\python.exe -m pytest tests/test_cancellation_deadlines.py tests/test_cancellation_flow.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature005-t005.json --junitxml=test-results-feature005-t005.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
~~~

Quickstart atualizado e fluxo HTTP verificado por testes Django; não houve inspeção visual em navegador nesta rodada. Não concluir T006/T007 ou T026 integral com esta evidência.

## Arquivos alterados/criados

- [views.py](../../rides/views.py), [urls.py](../../rides/urls.py), [my_bookings.html](../../rides/templates/rides/my_bookings.html), [test_cancellation_flow.py](../../tests/test_cancellation_flow.py).
- [spec.md](spec.md), [plan.md](plan.md), [tasks.md](tasks.md), [contratos](contracts/web-routes.md), [quickstart.md](quickstart.md) e esta evidência.
- [README](../../README.md), [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md), JSON/JUnit citados acima.

Commit sugerido: feat(005/T005): permitir cancelamento de reserva por POST — REQ-007, REQ-003, REQ-017
