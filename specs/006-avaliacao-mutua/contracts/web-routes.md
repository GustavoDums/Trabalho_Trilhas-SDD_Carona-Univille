# Contratos: Avaliação mútua pós-viagem

**Status**: proposto; decisões na [spec](../spec.md).

GET/POST /avaliacoes/caronas/<offer_id>/usuarios/<reviewed_id>/nova/ em reviews/urls.py, sessão acadêmica ativa, contraparte validada no servidor. Form contém rating e comment; reviewer nunca é campo editável. GET exibe formulário, POST grava uma vez e redireciona; recusa de elegibilidade não revela dados do alvo.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Nomes propostos serão fixados na tarefa de decisão. Sem notificações externas nesta feature.
