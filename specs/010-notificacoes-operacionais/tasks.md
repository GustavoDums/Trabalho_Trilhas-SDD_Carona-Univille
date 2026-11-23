# Tasks: Notificações operacionais

**Feature**: 010-notificacoes-operacionais  
**Input**: [spec](spec.md), [plan](plan.md), [dados](data-model.md), [contratos](contracts/events.md), [quickstart](quickstart.md).  
**Tests**: dados fictícios e PostgreSQL. Executar TDD e regressão.

## Fase 1 — Pré-requisitos

O bônus foi incluído para executar T037 e T038. Canal interno e matriz de destinatários registrados. As funcionalidades de identidade, reserva e cancelamento dos itens T002, T021 e T025 do roadmap já existem.

## Fase 2 — US1, avisos de transições (P1)

- [x] T001 [US1] Implementar integralmente a T037. Executar `tests/test_notifications.py` em vermelho antes da implementação. Criar app, modelo e migração em `notifications/`, registrar o app em `carona_univille/settings.py` e criar `NotificationService` em `notifications/services.py`. Integrar os três gatilhos em `rides/services/booking_service.py` e `rides/services/cancellation_service.py`. Verificar a matriz por evento, origens protegidas, repetição, concorrência, recusas, rollback e migração. **Requisitos**: REQ-012, REQ-003, REQ-017, FR-001–FR-003 e SC-001–SC-003 no recorte de escrita. **Depende**: T002, T021 e T025 do roadmap, concluídas. **Conclusão**: avisos, migração e regressão aprovados na [evidência](evidence-t037.md). **Roadmap**: T037.

## Fase 3 — US2, consulta privada (P2)

- [x] T002 [US2] Implementar a consulta do titular, a marcação como lida e o sino com contador. Criar rotas, views e templates do app e integrar a navegação. Os testes verificam sessão, privacidade, CSRF em mutação, contagem e acesso de terceiros. **Requisitos**: REQ-012, REQ-002, REQ-003, REQ-017, FR-003/FR-004 e SC-003. **Depende**: T001. **Conclusão**: critérios e regressão aprovados na [evidência](evidence-t038.md). **Roadmap**: T038.

## Dependências e ordem

T001 → T002. Lembretes exigem definição de prazo e acionamento em recorte próprio.
