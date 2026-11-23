# Trabalho_Trilhas-SDD_Carona-Univille

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
