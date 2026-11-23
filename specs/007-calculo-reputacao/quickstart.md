# Quickstart de validação: Feature 007

**Estado 2026-11-23**: T001 homologada, [cálculo e rebuild explícito](evidence-t030.md) na T002 e recálculo automático na T004. Perfil e busca são critérios da T005.

1. Fechar decisões da [spec](spec.md), implementar dependências, usar venv e PostgreSQL existentes, sem imprimir segredos.
2. Após implementação, da raiz:

~~~powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe -m pytest tests/test_reputation_calc.py
.\venv\Scripts\python.exe -m pytest tests/test_reputation_integration.py -q --tb=short
~~~

3. Executar SC-001, SC-002, SC-003, SC-004 da [spec](spec.md), com contas/ofertas fictícias; conferir banco antes/depois, autorização e rollback.
4. Concorrência requer conexões PostgreSQL independentes e testes transacionais; SQLite/mocks de lock não comprovam integridade.
5. Rodar regressão das dependências; script de qualidade da tarefa final gera JUnit e cobertura identificados por feature, >=80% de linhas e ramificações críticas; README somente com números reais. Auditoria MVP da 005 consolida REQ-001–REQ-007.
6. Conferir [interface](contracts/web-routes.md), tentativa por terceiros e evidência de migração. Não marcar checklist se faltar decisão, teste ou meta.

## Cálculo/rebuild — T002 unificada / T030

API interna: calculate_score(ratings) para conjunto já selecionado de até 20 notas inteiras 1..5; ReputationService.rebuild(*, user_id, at=None) seleciona as últimas 20 recebidas por created_at/id decrescentes com data <= referência e atualiza/cria cache. Sem corte de 30 dias, sem peso por carona; novato 5.00 não é nota virtual. Usar Decimal com arredondamento final HALF_UP. Exemplos 4.60 e 4.00 reproduzidos pelos testes, além de 4.125→4.13.

Sem at, relógio servidor é capturado uma vez após lock do usuário. Referência explícita deve ser aware e é normalizada a UTC; reconstrução histórica é apenas interna, não recebe parâmetros de cliente HTTP. computed_at NULL indica cache ainda não calculado. A migração cria tabela vazia, sem pontuar automaticamente cadastros/avaliações. Rebuild não muda RideReview e é transacional/idempotente com as mesmas fontes e referência. Signals, leitura no perfil/busca e integração de penalidades não foram conectados nesta tarefa.

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_reputation_calc.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature007-t030.json --junitxml=test-results-feature007-t030.xml
~~~

Migração reviews 0002 verificada/aplicada no PostgreSQL local, preservando os dados anteriores. Cenários SC-001/SC-002 cobertos; SC-003/SC-004 dependem da integração T031 e não são concluídos nesta rodada. Sem nova rota para testar em navegador.
