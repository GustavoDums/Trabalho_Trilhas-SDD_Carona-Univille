# Evidência da Feature 007 / T005 local / T031 do roadmap

**Data** 2026-11-23 · **Requisitos** REQ-009, REQ-003 e REQ-017 · **Critérios** FR-004 e SC-004.

O perfil próprio e os cartões da busca mostram a nota de reputação com estrela decorativa e valor decimal legível. O perfil lê a nota do usuário da sessão. A busca projeta apenas a nota do motorista e preserva os filtros e campos de privacidade. O valor inicial de 5,00 é mostrado quando a projeção não existe, e uma nota registrada de 0,00 é preservada.

O cálculo atualiza a projeção pelo signal existente. A busca usa a relação com a nota na consulta de ofertas, com a mesma quantidade de consultas em cenários de uma e quatro ofertas. A leitura não cria projeções.

## Verificações em PostgreSQL

| Verificação | Resultado |
| --- | --- |
| TDD | Dois cenários falharam pela ausência da nota no perfil e no DTO da busca. |
| Suíte focada | 169 testes passaram, incluindo cálculo integrado, busca e privacidade. |
| Suíte completa | 992 testes passaram no PostgreSQL 16.15, incluindo dois novos e 990 de regressão. |
| Cobertura | **98.96401308615049% em linhas** (1815/1834) e **96.41148325358851% em ramificações** (403/418). |
| Django | `check` passou e `makemigrations --check --dry-run` não encontrou mudanças. |

[Cobertura JSON](../../coverage-feature007-t005.json) · [Resultados JUnit](../../test-results-feature007-t005.xml).

## Reprodução

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_reputation_integration.py tests/test_matching.py tests/test_ride_search.py tests/test_privacy_lgpd.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=notifications --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature007-t005.json --junitxml=test-results-feature007-t005.xml
~~~
