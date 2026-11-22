# Trabalho_Trilhas-SDD_Carona-Univille

Feature 001 / T008 — 94 testes aprovados. Cobertura de `accounts/`: **96,04743083003953%**
(linhas: 207/213 = 97,1830985915493%; ramificações: 36/40 = 90%).
Relatório: [coverage.json](coverage.json). Medição em 2026-11-22.

Verificação da T008 e regressão de T002–T007: `venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_foundation.py tests/test_registration.py tests/test_activation.py --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
