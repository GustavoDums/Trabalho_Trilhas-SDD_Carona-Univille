# Trabalho_Trilhas-SDD_Carona-Univille

Feature 001 / T005 — 60 testes aprovados. Cobertura de `accounts/`: **96,3855421686747%**
(linhas: 140/144 = 97,22222222222223%; ramificações: 20/22 = 90,9090909090909%).
Relatório: [coverage.json](coverage.json). Medição em 2026-11-22.

Verificação da T005 e regressão de T002–T004: `venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_foundation.py tests/test_registration.py --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
