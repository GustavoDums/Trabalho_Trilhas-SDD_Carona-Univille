# Implementation Plan: Cancelamento e liberação de vaga

**Feature**: 005-cancelamento-liberacao-vaga | **Date**: 2026-11-22 | **Spec**: [spec.md](spec.md)
**Branch**: nenhuma criada/alterada; ponteiro da Feature 003 preservado.
**Status**: D005-01/D005-02 confirmadas; T001–T006 concluídas; interfaces de reserva/oferta verificadas. T007 concluída; [auditoria MVP](evidence-t027.md). [Evidência T006](evidence-t006.md). [Evidência T005](evidence-t005.md). [Evidência T004](evidence-t025.md). [Evidência](evidence-t024.md).

## Summary

Atender REQ-007 no monólito existente, preservando identidade, privacidade e histórico. [research.md](research.md) distingue proposta técnica de produto não homologado.

## Technical Context

Python 3.12+, Django 5.1.x, PostgreSQL 15+, pytest/pytest-django/pytest-cov, templates server-side, venv existente. Sem nova biblioteca/worker/fornecedor. Configuração em carona_univille/settings.py e carona_univille/urls.py deve ser conferida na execução. Concorrência usa PostgreSQL real; verificar consultas sem N+1, sem SLA artificial.

## Constitution Check

- I: vínculo ativo, papéis, minimização e dados fictícios preservados.
- II: integridade transacional, locks e testes dos critérios.
- III: >=80% linhas e ramificações críticas, relatórios e números medidos no README.
- IV/V: spec → plan → tasks → código; rastreabilidade local/roadmap e prompts.
- VI: stack preservada; D005-01/D005-02 homologadas; gate atendido para T002/T003.
- Pós-design: documentação segura preparada; nenhuma exceção constitucional homologada. Alteração da constitution exige consenso em rodada própria.

## Project Structure & Design

[Spec](spec.md), [pesquisa](research.md), [dados](data-model.md), [contratos](contracts/web-routes.md), [validação](quickstart.md) e [tarefas](tasks.md).

CancellationService em rides/services/cancellation_service.py bloqueia oferta, usuários por PK e depois reservas por PK, mesma ordem usada por BookingService. T002/T003 cancelam apenas reserva individual e gravam auditoria no mesmo commit; fechamento de oferta em lote pertence à T004; não somar/decrementar capacidade. Atualizar BookingService/MatchingService para excluir oferta CANCELADA. Política temporal isolada e testável por relógio injetado; nada de sleep. Evento tardio preparado para consumo idempotente pela 008; não criar dependência circular da 005 para 008.

Caminhos novos são planejados. Pacote rides/services já existe; preservar imports e publicação.

## Data & Interfaces

[data-model.md](data-model.md) é fonte canônica do desenho proposto; [contratos](contracts/web-routes.md) define interfaces e autorização. 0004_cancellation_support gerada/aplicada/verificada no PostgreSQL local, preservando campos anteriores e inicializando ABERTA/datas nulas. Na implementação: revisar dados legados e plano, aplicar migração e verificar no PostgreSQL local sem reset.

## Implementation Order

Feature 004 funcional, com T007 de qualidade final pendente; Feature 003 para disponibilidade na busca; auditoria MVP depende de todas as implementações T001–T026 do roadmap, não apenas destes documentos.

T001 fecha decisões → testes/modelo → serviço → interface → integração → qualidade, seguindo dependências explícitas em [tasks.md](tasks.md). Bônus 010/011 não são pré-requisitos. T041–T045 são marcos gerais, não concluídos por esta feature.

## Verification Strategy

TDD: falha comportamental esperada antes, implementação e verde; regressão pertinente após cada mudança. Serviço sem HTTP e interface com sessão/CSRF reais; constraints no banco, rollback e conexões independentes para concorrência. Relógio injetado, sem sleep para bordas. Cobrir todos os SC; seguir [quickstart](quickstart.md). Separar testes novos/regressão e não inventar métricas.

## Complexity Tracking

Persistência auditável, serviços e projeções limitados ao requisito; sem arquitetura distribuída. Campos dependentes de produto não serão inventados para contornar decisões.
