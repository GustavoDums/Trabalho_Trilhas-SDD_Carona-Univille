# Contratos: Caronas recorrentes

**Status**: política homologada na [spec](../spec.md).

GET/POST /caronas/recorrentes/ atende motorista titular ativo, com listagem própria e criação com CSRF. O POST cria a regra, suas paradas e as ofertas na mesma transação. O GET exibe as datas existentes na janela atual e o estado de cada oferta. GET e leitura da busca são operações sem escrita.

O operador de confiança executa `manage.py generate_recurring_rides --all` na rotina diária ou usa `--rule ID` para uma regra. O comando usa a mesma referência para todas as regras da execução, ignora titulares inelegíveis e imprime apenas a identificação da regra e as datas criadas ou existentes. Um erro reverte o lote da regra afetada. Regras independentes podem concluir, e o comando retorna erro ao final se algum lote falhar.

Na T035, `RecurringRideService.generate(rule_id=..., driver=...)` retorna as datas criadas e já existentes para o titular. O horizonte de 16 dias corridos inclui a data local de referência, com partidas estritamente futuras. Repetição conserva a oferta original de cada data, inclusive se cancelada.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Sem notificações externas nesta feature.
