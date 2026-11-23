# Evidência da Feature 008 / T004 local / T033 do roadmap

**Data**: 2026-11-23. **Requisitos**: REQ-010, REQ-003, REQ-017; FR-001, FR-005; SC-003. **Dependências**: [Feature 008/T003](evidence-t003.md) e [Feature 006/T004](../006-avaliacao-mutua/evidence-t029.md), que incorporou a antiga T005.

O motorista titular registra a conclusão em Minhas ofertas. A contraparte confirmada declara o não comparecimento em Minhas reservas. Autor e alvo vêm da sessão e da reserva, e os horários vêm do servidor. O fim da tolerância é o instante da ocorrência. Quando não há conclusão registrada e o motorista é o ausente, o fim da tolerância também inicia a janela de 2 horas. O modelo atual tem horário previsto para a origem.

Uma ocorrência por usuário e oferta alimenta a nota automática 1,0, a dedução 0,50 e a projeção de 14 dias de suspensão após três no-shows distintos em 30 dias. O terceiro evento é identificado pelo horário da ocorrência, inclusive quando as denúncias chegam em outra ordem. A transação grava a declaração, os efeitos sobre a reputação, o marcador de reserva para ausência do passageiro e a projeção disciplinar. Os testes reproduzem falha após a gravação da penalidade e confirmam o rollback da operação.

## Verificações no PostgreSQL 16.15

| Verificação | Resultado |
| --- | --- |
| TDD inicial | 23 falhas esperadas antes da existência do serviço e das rotas. Os 40 testes anteriores de penalidades passaram. |
| Suíte focada | 278 testes aprovados. Inclui sessão, CSRF, autorização, adulteração de dados, tolerância e limites inclusivos, duplicidade concorrente, rollback e projeção fora da ordem de denúncia. |
| Suíte completa | 895 aprovados, incluindo 26 novos e 869 de regressão. Zero falhas ou testes ignorados. |
| Cobertura de accounts/rides/reviews/carona_univille | 98.91461649782923% em linhas (1367/1382) e 96.64634146341463% em ramificações (317/328). PenaltyService atingiu 100% em linhas e 93,75% em ramificações. |
| Django | `check` sem problemas. `makemigrations --check --dry-run` sem alterações. |

[Cobertura JSON](../../coverage-feature008-t004.json) · [Resultados JUnit](../../test-results-feature008-t004.xml).

## Reprodução

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_penalties_flow.py tests/test_penalties.py tests/test_reviews.py tests/test_rides_offer.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature008-t004.json --junitxml=test-results-feature008-t004.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
~~~
