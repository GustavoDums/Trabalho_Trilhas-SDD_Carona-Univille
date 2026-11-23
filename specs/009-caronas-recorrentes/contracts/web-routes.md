# Contratos: Caronas recorrentes

**Status**: política homologada na [spec](../spec.md).

GET/POST /caronas/recorrentes/ atende motorista titular ativo, com listagem própria e criação com CSRF. O POST cria a regra, suas paradas e as ofertas na mesma transação. O GET exibe as datas existentes na janela atual e o estado de cada oferta. GET e leitura da busca são operações sem escrita.

O operador de confiança executa `manage.py generate_recurring_rides --all` na rotina diária ou usa `--rule ID` para uma regra. O comando usa a mesma referência para todas as regras da execução, ignora titulares inelegíveis e imprime apenas a identificação da regra e as datas criadas ou existentes. Um erro reverte o lote da regra afetada. Regras independentes podem concluir, e o comando retorna erro ao final se algum lote falhar.

`RecurringRideService.generate(rule_id=..., driver=...)` retorna as datas criadas e já existentes para o titular. O horizonte da D009-01 revisada vai da data local de referência até o 15º dia útil, inclusive, com partidas estritamente futuras. Repetição conserva a oferta original de cada data, inclusive se cancelada.

O calendário vem de `GET https://brasilapi.com.br/api/feriados/v1/{ano}?uf=SC`. O serviço usa o campo `date` de cada item e consulta o ano seguinte quando a janela cruza dezembro. Cada resposta válida é reutilizada por até 24 horas no cache Django. Feriados municipais ficam fora do calendário fornecido pelo endpoint.

Se a BrasilAPI falhar e o calendário necessário estiver fora do cache, o POST retorna 503 e reverte a criação da regra. A consulta segue disponível com as ocorrências já gravadas a partir de hoje. O comando informa a indisponibilidade e encerra a execução com erro.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Sem notificações externas nesta feature.
