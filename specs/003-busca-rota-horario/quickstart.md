# Quickstart previsto — Feature 003

Roteiro para depois da implementação. Nesta rodada não há matching, formulário ou rota de busca executados.

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

## Formulário e HTTP

Após T003/T004 locais:

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
