# Evidência — Feature 003 / T004 local / roadmap T019

Data: 2026-11-22. Requisitos: REQ-005 e REQ-017; acesso/privacidade REQ-002 e REQ-003; medição REQ-018/REQ-019.

## Escopo e decisão

Correspondência única pelo objetivo: T019 do roadmap = T004 local, view e rota de busca para passageiro ativo. T001–T003 locais concluídas anteriormente.
Usuário confirmou seguir plano/tarefa local **sem paginação** e corrigir o termo legado na tabela do roadmap.
T005 local (aceitação final, script próprio, inspeção visual e demo humana) permanece aberta.

## TDD

Antes de alterar produção, 36 casos HTTP foram acrescentados ao módulo existente de 27 casos de formulário/renderização.
Execução vermelha: **32 falhas e 31 aprovações**. Falhas esperadas: HTTP 404 onde se esperavam respostas da busca, ausência de RideSearchView e NoReverseMatch de rides:search. Entre as aprovações já existentes estavam middleware e preservação de rotas.
Após implementação houve uma falha de comparação no próprio teste: QueryDict foi comparado diretamente a dict. Corrigida para comparar .dict(), mantendo todos os valores esperados dos filtros; não foi mudança de comportamento do produto.
Verde: **63 aprovados**, incluindo os mesmos 27 anteriores e 36 novos.

## Critérios verificados

- FR-001 / SC-004: visitante e desabilitado vão ao login com next, pendente à ativação, motorista recebe 403, passageiro ativo acessa; mixin também recusa estados proibidos quando chamado sem middleware.
- FR-002/FR-009: inicial com form não vinculado e searched=False; qualquer parâmetro inicia tentativa; inválidos/ausentes/iguais têm erro sem chamar matching; estado válido vazio distinto.
- FR-003–FR-007: formulário gera SearchQuery com PKs e datetime aware; sessão encaminhada ao serviço; duas ofertas de motoristas diferentes, ordenação, unicidade, embarque/desembarque intermediários e inversão; matriz completa de rota/bordas já coberta pela regressão de matching.
- FR-008 / SC-003: contexto de resultados contém apenas SearchResult, HTML sem nomes completos/e-mails/placa e sem JSON/reserva; mantém aviso de saída da origem.
- FR-010: próxima consulta exclui motorista pendente, desabilitado ou papel inadequado, oferta passada, partida igual a now e instante fora da janela; extras não alteram janela, autor ou usuário.
- FR-011 / SC-004: snapshot integral de ofertas/paradas/catálogo/contas inalterado pelo GET; POST/PUT/PATCH/DELETE devolvem 405 sem executar matching. GETs usam Client com CSRF habilitado; testes de métodos usam Client padrão para isolar 405 da recusa CSRF.
- Erro de revalidação do serviço vira erro de formulário; PermissionDenied permanece 403; nenhuma resposta expõe segredos.
- Rotas de publicação, minhas ofertas e placeholder /caronas/ preservadas e verificadas.

## Regressão e relatórios

Comando executado na venv do projeto e PostgreSQL existente:

~~~powershell
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature003-t019.json --junitxml=test-results-feature003-t019.xml
~~~

**395 aprovados; 0 falhas, 0 erros e 0 ignorados.**
Distribuição: 152 accounts + 115 ofertas (regressão), 65 matching e 63 formulário/HTTP. São 128 testes funcionais acumulados da Feature 003 e **36 novos nesta T004**.

Cobertura de rides: **310/310 linhas (100%)**, **71/74 ramificações (95.94594594594595%)**, combinada **99.21875%**. Matching: 60/60 linhas e 18/18 ramificações; views: 66/66 linhas e 6/6 ramificações. Meta >=80% atendida no conjunto medido, não cobertura global de accounts.

Relatórios versionáveis: [coverage-feature003-t019.json](../../coverage-feature003-t019.json) e [test-results-feature003-t019.xml](../../test-results-feature003-t019.xml). Medições anteriores preservadas.
manage.py check: sem problemas. makemigrations --check --dry-run: No changes detected.
Editor: sem diagnósticos nos arquivos Python alterados. Whitespace e links conferidos ao encerrar.

## Arquivos criados/alterados

- [rides/views.py](../../rides/views.py): ActivePassengerRequiredMixin e RideSearchView.
- [rides/urls.py](../../rides/urls.py): rides:search em /caronas/buscar/.
- [tests/test_ride_search.py](../../tests/test_ride_search.py): 36 casos HTTP adicionais.
- [spec.md](spec.md), [plan.md](plan.md), [tasks.md](tasks.md), [quickstart.md](quickstart.md), [contracts/web-routes.md](contracts/web-routes.md) e este registro: estado e evidência da entrega.
- [roadmap](../../docs/roadmap-implementacao.md): T019 concluída e paginação removida da descrição histórica conforme confirmação.
- [prompts](../../docs/prompts.md): prompt e confirmação integrais, preservando alteração anterior.
- [README](../../README.md): contagem e cobertura reais desta entrega; relatórios listados acima.

Sem mudanças em modelos, migrações, middleware, matching, formulário ou templates. Sem staging/commit; sem afirmação de demo humana SC-005 executada.
