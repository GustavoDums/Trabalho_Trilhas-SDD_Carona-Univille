# Evidência — Feature 002 / T007 local (concluída por aceite final)

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

## Atualização de validação humana — 2026-11-23

Usuário acessou aplicação Django local com conta motorista ativa, publicou uma oferta e relatou: “deu certo, salvou”; depois informou “foi algo em torno de 2 minutos sim”. Esse tempo é estimativa humana, não medição cronometrada nem duração de teste automatizado. Não foi convertido em 120 segundos exatos ou prova inequívoca de <=120s.

Leitura da página real /caronas/minhas-ofertas/ confirmou mensagem “Oferta de carona publicada com sucesso.” e itinerário persistido com duas paradas: Terminal Central (origem) → Terminal Norte → Bairro América → Campus Univille (destino). A sequência é a escolhida pelo usuário, distinta do exemplo do roteiro, e usa quatro pontos distintos válidos. O usuário havia relatado que “a princípio está de acordo”; isso é avaliação preliminar, sem detalhamento visual conclusivo.

Publicação humana e presença de duas paradas estão comprovadas. Permanecem sem comprovação estrita a duração <=120s (estimativa no limite) e inspeção visual final. T007 continua aberta; nenhuma mudança de requisito ou dispensa de critério foi presumida. Nenhum teste repetido por atualização exclusivamente documental.

## Aceite final do usuário — 2026-11-23

Após esclarecer a ausência de cronometragem exata e confirmação visual, o usuário determinou: “pode encerrar na verdade, está tudo de acordo”. Essa aprovação encerra a inspeção visual e aceita, para esta rodada, o relato humano de aproximadamente dois minutos sem exigir nova execução cronometrada. T007 concluída por aceite explícito, com ressalva documental: não existe medição exata que demonstre <=120s. Não converter estimativa em duração exata ou duração de teste automatizado.

Os registros parciais anteriores são históricos e substituídos por este aceite quanto ao estado da tarefa. Resultado técnico: 661 testes aprovados (115 oferta/546 regressão), linhas 99.83844911147011%, ramificações 97.5609756097561%. Encerramento documental, sem rerodar testes, staging ou commit. Feature 003/T005 e Feature 005/T007 não iniciadas.
