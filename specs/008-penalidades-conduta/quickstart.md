# Quickstart de validação: Feature 008

O modelo da T002 e a integração da T003 podem ser verificados no passo abaixo. Os fluxos de denúncia, suspensão e extrato têm tarefas próprias.

1. Fechar decisões da [spec](spec.md), implementar dependências, usar venv e PostgreSQL existentes, sem imprimir segredos.
2. Após implementação, da raiz:

~~~powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe -m pytest tests/test_penalties.py -q --tb=short
~~~

3. Para a T002/T003, verificar unicidade, rollback, dedução decimal, nota automática de registros existentes e projeção de suspensão com dados fictícios. Cancelamento tardio de reserva ou de oferta deve persistir uma única penalidade para quem cancelou. Cancelamento no limite do prazo mantém a nota. As tarefas de fluxo completam SC-001 a SC-004 da [spec](spec.md).
4. Concorrência requer conexões PostgreSQL independentes e testes transacionais; SQLite/mocks de lock não comprovam integridade.
5. Rodar regressão das dependências; script de qualidade da tarefa final gera JUnit e cobertura identificados por feature, >=80% de linhas e ramificações críticas; README somente com números reais. Auditoria MVP da 005 consolida REQ-001–REQ-007.
6. Conferir [interface](contracts/web-routes.md), tentativa por terceiros e evidência de migração. Não marcar checklist se faltar decisão, teste ou meta.
