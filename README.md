# Trabalho_Trilhas-SDD_Carona-Univille

<!-- feature-008-t003-quality:start -->
Feature 008 / T003 local / roadmap T033 — **869 testes aprovados**, 0 ignorados, com 13 novos e 856 de regressão.
Cobertura de accounts/rides/reviews/carona_univille — **98.82720875684129% em linhas** (1264/1279) e **96.95945945945945% em ramificações** (287/296). Os serviços de penalidade e reputação atingiram 100% em ambas as medidas.
Medição em 2026-11-23 no PostgreSQL 16.15. [Cobertura JSON](coverage-feature008-t003.json) · [JUnit](test-results-feature008-t003.xml) · [Evidência e reprodução](specs/008-penalidades-conduta/evidence-t003.md).
<!-- feature-008-t003-quality:end -->

<!-- feature-008-t032-quality:start -->
Feature 008 / T002 local / roadmap T032 — **856 testes aprovados**, 0 ignorados, com 27 novos e 829 de regressão.
Cobertura de accounts/rides/reviews/carona_univille — **98.79711307137129% em linhas** (1232/1247) e **96.93877551020408% em ramificações** (285/294). PenaltyRecord e ConductProfile atingiram 100% em ambas as medidas.
Medição em 2026-11-23 no PostgreSQL 16.15. [Cobertura JSON](coverage-feature008-t032.json) · [JUnit](test-results-feature008-t032.xml) · [Evidência e reprodução](specs/008-penalidades-conduta/evidence-t032.md).
<!-- feature-008-t032-quality:end -->

<!-- feature-007-t004-quality:start -->
Feature 007 / T004 local / roadmap T031 — **829 testes aprovados**, 0 ignorados, com 9 novos e 820 de regressão.
Cobertura de accounts/rides/reviews/carona_univille — **98.73524451939292% em linhas** (1171/1186) e **96.80851063829788% em ramificações** (273/282). O signal e o serviço de reputação atingiram 100% em ambas as medidas.
Medição em 2026-11-23 no PostgreSQL 16.15. [Cobertura JSON](coverage-feature007-t004.json) · [JUnit](test-results-feature007-t004.xml) · [Evidência e reprodução](specs/007-calculo-reputacao/evidence-t004.md).
<!-- feature-007-t004-quality:end -->

<!-- feature-007-t030-quality:start -->
Feature 007 / T001 documental + T002 unificada / roadmap T030 — **820 testes aprovados**, 0 ignorados: 55 novos e 765 anteriores. TDD inicial: 53 falhas pelo recurso ausente, depois verde; caso adicional de contexto Decimal externo falhou e foi corrigido antes da regressão final.
Cobertura consolidada de accounts/rides/reviews/carona_univille: **98.34824501032347%** combinada; linhas 1158/1173 (**98.72122762148338%**); ramificações 271/280 (**96.78571428571429%**). Serviço de reputação: **100% de linhas e ramificações**. Meta: 80%.
Relatórios: [JSON](coverage-feature007-t030.json), [JUnit](test-results-feature007-t030.xml), [evidência](specs/007-calculo-reputacao/evidence-t030.md). Medição: 2026-11-23.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature007-t030.json --junitxml=test-results-feature007-t030.xml`.
Migração reviews 0002 aplicada/verificada com dados anteriores preservados. Média simples das últimas 20 avaliações, Decimal/HALF_UP e rebuild explícito serializado; signals/exibição pública e penalidades permanecem tarefas futuras.
<!-- feature-007-t030-quality:end -->


<!-- feature-006-t029-quality:start -->
Feature 006 / T004 unificada (antigas T004/T005) / roadmap T029 — **765 testes aprovados**, 0 ignorados: 42 novos e 723 anteriores. TDD inicial: 41 falhas esperadas pela interface ausente, depois verde e verificação adicional de revalidação durante POST.
Cobertura consolidada de accounts/rides/reviews/carona_univille: **98.31130690161527%** combinada; linhas 1087/1102 (**98.6388384754991%**); ramificações 252/260 (**96.92307692307692%**). Pacote reviews: **100% de linhas e ramificações**. Meta: 80%.
Relatórios: [JSON](coverage-feature006-t029.json), [JUnit](test-results-feature006-t029.xml), [evidência](specs/006-avaliacao-mutua/evidence-t029.md). Medição: 2026-11-23.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature006-t029.json --junitxml=test-results-feature006-t029.xml`.
Formulário/rotas de avaliação integrados, CSRF e duplicata concorrente HTTP verificados no PostgreSQL; nenhuma nova migração. Qualidade final T006 permanece aberta.
<!-- feature-006-t029-quality:end -->


<!-- feature-006-t028-quality:start -->
Feature 006 / T001 documental + T002 unificada / roadmap T028 — **723 testes aprovados**, 0 ignorados: 55 novos e 668 anteriores. TDD inicial: 50 falhas pelo recurso ausente, depois verde; verificações complementares e regressão concluídas.
Cobertura consolidada de accounts/rides/reviews/carona_univille: **98.2361963190184%** combinada; linhas 1033/1048 (**98.56870229007633%**); ramificações 248/256 (**96.875%**). Pacote reviews, modelo e serviço: **100% de linhas e ramificações**. Meta: 80%.
Relatórios: [JSON](coverage-feature006-t028.json), [JUnit](test-results-feature006-t028.xml), [evidência](specs/006-avaliacao-mutua/evidence-t028.md). Medição: 2026-11-23.
Reproduzir: `venv/Scripts/python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature006-t028.json --junitxml=test-results-feature006-t028.xml`.
Migrações rides 0005/reviews 0001 aplicadas e verificadas no PostgreSQL local, com dados anteriores preservados. Conclusão e avaliação somente por serviço; formulários/rotas, marcação de no-show e reputação permanecem tarefas futuras.
<!-- feature-006-t028-quality:end -->


<!-- mvp-quality:start -->
MVP / Feature 005 / T007 local / roadmap T027 — **668 testes aprovados**, 0 ignorados; REQ-001–REQ-007. Medição: 2026-11-23.
Cobertura consolidada de `accounts/`, `rides/` e `carona_univille/`: **97.975352112676063%** combinada; linhas 905/920 (**98.3695652173913%**); ramificações 208/216 (**96.296296296296276%**). Meta: >=80% combinada, linhas e ramificações, também por módulo crítico de negócio.
Relatórios: [coverage-mvp.json](coverage-mvp.json), [test-results-mvp.xml](test-results-mvp.xml), [auditoria](specs/005-cancelamento-liberacao-vaga/evidence-t027.md).
Reproduzir: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-mvp-quality.ps1`. Métricas consolidadas; não são testes exclusivos da Feature 005. T041–T045 e tarefas de qualidade próprias de outras features não são concluídas automaticamente.
<!-- mvp-quality:end -->

<!-- feature-003-quality:start -->
Feature 003 / T005 â€” **142 testes de busca/matching aprovados**, 526 de regressÃ£o; total 668 aprovados, 0 ignorados. MediÃ§Ã£o: 2026-11-23.
Cobertura do pacote tÃ©cnico atual `rides/` com regressÃ£o: **99.36143039591316%** combinada; linhas 618/619 (99.838449111470112%); ramificaÃ§Ãµes 160/164 (97.5609756097561%). Meta: 80% em cada medida. Estes percentuais incluem as features posteriores de rides.
Matching separado: 100% linhas e 100% ramificaÃ§Ãµes. Novos nesta tarefa: 7; regressÃ£o anterior: 661 (grupos no JUnit).
RelatÃ³rios: [coverage-feature003.json](coverage-feature003.json), [test-results-feature003.xml](test-results-feature003.xml). Reproduzir: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-feature003-quality.ps1`.
DemonstraÃ§Ã£o humana SC-005 (atÃ© 1 minuto) e inspeÃ§Ã£o visual sÃ£o evidÃªncias separadas; este script nÃ£o as aprova nem conclui T005 automaticamente. [EvidÃªncia](specs/003-busca-rota-horario/evidence-t005.md).
<!-- feature-003-quality:end -->

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
Feature 002 / T007 â€” **115 testes de oferta aprovados**, 546 de regressÃ£o; total 661 aprovados, 0 ignorados. MediÃ§Ã£o: 2026-11-23.
Cobertura do pacote tÃ©cnico atual `rides/` com regressÃ£o: **99.36143039591316%** combinada; linhas 618/619 (99.838449111470112%); ramificaÃ§Ãµes 160/164 (97.5609756097561%). Meta: 80% em cada medida. Estes percentuais incluem as features posteriores de rides.
RelatÃ³rios: [coverage-feature002.json](coverage-feature002.json), [test-results-feature002.xml](test-results-feature002.xml). Reproduzir: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-feature002-quality.ps1`.
DemonstraÃ§Ã£o humana SC-005 e inspeÃ§Ã£o visual sÃ£o evidÃªncias separadas; este script nÃ£o as aprova nem conclui T007 automaticamente. [EvidÃªncia](specs/002-oferta-caronas-paradas/evidence-t007.md).
<!-- feature-002-quality:end -->
