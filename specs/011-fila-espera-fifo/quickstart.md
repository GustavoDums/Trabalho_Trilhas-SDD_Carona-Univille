# Verificação da T039

Em PostgreSQL isolado, execute `python manage.py migrate --plan`, `python -m pytest tests/test_waitlist.py -k test_fifo` e `python -m pytest tests/test_waitlist.py`.

O teste isolado cria uma oferta futura lotada, inscreve dois passageiros fictícios e libera capacidade sem acionar o cancelamento. Ao chamar o serviço de repasse, o primeiro elegível recebe a reserva e o seguinte continua à espera.

## Verificação da T040

Execute `python -m pytest tests/test_waitlist_flow.py`. Abra **Minhas reservas** com as duas contas da fila e confira as posições 1 e 2. Cancele a reserva com o titular. A primeira conta recebe a confirmação em **Notificações** e a segunda passa à posição 1. Repita o cancelamento para conferir que a mesma vaga não é repassada novamente.
