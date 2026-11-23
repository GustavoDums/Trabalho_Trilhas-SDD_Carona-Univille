# Implementation Plan: Caronas recorrentes

**Feature**: 009-caronas-recorrentes | **Date**: 2026-11-22 | **Spec**: [spec.md](spec.md)
**Branch**: nenhuma criada/alterada; ponteiro da Feature 003 preservado.
**Status**: D009-01 e D009-02 homologadas em 2026-11-23.

## Summary

Atender REQ-011 no monólito existente, preservando identidade, privacidade e histórico. [research.md](research.md) distingue proposta técnica de produto não homologado.

## Technical Context

Python 3.12+, Django 5.1.x, PostgreSQL 15+, pytest/pytest-django/pytest-cov, templates server-side, venv existente. Sem nova biblioteca/worker/fornecedor. Configuração em carona_univille/settings.py e carona_univille/urls.py deve ser conferida na execução. Concorrência usa PostgreSQL real; verificar consultas sem N+1, sem SLA artificial.

## Constitution Check

- I: vínculo ativo, papéis, minimização e dados fictícios preservados.
- II: integridade transacional, locks e testes dos critérios.
- III: >=80% linhas e ramificações críticas, relatórios e números medidos no README.
- IV/V: spec → plan → tasks → código; rastreabilidade local/roadmap e prompts.
- VI: stack preservada, com D009-01 e D009-02 homologadas na spec.
- Pós-design: documentação segura preparada; nenhuma exceção constitucional homologada. Alteração da constitution exige consenso em rodada própria.

## Project Structure & Design

[Spec](spec.md), [pesquisa](research.md), [dados](data-model.md), [contratos](contracts/web-routes.md), [validação](quickstart.md) e [tarefas](tasks.md).

RecurringRideService calcula as datas no fuso homologado e chama o publish_offer existente para cada ocorrência. O lote PostgreSQL bloqueia primeiro a regra e depois o motorista, revalida sua elegibilidade e publica em ordem de data. A restrição única por regra e data complementa o lock. Falha intermediária reverte o lote.

A T035 entrega o serviço e comprova independência da ocorrência cancelada. A T036 reutiliza o serviço na criação da regra pela interface e no comando interno da execução diária.

## Data & Interfaces

[data-model.md](data-model.md) define o esquema, e os [contratos](contracts/web-routes.md) definem interfaces e autorização. A migração rides.0006 cria as três tabelas de recorrência e foi validada com dados preexistentes em PostgreSQL temporário.

## Implementation Order

Feature 002 para publicação atômica; Feature 003/T001 para pacote de serviços e busca para integração; Feature 005 para comprovar independência no cancelamento.

T001 fecha decisões → testes/modelo → serviço → interface → integração → qualidade, seguindo dependências explícitas em [tasks.md](tasks.md). Bônus 010/011 não são pré-requisitos. T041–T045 são marcos gerais, não concluídos por esta feature.

## Atualização de calendário — T008 local

Consultar `GET https://brasilapi.com.br/api/feriados/v1/{ano}?uf=SC` com timeout de cinco segundos e cache Django de 24 horas por ano. A consulta transmite somente ano e UF. Validar as datas antes de armazenar respostas bem-sucedidas. Formulário, listagem e comando compartilham o cálculo da data limite. Sem calendário válido, a publicação é recusada e a listagem continua exibindo as ocorrências futuras já gravadas. A alteração reaproveita a stack e o esquema atuais. Cobrir a virada do ano, feriados, validade do cache, indisponibilidade e paridade entre formulário e comando.

## Verification Strategy

TDD: falha comportamental esperada antes, implementação e verde; regressão pertinente após cada mudança. Serviço sem HTTP e interface com sessão/CSRF reais; constraints no banco, rollback e conexões independentes para concorrência. Relógio injetado, sem sleep para bordas. Cobrir todos os SC; seguir [quickstart](quickstart.md). Separar testes novos/regressão e não inventar métricas.

## Complexity Tracking

Persistência auditável, serviços e projeções limitados ao requisito; sem arquitetura distribuída. Campos dependentes de produto não serão inventados para contornar decisões.
