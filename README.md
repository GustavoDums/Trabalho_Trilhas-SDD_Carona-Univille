# Trabalho_Trilhas-SDD_Carona-Univille

<!-- feature-005-t006-quality:start -->
Feature 005 / T006 local / fechamento da T026 — **661 testes aprovados**, 0 ignorados: 20 novos e 641 de regressão anterior. TDD inicial: 17 falhas esperadas, 3 casos de controle de acesso existentes aprovados; depois verde.
Cobertura de `rides/`: **99.36143039591316%** combinada; linhas 618/619 (**99.83844911147011%**); ramificações 160/164 (**97.5609756097561%**). Views: 100% de linhas e ramificações. Meta: 80%.
Relatórios: [JSON](coverage-feature005-t006.json), [JUnit](test-results-feature005-t006.xml), [evidência](specs/005-cancelamento-liberacao-vaga/evidence-t006.md). Medição: 2026-11-23.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature005-t006.json --junitxml=test-results-feature005-t006.xml`.
Interface de cancelamento de oferta verificada por testes Django: POST/CSRF, confirmação acessível, prazo, lote e histórico. T005/T006 completam T026. Sem migração; auditoria MVP/T007 permanece pendente.
<!-- feature-005-t006-quality:end -->


<!-- feature-005-t005-quality:start -->
Feature 005 / T005 local / parcela da T026 — **641 testes aprovados**, 0 ignorados: 20 novos e 621 de regressão anterior. TDD inicial: 17 falhas esperadas, 3 casos já atendidos pelo controle de acesso; depois verde.
Cobertura de `rides/`: **99.35064935064935%** combinada; linhas 605/606 (**99.83498349834983%**); ramificações 160/164 (**97.5609756097561%**). Views: 100% de linhas e ramificações. Meta: 80%.
Relatórios: [JSON](coverage-feature005-t005.json), [JUnit](test-results-feature005-t005.xml), [evidência](specs/005-cancelamento-liberacao-vaga/evidence-t005.md). Medição: 2026-11-23.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature005-t005.json --junitxml=test-results-feature005-t005.xml`.
Cancelamento de reserva por POST, confirmação acessível, CSRF, titularidade, prazo e privacidade verificados por testes Django. Sem migração; interface de oferta/T006 e auditoria MVP/T007 pendentes.
<!-- feature-005-t005-quality:end -->


<!-- feature-005-t025-quality:start -->
Feature 005 / T004 local / roadmap T025 — **621 testes aprovados**, 0 ignorados: 23 novos e 598 de regressão anterior. TDD: 23 falhas esperadas antes da implementação, depois verde.
Cobertura de `rides/`: **99.33862433862434%** combinada; linhas 591/592 (**99.83108108108108%**); ramificações 160/164 (**97.5609756097561%**). Serviço de cancelamento: 98.75% linhas e 96.875% ramificações. Meta: 80%.
Relatórios: [JSON](coverage-feature005-t025.json), [JUnit](test-results-feature005-t025.xml), [evidência](specs/005-cancelamento-liberacao-vaga/evidence-t025.md). Medição: 2026-11-23.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature005-t025.json --junitxml=test-results-feature005-t025.xml`.
Cancelamento de oferta atômico, histórico, privacidade, rollback e três corridas PostgreSQL verificados. Sem nova migração; interface e auditoria MVP permanecem pendentes.
<!-- feature-005-t025-quality:end -->


<!-- feature-005-t024-quality:start -->
Feature 005 / T002–T003 locais / T024 e parcela de reserva da T025 — **598 testes aprovados**, 0 ignorados.
**43 testes novos**, 555 de regressão anterior. TDD inicial: 42 falhas por funcionalidades ausentes, depois verde; 1 verificação adicional de esquema.
Cobertura de `rides/`: **99.30167597765363%** combinada; linhas: 563/564 (99.822695035461%); ramificações: 148/152 (97.36842105263158%). Serviço de cancelamento: 98.07692307692308% linhas e 95% ramificações. Meta: 80%.
Relatórios: [coverage-feature005-t024.json](coverage-feature005-t024.json), [test-results-feature005-t024.xml](test-results-feature005-t024.xml) e [evidência](specs/005-cancelamento-liberacao-vaga/evidence-t024.md). Medição: 2026-11-23.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature005-t024.json --junitxml=test-results-feature005-t024.xml`.
Migração 0004 aplicada/verificada no PostgreSQL local. Cancelamento de reserva idempotente; oferta, interface e penalidade numérica permanecem tarefas futuras.
<!-- feature-005-t024-quality:end -->


<!-- feature-004-t023-quality:start -->
Feature 004 / T005 local / roadmap T023 — **555 testes aprovados na suíte de regressão**, 0 ignorados.
**35 novos testes de URLs/fluxo HTTP nesta tarefa**; 160 acumulados da Feature 004, 395 de regressão anterior.
Cobertura de `rides/`: **99.50413223140495%** combinada; linhas: 479/479 (100%); ramificações: 123/126 (97.61904761904762%). Meta: 80%.
Relatórios: [coverage-feature004-t023.json](coverage-feature004-t023.json), [test-results-feature004-t023.xml](test-results-feature004-t023.xml) e [evidência](specs/004-reserva-sem-overbooking/evidence-t023.md). Medição: 2026-11-22.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature004-t023.json --junitxml=test-results-feature004-t023.xml`.
Rotas de reserva/consulta própria integradas; login real com CSRF, privacidade e esgotamento verificados por HTTP. Qualidade final T007 local ainda pendente.
<!-- feature-004-t023-quality:end -->


<!-- feature-004-t022-quality:start -->
Feature 004 / T004 local / roadmap T022 — **520 testes aprovados na suíte de regressão**, 0 ignorados.
**36 novos testes de views/projeção privada nesta tarefa**; 125 acumulados da Feature 004, 395 de regressão anterior.
Cobertura de `rides/`: **99.50413223140495%** combinada; linhas: 479/479 (100%); ramificações: 123/126 (97.61904761904762%). Views, formulários e consulta privada: 100% de linhas/ramificações. Meta: 80%.
Relatórios: [coverage-feature004-t022.json](coverage-feature004-t022.json), [test-results-feature004-t022.xml](test-results-feature004-t022.xml) e [evidência](specs/004-reserva-sem-overbooking/evidence-t022.md). Medição: 2026-11-22.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature004-t022.json --junitxml=test-results-feature004-t022.xml`.
Views/template validados isoladamente: dados privados somente à contraparte confirmada, sem e-mail/WhatsApp. Rotas e fluxo HTTP completo T005/T023 e qualidade final permanecem pendentes.
<!-- feature-004-t022-quality:end -->


<!-- feature-004-t006-quality:start -->
Feature 004 / T006 local / integração T021–T023 — **484 testes aprovados na suíte de regressão**, 0 ignorados.
**7 novos testes de disponibilidade nesta tarefa**; 89 acumulados da Feature 004 (49 modelo + 33 serviço + 7 integração), 395 de regressão anterior.
Cobertura de `rides/`: **99.41747572815534%** combinada; linhas: 403/403 (100%); ramificações: 109/112 (97.32142857142857%). Matching e serviço de reserva: 100% de linhas/ramificações. Meta: 80%.
Relatórios: [coverage-feature004-t006.json](coverage-feature004-t006.json), [test-results-feature004-t006.xml](test-results-feature004-t006.xml) e [evidência](specs/004-reserva-sem-overbooking/evidence-t006.md). Medição: 2026-11-22.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature004-t006.json --junitxml=test-results-feature004-t006.xml`.
Busca exibe saldo atual; esgotadas permanecem compatíveis com aviso e saldo zero. Interface/rotas de reserva e qualidade final ainda pendentes.
<!-- feature-004-t006-quality:end -->


<!-- feature-004-t021-quality:start -->
Feature 004 / T003 local / núcleo do roadmap T021 — **477 testes aprovados na suíte de regressão**, 0 ignorados.
**33 testes novos de serviço/concorrência nesta tarefa**; 82 acumulados da Feature 004 (49 modelo + 33 serviço), 395 de regressão anterior.
Cobertura de `rides/`: **99.41634241245136%** combinada; linhas: 402/402 (100%); ramificações: 109/112 (97.32142857142857%). Serviço de reserva: 100% de linhas/ramificações. Meta: 80%.
Relatórios: [coverage-feature004-t021.json](coverage-feature004-t021.json), [test-results-feature004-t021.xml](test-results-feature004-t021.xml) e [evidência](specs/004-reserva-sem-overbooking/evidence-t021.md). Medição: 2026-11-22.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature004-t021.json --junitxml=test-results-feature004-t021.xml`.
PostgreSQL: dois passageiros disputando a última vaga, uma confirmação, uma recusa por esgotamento, saldo zero. T006 (disponibilidade exibida) autorizada para próxima rodada, ainda pendente.
<!-- feature-004-t021-quality:end -->


<!-- feature-004-t020-quality:start -->
Feature 004 / T002 local / roadmap T020 — **444 testes aprovados na suíte de regressão**, 0 ignorados.
**49 testes novos de modelo de reserva**, 395 de regressão (152 accounts, 115 ofertas, 128 busca).
Cobertura de `rides/`: **99.32279909706546%** combinada; linhas: 351/351 (100%); ramificações: 89/92 (96.73913043478261%). RideBooking: 100% de linhas/ramificações. Meta: 80%.
Relatórios: [coverage-feature004-t020.json](coverage-feature004-t020.json), [test-results-feature004-t020.xml](test-results-feature004-t020.xml) e [evidência](specs/004-reserva-sem-overbooking/evidence-t020.md). Medição: 2026-11-22.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature004-t020.json --junitxml=test-results-feature004-t020.xml`.
Migração 0003 aplicada/verificada no PostgreSQL local. Entrega somente de modelo: serviço e concorrência da última vaga pertencem à T021 e continuam pendentes.
<!-- feature-004-t020-quality:end -->


<!-- feature-003-t019-quality:start -->
Feature 003 / T004 local / roadmap T019 — **395 testes aprovados na suíte de regressão**, 0 ignorados.
**36 novos testes HTTP nesta tarefa**; 128 funcionais acumulados da Feature 003 (65 matching + 63 formulário/HTTP), 152 accounts e 115 ofertas.
Cobertura de `rides/`: **99.21875%** combinada; linhas: 310/310 (100%); ramificações: 71/74 (95.94594594594595%). Matching e views: 100% de linhas/ramificações. Meta: 80%.
Relatórios: [coverage-feature003-t019.json](coverage-feature003-t019.json), [test-results-feature003-t019.xml](test-results-feature003-t019.xml) e [evidência](specs/003-busca-rota-horario/evidence-t019.md). Medição: 2026-11-22.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature003-t019.json --junitxml=test-results-feature003-t019.xml`.
Busca disponível em `/caronas/buscar/` para passageiro ativo, sem paginação. Qualidade/demo final T005 local continua pendente.
<!-- feature-003-t019-quality:end -->


<!-- feature-003-t018-quality:start -->
Feature 003 / entrega parcial T001–T003 locais / roadmap T017–T018 — **359 testes aprovados na suíte de regressão**, 0 ignorados.
São **92 testes novos funcionais da Feature 003** (65 matching + 27 formulário/HTML), 152 de accounts e 115 de ofertas (incluindo 1 contrato novo de import).
Cobertura de `rides/`: **99.17127071823204%** combinada; linhas: 290/290 (100%); ramificações: 69/72 (95.83333333333333%). Matching: 100% de linhas/ramificações. Meta: 80%.
Relatórios: [coverage-feature003-t018.json](coverage-feature003-t018.json), [test-results-feature003-t018.xml](test-results-feature003-t018.xml) e [evidência](specs/003-busca-rota-horario/evidence-t018.md). Medição: 2026-11-22.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature003-t018.json --junitxml=test-results-feature003-t018.xml`.
View/rota T004 local (T019) e qualidade/demo final T005 continuam pendentes; estes números não indicam conclusão integral da feature.
<!-- feature-003-t018-quality:end -->

<!-- feature-001-quality:start -->
Feature 001 / T012 — 152 testes aprovados; 0 ignorados. Meta: **80%**.
Cobertura combinada de `accounts/` e `carona_univille/views.py`: **96.845425867507885%**.
Linhas: 259/265 (97.735849056603769%); ramificações: 48/52 (92.3076923076923%).
Relatórios: [coverage.json](coverage.json) e [test-results.xml](test-results.xml). Medição: 2026-11-22.

Reproduzir: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-quality-metrics.ps1`.
<!-- feature-001-quality:end -->

<!-- feature-002-quality:start -->
Feature 002 / roadmap T016 / T006 local — **114 testes aprovados**.
Aceitação integrada de modelos, publicação e consulta própria; qualidade e demonstração final T007 local pendentes. Cobertura de `rides/`: **98.86792452830188%** combinada;
linhas: 213/213 (100%); ramificações: 49/52 (94.23076923076923%). Meta: 80%.
Relatórios: [coverage-feature002.json](coverage-feature002.json) e [test-results-feature002.xml](test-results-feature002.xml).
Medição: 2026-11-22. Reproduzir: `venv/Scripts/python.exe -m pytest tests/test_rides_offer.py --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature002.json --junitxml=test-results-feature002.xml`.
<!-- feature-002-quality:end -->
