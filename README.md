# Trabalho_Trilhas-SDD_Carona-Univille

<!-- feature-001-quality:start -->
Feature 001 / T012 — 152 testes aprovados; 0 ignorados. Meta: **80%**.
Cobertura combinada de `accounts/` e `carona_univille/views.py`: **96.845425867507885%**.
Linhas: 259/265 (97.735849056603769%); ramificações: 48/52 (92.3076923076923%).
Relatórios: [coverage.json](coverage.json) e [test-results.xml](test-results.xml). Medição: 2026-11-22.

Reproduzir: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-quality-metrics.ps1`.
<!-- feature-001-quality:end -->

<!-- feature-002-quality:start -->
Feature 002 / roadmap T014 (parcial) / T003 local — **70 testes aprovados**.
Modelos e publicação; T004 e tarefas seguintes ainda pendentes. Cobertura de `rides/`: **97.89915966386555%** combinada;
linhas: 191/192 (99.47916666666667%); ramificações: 42/46 (91.30434782608695%). Meta: 80%.
Relatórios: [coverage-feature002.json](coverage-feature002.json) e [test-results-feature002.xml](test-results-feature002.xml).
Medição: 2026-11-22. Reproduzir: `venv/Scripts/python.exe -m pytest tests/test_rides_offer.py --cov=rides --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature002.json --junitxml=test-results-feature002.xml`.
<!-- feature-002-quality:end -->
