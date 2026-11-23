# Evidência — Feature 003 / T005 local (concluída)

Data: 2026-11-23. REQ-005, REQ-003, REQ-017, REQ-018, REQ-019; SC-001–SC-005. Correspondência: governança/aceitação final da Feature 003, após roadmap T017–T019 (T002–T004 locais). Dependência T004 e Feature 002 disponíveis; Feature 002/T007 encerrada por aceite humano. Somente T005 autorizada nesta rodada; não executar T027.

## Aceitação e sequência de testes

Adicionados sete casos em [test_ride_search.py](../../tests/test_ride_search.py): cadastro/login/ativação HTTP reais com sessão e CSRF, motorista publica oferta com duas paradas pela view existente, passageiro ativo busca trecho intermediário; centro/±30min inclusivos e ±30min01s fora; nome completo/e-mail/placa não aparecem; consulta não altera ofertas/paradas/reservas; motorista recebe 403; ativação recusada para conta inelegível/ausente mantém passageiro bloqueado. Nenhum force_login nesses novos casos.

Testes foram escritos e executados antes de qualquer mudança de produção. Primeira execução falhou por import de Client ausente no helper de teste (NameError); corrigido apenas o teste, sete aprovados em 8.11s. Essa falha não é classificada como vermelho comportamental de produto. A aplicação existente já atende aos novos cenários; não se introduziu alteração de comportamento ou falha artificial para simular TDD. Nenhum arquivo de produção alterado.

## Qualidade automatizada

[check-feature003-quality.ps1](../../scripts/check-feature003-quality.ps1) executa toda tests/, incluindo ofertas e seis módulos de accounts. Mede rides atual com regressão e matching_service separadamente, rejeita resultados abaixo de 80% em linhas/ramificações ou cobertura combinada, publica JSON/JUnit próprios e atualiza somente bloco Feature 003 do README após sucesso. Não conclui demo/checklist automaticamente.

- 668 aprovados, zero ignorados/falhas, 94.04s.
- 142 de busca/matching: 77 em test_ride_search.py e 65 em test_matching.py; 526 dos demais módulos, incluindo 115 de oferta.
- Nesta tarefa: 7 novos e 661 de regressão anterior. Propriedades feature003_new_tests=7 e previous_regression_tests=661 no JUnit; não confundir 142 acumulados com testes novos.
- rides: 618/619 linhas (99.83844911147011%), 160/164 ramificações (97.5609756097561%), combinada 99.36143039591316%. Inclui funcionalidades posteriores de rides, sem omitir código para inflar cobertura.
- matching_service: 61/61 linhas e 18/18 ramificações, 100% de ambas. Meta >=80% atendida.
- [JSON](../../coverage-feature003.json), [JUnit](../../test-results-feature003.xml), [README](../../README.md). Relatórios anteriores das outras features não sobrescritos.
- manage.py check sem problemas, makemigrations --check --dry-run sem alterações, migrate --plan sem operações. PostgreSQL de testes existente; sem mudança em dados locais ou schema.
- Diagnósticos do editor sem erros no arquivo Python alterado. git diff --check sem erros. Checklist documental requirements.md 16/16 já marcado, não editado; sem hooks. Ponteiro de feature preservado, git inicialmente limpo.

~~~powershell
.\venv\Scripts\python.exe -m pytest tests/test_ride_search.py -k acceptance_search -q --tb=short
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-feature003-quality.ps1
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
~~~

## Critério humano ainda pendente

HTML verificado por testes; não foi feita inspeção visual nova nem demo humana de busca nesta rodada. [Quickstart](quickstart.md) contém roteiro com passageiro ativo em sessão distinta do motorista. Publicar uma oferta pela Feature 002 não equivale a demonstrar busca pela Feature 003. Medir consulta com filtros preparados até identificar resultado em <=60 segundos, conferir aviso de saída da origem/±30min, nome abreviado e ausência de placa/e-mail. Relatar duração e qualquer problema visual. Não usar 94.04s de suíte como duração humana.

T005 permanece aberta até comprovação desse critério ou decisão explícita do usuário. Sem staging/commit. Arquivos: teste e script citados, JSON/JUnit, README, [tasks](tasks.md), [plan](plan.md), [quickstart](quickstart.md), [prompts](../../docs/prompts.md) e esta evidência. Nenhuma tarefa Feature 005/T007 executada.

Commit sugerido: test(003/T005): validar busca integrada e métricas — REQ-005, REQ-003, REQ-017, REQ-018, REQ-019

## Aceite humano final — 2026-11-23

Após relato de que o teste funcionou, foi perguntado explicitamente se o usuário também realizou a busca, encontrou a oferta em até um minuto e conferiu a legibilidade da tela, em vez de apenas ativar o perfil. Resposta: “sim”. SC-005 e inspeção visual aprovados por confirmação humana, sem atribuir tempo exato em segundos ou usar duração de pytest. T005 concluída; registros parciais anteriores são históricos e substituídos por este aceite quanto às pendências.

Resultado técnico permanece 668 testes aprovados (7 novos/661 de regressão anterior), rides 99.83844911147011% linhas e 97.5609756097561% ramificações; matching 100% em ambas. Somente documentação atualizada nesta confirmação, sem repetir testes, staging ou commit. Feature 005/T007, correspondente à T027 do roadmap, ainda não executada.
