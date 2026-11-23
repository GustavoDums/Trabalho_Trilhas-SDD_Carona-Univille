# Contratos: Cancelamento e liberação de vaga

**Status**: proposto; decisões na [spec](../spec.md).

POST /caronas/reservas/<booking_id>/cancelar/ e POST /caronas/<offer_id>/cancelar/, CSRF, somente titular ativo conforme política. Confirmação por formulário/modal acessível; GET não cancela. Repetição informa estado já cancelado sem nova liberação. A resposta de tardio aguarda D005-02; oferta cancelada não aparece como reservável.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Nomes propostos serão fixados na tarefa de decisão. Sem notificações externas nesta feature.
