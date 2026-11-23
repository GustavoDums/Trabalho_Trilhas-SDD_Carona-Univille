# Evidência — Feature 003 / T001–T003 locais / roadmap T017–T018

Data: 2026-11-22. Requisitos: REQ-005, REQ-002, REQ-003, REQ-017–REQ-019.
Escopo autorizado após identificação de dependências: preparação compatível, matching, formulário e cartões sem nota. Sem view/rota da busca (T004 local/T019) e sem conclusão da qualidade final (T005).

## T001 — preparação sem alteração de comportamento

- Baseline de ofertas: 114 testes aprovados.
- Teste de contrato de import/assinatura adicionado antes da refatoração: 115 aprovados.
- Movido services.py para services/offers.py com alteração somente do import relativo de modelos; __init__.py reexporta publish_offer.
- Depois: os mesmos 115 aprovados e manage.py check sem problemas. Não fabricar falha de comportamento para refatoração.
- Sem necessidade de alterar mocks: alvos existentes continuam válidos.

## T002 — roadmap T017 / matching

Testes escritos antes do módulo. A primeira execução revelou erro na fixture (criação de conta ATIVA contrariava estado inicial PENDENTE). Fixture corrigida para criar PENDENTE e ativar posteriormente; essa falha não conta como evidência de produto.

Vermelho válido: **65 falhas**, todas pela ausência de rides.services.matching_service (ModuleNotFoundError), sem erros de fixture. Verde depois: **65 aprovados** no PostgreSQL.

Cobertura funcional: 16 combinações de pontos, rota direta/ausente/ambígua; ±30min inclusivos e um segundo fora; meia-noite, offsets e precisão; partida estritamente futura; referência na saída da origem com embarque intermediário; autorização reconsultada no banco; ordenação saída/criação/ID; resultado único, DTO imutável sem segredos; ausência de escrita e N+1; relógio capturado uma vez.

## T003 — roadmap T018 / formulário e cartões

Vermelho: **27 falhas** por RideSearchForm inexistente (AttributeError). Verde: **27 aprovados** após implementação.

Testes de ModelChoiceFields/catálogo, campos obrigatórios/distintos, horário inválido, segundos/offset preservados e America/Sao_Paulo independente do fuso ativo; passado permitido, parâmetros extras sem efeito. Renderização por RequestFactory sem endpoint: GET, filtros, inicial/erro/vazio/resultados, DTO público, rótulos escapados e aviso temporal no topo e junto a cada saída. Sem e-mail, placa, nome completo, nota ou reserva nos cartões.

## Regressão e medição desta entrega parcial

Comando executado na venv e PostgreSQL existentes:

~~~powershell
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature003-t018.json --junitxml=test-results-feature003-t018.xml
~~~

**359 aprovados, 0 falhas, 0 erros, 0 ignorados**: 152 de accounts (regressão), 115 de ofertas (114 anteriores + 1 contrato de refatoração), 65 matching e 27 formulário/HTML (92 testes novos funcionais da Feature 003).

Cobertura de rides: **290/290 linhas (100%)**, **69/72 ramificações (95.83333333333333%)**, combinada **99.17127071823204%**. Matching isolado: 60/60 linhas e 18/18 ramificações (100%). Meta >=80% atendida nesse conjunto; isto não é cobertura global de accounts nem da futura view.

Relatórios: [cobertura](../../coverage-feature003-t018.json), [JUnit](../../test-results-feature003-t018.xml). [README](../../README.md) identifica a entrega parcial sem sobrescrever medições anteriores.

Outras verificações: manage.py check sem problemas; makemigrations --check --dry-run: No changes detected; showmigrations rides: 0001 e 0002 aplicadas. Não há nova migração nem mudança de esquema.
Diagnósticos do editor nos arquivos novos/alterados: sem erros.

## Limites

T004/T019 e T005 permanecem abertas. Acesso HTTP da busca e demo humana SC-005 não foram executados e não são dados como concluídos. Quickstart distingue serviço/formulário disponíveis de roteiro HTTP futuro. Sem staging/commit; alterações prévias de prompts preservadas.

## Arquivos desta rodada

Código:
- [formulário](../../rides/forms.py).
- Módulo antigo rides/services.py movido para [services/offers.py](../../rides/services/offers.py), com [reexportação](../../rides/services/__init__.py).
- [matching_service.py](../../rides/services/matching_service.py).
- [search.html](../../rides/templates/rides/search.html) e [_search_result.html](../../rides/templates/rides/_search_result.html).
- [test_matching.py](../../tests/test_matching.py), [test_ride_search.py](../../tests/test_ride_search.py) e [contrato acrescentado em test_rides_offer.py](../../tests/test_rides_offer.py).

Documentação:
- [spec.md](spec.md), [plan.md](plan.md), [tasks.md](tasks.md), [quickstart.md](quickstart.md) e este registro.
- [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md) e [README](../../README.md).
- Relatórios de cobertura/JUnit já vinculados acima. Não foram alterados modelos, migrações, views ou rotas.
