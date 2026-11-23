# Contratos: Caronas recorrentes

**Status**: política homologada na [spec](../spec.md).

Na T036, GET/POST /caronas/recorrentes/ atende motorista titular ativo, com listagem própria e criação com CSRF. A criação aciona o gerador automaticamente. O comando interno `manage.py generate_recurring_rides` é executado pelo operador de confiança na rotina diária, com seleção explícita de regra ou das regras ativas e revalidação do titular. GET e leitura da busca são operações sem escrita.

Na T035, `RecurringRideService.generate(rule_id=..., driver=...)` retorna as datas criadas e já existentes para o titular. O horizonte de 16 dias corridos inclui a data local de referência, com partidas estritamente futuras. Repetição conserva a oferta original de cada data, inclusive se cancelada.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Sem notificações externas nesta feature.
