# Evidência — Feature 004 / T004 local / roadmap T022

Data: 2026-11-22. Requisitos: REQ-003 e REQ-006; apoio de REQ-002/REQ-017; medição REQ-018/REQ-019.

## Correspondência e escopo

Correspondência única: T022 → T004 local. Dependência T003 de reserva transacional concluída; decisão D004-02 mantida, com nome completo/placa somente à contraparte CONFIRMADA, nenhum e-mail e WhatsApp adiado.

Implementados BookRideView, MyBookingsView, RideBookingForm, BookingQueryService/BookingSummary e my_bookings.html. **Nenhuma rota de produção adicionada**: mapeamento e fluxo HTTP ponta a ponta pertencem à T005/T023. Views verificadas por RequestFactory, sem simular que endpoints estão publicados.

## Comportamento

BookRideView é POST-only para passageiro ativo; passa request.user e pontos válidos ao BookingService existente. passenger_id/status/offer_id/next enviados no corpo não substituem ator, estado, oferta da URL ou redirecionamento. Sucesso gera mensagem neutra e redirect fixo para /caronas/minhas-reservas/. Erros de pontos são mapeados para campos do formulário; validações gerais, duplicidade e esgotamento não alteram registros. PermissionDenied continua recusa.

MyBookingsView permite consulta própria por ambos os papéis ativos. BookingQueryService reconsulta conta atual, filtra por passageiro ou motorista da oferta e retorna somente DTOs imutáveis. IDs de terceiros na query string não governam acesso. Um passageiro não recebe outro passageiro da mesma oferta.

CONFIRMADA expõe nome completo da contraparte e placa. CANCELADA entrega apenas display_name e vehicle_plate=None, sem valores privados ocultos no DTO/HTML. Nunca incluir e-mail, telefone, IDs de contas ou objetos ORM na projeção. Consulta sem escrita e sem N+1, ordenada por saída/criação/ID; rótulos escapados.

## TDD

Antes da produção: **36 falhas novas**, por projeção/views ausentes (ModuleNotFoundError/AttributeError), e **49 anteriores aprovadas**.

Após implementação, quatro asserções novas foram corrigidas: a página de erro pode mostrar os dados privados de outra reserva CONFIRMADA do próprio usuário, mas nunca os de uma reserva alheia. A correção verifica IDs próprios exatos e ausência de nome/placa da oferta não confirmada para aquele ator; não remove a proteção de privacidade.

Verde: **85 aprovados** no módulo (49 modelo + 36 novos de apresentação).

Matriz de casos:
- Passageiros isolados, motorista titular, motorista externo e terceiro; nenhuma reserva alheia.
- Nome completo/placa confirmados, cancelamento com redação, DTO congelado e whitelist sem e-mail.
- IDs trocados e filtros de identidade ignorados; texto HTML escapado.
- Conta stale pendente/desabilitada/papel inválido, visitante e conta ausente recusados pelo serviço; views também negam sem middleware.
- Lista vazia, snapshot de domínio inalterado e consultas constantes quando a lista cresce.
- POST forjado não substitui usuário/status/oferta/redirect; erros obrigatórios/iguais/fora da rota, oferta ausente, duplicidade e esgotamento preservam dados.
- GET de escrita e POST de leitura recusados com 405.
- Template inclui csrf_token; CsrfViewMiddleware recusa POST sem token antes da view. Fluxo completo com middleware/URLs será verificado na T005.

Testes diretos sem middleware recebem recusa 403 para conta pendente; o redirecionamento acadêmico continua responsabilidade do middleware existente e não foi alterado.

## Regressão e medição

~~~powershell
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature004-t022.json --junitxml=test-results-feature004-t022.xml
~~~

**520 aprovados; 0 falhas, 0 erros, 0 ignorados.**
36 novos desta tarefa; Feature 004 acumula 125 (49 modelo + 33 serviço + 7 disponibilidade + 36 apresentação); 395 de regressão anterior (152 accounts, 115 ofertas, 128 busca).

Cobertura rides: **479/479 linhas (100%)**, **123/126 ramificações (97.61904761904762%)**, combinada **99.50413223140495%**. booking_queries 35/35 linhas e 6/6 ramificações; views 97/97 linhas e 12/12 ramificações; forms 55/55 linhas e 8/8 ramificações (100%). Meta >=80% atendida nesse conjunto, sem atribuir essa cobertura a accounts.

Relatórios versionáveis: [coverage-feature004-t022.json](../../coverage-feature004-t022.json) e [test-results-feature004-t022.xml](../../test-results-feature004-t022.xml). Medições anteriores preservadas.
Django check sem problemas; makemigrations --check --dry-run sem mudanças. Sem erros do editor em Python/template. Links/whitespace verificados ao encerrar. HTML e privacidade verificados por renderização; não declarar demo humana final executada.

## Arquivos criados/alterados

Produção/testes:
- [rides/views.py](../../rides/views.py): BookRideView, MyBookingsView e acesso acadêmico próprio.
- [rides/forms.py](../../rides/forms.py): formulário mínimo.
- [booking_queries.py](../../rides/services/booking_queries.py): projeção própria/redigida.
- [my_bookings.html](../../rides/templates/rides/my_bookings.html).
- [test_booking_flow.py](../../tests/test_booking_flow.py): 36 casos adicionais, sem mapear URLs.

Documentação:
- [spec.md](spec.md), [plan.md](plan.md), [tasks.md](tasks.md), [data-model.md](data-model.md), [research.md](research.md), [contracts/web-routes.md](contracts/web-routes.md), [quickstart.md](quickstart.md) e este registro.
- [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md), [README](../../README.md) e relatórios acima.

## Limites e revisão

T004/T022 concluída. T005/T023 de rotas/fluxo e T007 de qualidade final continuam abertas. Sem novos modelos/migrações, WhatsApp, e-mail, cancelamento ou notificações.
BookingService, matching, middleware e URLconf permanecem inalterados. Sem staging/commit; alterações anteriores preservadas.
