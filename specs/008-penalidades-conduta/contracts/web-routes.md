# Contratos: Penalidades por cancelamento tardio e no-show

**Status**: conclusão e denúncia homologadas na [spec](../spec.md) e executadas na [T004](../evidence-t004.md). O extrato pertence à T006.

GET /conta/conduta/ retorna o extrato próprio. POST de no-show exige sessão, CSRF, contraparte confirmada e declaração vinculada à reserva com horário registrado. O prazo é de até 2 horas após a conclusão registrada, depois dos 10 minutos de tolerância a partir do horário previsto de embarque. A denúncia fica indisponível enquanto a parada não tiver horário previsto. Contestação segue revisão administrativa. Durante a suspensão, ficam disponíveis a conta, o extrato e o cancelamento de compromissos existentes. Novas ofertas e reservas ficam bloqueadas.

- `POST /avaliacoes/caronas/<offer_id>/concluir/` registra a conclusão pelo motorista titular ativo usando o relógio do servidor. A ação está em Minhas ofertas e preserva a primeira conclusão.
- `GET /avaliacoes/reservas/<booking_id>/no-show/` apresenta a declaração à contraparte elegível. O POST na mesma rota registra a declaração explícita. O usuário autenticado é o denunciante, o alvo é a contraparte da reserva e o servidor deriva os horários. Sucesso redireciona para Minhas reservas.
- A janela é inclusiva. Havendo conclusão, começa no maior instante entre a conclusão e o fim da tolerância e termina 2 horas após a conclusão. Sem conclusão, somente o passageiro pode declarar ausência do motorista, entre o fim da tolerância e 2 horas depois. O horário previsto conhecido no modelo atual é a saída da origem, usada apenas para embarque na origem.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Sem notificações externas nesta feature.

## Integração interna da T003

`PenaltyService.apply_cancellation(cancellation_id=...)` consome um evento persistido. Cancelamento tempestivo retorna sem efeito. Cancelamento tardio cria ou recupera a penalidade do titular e recalcula sua reputação. A chamada também permite reprocessar um evento legado conhecido. O serviço fica atrás das rotas existentes de cancelamento.
