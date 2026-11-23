# Contratos: Penalidades por cancelamento tardio e no-show

**Status**: proposto; decisões na [spec](../spec.md).

GET /conta/conduta/ retorna extrato próprio, sem parâmetro user_id; POST de no-show somente no endpoint autenticado da contraparte a definir em D008-02, CSRF e autorização de participação, nunca GET mutante. Respostas explicam suspensão/expiração ao titular, sem mostrar histórico no perfil público. Matriz de ações liberadas/bloqueadas integra contrato após decisão.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Nomes propostos serão fixados na tarefa de decisão. Sem notificações externas nesta feature.
