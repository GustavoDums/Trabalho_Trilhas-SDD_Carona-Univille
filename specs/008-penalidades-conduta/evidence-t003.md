# Evidência da Feature 008 / T003 local / T033 do roadmap

**Data**: 2026-11-23. **Requisitos**: REQ-007, REQ-009, REQ-010, REQ-003 e REQ-017. **Dependências**: [Feature 008/T002](evidence-t032.md), [Feature 005/T002](../005-cancelamento-liberacao-vaga/tasks.md) e [Feature 007/T004](../007-calculo-reputacao/evidence-t004.md).

O cancelamento tardio de reserva ou oferta atualiza o estado, grava o evento e aplica uma dedução de 0,20 ao titular na mesma transação. O evento tempestivo mantém a nota. Reprocessar explicitamente um evento legado conhecido recupera sua penalidade e recompõe o cache a partir do histórico, inclusive quando o cache está ausente.

O recálculo usa as últimas 20 notas elegíveis. Em empate de instante entre avaliações mútuas e notas automáticas de no-show, as mútuas vêm primeiro. Dentro de cada origem, o maior PK tem prioridade. As deduções consideram as ocorrências até o instante de referência, inclusive quando a nota daquele no-show ficou fora da janela de 20. O fluxo que registra a denúncia e aplica a suspensão pertence à T004 local.

## Verificações no PostgreSQL 16.15

| Verificação | Resultado |
| --- | --- |
| TDD inicial | 11 falhas esperadas pela ausência de PenaltyService e da integração ao recálculo, com os 27 testes anteriores aprovados. |
| Concorrência | Um teste adicional reproduziu deadlock entre gravação direta de avaliação e cancelamento. O ajuste de locks de conta e oferta para FOR NO KEY UPDATE permite a validação das chaves estrangeiras e mantém as escritas serializadas. |
| Suíte focada | 307 testes aprovados. Inclui dedução única, replay de evento legado, rollback de reserva e oferta, cancelamentos simultâneos e coexistência do cancelamento com o signal de avaliação. |
| Suíte completa | 869 aprovados, incluindo 13 novos e 856 de regressão. Zero falhas ou testes ignorados. |
| Cobertura de accounts/rides/reviews/carona_univille | 98.82720875684129% em linhas (1264/1279) e 96.95945945945945% em ramificações (287/296). PenaltyService e ReputationService com 100% em ambas as medidas. |
| Django | `check` sem problemas. `makemigrations --check --dry-run` sem alterações. O esquema existente foi aplicado num banco PostgreSQL temporário e `migrate --plan` ficou vazio. |

[Cobertura JSON](../../coverage-feature008-t003.json) · [Resultados JUnit](../../test-results-feature008-t003.xml).

## Reprodução

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_penalties.py tests/test_cancellation_deadlines.py tests/test_cancellation_flow.py tests/test_reputation_calc.py tests/test_reputation_integration.py tests/test_reviews.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature008-t003.json --junitxml=test-results-feature008-t003.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
~~~
