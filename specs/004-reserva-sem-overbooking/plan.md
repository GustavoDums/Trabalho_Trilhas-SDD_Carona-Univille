# Implementation Plan: Reserva de vagas sem overbooking

**Feature**: 004-reserva-sem-overbooking | **Date**: 2026-11-22 | **Spec**: [spec.md](spec.md)
**Branch**: nenhuma criada/alterada; ponteiro da Feature 003 preservado.
**Status**: plano condicionado à aprovação das decisões de produto.

## Summary

Atender REQ-006 no monólito existente, preservando identidade, privacidade e histórico. [research.md](research.md) distingue proposta técnica de produto não homologado.

## Technical Context

Python 3.12+, Django 5.1.x, PostgreSQL 15+, pytest/pytest-django/pytest-cov, templates server-side, venv existente. Sem nova biblioteca/worker/fornecedor. Configuração em carona_univille/settings.py e carona_univille/urls.py deve ser conferida na execução. Concorrência usa PostgreSQL real; verificar consultas sem N+1, sem SLA artificial.

## Constitution Check

- I: vínculo ativo, papéis, minimização e dados fictícios preservados.
- II: integridade transacional, locks e testes dos critérios.
- III: >=80% linhas e ramificações críticas, relatórios e números medidos no README.
- IV/V: spec → plan → tasks → código; rastreabilidade local/roadmap e prompts.
- VI: stack preservada; D004-01, D004-02 pendentes. Gate de implementação **não passou**.
- Pós-design: documentação segura preparada; nenhuma exceção constitucional homologada. Alteração da constitution exige consenso em rodada própria.

## Project Structure & Design

[Spec](spec.md), [pesquisa](research.md), [dados](data-model.md), [contratos](contracts/web-routes.md), [validação](quickstart.md) e [tarefas](tasks.md).

BookingService.create_booking em rides/services/booking_service.py: transaction.atomic, bloquear RideOffer com select_for_update, revalidar contas e oferta, contar CONFIRMADA e criar reserva. Todos os escritores futuros usam o mesmo lock da oferta. Constraint parcial cobre duplicidade, mas limite agregado depende do serviço transacional. Usar ordem estável de locks e tratar IntegrityError fora do bloco quebrado. DTOs de leitura filtram dados por participante. Integrar MatchingService com disponibilidade sem mudar matching de rota/tempo.

Caminhos novos são planejados. Não criar pacote rides/services concorrente com rides/services.py: aguardar Feature 003/T001 e preservar import público publish_offer.

## Data & Interfaces

[data-model.md](data-model.md) é fonte canônica do desenho proposto; [contratos](contracts/web-routes.md) define interfaces e autorização. Nenhuma migração gerada nesta rodada. Na implementação: revisar dados legados e plano, aplicar migração e verificar no PostgreSQL local sem reset.

## Implementation Order

Features 001/002 implementadas; Feature 003/T001 (pacote de serviços) antes de criar módulos; Feature 003/T002–T004 antes da integração de disponibilidade na busca.

T001 fecha decisões → testes/modelo → serviço → interface → integração → qualidade, seguindo dependências explícitas em [tasks.md](tasks.md). Bônus 010/011 não são pré-requisitos. T041–T045 são marcos gerais, não concluídos por esta feature.

## Verification Strategy

TDD: falha comportamental esperada antes, implementação e verde; regressão pertinente após cada mudança. Serviço sem HTTP e interface com sessão/CSRF reais; constraints no banco, rollback e conexões independentes para concorrência. Relógio injetado, sem sleep para bordas. Cobrir todos os SC; seguir [quickstart](quickstart.md). Separar testes novos/regressão e não inventar métricas.

## Complexity Tracking

Persistência auditável, serviços e projeções limitados ao requisito; sem arquitetura distribuída. Campos dependentes de produto não serão inventados para contornar decisões.
