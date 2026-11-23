# Evidência da Feature 010 / T002 local / T038 do roadmap

**Data** 2026-11-23. **Requisitos** REQ-012, REQ-002, REQ-003, REQ-017, FR-003, FR-004 e SC-003. O recorte da interface usa os avisos registrados pela [T037](evidence-t037.md).

O sino na navegação mostra o total de avisos não lidos da própria conta. A lista exibe o tipo do evento, a referência da carona, a data e o estado de leitura. A marcação exige POST com CSRF, preserva o primeiro instante de leitura e retorna à lista com o contador atualizado. A lista, a contagem e a atualização são filtradas pelo titular da sessão com vínculo acadêmico ativo.

## Verificações no PostgreSQL 16.15

| Verificação | Resultado |
| --- | --- |
| TDD inicial | Três falhas esperadas pela ausência do sino e das rotas. A proteção acadêmica já existente passou. |
| Regressão de renderização | A primeira execução detectou cinco falhas ao renderizar cadastro e busca sem middleware de autenticação. O processador de contexto passou a omitir o sino quando a requisição chega sem usuário. |
| Suítes focadas | 51 testes de notificações e cadastro aprovados após o ajuste, além dos quatro cenários de renderização da busca. |
| Suíte completa | 975 aprovados, incluindo quatro novos e 971 de regressão. Zero falhas, erros ou testes ignorados. |
| Cobertura consolidada | **99.13544668587896% em linhas** (1720/1735) e **96.48241206030151% em ramificações** (384/398). O pacote notifications atingiu 100% em ambas as medidas. |
| Django | `check` sem problemas e `makemigrations --check --dry-run` sem alterações. |

[Cobertura JSON](../../coverage-feature010-t038.json) · [Resultados JUnit](../../test-results-feature010-t038.xml).

## Reprodução em PostgreSQL

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_notifications.py tests/test_registration.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=notifications --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature010-t038.json --junitxml=test-results-feature010-t038.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
~~~
