# Verificação da T039

Em PostgreSQL isolado, execute `python manage.py migrate --plan`, `python -m pytest tests/test_waitlist.py -k test_fifo` e `python -m pytest tests/test_waitlist.py`.

Com uma oferta futura lotada e passageiros fictícios, faça dois ingressos pela busca. Ao liberar capacidade e acionar o serviço, confira que o primeiro elegível recebe a reserva e que o seguinte continua à espera. O teste integrado com o cancelamento pertence à T040.
