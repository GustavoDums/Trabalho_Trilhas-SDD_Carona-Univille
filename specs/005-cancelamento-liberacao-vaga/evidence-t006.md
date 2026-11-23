# Evidência — Feature 005 / T006 local / fechamento da T026

Data: 2026-11-23. Requisitos REQ-007, REQ-003 e REQ-017; FR-001/FR-003/FR-004; SC-003/SC-004. Dependências T004/T005 concluídas. Usuário autorizou somente T006 local para completar T026, após rodada anterior da T005. T007/auditoria MVP permanece aberta.

## Entrega e comportamento

CancelOfferView, rota POST /caronas/<offer_id>/cancelar/ (rides:cancel_offer) e confirmação acessível details/summary em Minhas ofertas. A lista mantém ofertas canceladas no histórico e exibe estado, sem nova ação quando CANCELADA. Explica prazo de 4h inclusivas pela saída da origem, tardio aceito antes da partida e recusa na partida/depois. Sem JavaScript obrigatório.

View usa motorista ativo da sessão e alvo da URL, ignora user_id/offer_id/next do corpo e delega a CancellationService.cancel_offer. POST exige CSRF; demais métodos retornam 405 para motorista elegível. Passageiro/terceiro recebe 403; anônimo/inativo segue login e pendente segue ativação. Sucesso/repetição redireciona à lista própria fixa; recusa temporal retorna 400 com alerta, outro ValidationError retorna 400 genérico e somente ofertas próprias. Sem detalhes de terceiros nas recusas.

Serviço existente cancela oferta e reservas confirmadas no mesmo commit; preserva capacidade e reservas/auditorias já canceladas. Repetição, inclusive após a partida, não altera datas/eventos. Busca exclui oferta cancelada; projeções privadas das reservas retiram placa/nome completo da contraparte. Nenhuma mudança em serviços, modelos ou migrações foi necessária; nenhuma notificação ou penalidade implementada.

## TDD e verificações

- Vermelho inicial: 20 casos novos; 17 falhas por interface/rota/CSRF ausentes, 3 casos aprovados pelos controles existentes.
- Primeira implementação: 103 passaram e 3 detectaram renderização incorreta nas recusas (ListView exigia self.object_list); inicialização corrigida e suíte focada ficou verde.
- Verde focado: 106 testes de cancelamento aprovados (86 anteriores + 20 novos).
- Regressão completa PostgreSQL: 661 aprovados, 0 ignorados/falhas, 84.44s; 641 casos anteriores preservados, incluindo rollback e concorrência com transações independentes.
- Novos testes: rota nomeada, confirmação e histórico da oferta; sessão/CSRF válido, ausente e inválido; GET/HEAD/PUT/PATCH/DELETE/OPTIONS 405; anônimo, pendente, desabilitado, passageiro e outro motorista; IDs/next forjados; bordas 240min01s/240min/239min59s; partida/depois; duas confirmadas e uma cancelada anterior; preservação de histórico e capacidade; privacidade dos envolvidos; exclusão da busca; repetição após partida e alvo ausente.
- Cobertura rides/: 618/619 linhas (99.83844911147011%), 160/164 ramificações (97.5609756097561%), combinada 99.36143039591316%. Views: 124/124 linhas e 12/12 ramificações, 100% de ambas. Meta >=80% atendida. Lacunas preexistentes permanecem na defesa de reconsulta da reserva e três ramificações de modelos.
- Django check: nenhum problema. makemigrations --check --dry-run: nenhuma alteração. migrate --plan: nenhuma operação. Banco local confirmado postgresql, sem mudanças de dados de desenvolvimento.
- Diagnósticos do editor sem erros nos três arquivos Python alterados; git diff --check sem erros. Repositório limpo no início; relatórios anteriores e ponteiro de feature preservados. Sem hooks/checklists adicionais. Sem staging ou commit.

[JSON de cobertura](../../coverage-feature005-t006.json), [JUnit](../../test-results-feature005-t006.xml).

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_cancellation_flow.py -k offer_cancel_http -q --tb=short
.\venv\Scripts\python.exe -m pytest tests/test_cancellation_deadlines.py tests/test_cancellation_flow.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature005-t006.json --junitxml=test-results-feature005-t006.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
~~~

Quickstart atualizado; HTTP e conteúdo de templates verificados por testes Django. Inspeção visual em navegador não realizada. T006 e T026 concluídas; T007 não executada nem marcada.

## Arquivos alterados/criados

- [views.py](../../rides/views.py), [urls.py](../../rides/urls.py), [my_offers.html](../../rides/templates/rides/my_offers.html), [test_cancellation_flow.py](../../tests/test_cancellation_flow.py).
- [spec.md](spec.md), [plan.md](plan.md), [tasks.md](tasks.md), [contratos](contracts/web-routes.md), [quickstart.md](quickstart.md) e esta evidência.
- [README](../../README.md), [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md), relatórios JSON/JUnit acima.

Commit sugerido: feat(005/T006): cancelar oferta pela interface e concluir T026 — REQ-007, REQ-003, REQ-017
