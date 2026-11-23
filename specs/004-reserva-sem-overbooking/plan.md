# Implementation Plan: Reserva de vagas sem overbooking

**Feature**: 004-reserva-sem-overbooking | **Date**: 2026-11-22 | **Spec**: [spec.md](spec.md)
**Branch**: nenhuma criada/alterada; ponteiro da Feature 003 preservado.
**Status**: modelo T002/T020 e serviço/concorrência T003/T021 concluídos; integração T006 concluída ([evidência](evidence-t006.md)); Views/projeção T004 verificadas isoladamente ([evidência](evidence-t022.md)); rotas/fluxo T005 concluídos ([evidência HTTP](evidence-t023.md)); qualidade final T007 pendente. [Evidência transacional](evidence-t021.md).

## Summary

Atender REQ-006 no monólito existente, preservando identidade, privacidade e histórico. [research.md](research.md) distingue proposta técnica de produto não homologado.

## Technical Context

Python 3.12+, Django 5.1.x, PostgreSQL 15+, pytest/pytest-django/pytest-cov, templates server-side, venv existente. Sem nova biblioteca/worker/fornecedor. Configuração em carona_univille/settings.py e carona_univille/urls.py deve ser conferida na execução. Concorrência usa PostgreSQL real; verificar consultas sem N+1, sem SLA artificial.

## Constitution Check

- I: vínculo ativo, papéis, minimização e dados fictícios preservados.
- II: integridade transacional, locks e testes dos critérios.
- III: >=80% linhas e ramificações críticas, relatórios e números medidos no README.
- IV/V: spec → plan → tasks → código; rastreabilidade local/roadmap e prompts.
- VI: stack preservada; D004-01/D004-02 confirmadas; gate de decisões atendido para T002.
- Pós-design: documentação segura preparada; nenhuma exceção constitucional homologada. Alteração da constitution exige consenso em rodada própria.

## Project Structure & Design

[Spec](spec.md), [pesquisa](research.md), [dados](data-model.md), [contratos](contracts/web-routes.md), [validação](quickstart.md) e [tarefas](tasks.md).

BookingService.create_booking em rides/services/booking_service.py: transaction.atomic, bloquear RideOffer com select_for_update e depois as contas por PK crescente, revalidar contas e oferta, contar CONFIRMADA e criar reserva. Todos os escritores futuros usam o mesmo lock da oferta. Constraint parcial cobre duplicidade, mas limite agregado depende do serviço transacional. Usar ordem estável de locks e tratar IntegrityError fora do bloco quebrado. DTO BookingSummary em rides/services/booking_queries.py é filtrado por participante e papel atual por BookingQueryService; CONFIRMADA recebe nome completo/placa e CANCELADA somente abreviação/placa None. MyBookingsView e BookRideView em rides/views.py usam essa projeção; formulário mínimo em rides/forms.py. Select_related evita N+1, templates não recebem modelos de usuário/oferta. T004 validou classes por RequestFactory; T005 registrou URLs definitivas e validou fluxo por Client com middleware/CSRF, sem mudar os serviços. Integrar MatchingService com disponibilidade sem mudar matching de rota/tempo.

Caminhos novos são planejados. Pacote rides/services já disponível pela Feature 003/T001; preservar import público publish_offer.

## Data & Interfaces

[data-model.md](data-model.md) é fonte canônica do desenho proposto; [contratos](contracts/web-routes.md) define interfaces e autorização. T002 adicionou RideBooking, boarding_point/alighting_point, enum de status e unicidade ativa conforme desenho canônico; sem contador de vagas. Modelo valida autorreserva, passageiro elegível na criação e ordem de pontos. Limite agregado/concorrência implementado na T003; assinatura e erros em contracts/web-routes.md. T006 integrou disponibilidade por Count SQL filtrado/distinto das CONFIRMADA, sem N+1, com campo transitório SearchResult.available_seats separado da capacidade. Esgotadas seguem visíveis; filtros/ordenação preservados e BookingService inalterado. Na implementação: revisar dados legados e plano, aplicar migração e verificar no PostgreSQL local sem reset.

## Implementation Order

Features 001/002 implementadas; Feature 003/T001 (pacote de serviços) antes de criar módulos; Feature 003/T002–T004 antes da integração de disponibilidade na busca.

T001 fecha decisões → testes/modelo → serviço → interface → integração → qualidade, seguindo dependências explícitas em [tasks.md](tasks.md). Bônus 010/011 não são pré-requisitos. T041–T045 são marcos gerais, não concluídos por esta feature.

## Verification Strategy

TDD: falha comportamental esperada antes, implementação e verde; regressão pertinente após cada mudança. Serviço sem HTTP e interface com sessão/CSRF reais; constraints no banco, rollback e conexões independentes para concorrência. Relógio injetado, sem sleep para bordas. Cobrir todos os SC; seguir [quickstart](quickstart.md). Separar testes novos/regressão e não inventar métricas.

## Complexity Tracking

Persistência auditável, serviços e projeções limitados ao requisito; sem arquitetura distribuída. Campos dependentes de produto não serão inventados para contornar decisões.
