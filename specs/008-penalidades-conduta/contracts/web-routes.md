# Contratos: Penalidades por cancelamento tardio e no-show

**Status**: política homologada na [spec](../spec.md). A implementação HTTP pertence às tarefas posteriores.

GET /conta/conduta/ retorna o extrato próprio. POST de no-show exige sessão, CSRF, contraparte confirmada e declaração vinculada à reserva com horário registrado. O prazo é de até 2 horas após a conclusão registrada, depois dos 10 minutos de tolerância a partir do horário previsto de embarque. A denúncia fica indisponível enquanto a parada não tiver horário previsto. Contestação segue revisão administrativa. Durante a suspensão, ficam disponíveis a conta, o extrato e o cancelamento de compromissos existentes. Novas ofertas e reservas ficam bloqueadas.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Sem notificações externas nesta feature.

## Integração interna da T003

`PenaltyService.apply_cancellation(cancellation_id=...)` consome um evento persistido. Cancelamento tempestivo retorna sem efeito. Cancelamento tardio cria ou recupera a penalidade do titular e recalcula sua reputação. A chamada também permite reprocessar um evento legado conhecido. O serviço fica atrás das rotas existentes de cancelamento.
