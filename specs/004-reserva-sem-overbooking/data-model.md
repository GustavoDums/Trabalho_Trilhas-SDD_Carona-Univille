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

Itinerário = origem + Waypoint por position + destino. Recusar pontos ausentes, invertidos, iguais ou itinerário ambíguo com repetições. Esta verificação entre tabelas e a proibição de autorreserva são validações do modelo; não podem ser representadas por CHECK SQL com join. O serviço T003 repetirá validações no estado corrente e sob lock. save usa full_clean conforme padrão ValidatedModel do projeto; bulk_create/update/SQL podem contornar regras Python e não são API de reserva.

A elegibilidade do passageiro na criação não impede manutenção do histórico quando seu vínculo mudar posteriormente. Revalidação de motorista/partida/capacidade e serialização da operação suportada de reserva pertencem à T003, não a um contador ou lock parcial nesta modelagem.

## Capacidade e estados

RideOffer.seats continua capacidade original, inteiro positivo já existente; não adicionar contador nem incrementar capacidade ao cancelar. Uma reserva CONFIRMADA ocupa uma vaga durante toda a oferta; não reutilizar vaga entre trechos.
Disponibilidade futura = seats - quantidade de CONFIRMADA. Limite agregado entre linhas depende do BookingService transacional da T003; esta migração não comprova zero overbooking sozinha.

Estados persistidos: CONFIRMADA e CANCELADA. Não há espera por aceite do motorista. Sem fluxo de cancelamento, reconfirmação ou HTTP implementado pela T002; esses estados permitem evolução sem apagar histórico.

## Persistência e privacidade

PostgreSQL, FKs protegidas e timestamps aware. Criar tabela vazia para reservas sem reescrever ofertas/contas/catálogo atuais. Verificar plano/aplicação local e constraints no banco isolado de testes, sem reset destrutivo.

Não adicionar telefone, e-mail, nome completo ou placa ao registro de reserva; relações referem os registros existentes. WhatsApp adiado; e-mail nunca divulgado a terceiros. Contato/placa por contraparte pertence às tarefas de apresentação.
