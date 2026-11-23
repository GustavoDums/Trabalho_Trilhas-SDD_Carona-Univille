# Implementation Plan: Avaliação mútua pós-viagem

**Feature**: 006-avaliacao-mutua | **Date**: 2026-11-22 | **Spec**: [spec.md](spec.md)
**Branch**: nenhuma criada/alterada; ponteiro da Feature 003 preservado.
**Status**: D006-01/D006-02 homologadas; T001 documental concluída, T002 concluída ([evidência](evidence-t028.md)).

## Summary

Atender REQ-008 no monólito existente, preservando identidade, privacidade e histórico. [research.md](research.md) distingue proposta técnica de produto não homologado.

## Technical Context

Python 3.12+, Django 5.1.x, PostgreSQL 15+, pytest/pytest-django/pytest-cov, templates server-side, venv existente. Sem nova biblioteca/worker/fornecedor. Configuração em carona_univille/settings.py e carona_univille/urls.py deve ser conferida na execução. Concorrência usa PostgreSQL real; verificar consultas sem N+1, sem SLA artificial.

## Constitution Check

- I: vínculo ativo, papéis, minimização e dados fictícios preservados.
- II: integridade transacional, locks e testes dos critérios.
- III: >=80% linhas e ramificações críticas, relatórios e números medidos no README.
- IV/V: spec → plan → tasks → código; rastreabilidade local/roadmap e prompts.
- VI: stack preservada; D006-01/D006-02 homologadas em 2026-11-23; gate documental atendido.
- Pós-design: documentação segura preparada; nenhuma exceção constitucional homologada. Alteração da constitution exige consenso em rodada própria.

## Project Structure & Design

[Spec](spec.md), [pesquisa](research.md), [dados](data-model.md), [contratos](contracts/web-routes.md), [validação](quickstart.md) e [tarefas](tasks.md).

Novo app reviews com migrations, configuração em carona_univille/settings.py conforme nome real do módulo verificado na execução. ReviewService valida elegibilidade e janela em transação, bloqueia primeiro oferta e depois usuários por PK, seguindo a ordem global oferta → usuários → registros filhos e usa constraint contra duplicata. Decisão de término pode exigir migração de RideOffer/registro de conclusão: somente após D006-01, com tratamento de ofertas legadas não avaliáveis sem evidência. Form e view usam serviço; cálculo de nota pública reservado à 007.

Pacote rides/services existente preservado. Novo app reviews e serviço reviews/services/review_service.py; migrações aditivas, sem alterar import público publish_offer.

## Data & Interfaces

[data-model.md](data-model.md) é fonte canônica do desenho proposto; [contratos](contracts/web-routes.md) define interfaces e autorização. Nenhuma migração gerada nesta rodada. Na implementação: revisar dados legados e plano, aplicar migração e verificar no PostgreSQL local sem reset.

## Implementation Order

Feature 004 para participantes; Feature 005 para estado cancelado. Criar app reviews somente na execução das tarefas; não existe hoje.

T001 fecha decisões → testes/modelo → serviço → interface → integração → qualidade, seguindo dependências explícitas em [tasks.md](tasks.md). Bônus 010/011 não são pré-requisitos. T041–T045 são marcos gerais, não concluídos por esta feature.

## Verification Strategy

TDD: falha comportamental esperada antes, implementação e verde; regressão pertinente após cada mudança. Serviço sem HTTP e interface com sessão/CSRF reais; constraints no banco, rollback e conexões independentes para concorrência. Relógio injetado, sem sleep para bordas. Cobrir todos os SC; seguir [quickstart](quickstart.md). Separar testes novos/regressão e não inventar métricas.

## Complexity Tracking

Persistência auditável, serviços e projeções limitados ao requisito; sem arquitetura distribuída. Campos dependentes de produto não serão inventados para contornar decisões.

## Consolidação da T028 — 2026-11-23

A pedido do usuário, T002 local reúne modelo/migrações, referência de término e ReviewService, antes divididos entre T002 e T003. Correspondência única: roadmap T028 → T002 local. T003 foi incorporada e permanece apenas como referência histórica; T004 depende agora de T002. T001 → T002 → T004 → T005 → T006, sem alterar ordem interna de TDD/modelo/serviço nem escopo funcional. D006-01/D006-02 permanecem pendentes; esta reorganização não homologa as recomendações de produto e não inicia implementação.

## Homologação D006-01/D006-02 — 2026-11-23

Usuário aprovou as recomendações e autorizou T001 documental seguida da T002 unificada (antigas T002/T003). D006-01 CONFIRMADA: motorista titular ativo registra explicitamente conclusão após a partida (instante >= departure_at), relógio do servidor aware em UTC. RideOffer.completed_at opcional representa o término informado, não previsão de chegada nem detecção automática. Repetição autorizada preserva a primeira data. Oferta CANCELADA não pode ser concluída; ofertas legadas recebem NULL e não permitem avaliação sem conclusão registrada.

D006-02 CONFIRMADA: janela fechada [completed_at, completed_at+48h], ambos extremos inclusivos; bloquear antes e depois. Somente motorista↔passageiro com reserva CONFIRMADA na mesma oferta, ambos habilitados/com vínculo ativo; excluir cancelados e no-show. Uma avaliação por oferta/avaliador/avaliado, nota inteira 1..5, comentário opcional até 500 caracteres, sem edição. Sem passageiro↔passageiro, autoavaliação, reputação, penalidade ou interface nesta rodada.

Referências a decisões pendentes nas seções anteriores representam o estado histórico e são substituídas por esta homologação. T002 abrange domínio/migrações/serviços/testes; formulários e rotas permanecem T004/T005.
