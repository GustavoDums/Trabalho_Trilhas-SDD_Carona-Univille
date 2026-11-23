# Evidência da Feature 008 / T005 e T006 locais / T034 do roadmap

**Data**: 2026-11-23. **Requisitos**: REQ-002, REQ-003, REQ-010 e REQ-017; FR-003, FR-004 e SC-004. **Dependências**: middleware da Feature 001/T009 e [fluxo de no-show da Feature 008/T004](evidence-t004.md).

Na T005, o middleware retorna HTTP 403 durante a suspensão para as rotas de oferecer e reservar carona. Os serviços também consultam a suspensão após bloquear o usuário, antes das escritas. O limite é exclusivo, então a ação volta a ser permitida no instante de expiração. O vínculo acadêmico, a autenticação e o cancelamento de compromissos existentes seguem os contratos aprovados. A rota de saída por POST com CSRF está disponível a partir do perfil.

Na T006, o extrato em /conta/conduta/ usa somente a identidade da sessão. Exibe motivo, prazo e estado da suspensão e tipo, data e dedução das próprias ocorrências. A resposta tem no-store, e o template não recebe dados de identificação de contrapartes. O extrato é acessível no perfil e no aviso de suspensão.

## Verificações no PostgreSQL 16.15

| Verificação | Resultado |
| --- | --- |
| TDD da T005 | 7 falhas esperadas antes da integração do bloqueio e da rota de saída, seguidas de 7 aprovações. |
| TDD da T006 | 3 falhas esperadas antes do extrato e dos links. |
| Suíte focada | 34 testes aprovados. Cobrem bloqueio em HTTP e serviço, terceiro no-show, expiração, login, saída protegida por CSRF, cancelamento, privacidade do extrato e regressão da tela de ativação. |
| Suíte completa | 905 aprovados, incluindo 10 novos e 895 de regressão. Zero falhas ou testes ignorados. |
| Cobertura consolidada | 98.94957983193277% em linhas (1413/1428) e 96.7065868263473% em ramificações (323/334). Middleware e serviço de suspensão com 100% em ambas as medidas. View do extrato com 13/13 linhas cobertas. |
| Django | `check` sem problemas. `makemigrations --check --dry-run` sem alterações. |

[Cobertura JSON](../../coverage-feature008-t034.json) · [Resultados JUnit](../../test-results-feature008-t034.xml).

## Reprodução

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_penalties_flow.py tests/test_activation.py::test_activation_get_shows_own_data_without_side_effects -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature008-t034.json --junitxml=test-results-feature008-t034.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
~~~
