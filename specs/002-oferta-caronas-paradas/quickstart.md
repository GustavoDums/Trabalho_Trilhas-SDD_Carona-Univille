# Quickstart de validação — Feature 002

Este é um roteiro previsto para após a implementação das tarefas. Os comandos de rides ainda não podem ser tratados como verificados nesta entrega documental.

## Ambiente

Reutilizar venv, `.env` e PostgreSQL da Feature 001. Não sobrescrever credenciais ou recriar bancos existentes. Django cria o banco isolado de testes via pytest-django; usuário local precisa de permissão apropriada. Exclusivamente dados fictícios.

## Validações por etapa

Após T001/T002 locais:

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py migrate --plan
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe manage.py showmigrations rides
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe -m pytest tests/test_rides_offer.py -k model
```

Verificar migrações estrutural e de catálogo aplicadas no PostgreSQL, quatro códigos do catálogo de research.md, constraints, zero paradas e ordem preservada. Testar limites de clean/save e SQL conforme data-model.md. Cada tarefa segue vermelho → verde: escrever/rodar testes antes do código e registrar a falha esperada, sem usar apenas collect-only como sucesso.

Após publicação/consulta implementadas:

```powershell
.\venv\Scripts\python.exe -m pytest tests/test_rides_offer.py
.\venv\Scripts\python.exe -m pytest tests/test_models.py tests/test_foundation.py tests/test_registration.py tests/test_activation.py tests/test_access_control.py tests/test_privacy_lgpd.py
```

Na etapa de qualidade, executar o futuro `scripts/check-feature002-quality.ps1`: pytest-cov em `rides`, com branch, meta 80% combinada e separada em linhas/ramificações, relatórios `coverage-feature002.json` e `test-results-feature002.xml`; atualizar somente bloco Feature 002 do README. Conservar script e métricas Feature 001 sem misturar contagens. Não declarar cobertura de templates por coverage.py.

## Roteiro funcional

1. Registrar conta fictícia MOTORISTA, fazer login manual e ativar com e-mail elegível da whitelist existente. Visitante vai para login; pendente para ativação; passageiro ativo recebe 403 nas duas rotas de rides.
2. Abrir `/caronas/oferecer/`. Informar veículo sintético (modelo “Veículo Demo”, cor “Azul”, placa “FICTICIO”), saída futura e 3 vagas. Selecionar Terminal Central → Bairro América → Terminal Norte → Campus Univille.
3. Publicar. Esperar mensagem de sucesso e lista própria com exatamente uma oferta, duas paradas nessa ordem, sem e-mail ou placa. Reabrir lista e confirmar a persistência.
4. Publicar trajeto direto. Confirmar que ausência de paradas é válida.
5. Tentar vagas 0, -1 e 1,5; horário passado e igual ao instante de publicação; destino igual à origem; ponto desconhecido; parada repetida; linha vazia; modelo/cor/placa ausentes. Esperar erros e nenhuma publicação parcial. Testes de instante exato usam relógio controlado; não depender da digitação humana para esse limite.
6. Nova oferta deve sugerir veículo da última publicação própria; mudar valores e publicar não altera o veículo da oferta anterior. Tentativas de trocar autor por POST são ignoradas.
7. Usar segundo motorista em sessão separada: lista não contém a primeira oferta; parâmetros `driver`/`user_id` não mudam o filtro da sessão. Lista vazia informa como criar; POST de alteração na lista não é aceito.
8. Com dados preparados, medir tempo humano para publicar com duas paradas e conferir: até 2 minutos (SC-005). Registrar duração, condições e resultado; não inferir esse tempo da duração do pytest.

## Evidências esperadas

Testes executados e resultado real; relatórios de qualidade; verificação de migração no PostgreSQL; inspeção visual do formset e mensagens; duração da demo. Falhas de infraestrutura na criação de Waypoint devem reverter também RideOffer. Não usar dados reais nem liberar placa a terceiros. Matching, reserva, cancelamento e frota não fazem parte desta validação.
