# Contratos: Cálculo matemático de reputação

**Status**: proposto; decisões na [spec](../spec.md).

Não cria endpoint de alteração pública da nota. Signal/serviço interno recebe user_id e instante aware; devolve projeção decimal. Templates de perfil e resultado de busca recebem score pronto e formato acessível; cliente não escolhe pontuação/pesos. Rebuild autorizado por comando administrativo futuro apenas se necessário à política aprovada.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Nomes propostos serão fixados na tarefa de decisão. Sem notificações externas nesta feature.
