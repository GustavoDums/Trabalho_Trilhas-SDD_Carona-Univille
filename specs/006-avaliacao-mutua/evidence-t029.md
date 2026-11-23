# Evidência — Feature 006/T004 unificada / roadmap T029

Data: 2026-11-23. REQ-008, REQ-003, REQ-017; FR-001–FR-004; SC-001/SC-002/SC-003. Dependência T002 concluída e D006-01/D006-02 homologadas. Usuário autorizou unificar T004/T005 e executar a interface numa rodada. T005 incorporada como referência histórica, demais IDs preservados. T006 não executada.

## Implementação

RideReviewForm contém somente rating (inteiro 1..5) e comment (texto opcional <=500), com labels/help text. Template herda accounts/base, exibe contraparte abreviada e instantes, explica janela de 48h/imutabilidade, escapa entradas e usa POST/CSRF. Não recebe instância ORM da contraparte, placa ou e-mail.

SubmitReviewView em GET/POST /avaliacoes/caronas/<offer_id>/usuarios/<reviewed_id>/nova/ (reviews:submit_review), incluída no URLconf raiz. Usuário ativo/habilitado, autoria da sessão e alvo da URL; campos extras reviewer/reviewed_user/offer_id/created_at/next não substituem esses valores. GET é somente leitura de domínio e só apresenta formulário após validação. POST revalida antes de gravar e redireciona a /accounts/profile/ com mensagem neutra. Erros de formulário retornam 400 com entrada escapada; ValidationError de elegibilidade/estado/alvo/janela/duplicata retorna 400 genérico sem formulário nem dados da contraparte; PermissionDenied 403. Anônimo/desabilitado segue login, pendente segue ativação. PUT/PATCH/DELETE/HEAD/OPTIONS 405 para usuário ativo. CSRF obrigatório.

ReviewService._review_inputs concentra as regras existentes e recusa duplicata antes de apresentar formulário. review_context retorna somente counterpart_name, departure_at, completed_at; create_review mantém assinatura e revalida independentemente da consulta anterior. Locks oferta → usuários por PK → reserva, transações e constraint de unicidade preservados. GET pode adquirir locks temporários, mas não grava domínio. Nenhuma nova migração, edição de avaliação, reputação, no-show ou interface de conclusão.

## TDD e regressão

- Vermelho inicial: 41 testes novos falharam por formulário/namespace de rotas ausentes antes da produção; 55 casos existentes não foram selecionados nessa rodada inicial.
- Após implementação: 96 testes reviews aprovados.
- Verificação adicional: alteração da reserva entre preparo e gravação no mesmo POST é revalidada e recusada, sem inserir; total focado 97 aprovados (42 novos/55 anteriores).
- Focado com cobertura: pacote reviews **100% de linhas e ramificações**.
- Regressão completa PostgreSQL: **765 aprovados, 0 ignorados/falhas, 87.99s**; 42 novos e 723 anteriores, incluindo reservas/cancelamentos/matching/cadastro e os 55 testes de domínio da T002.

Casos novos: limites 1/5, inválidas 0/6/fracionária/bool/vazio/texto; comentário 500/501, opcional e escape; GET autorizado sem escrita e contexto mínimo; ambos sentidos motorista↔passageiro; login real por e-mail com CSRF; IDs/tempo/next forjados ignorados; CSRF ausente/inválido; métodos 405; sessão/pendência/desabilitação/terceiro/contraparte inativa; legado sem término, cancelada/no-show, antes da conclusão, fora de 48h, duplicata e alvo ausente; recusa sem dados/sem formulário; estado alterado entre GET/POST e durante POST; duplicata HTTP concorrente.

### Concorrência PostgreSQL

Metadados preservados no [JUnit](../../test-results-feature006-t029.xml). Duplicata direta de domínio: PIDs 32608/12880, TxIDs 59330/59331, duplicate/created. Duplicata por HTTP com CSRF válido e sessões independentes: PIDs 38824/27972, TxIDs 59379/59380, respostas 400/302, exatamente uma avaliação. Barreira antes dos POSTs e transações/conexões independentes com lock_timeout 10s; sem sleep ou mock de locks.

## Cobertura e checks

[JSON](../../coverage-feature006-t029.json): accounts/rides/reviews/carona_univille, 1087/1102 linhas (**98.6388384754991%**), 252/260 ramificações (**96.92307692307692%**), combinada **98.31130690161527%**. reviews: 174/174 linhas, 44/44 ramificações, **100%**; views 34/34 e 2/2, serviço 88/88 e 32/32, modelo 30/30 e 10/10. Meta >=80% atendida. Lacunas consolidadas preexistentes em accounts/ASGI/WSGI e defesa de cancelamento, sem exclusões para inflar cobertura.

Django check sem problemas; makemigrations --check --dry-run sem alterações; migrate --plan sem operações. Nenhuma migração ou dado de desenvolvimento alterado nesta rodada. Diagnósticos do editor sem erros em formulário/view/serviço/testes. Pré-requisitos Spec Kit atendidos, sem hooks/checklist adicional, ponteiro preservado. git diff --check sem erros. Repositório inicialmente limpo e relatórios anteriores preservados. Sem staging ou commit.

HTML, labels, escape, sessão, CSRF e fluxo verificados pelo cliente HTTP Django; inspeção visual humana não realizada. Qualidade final/roteiro amplo pertence à T006, mantida aberta; T029 não requer medição humana de duração. Pré-condição da interface: conclusão já registrada pelo serviço da T002; nova rota/botão de conclusão não pertence ao recorte aprovado desta T004.

## Reprodução e arquivos

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_reviews.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature006-t029.json --junitxml=test-results-feature006-t029.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
~~~

Código/testes: [forms.py](../../reviews/forms.py), [views.py](../../reviews/views.py), [urls.py](../../reviews/urls.py), [template](../../reviews/templates/reviews/submit_review.html), [serviço](../../reviews/services/review_service.py), [URLconf raiz](../../carona_univille/urls.py), [test_reviews.py](../../tests/test_reviews.py).

Documentação: [spec](spec.md), [plan](plan.md), [tasks](tasks.md), [dados](data-model.md), [contratos](contracts/web-routes.md), [quickstart](quickstart.md), esta evidência, [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md), [README](../../README.md), JSON/JUnit citados.

T004 e T029 concluídas, T005 incorporada, T006 aberta. Commit sugerido: feat(006/T004): integrar avaliação pela interface e concluir T029 — REQ-008, REQ-003, REQ-017
