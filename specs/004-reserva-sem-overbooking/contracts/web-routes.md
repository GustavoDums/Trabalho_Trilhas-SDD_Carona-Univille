# Contratos: Reserva de vagas sem overbooking

**Status**: decisões D004-01/D004-02 homologadas em 2026-11-22; endpoints futuros, não implementados por T020/T002. [Spec](../spec.md).

POST /caronas/<offer_id>/reservar/ (rides:book), CSRF, passageiro ativo; GET /caronas/minhas-reservas/ (rides:my_bookings), somente próprias. Sucesso usa redirect-after-POST; falha de capacidade retorna mensagem de esgotamento sem dados privados. GET na ação retorna 405; IDs de terceiros não concedem acesso. Reserva instantânea CONFIRMADA, sem aceite; requisição futura informa boarding_point/alighting_point do catálogo e serviço valida ordem da rota. Sem reutilização por trecho. Na consulta privada, somente nome completo e placa da contraparte confirmada, nunca e-mail. WhatsApp adiado, sem campo de telefone.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Nomes propostos serão fixados na tarefa de decisão. Sem notificações externas nesta feature.
