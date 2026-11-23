# Quickstart de validação: Feature 008

O passo abaixo verifica os modelos, o cancelamento, a denúncia, as restrições disciplinares e o extrato.

1. Fechar decisões da [spec](spec.md), implementar dependências, usar venv e PostgreSQL existentes, sem imprimir segredos.
2. Após implementação, da raiz:

~~~powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe -m pytest tests/test_penalties.py tests/test_penalties_flow.py -q --tb=short
~~~

3. Verificar unicidade, rollback, deduções e suspensão com dados fictícios. Em Minhas ofertas, o motorista titular registra a conclusão na partida ou depois. Em Minhas reservas, a contraparte declara a ausência após a tolerância e dentro da janela descrita no [contrato](contracts/web-routes.md). Validar ambos os fluxos e as fronteiras de tempo, incluindo a ausência do motorista sem conclusão.
   Para a T034, verificar que o titular suspenso entra na conta e consulta o extrato, consegue cancelar um compromisso existente e recebe HTTP 403 ao tentar publicar ou reservar. No instante da expiração, repetir a ação e conferir a liberação. Em outra sessão, consultar o extrato e verificar que somente as ocorrências daquela sessão são exibidas.
4. Concorrência requer conexões PostgreSQL independentes e testes transacionais; SQLite/mocks de lock não comprovam integridade.
5. Rodar regressão das dependências; script de qualidade da tarefa final gera JUnit e cobertura identificados por feature, >=80% de linhas e ramificações críticas; README somente com números reais. Auditoria MVP da 005 consolida REQ-001–REQ-007.
6. Conferir [interface](contracts/web-routes.md), tentativa por terceiros e evidência de migração. Não marcar checklist se faltar decisão, teste ou meta.
