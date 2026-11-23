# Tasks: Fila de Espera Automática com Repasse FIFO

**Feature** 011-fila-espera-fifo · [Spec](spec.md) · [Plano](plan.md)

## Pré-requisito

A T020 do roadmap já entregou o modelo da reserva. As autorizações para T039 e T040 estão registradas no [planejamento](../../docs/preparacao-features-004-009.md).

## US1 — Ingresso e repasse FIFO

- [x] T001 [US1] Implementar modelo `WaitlistEntry` em `rides/models.py`, migração, `rides/services/waitlist_service.py`, ingresso em `rides/views.py`, `rides/urls.py` e templates. **Campos**: [data-model.md](data-model.md): WaitlistEntry.id, WaitlistEntry.offer, WaitlistEntry.passenger, WaitlistEntry.boarding_point e WaitlistEntry.alighting_point. Escrever e executar primeiro `tests/test_waitlist.py`. **Requisitos**: REQ-013, REQ-017, REQ-002 e REQ-003; FR-001/FR-002 e SC-001/SC-002. **Depende**: T020 do roadmap. **Conclusão**: ingresso e repasse imediato FIFO aprovados com PostgreSQL, inclusive acesso, duplicidade, inelegibilidade, concorrência e rollback. [Evidência](evidence-t039.md). **Roadmap**: T039.

## US2 — Repasse após cancelamento

- [x] T002 [US2] Integrar o serviço no `rides/services/cancellation_service.py`, exibir posição no painel do passageiro e validar `tests/test_waitlist_flow.py`. **Requisitos**: REQ-007, REQ-013 e REQ-017; FR-003 e SC-003. **Depende**: T001 local e T024 do roadmap. **Conclusão**: repasse, aviso, posição privada e regressão aprovados na [evidência](evidence-t040.md). **Roadmap**: T040.

## Ordem de execução

T001 → T002. Na T001, testes de ingresso e do repasse podem ser escritos em paralelo. A validação direta do serviço independe da integração da T002.
