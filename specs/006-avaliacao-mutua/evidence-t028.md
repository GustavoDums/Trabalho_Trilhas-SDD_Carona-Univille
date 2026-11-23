# Evidência — Feature 006 / T001 e T002 unificada / roadmap T028

Data: 2026-11-23. REQ-008, REQ-003, REQ-017; FR-001/FR-002/FR-004; SC-001/SC-002. T001 documental homologou D006-01/D006-02; T002 absorveu antiga T003 por solicitação explícita do usuário. Dependências Feature 004/T002 e Feature 005/T004 concluídas. Alterações documentais preexistentes de consolidação preservadas.

## Decisões e entrega

Motorista titular ativo registra término explícito via ReviewService.complete_offer, relógio servidor aware, instante >= departure_at; oferta cancelada não conclui e repetição preserva a primeira data. RideOffer.completed_at nullable, legado NULL sem inventar término. CheckConstraint exige NULL ou conclusão >= partida em oferta ABERTA. Não há detecção automática de chegada.

ReviewService.create_review exige motorista↔passageiro com reserva CONFIRMADA, ambos ativos/habilitados, sem no-show; janela fechada [completed_at, completed_at+48h] em UTC. Bloqueio oferta → usuários por PK → reserva; duplicata recusada e transação reverte gravação em erro. Rating inteiro 1..5, comentário opcional texto até 500, sem autoavaliação ou edição posterior. Mudança de reputação não implementada.

RideReview tem FKs PROTECT para oferta/avaliador/avaliado, unique offer/reviewer/reviewed_user e checks de nota/usuários distintos. Model.save/full_clean protege entrada e imutabilidade; SQL protege invariantes locais, enquanto elegibilidade entre linhas depende do serviço. Bulk/SQL não são API de domínio. Comentário vazio permitido, None recusado antes do banco; normalização de espaços externos. Regravar sem alterações preserva histórico.

RideBooking.no_show_at nullable é marcador de inelegibilidade preparado para a Feature 008. Esta tarefa não marca no-show por API, não aplica penalidade e não inventa evento histórico. Views/forms/rotas de avaliação e conclusão não foram criados; T004/T005 futuras. T003 foi incorporada, sem tarefa executável independente.

## TDD e testes

- Vermelho inicial: 50 falhas por módulo reviews ausente, após testes escritos e executados no PostgreSQL com fixtures existentes.
- Implementação: 50 aprovados.
- Primeira regressão: 717 aprovados/1 falha na lista fechada de campos de reserva, pois novo no_show_at não estava no contrato esperado. Atualizado teste estrito para incluir o campo e validar null/blank, sem enfraquecer as demais asserções.
- Cinco verificações adicionais: sem alteração no histórico ao regravar, protocolo de campos excluídos por ModelForm, comentário None, esquema/legado/constraints. Teste de None encontrou NOT NULL em vez de ValidationError; validação corrigida e confirmada antes de gravação.
- Verde focado final: 175 aprovados (55 reviews + 120 booking).
- Regressão final: **723 aprovados, 0 ignorados/falhas, 89.13s**; 55 novos e 668 anteriores. Sem interface ou mudança de comportamento de outras features.

Casos: notas 1/5, inválidas 0/6/fracionária/bool/None; comentário vazio/500/501/None; autoavaliação e SQL raw; unicidade; pares e participação; ofertas/reservas canceladas/no-show; legado sem conclusão; ator anônimo/terceiro/pendente/desabilitado; IDs inválidos/ausentes; conclusão antes/exata/depois da partida; janela antes/exata/48h/48h+1s; relógio naive recusado; repetição de conclusão; avaliação mútua; rollback após inserção; constraints de conclusão e timestamps; FKs históricas.

Duplicata concorrente em PostgreSQL: PIDs 21824 e 13104, TxIDs 53508 e 53509; resultados duplicate/created e exatamente uma avaliação. Barreira, transações/conexões independentes e lock_timeout 10s, sem sleep ou mock de lock. Metadados em [JUnit](../../test-results-feature006-t028.xml).

## Cobertura e qualidade

[JSON](../../coverage-feature006-t028.json): accounts/rides/reviews/carona_univille, linhas 1033/1048 (**98.56870229007633%**), ramificações 248/256 (**96.875%**), combinada **98.2361963190184%**. Meta >=80% atendida.

Pacote reviews: 120/120 linhas, 40/40 ramificações, 100% de ambas. RideReview: 30/30 linhas e 10/10 ramificações. ReviewService: 76/76 linhas e 30/30 ramificações. Lacunas consolidadas são preexistentes em accounts, bootstrap ASGI/WSGI e defesa da reconsulta de cancelamento. Relatórios anteriores preservados.

Django check sem problemas; makemigrations --check --dry-run sem alteração; migrate --plan sem operação após aplicação. Diagnósticos do editor sem erros nos arquivos Python alterados; git diff --check sem erros.

## Migrações e preservação de dados

Plano e SQL revisados antes da aplicação. rides 0005 adiciona timestamps opcionais e check; reviews 0001 cria tabela, unique/checks e três FKs. Aplicadas no PostgreSQL local sem reset; banco de testes também aplicou as migrações.

Snapshot em memória de todas as colunas antigas, comparado antes/depois: accounts_academicuser 3 linhas, academicvalidationrecord 4, routepoint 4, rideoffer 1, waypoint 2, ridebooking 0, cancellationrecord 0. Todos os valores e contagens preservados; dados/credenciais não impressos ou versionados. completed_at/no_show_at NULL em legados, reviews vazia; introspecção confirmou três FKs e constraints. Script temporário de verificação em cache não versionado.

## Reprodução e arquivos

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_reviews.py tests/test_booking_flow.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature006-t028.json --junitxml=test-results-feature006-t028.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
~~~

Código: [reviews/apps.py](../../reviews/apps.py), [reviews/models.py](../../reviews/models.py), [review_service.py](../../reviews/services/review_service.py), inicializadores de pacote; [rides/models.py](../../rides/models.py), [settings.py](../../carona_univille/settings.py), migrações [rides 0005](../../rides/migrations/0005_ridebooking_no_show_at_rideoffer_completed_at_and_more.py) e [reviews 0001](../../reviews/migrations/0001_initial.py).

Testes: [test_reviews.py](../../tests/test_reviews.py), [test_booking_flow.py](../../tests/test_booking_flow.py). Artefatos: [spec](spec.md), [plan](plan.md), [tasks](tasks.md), [dados](data-model.md), [pesquisa](research.md), [contratos](contracts/web-routes.md), [quickstart](quickstart.md), esta evidência, [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md), [README](../../README.md), relatórios JSON/JUnit citados.

T001 e T002 concluídas; T028 concluída; T003 incorporada e T004–T006 abertas. Sem staging ou commit, sem nova feature, sem interface ou reputação.

Commit sugerido: feat(006/T002): implementar avaliações e concluir T028 — REQ-008, REQ-003, REQ-017
