# Evidência — Feature 007/T001 e T002 unificada / roadmap T030

Data: 2026-11-23. REQ-009, REQ-003, REQ-017; FR-001/FR-002; SC-001/SC-002. D007-01/D007-02 homologadas antes da produção; usuário autorizou T001 documental e T002 unificada incorporando antiga T003. Dependência Feature 006/T002 concluída; referências antigas aos IDs incorporados da 006 remapeadas, sem concluir a qualidade própria dessa feature. T031/signals/apresentação não executadas.

## Política e implementação

Média simples das últimas 20 avaliações recebidas, pesos iguais inclusive na mesma oferta, sem expiração por 30 dias ou agrupamento por carona. Seleção RideReview.reviewed_user_id, created_at <= referência, ordem created_at DESC/id DESC e LIMIT 20. Novato 5.00 somente no conjunto vazio, sem nota virtual. Exemplos [5,5,4,5,4]=4.60 e [5,5,5,1]=4.00; arredondamento 4.125→4.13.

calculate_score valida até 20 notas inteiras 1..5, rejeita bool/float/texto/fração e usa Decimal em Context próprio (precisão 28, HALF_UP), isolado da precisão, arredondamento e traps do chamador. Quantização para duas casas somente no final.

ReputationProfile: user OneToOne/PROTECT, score Decimal(3,2) default 5.00 e intervalo 0.00..5.00 com validadores/check; computed_at aware opcional, NULL quando nunca reconstruído. Modelo rejeita floats/bools, valores não finitos e excesso de casas sem truncamento silencioso. SQL numeric limita escala; escritas SQL/bulk não são API de domínio. Zero é permitido para futura integração 008, sem aplicar penalidades aqui.

ReputationService.rebuild é interno, sem endpoint: bloqueia usuário mesmo com cache ausente, captura referência aware uma vez (ou recebe at interno), normaliza UTC, seleciona fontes persistidas e recalcula integralmente. Bloqueia profile após usuário e grava/cria na mesma transação. Repetição com mesmas fontes/referência mantém mesmo profile/valor, sem somar delta ou alterar avaliações. Referência histórica explícita é suportada; não reclassifica avaliações antigas devido a mudanças atuais de vínculo. Cache é reconstruível, não substitui RideReview.

Nenhuma criação automática no cadastro/avaliação, signal, template, DTO de busca ou API pública conectada; T031 fará integração. Penalidades ficam 008. Sem contador novo ou dados pessoais na pontuação pública nesta rodada.

## TDD e regressão

- Vermelho inicial: 53 falhas por modelo ReputationProfile/serviço ausentes, depois 53 aprovados.
- Verificação adicional de timestamp aware no perfil: 54 aprovados. Primeira regressão completa: 819 aprovados.
- Teste adicional de contexto Decimal externo com trap Inexact: falhou por decimal.Inexact ao arredondar. Substituído contexto herdado por Context próprio, sem mudar fórmula; focado final 55 aprovados, serviço 100% de linhas/branches.
- Regressão final: **820 aprovados, 0 ignorados/falhas, 89.57s**; 55 novos e 765 anteriores.

Cobertura dos casos: novato/nota única sem base virtual; exemplos determinísticos; HALF_UP/precisão/traps externos; nota fora do intervalo/tipo/fração/mais de 20; limites armazenados 0/5; NaN/Infinity/float/bool/None/excesso de casas; OneToOne/PROTECT e SQL; 21ª expulsando mais antiga; corte temporal inclusivo e um microssegundo antes; empate por ID; múltiplas avaliações da mesma viagem; ausência de expiração após 90 dias; isolamento por avaliado; conta historicamente desabilitada; cache ausente/stale/repetição; IDs inválidos e usuário ausente; referência naive/texto recusada e offset UTC equivalente; relógio capturado uma vez; rollback em criação/atualização; concorrência PostgreSQL.

Concorrência: PIDs **30520/37156**, TxIDs **69690/69691**, ambos retornaram **4.60**, mesmo profile **26**, exatamente uma projeção. Conexões/transações independentes com barreira e lock_timeout 10s, sem sleep ou mock de lock. Metadados no [JUnit](../../test-results-feature007-t030.xml).

## Métricas e verificações

[JSON](../../coverage-feature007-t030.json): accounts/rides/reviews/carona_univille, linhas **1158/1173 (98.72122762148338%)**, ramificações **271/280 (96.78571428571429%)**, combinada **98.34824501032347%**. Serviço de reputação: **43/43 linhas e 14/14 ramificações (100%)**. Módulo reviews/models.py: 49/49 linhas (100%) e 15/16 ramificações (93.75%); ramo não coberto é exclusão explícita do campo score na validação, fora da API atual. Demais lacunas consolidadas preexistentes em accounts/ASGI/WSGI e defesa da reconsulta de cancelamento. Meta >=80% atendida, sem exclusões para inflar cobertura.

Django check sem problemas; makemigrations --check --dry-run sem alterações; migrate --plan sem operações após aplicação. Diagnósticos do editor sem erros em modelo/serviço/testes; git diff --check sem erros. Pré-requisitos Spec Kit conferidos, sem hooks/checklist adicional, ponteiro da feature preservado. Git inicialmente limpo; relatórios anteriores preservados. Sem staging ou commit.

## Migração local

Plano e SQL de reviews.0002_reputationprofile revisados e aplicados no PostgreSQL local sem reset. Nova tabela vazia, sem backfill de notas. Snapshot em memória de todas as colunas anteriores preservado: accounts_academicuser 3, academicvalidationrecord 4, routepoint 4, rideoffer 1, waypoint 2, ridebooking 0, cancellationrecord 0, ridereview 0. Nenhum conteúdo de usuário/credencial impresso ou versionado. Introspecção confirmou FK, unicidade user_id e reputation_score_range. Banco de testes aplica a migração; dados sintéticos das fontes foram criados pelo fluxo de reserva/conclusão/avaliação já existente.

## Reprodução e arquivos

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_reputation_calc.py -q --tb=short
.\venv\Scripts\python.exe -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=reviews --cov=carona_univille --cov-branch --cov-report=term-missing --cov-report=json:coverage-feature007-t030.json --junitxml=test-results-feature007-t030.xml
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
~~~

Código: [reviews/models.py](../../reviews/models.py), [reputation_service.py](../../reviews/services/reputation_service.py), [migração 0002](../../reviews/migrations/0002_reputationprofile.py), [test_reputation_calc.py](../../tests/test_reputation_calc.py).

Artefatos: [spec](spec.md), [plan](plan.md), [tasks](tasks.md), [dados](data-model.md), [pesquisa](research.md), [contratos](contracts/web-routes.md), [quickstart](quickstart.md), esta evidência, [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md), [prompts](../../docs/prompts.md), [README](../../README.md), JSON/JUnit acima. Não há interface nova para demo nesta tarefa; roteiro técnico verificado, sem alegação de inspeção visual ou atualização automática.

T001/T002 e T030 concluídas; T003 incorporada, T004–T006 abertas. Commit sugerido: feat(007/T002): calcular reputação e concluir T030 — REQ-009, REQ-003, REQ-017
