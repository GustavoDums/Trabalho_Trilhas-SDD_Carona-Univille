# Contratos: Cancelamento e liberação de vaga

**Status**: decisões homologadas; rotas de reserva/oferta implementadas nas T005/T006, serviço T002–T004 implementado/verificado ([evidência](../evidence-t024.md)). [Spec](../spec.md).

POST /caronas/reservas/<booking_id>/cancelar/ e POST /caronas/<offer_id>/cancelar/, CSRF, somente titular ativo conforme política. Confirmação por formulário/modal acessível; GET não cancela. Repetição informa estado já cancelado sem nova liberação. Tardio anterior à partida é aceito/auditado, partida ou posterior é recusado; oferta cancelada não aparece como reservável.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Nomes propostos serão fixados na tarefa de decisão. Sem notificações externas nesta feature.

## Serviço aprovado — T002/T003

CancellationPolicy.classify(*, role, departure_at, at) retorna TEMPESTIVO/TARDIO segundo data-model.md; rejeita papel inválido, datetime inválido/naive e instante >= partida. Política de 4h aplicada também por cancel_offer na T004.

CancellationService.cancel_booking(*, user, booking_id, clock=None) reconsulta titular PASSAGEIRO/ATIVA/is_active, bloqueia oferta → usuários → reserva, captura clock() (ou timezone.now) uma vez para nova transição, classifica, grava CANCELADA/cancelled_at e CancellationRecord atomicamente. Retorna RideBooking. Repetição autorizada de CANCELADA retorna estado sem novas datas/eventos; não reclassifica nem recusa repetição apenas por tempo posterior.

Recusa temporal: CancellationRefused, ValidationError com code departure_reached; estados/datas/auditoria/capacidade preservados. Terceiro/ator inelegível: PermissionDenied. IDs inválidos/ausentes: ValidationError. Falha de auditoria reverte toda a alteração.

T003 prova liberação por contagem derivada e corrida com nova reserva no PostgreSQL. Atualizar checagem de status em BookingService/MatchingService é adaptação necessária ao novo campo, sem implementar cancelamento de oferta. Rotas/views permanecem T005/T006 e não serão criadas nesta rodada.

## Serviço de oferta — T004 local / roadmap T025

CancellationService.cancel_offer(*, user, offer_id, clock=None) retorna RideOffer. Reconsulta motorista titular ATIVA/is_active, bloqueia oferta → usuários por PK → reservas confirmadas por PK. Captura o relógio uma vez após os locks e aplica a política de 4h da origem, inclusiva. Tardio antes da partida é aceito; na partida ou depois, CancellationRefused sem mutação.

Grava status CANCELADA e cancelled_at da oferta e de todas as reservas confirmadas no mesmo atomic. Preserva capacidade, reservas já canceladas e auditorias anteriores. Um CancellationRecord com booking=None representa a transição da oferta e o lote causado pelo motorista, sem imputar cancelamento aos passageiros. Erro em qualquer gravação reverte todo o lote.

Repetição autorizada retorna oferta já cancelada sem consultar relógio, alterar datas ou fabricar auditoria legada. IDs inválidos/ausentes: ValidationError; ator inelegível/terceiro: PermissionDenied. MatchingService exclui a oferta e BookingService rejeita novas reservas após commit. Nenhuma rota, interface ou notificação adicionada na T004.
## Interface de reserva — T005 local / parcela da T026

POST /caronas/reservas/<booking_id>/cancelar/, nome rides:cancel_booking, CancelBookingView. Somente passageiro titular ativo, identidade da sessão e alvo da URL; campos user_id/booking_id/next enviados no corpo não substituem esses valores. CSRF obrigatório, métodos diferentes de POST retornam 405 para ator elegível. Contas anônimas/inativas seguem autenticação existente, pendentes seguem ativação e terceiros recebem 403 sem detalhes privados.

Minhas reservas exibe confirmação em details/summary acessível apenas para passageiro com reserva CONFIRMADA. Formulário com CSRF e botão explícito, sem JavaScript obrigatório. Texto informa referência na origem, 2h inclusivas, tardio aceito antes da partida e recusa na partida/depois. GET da lista não altera o estado; GET da ação retorna 405.

View delega a CancellationService.cancel_booking; sucesso/repetição redireciona somente a /caronas/minhas-reservas/ e informa que a reserva está cancelada. Recusa temporal retorna 400 com alerta de prazo; outro ValidationError retorna 400 genérico. Reexibe somente projeções próprias de BookingQueryService, que retiram placa e nome completo da contraparte após CANCELADA. PermissionDenied não é convertido em sucesso. Rotas/GUI de oferta implementadas na T006, conforme contrato abaixo.

## Interface de oferta — T006 local / fechamento da T026

POST /caronas/<offer_id>/cancelar/, nome rides:cancel_offer, CancelOfferView. Exige motorista titular ativo, POST e CSRF. Ator vem da sessão e alvo da URL, ignorando user_id/offer_id/next do corpo. Demais métodos retornam 405 para motorista elegível; terceiros/passageiros recebem 403, sessão anônima/inativa segue login e vínculo pendente segue ativação.

Minhas ofertas mantém todas as ofertas próprias, incluindo CANCELADA, mostra estado e confirmação acessível details/summary apenas para ABERTA. Texto informa cancelamento das reservas confirmadas, preservação do histórico e prazo inclusivo de 4h pela saída da origem. Antes da partida, tardio é aceito/auditado; na partida ou depois, recusado.

View delega a CancellationService.cancel_offer. Sucesso e repetição redirecionam somente a /caronas/minhas-ofertas/, com mensagem de estado cancelado. CancellationRefused retorna 400 com alerta de prazo; demais ValidationError retornam 400 genérico e lista somente de ofertas próprias. PermissionDenied permanece 403. Serviço cancela lote, preserva histórico e impede novas reservas; projeções de reservas retiram placa/nome completo após cancelamento. Nenhuma notificação/penalidade implementada. T005/T006 encerram T026; T007 é auditoria futura.
