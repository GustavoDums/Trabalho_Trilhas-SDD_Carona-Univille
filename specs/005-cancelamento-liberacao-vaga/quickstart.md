# Quickstart de validação: Feature 005

**Estado em 2026-11-23**: T001–T005 implementadas/verificadas; 86 testes de prazos/fluxo, 641 na regressão completa e migração 0004 aplicada no PostgreSQL local. [Evidência](evidence-t024.md). Cancelamento de oferta verificado na T004 ([evidência](evidence-t025.md)); interface de reserva verificada na T005 ([evidência](evidence-t005.md)); interface de oferta aguarda T006.

1. D005-01/D005-02 da [spec](spec.md) homologadas; usar venv e PostgreSQL existentes, sem imprimir segredos.
2. Da raiz, repetir a verificação da API de cancelamento de reserva e oferta:

~~~powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe -m pytest tests/test_cancellation_deadlines.py tests/test_cancellation_flow.py
~~~

3. Executar SC-001, SC-002, SC-003, SC-004, SC-005 da [spec](spec.md), com contas/ofertas fictícias; conferir banco antes/depois, autorização e rollback.
4. Concorrência requer conexões PostgreSQL independentes e testes transacionais; SQLite/mocks de lock não comprovam integridade.
5. Rodar regressão das dependências; script de qualidade da tarefa final gera JUnit e cobertura identificados por feature, >=80% de linhas e ramificações críticas; README somente com números reais. Auditoria MVP da 005 consolida REQ-001–REQ-007.
6. Conferir [interface](contracts/web-routes.md), tentativa por terceiros e evidência de migração. Não marcar checklist se faltar decisão, teste ou meta.

## Interface de reserva — T005

Entrar com passageiro sintético ativo que possua reserva confirmada. Em /caronas/minhas-reservas/, abrir “Cancelar reserva”, conferir a regra e acionar “Confirmar cancelamento”. O POST com CSRF redireciona à mesma lista, com estado CANCELADA e sem placa/nome completo da contraparte. A busca reflete a liberação. Abrir a confirmação sem enviar não cancela; GET da rota de ação retorna 405. Na partida ou depois, POST retorna 400 e preserva a reserva. Motorista/terceiro não pode cancelar essa reserva. Repetição não duplica auditoria. Esses casos são automatizados em tests/test_cancellation_flow.py; conferência visual em navegador não realizada nesta rodada. Cancelamento de oferta pela interface ainda aguarda T006.
