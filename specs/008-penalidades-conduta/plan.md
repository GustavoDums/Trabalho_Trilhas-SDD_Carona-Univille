# Implementation Plan: Penalidades por cancelamento tardio e no-show

**Feature**: 008-penalidades-conduta | **Date**: 2026-11-22 | **Spec**: [spec.md](spec.md)
**Branch**: nenhuma criada/alterada; ponteiro da Feature 003 preservado.
**Status**: D008-01 e D008-02 homologadas em 2026-11-23.

## Summary

Atender REQ-010 no monólito existente, preservando identidade, privacidade e histórico. [research.md](research.md) distingue proposta técnica de produto não homologado.

## Technical Context

Python 3.12+, Django 5.1.x, PostgreSQL 15+, pytest/pytest-django/pytest-cov, templates server-side, venv existente. Sem nova biblioteca/worker/fornecedor. Configuração em carona_univille/settings.py e carona_univille/urls.py deve ser conferida na execução. Concorrência usa PostgreSQL real; verificar consultas sem N+1, sem SLA artificial.

## Constitution Check

- I: vínculo ativo, papéis, minimização e dados fictícios preservados.
- II: integridade transacional, locks e testes dos critérios.
- III: >=80% linhas e ramificações críticas, relatórios e números medidos no README.
- IV/V: spec → plan → tasks → código; rastreabilidade local/roadmap e prompts.
- VI: stack preservada; D008-01 e D008-02 registradas na spec.
- Pós-design: documentação segura preparada; nenhuma exceção constitucional homologada. Alteração da constitution exige consenso em rodada própria.

## Project Structure & Design

[Spec](spec.md), [pesquisa](research.md), [dados](data-model.md), [contratos](contracts/web-routes.md), [validação](quickstart.md) e [tarefas](tasks.md).

PenaltyService em reviews/services/penalty_service.py consome CancellationRecord idempotentemente e fluxo autorizado de no-show. Bloquear oferta antes de usuário, ordem compartilhada pelos serviços; transação grava ocorrência e reconstrói projeções. Signal de reputação não cria segunda punição. Middleware acadêmico mantém responsabilidade de vínculo e delega restrição disciplinar separada; serviços também verificam suspensão para impedir bypass. Integrar extrato em accounts sem divulgar histórico a terceiros. Sem processo externo, sensor de presença ou notificação bônus.

A T002 cobre o modelo, as restrições, a dedução decimal e a projeção de suspensão. Na T003, CancellationService delega ao PenaltyService, que vincula o cancelamento tardio à penalidade e reconstrói a nota pelo ReputationService na mesma transação. Na T004, o motorista titular registra a conclusão em Minhas ofertas, e a contraparte confirmada declara ausência em Minhas reservas. A transação mantém o relato e a projeção disciplinar consistentes com a reputação.

A T005 consulta o prazo disciplinar para as ações de publicar e reservar. Os serviços verificam o prazo após bloquear a conta do autor. A T006 apresenta o próprio extrato a partir da sessão e consulta o histórico do titular.

## Data & Interfaces

[data-model.md](data-model.md) define entidades e restrições, e os [contratos](contracts/web-routes.md) definem interfaces e autorização. A migração reviews.0003 foi validada na [T002](evidence-t032.md). A T003 usa esse esquema.

## Implementation Order

A modelagem depende do cálculo de reputação da Feature 007/T002 (roadmap T030). Os fluxos usam os eventos e interfaces existentes das Features 005, 006 e 007.

T001 fecha decisões → testes/modelo → serviço → interface → integração → qualidade, seguindo dependências explícitas em [tasks.md](tasks.md). Bônus 010/011 não são pré-requisitos. T041–T045 são marcos gerais, não concluídos por esta feature.

## Verification Strategy

TDD: falha comportamental esperada antes, implementação e verde; regressão pertinente após cada mudança. Serviço sem HTTP e interface com sessão/CSRF reais; constraints no banco, rollback e conexões independentes para concorrência. Relógio injetado, sem sleep para bordas. Cobrir todos os SC; seguir [quickstart](quickstart.md). Separar testes novos/regressão e não inventar métricas.

## Complexity Tracking

Persistência auditável, serviços e projeções limitados ao requisito; sem arquitetura distribuída. Campos dependentes de produto não serão inventados para contornar decisões.
