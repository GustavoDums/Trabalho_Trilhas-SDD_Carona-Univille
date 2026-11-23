# Quickstart previsto — Feature 003

Atualização 2026-11-22: matching e formulário/cartões implementados e testados, conforme [evidência](evidence-t018.md). View/rota T004 local também implementada/verificada ([evidência HTTP](evidence-t019.md)); somente demo/qualidade final T005 permanece pendente. O roteiro HTTP está disponível; não há evidência de demo humana cronometrada nesta rodada.

## Pré-requisitos

Venv e PostgreSQL existentes, Features 001/002 disponíveis, catálogo da migração de rides carregado. Preservar `.env`, contas locais e relatórios anteriores. Testes e demo somente com dados sintéticos; pytest-django usa banco separado.

## Preparação e matching

Depois da T001 local (compatibilidade de serviços):

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe -m pytest tests/test_rides_offer.py
```

Após T002 local, correspondente à T017:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_matching.py
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
```

Não são previstas migrações. Testar todas as combinações de pontos na rota origem → parada1 → parada2 → destino; IDs deliberadamente fora da ordem do trajeto. Verificar inversão, ponto igual/ausente e rota direta.

Usar relógio controlado e horário desejado suficientemente futuro: referências −30min/0/+30min passam; −30min−1s/+30min+1s falham. Adicionar meia-noite, offsets equivalentes e partida exatamente now. A janela aprovada usa saída da origem, não passagem no embarque.

## Formulário isolado (T003 local)

Executado: `venv/Scripts/python.exe -m pytest tests/test_ride_search.py` — 27 testes aprovados com RequestFactory, sem endpoint.

## Formulário e HTTP

T003/T004 locais concluídas: 63 testes de formulário/HTTP aprovados. Para reproduzir:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_ride_search.py
.\venv\Scripts\python.exe -m pytest tests/test_models.py tests/test_foundation.py tests/test_registration.py tests/test_activation.py tests/test_access_control.py tests/test_privacy_lgpd.py tests/test_rides_offer.py
```

Confirmar formulário vazio sem resultados automáticos, erros dos três campos, estado vazio após busca válida, cartões sem nome completo/email/placa e sem reputação. `tolerance=999` não amplia janela. Comparar registros de domínio antes/depois da busca para provar ausência de escrita.

## Demo manual prevista

1. Publicar oferta sintética por motorista ativo, com saída futura, 3 vagas e dois pontos intermediários do catálogo.
2. Em sessão separada, cadastrar/ativar passageiro fictício e abrir `/caronas/buscar/`.
3. Selecionar embarque anterior ao desembarque e horário compatível com saída da origem. Confirmar nome abreviado, trajeto e aviso explícito de ausência de previsão de passagem.
4. Inverter pontos e confirmar nenhum resultado; corrigir e verificar bordas pela suíte automatizada, sem depender de digitar instantes de segundo exato.
5. Testar visitante/pendente/motorista bloqueados; desabilitar vínculo de um motorista sintético e confirmar que uma nova consulta não lista sua oferta.
6. Medir consulta com filtros preparados até identificar resultado em <=1 minuto (SC-005). Registrar tempo humano, condições e resultado; tempo do pytest não comprova essa meta.

## Qualidade

T005 local criará script e relatórios próprios, sem sobrescrever métricas das Features 001/002. Medir conjunto técnico `rides` executando regressão de ofertas e novos testes, verificando também o módulo de matching separadamente (linhas/ramificações >=80%). JUnit identifica quantos testes são novos da Feature 003 e quantos são regressão; não rotular toda a contagem combinada como testes exclusivos desta feature.

Relatórios previstos: `coverage-feature003.json`, `test-results-feature003.xml`. Atualizar bloco Feature 003 do README apenas após testes e metas passarem. Templates requerem testes do HTML e inspeção visual; coverage.py não mede HTML. Não alegar feature entregue enquanto checklist de implementação estiver aberto.

## Qualidade executada — 2026-11-23

Script disponível: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-feature003-quality.ps1`. 668 testes aprovados, 7 novos/661 anteriores; rides >=80% linhas/ramificações, matching 100%. [Evidência](evidence-t005.md). Relatórios das outras features preservados. Inspeção visual e demo humana continuam pendentes.

### Próximo passo humano — SC-005

Usar sessão separada (outro perfil/janela privada) para não perder o login de motorista. Cadastrar uma conta fictícia PASSAGEIRO com e-mail elegível, por exemplo lucas.aluno@univille.br se ainda não usado com outro papel; definir senha, fazer login e acionar validação de vínculo. Não há senha padrão. Papel fixo: conta motorista não pode buscar.

Abrir http://127.0.0.1:8000/caronas/buscar/. Com dados preparados de uma oferta ainda futura, iniciar cronômetro, selecionar embarque anterior ao desembarque e horário desejado igual à saída da origem (não ao horário suposto da parada), buscar e identificar o resultado. Parar a contagem na identificação. Limite <=60 segundos. Conferir rota, nome abreviado, ausência de placa/e-mail e aviso de ±30 minutos pela saída da origem. Depois inverter pontos para verificar vazio. Informar tempo real e se campos, mensagens e resultados estão legíveis, sem problemas visuais. Não confundir com demonstração de publicação já aceita na Feature 002. Caso a oferta tenha passado, preparar outra oferta sintética futura antes do cronômetro.

## Aceite humano final — 2026-11-23

Após relato de que o teste funcionou, foi perguntado explicitamente se o usuário também realizou a busca, encontrou a oferta em até um minuto e conferiu a legibilidade da tela, em vez de apenas ativar o perfil. Resposta: “sim”. SC-005 e inspeção visual aprovados por confirmação humana, sem atribuir tempo exato em segundos ou usar duração de pytest. T005 concluída; registros parciais anteriores são históricos e substituídos por este aceite quanto às pendências.

Resultado técnico permanece 668 testes aprovados (7 novos/661 de regressão anterior), rides 99.83844911147011% linhas e 97.5609756097561% ramificações; matching 100% em ambas. Somente documentação atualizada nesta confirmação, sem repetir testes, staging ou commit. Feature 005/T007, correspondente à T027 do roadmap, ainda não executada.
