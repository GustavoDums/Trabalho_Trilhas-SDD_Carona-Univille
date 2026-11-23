# Quickstart de validação: Feature 006

**Estado 2026-11-23**: T001 homologada e T002 unificada concluída ([evidência](evidence-t028.md)). Serviços e interface T004 unificada disponíveis ([evidência T029](evidence-t029.md)); T005 incorporada, qualidade final T006 pendente.

1. Fechar decisões da [spec](spec.md), implementar dependências, usar venv e PostgreSQL existentes, sem imprimir segredos.
2. Após implementação, da raiz:

~~~powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe -m pytest tests/test_reviews.py
~~~

3. Executar SC-001, SC-002, SC-003 da [spec](spec.md), com contas/ofertas fictícias; conferir banco antes/depois, autorização e rollback.
4. Concorrência requer conexões PostgreSQL independentes e testes transacionais; SQLite/mocks de lock não comprovam integridade.
5. Rodar regressão das dependências; script de qualidade da tarefa final gera JUnit e cobertura identificados por feature, >=80% de linhas e ramificações críticas; README somente com números reais. Auditoria MVP da 005 consolida REQ-001–REQ-007.
6. Conferir [interface](contracts/web-routes.md), tentativa por terceiros e evidência de migração. Não marcar checklist se faltar decisão, teste ou meta.

## Domínio de avaliação — T002 unificada

ReviewService em reviews/services/review_service.py fornece complete_offer(user, offer_id, clock=None) e create_review(user, offer_id, reviewed_user_id, rating, comment='', clock=None), apenas argumentos nomeados. Na aplicação, clock deve ser omitido para usar relógio do servidor; injeção é suporte a testes determinísticos. Conclusão exige motorista titular ativo e partida atingida; repetição preserva primeiro término. Sem interface de conclusão/avaliação nesta tarefa. Não editar completed_at/booking/status por SQL para simular fluxo de produto.

Janela fechada de 48h a partir de completed_at; motorista↔passageiro com reserva CONFIRMADA, ambos ativos/habilitados. Não avaliar cancelados/no-show ou legado sem conclusão. Marcador no_show_at reservado à futura integração 008, sem API de marcação nesta entrega. Avaliação imutável, nota inteira 1..5, comentário texto opcional até 500. Duplicata recusada, inclusive sob concorrência.

SQL/plano das migrações rides 0005 e reviews 0001 revisados e aplicados no PostgreSQL local, preservando campos anteriores. Novos campos de término/no-show NULL e tabela de avaliações vazia; não há backfill fictício. Testes verificam model/serviço/constraints, relógio controlado, rollback e duplicata em transações PostgreSQL independentes.

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_reviews.py tests/test_booking_flow.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature006-t028.json --junitxml=test-results-feature006-t028.xml
~~~

## Interface de avaliação — T004 unificada / T029

Pré-condição: oferta com conclusão registrada pelo serviço e reserva CONFIRMADA, sem no-show, ambos usuários ativos; janela inclusiva de 48h ainda aberta. T029 não adiciona botão/rota para concluir a viagem: usar o serviço de conclusão já documentado para preparar o domínio, sem inventar término na partida ou editar histórico por SQL.

Com a sessão da contraparte elegível, abrir /avaliacoes/caronas/<offer_id>/usuarios/<reviewed_id>/nova/. Os IDs são da oferta e contraparte existentes, não do avaliador. Formulário contém nota 1..5 e comentário opcional até 500. GET só consulta e exibe nome abreviado/instantes, sem e-mail/placa. POST com CSRF grava uma única avaliação e redireciona a /accounts/profile/ com mensagem neutra. Repetição, oferta sem conclusão, reserva cancelada/no-show ou janela encerrada retornam 400 genérico; ator/contraparte sem permissão retorna 403. Entrada inválida é reapresentada com escape e sem gravação. GET nunca envia avaliação; PUT/PATCH/DELETE/HEAD/OPTIONS retornam 405 para usuário elegível.

Execução automatizada: `venv/Scripts/python.exe -m pytest tests/test_reviews.py -q --tb=short`. Inclui login real, CSRF e duplicata concorrente por HTTP. Não houve inspeção visual humana nesta rodada; HTML/labels/escape foram verificados por testes Django. Qualidade final T006 permanece aberta.
