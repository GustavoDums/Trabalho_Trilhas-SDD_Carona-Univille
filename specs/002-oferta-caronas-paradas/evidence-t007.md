# Evidência parcial — Feature 002 / T007 local

Data: 2026-11-23. Requisitos REQ-004, REQ-018, REQ-019; SC-001–SC-005. Dependência T006 concluída. Escopo autorizado após diagnóstico de T027: executar somente Feature 002/T007, antes de Feature 003/T005 e Feature 005/T007. Nenhuma mudança de produto, staging ou commit.

## Qualidade técnica verificada

Criado [check-feature002-quality.ps1](../../scripts/check-feature002-quality.ps1), PowerShell 5.1+, venv existente. Executa toda tests/, incluindo test_rides_offer.py e seis módulos de accounts, mede pacote rides atual com branches e meta combinada/linhas/branches >=80%, gera JSON/JUnit, conta suíte de oferta separada da regressão e atualiza somente bloco Feature 002 do README após sucesso. Não aprova demo nem altera checklist automaticamente. Mantém código de saída de erro e README preservado se testes/meta falharem.

Medição inicial isolada: 115 testes de oferta aprovados em 9.99s; cobertura do pacote rides atual aproximadamente 55%, pois agora contém serviços de busca/reserva/cancelamento. Sem excluir código para inflar cobertura, o script inclui regressão das funcionalidades atuais. Não confundir cobertura de pacote técnico com cobertura exclusiva de oferta.

Execução do script: 661 aprovados, 0 ignorados, 81.26s; 115 de oferta e 546 de regressão. [Cobertura](../../coverage-feature002.json): 618/619 linhas (99.83844911147011%), 160/164 ramificações (97.5609756097561%), combinada 99.36143039591316%. [JUnit](../../test-results-feature002.xml). Meta >=80% atendida. Relatórios da Feature 001 não alterados; indicadores anteriores das demais features preservados. Sem novos testes de produto nem falha artificial de TDD: mudança apenas em automação de qualidade/documentação; a suíte existente foi executada antes do script e a implementação do script foi executada com sucesso.

Django check sem problemas; makemigrations --check --dry-run sem alterações; migrate --plan sem operações. Nenhuma migração ou dado de desenvolvimento modificado.

## Navegador e limites da evidência

Preview temporário renderizado do template atual com formulário/formset e catálogo local, em .pytest_cache (não versionado), com JavaScript real de offer.js. Sem sessão/POST/CSRF de aplicação nesse preview; não serve para comprovar persistência. Publicação e controles HTTP foram verificados pela suíte Django.

Árvore de acessibilidade mostrou rótulos e catálogo, contador de zero paradas; adicionar duas linhas resultou em duas paradas. Selecionadas Bairro América e Campus Univille; remover a primeira manteve Campus Univille e contador de uma parada. Nenhuma publicação ou dado persistido nessa interação. As tentativas de screenshot não forneceram imagem inspecionável; integração alternativa de captura retornou “The browser access host is unavailable”. Portanto inspeção visual de layout/mensagens não é declarada concluída.

**SC-005 pendente**: demonstração humana com duas paradas e conferência em até 2 minutos. Não usar 9.99s/81.26s de pytest ou interação automatizada como duração humana. Usuário deve executar o roteiro preparado no quickstart e informar duração real, sequência observada e problemas visuais. T007 permanece [ ] até isso e inspeção visual serem comprovados. Feature 003/T005 e T027 não executadas.

## Reprodução

~~~powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-feature002-quality.ps1
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
~~~

Arquivos alterados/criados: script citado, JSON/JUnit, [README](../../README.md), [tasks](tasks.md), [quickstart](quickstart.md), [prompts](../../docs/prompts.md) e esta evidência. Nenhum código de aplicação alterado.

Commit sugerido para a parte técnica: chore(002/T007): automatizar métricas de oferta e regressão — REQ-004, REQ-018, REQ-019
