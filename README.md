# Trabalho_Trilhas-SDD_Carona-Univille

Feature 001 / T009 — 130 testes aprovados. Cobertura de `accounts/`: **96,46643109540636%**
(linhas: 229/235 = 97,44680851063829%; ramificações: 44/48 = 91,66666666666667%).
Relatório: [coverage.json](coverage.json). Medição em 2026-11-22.

Verificação da T009 e regressão de T002–T008: `venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_foundation.py tests/test_registration.py tests/test_activation.py tests/test_access_control.py --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
