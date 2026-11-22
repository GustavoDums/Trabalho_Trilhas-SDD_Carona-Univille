# Trabalho_Trilhas-SDD_Carona-Univille

Feature 001 / T007 — 82 testes aprovados. Cobertura de `accounts/`: **95,65217391304348%**
(linhas: 188/194 = 96,90721649484536%; ramificações: 32/36 = 88,88888888888889%).
Relatório: [coverage.json](coverage.json). Medição em 2026-11-22.

Verificação da T007 e regressão de T002–T006: `venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_foundation.py tests/test_registration.py tests/test_activation.py --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
