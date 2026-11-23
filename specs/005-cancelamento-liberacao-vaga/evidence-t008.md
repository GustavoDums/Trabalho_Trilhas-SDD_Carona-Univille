# Feature 005 / T008 local — Remoção de ofertas do painel

**Data** 2026-11-23 · **Requisitos** REQ-003, REQ-007, REQ-014, REQ-017–REQ-019 · **Aceite** FR-006 e SC-006.

| Critério | Verificação |
| --- | --- |
| Remoção de carona aberta antes da partida | POST com sessão e CSRF cancela a oferta e a reserva, grava uma ocorrência de auditoria, notifica o passageiro e retira o cartão. A repetição preserva a data de remoção e evita novos eventos. |
| Remoção de carona já cancelada | Mesmo depois da partida, a ação preserva a data de cancelamento, a auditoria, as notificações e o vínculo da oferta com a série recorrente. |
| Horário limite | Na partida de uma carona aberta, a interface explica o limite e a rota recusa a mudança de estado. |
| Autorização e falha parcial | Os testes cobrem POST obrigatório, CSRF, sessão, titularidade, oferta inexistente e reversão conjunta quando a gravação da remoção falha. |
| Interface | No Microsoft Edge, com dados fictícios em 390 px e 1.200 px, a lixeira foi confirmada no canto superior direito, com abertura pela tecla Espaço e confirmação contida na largura do cartão. |
| Django e banco local | `manage.py check` e `makemigrations --check --dry-run` aprovados. Migração `rides.0008` aplicada e `migrate --check` aprovado. Servidor local respondeu com 200 no login e redirecionou o painel anônimo para autenticação. |

## Testes

O comando `python -m pytest tests/test_offer_removal.py tests/test_cancellation_flow.py tests/test_rides_offer.py` aprovou **191 testes** no PostgreSQL, incluindo os cinco casos novos. [Roteiro de verificação](quickstart.md#remoção-do-painel--t008).

A suíte consolidada aprovou **997 testes**, com zero falhas e zero ignorados. A cobertura foi de **98,51% combinada**, **98,98% em linhas** e **96,43% em ramificações**. A meta de 80% foi atendida globalmente e em todos os 37 módulos críticos. [JSON](../../coverage.json) · [JUnit](../../test-results-t043.xml) · [README](../../README.md).
