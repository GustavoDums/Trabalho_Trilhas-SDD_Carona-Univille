# Evidência — Feature 004 / T003 local / núcleo do roadmap T021

Data: 2026-11-22. Requisitos: REQ-006 e REQ-017; acesso/privacidade REQ-002 e REQ-003; medição REQ-018/REQ-019.

## Correspondência e autorização

A tabela local relaciona T021 a T003 (serviço e concorrência) e T006 (integração de disponibilidade na busca). O usuário confirmou executar **somente T003 nesta rodada** e autorizou T006 para a próxima. Modelo T002/T020 e pacote de serviços da Feature 003/T001 já disponíveis.

Contrato da função documentado antes do código: [serviço interno](contracts/web-routes.md).
Sem HTTP, matching, cartão, disponibilidade exibida ou mudanças de modelo nesta rodada.

## Proteção transacional implementada

BookingService.create_booking usa transaction.atomic e bloqueia primeiro a RideOffer por select_for_update; bloqueia também passageiro/motorista por PK crescente para revalidar contas atuais. Depois dos locks, captura o instante atual e exige partida futura, papéis e vínculos ativos; objetos antigos do chamador não autorizam a reserva.

Dentro da transação e sob lock da oferta: recusa autorreserva/duplicidade, conta todas as CONFIRMADA e cria somente abaixo de seats. Uma confirmação ocupa a oferta inteira, independentemente do trecho. Capacidade original nunca é modificada.

O modelo revalida pontos do itinerário. NoSeatsAvailable é ValidationError com code no_seats; duplicidade usa already_booked. Savepoint interno permite traduzir somente IntegrityError da unicidade ativa após restaurar a transação; erros SQL diferentes são propagados e revertidos. Falha após insert não deixa reserva parcial.

## TDD e testes

Antes do serviço: **33 falhas** por ModuleNotFoundError de rides.services.booking_service, sem erro de fixture.
Depois: **33 aprovados**.

Cobrem confirmação, esgotamento, duplicidade antes da checagem de capacidade, histórico CANCELADA sem consumir vaga; contas reconsultadas (status/papel/habilitação), visitante, usuário removido e autorreserva; saída passada/igual a now; IDs inválidos, ausentes e trecho inválido; rollback após insert, restrições SQL reais e conexão utilizável após falha.

### Prova concorrente no PostgreSQL

pytest.mark.django_db(transaction=True), fixture principal em autocommit, duas threads e conexões reais. Cada worker abre transaction.atomic independente, registra pg_backend_pid e txid_current e espera barreira **antes de chamar o serviço e obter locks**. Sem mock de lock nem sleep. Timeouts limitam falhas de sincronização; conexões encerradas em finally.

Resultados da execução final, também gravados nas propriedades do [JUnit](../../test-results-feature004-t021.xml):

| Caso | Backend PIDs | IDs de transação | Resultados | Confirmadas | Saldo |
| --- | --- | --- | --- | --- | --- |
| Dois passageiros elegíveis distintos | 22832, 37784 | 14148, 14149 | confirmed, no_seats | 1 | 0 |
| Mesmo passageiro em duas solicitações | 36688, 17316 | 14178, 14177 | already_booked, confirmed | 1 | 0 |

Assertivas: IDs de backend e transação distintos; exatamente um sucesso e uma recusa esperada; só um registro no banco; seats permanece 1 e seats - confirmadas = 0. O caso obrigatório de dois passageiros termina sem sobre-reserva.

## Regressão e cobertura

~~~powershell
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature004-t021.json --junitxml=test-results-feature004-t021.xml
~~~

**477 aprovados; 0 falhas, 0 erros, 0 ignorados**.
33 novos nesta tarefa; 49 de modelo da Feature 004 e 395 de regressão anterior (152 accounts, 115 ofertas, 128 busca).
Cobertura rides: **402/402 linhas (100%)**, **109/112 ramificações (97.32142857142857%)**, combinada **99.41634241245136%**. booking_service: 51/51 linhas e 20/20 ramificações (100%). Meta >=80% atendida no conjunto medido, não cobertura global de accounts.

Relatórios: [coverage-feature004-t021.json](../../coverage-feature004-t021.json) e [test-results-feature004-t021.xml](../../test-results-feature004-t021.xml). Relatórios anteriores preservados.
Django check sem problemas, makemigrations --check --dry-run sem alterações e editor sem diagnósticos nos dois arquivos Python novos. Nenhuma migração nova exigida.

## Arquivos criados/alterados

- [booking_service.py](../../rides/services/booking_service.py).
- [test_concurrency_booking.py](../../tests/test_concurrency_booking.py).
- [spec.md](spec.md), [plan.md](plan.md), [tasks.md](tasks.md), [data-model.md](data-model.md), [research.md](research.md), [contracts/web-routes.md](contracts/web-routes.md), [quickstart.md](quickstart.md) e este registro.
- [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md), [README](../../README.md) e os relatórios vinculados.

## Limites e próxima rodada

T003 concluída; T021 do roadmap concluída no objetivo de serviço/concorrência. T006 permanece aberta e autorizada para a próxima rodada; só ela alterará a disponibilidade na busca/cartão. T004/T005/T007 continuam abertas.
Sem alterações em modelos, migrações, publicação, matching, formulários, templates, views ou rotas. A futura Feature 005 adicionará cancelamento/estado de oferta e deverá respeitar o mesmo protocolo de locks.

Criação direta por modelo/bulk/SQL não é API suportada de reserva: constraints locais não substituem lock/contagem agregada. O serviço é a fronteira suportada de criação; futuros escritores precisam usar o mesmo protocolo. Sem staging ou commit.
