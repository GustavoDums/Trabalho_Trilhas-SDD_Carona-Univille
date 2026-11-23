# Contratos: Caronas recorrentes

**Status**: proposto; decisões na [spec](../spec.md).

GET/POST /caronas/recorrentes/ para MOTORISTA/ATIVA, lista somente própria e formulário com CSRF. Comando manage.py generate_recurring_rides com seleção explícita da regra e data de referência validada; opções definitivas após D009-02, dry-run proposto para inspecionar datas sem escrita. Não executar geração em GET nem em leitura da busca.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Nomes propostos serão fixados na tarefa de decisão. Sem notificações externas nesta feature.
