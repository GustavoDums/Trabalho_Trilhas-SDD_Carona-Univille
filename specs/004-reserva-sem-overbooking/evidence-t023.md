# Evidência — Feature 004 / T005 local / roadmap T023

Data: 2026-11-22. Requisitos: REQ-006, REQ-017; controles REQ-002/REQ-003; medição REQ-018/REQ-019.

## Correspondência e escopo

Entrada executável única: T005 local, mapeamento de URLs e testes HTTP completos. A T006 também citada na linha T023 já estava concluída; dependências T004/T006 atendidas.
Nenhuma decisão nova: confirmação instantânea, nome completo/placa só à contraparte confirmada, e-mail confidencial, WhatsApp adiado.

Mapeadas em rides/urls.py:
- POST /caronas/<int:offer_id>/reservar/ → BookRideView, nome rides:book.
- GET /caronas/minhas-reservas/ → MyBookingsView, nome rides:my_bookings.

Views, formulários, templates e serviços existentes foram reutilizados **sem alteração de produção fora de rides/urls.py**. Rotas antigas de busca/oferta/consulta própria/placeholder preservadas.

## TDD

35 casos HTTP novos escritos antes do mapeamento de rotas.
Vermelho: **29 falhas** por NoReverseMatch/404 onde se esperavam respostas da funcionalidade; **6 aprovações** pelo confinamento acadêmico já existente. 85 testes anteriores não selecionados nessa execução.
Após registrar as duas rotas: **120 aprovados** no módulo (85 anteriores + 35 novos). Não houve ajuste de comportamento de serviços nem redução de assertivas para obter verde.

## Fluxo HTTP real

Client(enforce_csrf_checks=True) obtém token no GET de login, envia e-mail/senha fictícios pelo login real e usa o token atual da sessão para reservar. Conta de teste já ativa; cadastro/ativação integral não é afirmado por este cenário.

Sequência verificada:
1. Busca pública mostra uma vaga, nome abreviado e ausência de placa/nome completo.
2. POST com pontos escolhidos cria CONFIRMADA para request.user; passenger_id/status/next forjados não substituem ator, estado ou destino.
3. Redirect fixo para minhas reservas retorna 200 e mensagem de sucesso; contexto contém somente DTOs próprios.
4. Contraparte confirmada vê nome completo/placa, sem e-mails, outros passageiros ou JSON privado.
5. Nova busca mostra saldo zero e Vagas esgotadas.
6. Repetição do POST retorna erro sem criar segunda reserva.

Matriz complementar:
- Visitante/desabilitado → login com next; pendente → ativação, usando middleware real.
- Motorista ativo não reserva (403), mas consulta somente reservas de suas ofertas; passageiro ativo reserva e consulta próprias.
- CSRF ausente ou inválido → 403 antes da escrita; caso de sucesso usa verificação CSRF habilitada.
- Métodos de escrita em leitura e GET/PUT/PATCH/DELETE na ação de reserva → 405.
- Campos ausentes, ponto desconhecido/igual/invertido, oferta inexistente, duplicidade e esgotamento retornam erro sem mudar snapshots de contas/ofertas/paradas/pontos/reservas.
- IDs de terceiros na query string não ampliam consulta própria; nenhuma lista revela e-mail.
- Alteração de estado para CANCELADA em fixture é refletida em novo GET com placa omitida e nome abreviado; não foi criado fluxo de cancelamento.
- GET de consulta própria não escreve domínio.

Condições de recusa/métodos usam Client padrão quando se deseja isolar o contrato HTTP da validação CSRF; os dois casos negativos de CSRF e o fluxo principal usam enforce_csrf_checks=True.

## Regressão e medição

~~~powershell
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature004-t023.json --junitxml=test-results-feature004-t023.xml
~~~

**555 aprovados; 0 falhas, 0 erros, 0 ignorados.**
35 novos nesta T005. Feature 004 acumula 160 (49 modelo + 33 serviço + 7 disponibilidade + 36 apresentação + 35 HTTP); 395 de regressão anterior (152 accounts, 115 ofertas, 128 busca).
Concorrência real da T003 e rollback continuam aprovados no PostgreSQL; serviços não foram alterados nesta rodada.

Cobertura rides: **479/479 linhas (100%)**, **123/126 ramificações (97.61904761904762%)**, combinada **99.50413223140495%**. Meta >=80% atendida no conjunto medido, sem atribuí-la a accounts. Mesma cobertura estrutural da entrega anterior, com novos cenários de integração de URLs/middleware/CSRF.
Relatórios: [coverage-feature004-t023.json](../../coverage-feature004-t023.json) e [test-results-feature004-t023.xml](../../test-results-feature004-t023.xml). Medições anteriores preservadas.

Django check sem problemas; makemigrations --check --dry-run: No changes detected. Editor sem erros nos dois arquivos Python alterados. Links e whitespace conferidos ao encerrar.

## Arquivos criados/alterados

- [rides/urls.py](../../rides/urls.py).
- [test_booking_flow.py](../../tests/test_booking_flow.py).
- [spec.md](spec.md), [plan.md](plan.md), [tasks.md](tasks.md), [research.md](research.md), [contracts/web-routes.md](contracts/web-routes.md), [quickstart.md](quickstart.md) e este registro.
- [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md), [README](../../README.md) e os relatórios acima.

## Limites e revisão

T005/T023 concluída. T001–T006 locais atendidas; T007 de qualidade final (script, inspeção visual e demonstração) permanece aberta.
Esta entrega valida contratos HTTP e suas rotas; não adiciona controles novos à tela de busca. Não há novas migrações, contato/WhatsApp, cancelamento ou notificações.
Sem alterações em serviços, views, formulários, templates ou middleware. Sem staging ou commit; alterações existentes preservadas.
