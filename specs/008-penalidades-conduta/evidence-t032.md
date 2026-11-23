# Evidência da Feature 008 / T002 local / T032 do roadmap

**Data**: 2026-11-23. **Requisitos**: REQ-010, REQ-003 e REQ-017. **Dependências**: [decisões D008-01/D008-02 da T001](spec.md) e [cálculo de reputação da Feature 007/T002](../007-calculo-reputacao/evidence-t030.md).

- `PenaltyRecord` preserva as referências históricas, vincula a dedução ao cancelamento tardio original e restringe no-show a uma ocorrência por usuário e oferta. O tipo de ocorrência determina a nota automática e o delta decimal é aplicado uma vez por origem.
- `ConductProfile` guarda a suspensão separadamente do vínculo acadêmico. O teste usa três no-shows distintos, inclui a borda de 30 dias e confirma liberação no instante de expiração após 14 dias.
- O cálculo do modelo entrega os componentes para a recomposição da nota e o prazo da suspensão. O serviço que aplica esses efeitos pertence à T033, e o bloqueio de ações no sistema à T034.

## Verificações no PostgreSQL 16.15

| Verificação | Resultado |
| --- | --- |
| TDD inicial | 25 testes falharam pela ausência dos modelos. |
| Suíte focada | 27 aprovados, incluindo dois casos adicionais de validação. |
| Suíte completa | 856 aprovados, incluindo 27 novos e 829 de regressão, com 0 falhas ou ignorados. |
| Cobertura de accounts/rides/reviews/carona_univille | 98.79711307137129% em linhas (1232/1247) e 96.93877551020408% em ramificações (285/294). PenaltyRecord e ConductProfile com 100% em ambas as medidas (52 linhas e 12 ramificações). |
| Unicidade e rollback | Duas transações concorrentes tentam registrar o mesmo no-show com chaves diferentes. Uma grava, a outra é rejeitada. O rollback preserva reputação e conduta. |
| Migração | `reviews.0003_penaltyrecord_conductprofile` aplicada em banco temporário com registros sintéticos preexistentes. A comparação confirmou a preservação integral de 2 contas, 4 pontos de rota, 1 oferta, 1 reserva, 1 cancelamento, 1 avaliação e 1 perfil de reputação. As duas novas tabelas foram criadas vazias. |
| Django | `check` sem problemas. `makemigrations --check --dry-run` sem alterações. `migrate --plan` vazio após a aplicação. |

[Cobertura JSON](../../coverage-feature008-t032.json) · [Resultados JUnit](../../test-results-feature008-t032.xml).

## Reprodução

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_penalties.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature008-t032.json --junitxml=test-results-feature008-t032.xml
.\venv\Scripts\python.exe manage.py sqlmigrate reviews 0003
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
~~~
