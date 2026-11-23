# Implementation Plan: Cálculo matemático de reputação

**Feature**: 007-calculo-reputacao | **Date**: 2026-11-22 | **Spec**: [spec.md](spec.md)
**Branch**: nenhuma criada/alterada; ponteiro da Feature 003 preservado.
**Status**: D007-01/D007-02 homologadas; T002 unificada concluída ([evidência](evidence-t030.md)).

## Summary

Atender REQ-009 no monólito existente, preservando identidade, privacidade e histórico. [research.md](research.md) distingue proposta técnica de produto não homologado.

## Technical Context

Python 3.12+, Django 5.1.x, PostgreSQL 15+, pytest/pytest-django/pytest-cov, templates server-side, venv existente. Sem nova biblioteca/worker/fornecedor. Configuração em carona_univille/settings.py e carona_univille/urls.py deve ser conferida na execução. Concorrência usa PostgreSQL real; verificar consultas sem N+1, sem SLA artificial.

## Constitution Check

- I: vínculo ativo, papéis, minimização e dados fictícios preservados.
- II: integridade transacional, locks e testes dos critérios.
- III: >=80% linhas e ramificações críticas, relatórios e números medidos no README.
- IV/V: spec → plan → tasks → código; rastreabilidade local/roadmap e prompts.
- VI: stack preservada; D007-01/D007-02 homologadas; gate documental atendido.
- Pós-design: documentação segura preparada; nenhuma exceção constitucional homologada. Alteração da constitution exige consenso em rodada própria.

## Project Structure & Design

[Spec](spec.md), [pesquisa](research.md), [dados](data-model.md), [contratos](contracts/web-routes.md), [validação](quickstart.md) e [tarefas](tasks.md).

ReputationService em reviews/services/reputation_service.py separa cálculo puro Decimal de seleção de fontes e persistência. Serializar atualização pelo usuário (bloquear AcademicUser, inclusive quando Profile ainda não existe) e recalcular fontes comprometidas, sem acumular delta em memória. Na futura T031, signal post_save RideReview encaminhará serviço com cuidado para transação/rollback e registro em AppConfig.ready sem duplicação. Integrar DTO de busca e perfil existentes; sem página pública nova. Se janela por dias, prever rebuild no instante de leitura ou comando explícito para expiração sem novas avaliações.

reviews/services/reputation_service.py implementado; pacote rides/services e import público publish_offer preservados. Signals e projeção de interface permanecem na T031.

## Data & Interfaces

[data-model.md](data-model.md) é fonte canônica do desenho proposto; [contratos](contracts/web-routes.md) define interfaces e autorização. Migração reviews.0002_reputationprofile gerada, aplicada e verificada no PostgreSQL local; dados anteriores preservados ([evidência](evidence-t030.md)). Na implementação: revisar dados legados e plano, aplicar migração e verificar no PostgreSQL local sem reset.

## Implementation Order

Feature 006 funcional (T002/T004 concluídas, qualidade T006 própria ainda aberta); Feature 003 para integração na busca; Feature 001 para perfil. Penalidades serão integradas pela 008 sem duplicar mecanismo.

T001 fecha decisões → testes/modelo → serviço → interface → integração → qualidade, seguindo dependências explícitas em [tasks.md](tasks.md). Bônus 010/011 não são pré-requisitos. T041–T045 são marcos gerais, não concluídos por esta feature.

## Verification Strategy

TDD: falha comportamental esperada antes, implementação e verde; regressão pertinente após cada mudança. Serviço sem HTTP e interface com sessão/CSRF reais; constraints no banco, rollback e conexões independentes para concorrência. Relógio injetado, sem sleep para bordas. Cobrir todos os SC; seguir [quickstart](quickstart.md). Separar testes novos/regressão e não inventar métricas.

## Complexity Tracking

Persistência auditável, serviços e projeções limitados ao requisito; sem arquitetura distribuída. Campos dependentes de produto não serão inventados para contornar decisões.

## Homologação e recorte — 2026-11-23

Usuário aprovou D007-01/D007-02 e autorizou T001 seguida da T002 unificada (antigas T002/T003, roadmap T030). D007-01: média aritmética simples das últimas 20 avaliações recebidas, cada avaliação com o mesmo peso mesmo na mesma viagem; sem janela de 30 dias. Selecionar created_at <= instante de referência e ordenar created_at DESC, id DESC, limit 20. A 21ª expulsa a mais antiga, não agrupar por oferta.

D007-02: novato 5.00 apenas quando conjunto vazio; base não entra como nota virtual. Calcular com Decimal e arredondar somente resultado final para duas casas com ROUND_HALF_UP, independente do contexto Decimal do chamador. [5,5,4,5,4]=4.60; [5,5,5,1]=4.00 (exatamente três notas 5 anteriores). Profile aceita 0.00..5.00; cálculo de notas 1..5 não gera zero, limite inferior prepara futura integração de penalidades da 008, não implementada agora.

ReputationProfile é projeção reconstruível sem substituir RideReview. Rebuild é serviço interno explícito, não endpoint; signals/atualização automática e exibição pública ficam T031. Referências anteriores a pendências/propostas divergentes são históricas e substituídas por esta homologação. Nenhuma aprovação de pesos, expiração por dias ou penalidades foi inferida.
