# Trabalho_Trilhas-SDD_Carona-Univille

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
