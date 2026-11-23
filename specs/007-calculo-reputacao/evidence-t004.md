# Evidência da Feature 007 / T004 local — 2026-11-23

A T004 cobre o recálculo automático da T031 do roadmap e atende a REQ-003, REQ-009, REQ-017, FR-003 e SC-003. As dependências são a [T002 da Feature 007](evidence-t030.md) e a [T004 da Feature 006](../006-avaliacao-mutua/evidence-t029.md). O perfil e a busca são critérios da T005 local.

O `post_save` de uma nova avaliação chama `ReputationService.rebuild` para o usuário avaliado. O save e o recálculo compartilham a transação. Um rollback reverte os dois. O serviço mantém a regra homologada e reconstrói a nota quando o cache falta. A oferta e as contas usadas pelo serviço de avaliações mantêm locks que serializam escritas e permitem verificações concorrentes de chaves estrangeiras no PostgreSQL.

| Verificação | Resultado |
| --- | --- |
| TDD inicial | 8 falhas esperadas pela ausência do signal. Os 8 casos passaram após a integração. |
| Regressão de concorrência | O teste adicional reproduziu um deadlock entre uma gravação direta e uma pelo serviço. Passou após o ajuste do lock da oferta e das contas. |
| Integração no PostgreSQL 16.15 | 9 testes aprovados. Cobrem atualização imediata do destinatário, cache ausente, idempotência, fixtures raw e saves sem criação, rollback com e sem cache, falha no recálculo e concorrência com conexões independentes. |
| Suíte completa | 829 aprovados, 0 falhas ou ignorados. Foram 9 testes novos e 820 de regressão. |
| Cobertura de accounts/rides/reviews/carona_univille | 98.73524451939292% das linhas (1171/1186) e 96.80851063829788% das ramificações (273/282). Signal e serviço de reputação com 100% em ambas as medidas. |
| Django | `manage.py check` sem problemas e `makemigrations --check --dry-run` sem alterações. |

Os testes usaram Python 3.12.10, PostgreSQL temporário local e dados fictícios. A execução aplicou as migrações existentes apenas nos bancos de teste. [Cobertura JSON](../../coverage-feature007-t004.json) · [Resultados JUnit](../../test-results-feature007-t004.xml).

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_reputation_integration.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature007-t004.json --junitxml=test-results-feature007-t004.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
~~~
