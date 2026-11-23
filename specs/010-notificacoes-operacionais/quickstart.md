# Quickstart: T037 e T038

Em um banco PostgreSQL isolado com dados fictícios, confira a migração e rode os testes do recorte.

~~~powershell
.\venv\Scripts\python.exe manage.py migrate --plan
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe -m pytest tests/test_notifications.py -q --tb=short
~~~

Confirme uma reserva, cancele-a e compare os destinatários com [a matriz](contracts/events.md). Para o cancelamento de oferta, inclua duas reservas confirmadas e uma previamente cancelada. Confira o aviso único do motorista, os dois avisos do lote e a ausência de aviso de lote para a reserva antiga.

Reexecute o evento e confirme a identidade dos avisos. Force uma falha da escrita em ambiente de teste e confira o rollback da operação original.

Para a T038, entre com o titular de um aviso sintético. Confira o contador no sino, abra a lista e marque o aviso como lido. O contador diminui e o aviso continua na lista com estado **Lida**. Entre com outra conta e confira que a lista contém somente os avisos dela. Os testes integrados também verificam CSRF, sessão pendente e o HTTP 404 ao tentar marcar um aviso de terceiro.
