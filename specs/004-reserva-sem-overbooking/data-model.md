# Data Model: Reserva de vagas sem overbooking

**Status**: decisões D004-01/D004-02 confirmadas pelo usuário em 2026-11-22. Modelo/migração T002 local/roadmap T020 implementados e verificados, conforme [evidência](evidence-t020.md). [Spec](spec.md).

## RideBooking — fonte canônica

| Campo canônico | Tipo e restrição |
| --- | --- |
| RideBooking.id | BigAutoField, chave primária |
| RideBooking.offer | FK obrigatória RideOffer, PROTECT, related_name bookings |
| RideBooking.passenger | FK obrigatória AcademicUser, PROTECT, related_name ride_bookings; não pode ser o motorista da oferta; na criação deve ser PASSAGEIRO/ATIVA/is_active |
| RideBooking.boarding_point | FK obrigatória RoutePoint, PROTECT, related_name boarding_bookings; ponto existente no itinerário da oferta |
| RideBooking.alighting_point | FK obrigatória RoutePoint, PROTECT, related_name alighting_bookings; existente no mesmo itinerário, distinto e posterior ao embarque |
| RideBooking.status | CharField max_length=10, choices CONFIRMADA/CANCELADA, default CONFIRMADA; enum também protegido por CheckConstraint |
| RideBooking.created_at | DateTimeField auto_now_add; aware |
| RideBooking.updated_at | DateTimeField auto_now; aware |

UniqueConstraint parcial em (offer, passenger) quando status=CONFIRMADA: no máximo uma reserva ativa do mesmo passageiro por oferta, independentemente do trecho. Registros CANCELADA preservam histórico e não impedem nova CONFIRMADA. CheckConstraint adicional boarding_point != alighting_point.

Itinerário = origem + Waypoint por position + destino. Recusar pontos ausentes, invertidos, iguais ou itinerário ambíguo com repetições. Esta verificação entre tabelas e a proibição de autorreserva são validações do modelo; não podem ser representadas por CHECK SQL com join. O serviço T003 repete validações no estado corrente e sob lock, conforme [evidência](evidence-t021.md). save usa full_clean conforme padrão ValidatedModel do projeto; bulk_create/update/SQL podem contornar regras Python e não são API de reserva.

A elegibilidade do passageiro na criação não impede manutenção do histórico quando seu vínculo mudar posteriormente. Revalidação de motorista/partida/capacidade e serialização da operação suportada de reserva pertencem à T003, não a um contador ou lock parcial nesta modelagem.

## Capacidade e estados

RideOffer.seats continua capacidade original, inteiro positivo já existente; não adicionar contador nem incrementar capacidade ao cancelar. Uma reserva CONFIRMADA ocupa uma vaga durante toda a oferta; não reutilizar vaga entre trechos.
Disponibilidade = seats - quantidade de CONFIRMADA. BookingService transacional da T003 protege o limite agregado; integração na busca T006 implementada/verificada ([evidência](evidence-t006.md)). A migração sozinha não substitui o serviço/locks.

Estados persistidos: CONFIRMADA e CANCELADA. Não há espera por aceite do motorista. Sem fluxo de cancelamento, reconfirmação ou HTTP implementado pela T002; esses estados permitem evolução sem apagar histórico.

## Persistência e privacidade

PostgreSQL, FKs protegidas e timestamps aware. Criar tabela vazia para reservas sem reescrever ofertas/contas/catálogo atuais. Verificar plano/aplicação local e constraints no banco isolado de testes, sem reset destrutivo.

Não adicionar telefone, e-mail, nome completo ou placa ao registro de reserva; relações referem os registros existentes. WhatsApp adiado; e-mail nunca divulgado a terceiros. Contato/placa por contraparte pertence às tarefas de apresentação.

## Projeção de disponibilidade — T006 local

SearchResult.seats preserva a capacidade original da oferta. Novo campo canônico SearchResult.available_seats: inteiro entre zero e seats, calculado como max(0, seats - quantidade de RideBooking CONFIRMADA). RideBooking CANCELADA não consome vaga; cada confirmação conta uma vez na oferta inteira, independentemente do trecho. Não persistir contador nem alterar RideOffer.seats.

A consulta agrega reservas no SQL por oferta e mantém prefetch das paradas, sem consultas extras por cartão. Preservar filtros de rota/tempo/elegibilidade e ordenação da Feature 003; oferta compatível esgotada continua visível com saldo zero e rótulo Vagas esgotadas. O cartão exibe somente available_seats e dados públicos já aprovados; sem novos dados pessoais.

Busca continua somente leitura e sem lock de escrita. Uma nova consulta reflete reservas comprometidas no banco, mas o resultado não garante disponibilidade até a confirmação: BookingService permanece responsável por revalidar saldo sob lock.

## Projeção privada — T004 local

BookingSummary é dataclass frozen transitória em rides/services/booking_queries.py; não persistir campos novos nem enviar instâncias ORM ao template.

| Campo canônico | Tipo e regra |
| --- | --- |
| BookingSummary.booking_id | int positivo da reserva própria |
| BookingSummary.offer_id | int positivo da oferta vinculada |
| BookingSummary.status | CONFIRMADA/CANCELADA do registro atual |
| BookingSummary.departure_at | datetime aware da saída da origem |
| BookingSummary.boarding_name | str do ponto de embarque; escapar no HTML |
| BookingSummary.alighting_name | str do ponto de desembarque; escapar no HTML |
| BookingSummary.counterpart_role | MOTORISTA para passageiro que consulta; PASSAGEIRO para motorista |
| BookingSummary.counterpart_name | full_name da contraparte somente se CONFIRMADA; display_name se CANCELADA; escapar no HTML |
| BookingSummary.vehicle_model | str do snapshot existente, sem alterar seus limites |
| BookingSummary.vehicle_color | str do snapshot existente |
| BookingSummary.vehicle_plate | str somente se CONFIRMADA; None se CANCELADA; escapar no HTML |

BookingQueryService reconsulta a conta ativa e filtra por passenger_id para PASSAGEIRO ou offer.driver_id para MOTORISTA. Query string não governa identidade. Um passageiro não recebe nome/registro de outro passageiro da mesma oferta. Ordem: saída, criação da reserva, ID. Sem email, telefone, IDs de contas ou objetos completos no DTO.

RideBookingForm possui boarding_point_id/alighting_point_id como ModelChoiceFields obrigatórios do catálogo, distintos. View converte para PKs e delega validação da rota/capacidade ao BookingService. Identidade/status não são campos editáveis.
