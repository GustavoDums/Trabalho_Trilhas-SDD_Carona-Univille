# Quickstart de validação: Feature 004

**Estado em 2026-11-22**: modelo/migração T002 local (T020) implementado, 49 testes de modelo aprovados e migração 0003 aplicada no PostgreSQL local. [Evidência](evidence-t020.md). Serviço/concorrência T003 também concluído: 33 testes aprovados e prova da última vaga em [evidence-t021.md](evidence-t021.md). Disponibilidade T006 também concluída ([evidência](evidence-t006.md)); HTTP de reserva e qualidade final continuam pendentes.

1. D004-01/D004-02 da [spec](spec.md) homologadas. Usar venv e PostgreSQL existentes, sem imprimir segredos. Para repetir a verificação do modelo: `venv/Scripts/python.exe -m pytest tests/test_booking_flow.py`.
2. Modelo e serviço disponíveis para repetir verificações abaixo. A busca mostra vagas disponíveis e esgotamento após T006; o roteiro HTTP de reserva aguarda T004/T005:

~~~powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe -m pytest tests/test_booking_flow.py tests/test_concurrency_booking.py tests/test_ride_search.py
~~~

3. Executar SC-001, SC-002, SC-003, SC-004 da [spec](spec.md), com contas/ofertas fictícias; conferir banco antes/depois, autorização e rollback.
4. Concorrência requer conexões PostgreSQL independentes e testes transacionais; SQLite/mocks de lock não comprovam integridade.
5. Rodar regressão das dependências; script de qualidade da tarefa final gera JUnit e cobertura identificados por feature, >=80% de linhas e ramificações críticas; README somente com números reais. Auditoria MVP da 005 consolida REQ-001–REQ-007.
6. Conferir [interface](contracts/web-routes.md), tentativa por terceiros e evidência de migração. Não marcar checklist se faltar decisão, teste ou meta.
