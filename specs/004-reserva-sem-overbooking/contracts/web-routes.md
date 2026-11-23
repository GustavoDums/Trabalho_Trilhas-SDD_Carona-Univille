# Contratos: Reserva de vagas sem overbooking

**Status**: decisões D004-01/D004-02 homologadas em 2026-11-22; serviço T003 e classes/projeção T004 implementados/verificados; rotas da aplicação mapeadas/verificadas na T005 ([evidência HTTP](../evidence-t023.md)). [Spec](../spec.md).

POST /caronas/<offer_id>/reservar/ (rides:book), CSRF, passageiro ativo; GET /caronas/minhas-reservas/ (rides:my_bookings), somente próprias. Sucesso usa redirect-after-POST; falha de capacidade retorna mensagem de esgotamento sem dados privados. GET na ação retorna 405; IDs de terceiros não concedem acesso. Reserva instantânea CONFIRMADA, sem aceite; requisição informa boarding_point_id/alighting_point_id do catálogo e serviço valida ordem da rota. Sem reutilização por trecho. Na consulta privada, somente nome completo e placa da contraparte confirmada, nunca e-mail. WhatsApp adiado, sem campo de telefone.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Nomes propostos serão fixados na tarefa de decisão. Sem notificações externas nesta feature.

## Serviço transacional — T003 local / núcleo da T021

Assinatura implementada: BookingService.create_booking(*, passenger, offer_id, boarding_point_id, alighting_point_id) em rides/services/booking_service.py. passenger é o usuário da sessão passado pelo chamador confiável, não um campo controlado pelo navegador. IDs devem ser inteiros positivos; o serviço reconsulta os registros atuais.

Retorna RideBooking CONFIRMADA após commit da própria transação (se chamado dentro de transação externa, o commit final pertence ao chamador). Embarque/desembarque devem satisfazer data-model.md; uma reserva ocupa a oferta inteira.

Ordem de bloqueio: oferta → contas de passageiro/motorista por PK crescente. Revalidar papel/vínculo/is_active de ambos; saída deve ser estritamente futura no instante capturado após obter locks. Não confiar nos objetos passados ou em saldo calculado anteriormente. Não há estado de cancelamento de oferta no esquema atual; sua futura inclusão e verificação ficam na Feature 005, sem campo fictício aqui.

Sob lock da oferta: recusar duplicidade CONFIRMADA por passageiro; contar todas as CONFIRMADA da oferta, independentemente do trecho, e criar somente se a contagem for menor que seats. Não alterar seats, não criar contador, não tocar matching/cartão (T006).

Erros: PermissionDenied para usuário não autenticado/inelegível ou autorreserva; ValidationError por ID/trecho/oferta inválida ou duplicidade (code already_booked); NoSeatsAvailable, subclasse de ValidationError com code no_seats, para esgotamento. Erro SQL de unicidade ativa é traduzido somente após rollback do savepoint; demais IntegrityError são propagados com rollback. Erros não incluem e-mail/placa/nome completo.

Todos os escritores de reservas/cancelamentos futuros devem respeitar o mesmo lock/ordem. Criação direta por modelo/bulk/SQL não é API de reserva; constraints locais não substituem limite agregado. Sem HTTP ou notificações nesta tarefa.

## Disponibilidade pública — T006 local

Implementada no matching e no cartão da busca: Count de CONFIRMADA por oferta, SearchResult.available_seats separado de seats, nenhuma escrita ou novo dado pessoal. Preservar filtros e ordenação; zero exibe Vagas esgotadas, mantendo a oferta compatível na lista. Não adicionar ação de reserva.

Capacidade e saldo seguem [data-model.md](../data-model.md). CANCELADA não entra na contagem; trecho não reutiliza vaga. GET não garante saldo futuro; BookingService revalida sob lock. [Evidência de TDD/regressão](../evidence-t006.md).

## Apresentação privada e views — T004 local / roadmap T022

T004 implementa BookRideView e MyBookingsView, formulário mínimo e template my_bookings.html; a T005/T023 mapeia as URLs definitivas e valida o fluxo HTTP completo. Classes isoladas foram verificadas na T004, sem rotas provisórias.

BookRideView aceita somente POST por passageiro ativo. Campos boarding_point_id/alighting_point_id são pontos do catálogo, distintos; offer_id vem do argumento da view. Identidade vem de request.user e extras como passenger_id/status/next são ignorados. Converter pontos em PKs e chamar BookingService existente. Sucesso redireciona fixamente a /caronas/minhas-reservas/ com mensagem neutra; validações retornam formulário com erros e somente resumos próprios. GET não cria reserva. Erros de campo boarding_point/alighting_point do modelo são mapeados aos campos *_id; demais validações são não relacionadas a campo. PermissionDenied continua recusa de acesso.

MyBookingsView permite GET por motorista ou passageiro ativo. BookingQueryService.list_for(*, user) reconsulta a conta, restringe pelo papel atual (passenger=user ou offer.driver=user) e retorna tuple de BookingSummary imutáveis, nunca modelos de usuário/oferta. Ignorar filtros de identidade/IDs de terceiros enviados na query string. Ordenar por saída, criação da reserva e ID.

BookingSummary contém booking_id, offer_id, status, departure_at, boarding_name, alighting_name, counterpart_role, counterpart_name, vehicle_model, vehicle_color e vehicle_plate. Nome da contraparte é completo somente para CONFIRMADA; para CANCELADA é display_name. vehicle_plate é string somente para CONFIRMADA, senão None. Não há email, telefone, IDs de usuários ou instâncias ORM no DTO. É vedado exibir outros passageiros ao passageiro da mesma oferta. Nome/placa são escapados no HTML; ator pendente/desabilitado/visitante não lê dados privados.

A consulta usa select_related para evitar N+1 e não escreve domínio. Não criar contato, WhatsApp, histórico novo, cancelamento ou notificações.

## Rotas definitivas — T005 local / roadmap T023

rides:book usa /caronas/<int:offer_id>/reservar/ e aceita somente POST por passageiro ativo; rides:my_bookings usa /caronas/minhas-reservas/ e aceita GET próprio por passageiro/motorista ativo. Nomes antigos e placeholder preservados. POST válido responde 302 para minhas reservas; erros de validação respondem 200 com formulário; ação de GET e métodos incompatíveis respondem 405 para ator autorizado.

Middleware real mantém visitante/desabilitado no login com next e pendente na ativação. Motorista ativo recebe 403 ao tentar reservar e pode consultar apenas reservas das próprias ofertas. CSRF ausente/inválido recebe 403 antes da escrita. Identidade/status/next forjados não substituem dados de sessão/estado/redirecionamento fixo. Consulta própria ignora IDs de terceiros. [Evidência](../evidence-t023.md).
