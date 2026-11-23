# Implementation Plan: Busca por rota e horário

**Feature**: 003-busca-rota-horario | **Date**: 2026-11-22 | **Spec**: [spec.md](spec.md)
**Branch**: nenhuma branch criada/alterada. Feature selecionada por `.specify/feature.json`.
**Status**: planejamento técnico; nenhuma implementação entregue.

## Summary

Implementar busca somente leitura para passageiro ativo, usando o catálogo e as ofertas existentes. Itinerário = origem + Waypoint por position + destino; matching exige i < j e departure_at dentro de ±30 minutos inclusivos do instante desejado. Partida também deve ser estritamente futura e motorista deve permanecer habilitado/ativo. A interface avisa que compara saída da origem, sem estimativa de passagem intermediária.

## Technical Context

- **Language/Version**: Python 3.12+, venv do projeto.
- **Primary Dependencies**: Django 5.x instalado, Auth/Sessions, ORM, Forms, templates e dataclasses nativos; nenhuma dependência nova.
- **Storage**: PostgreSQL existente para ofertas e testes; consulta/resultado transitórios, sem novas tabelas ou migrações previstas.
- **Testing**: pytest, pytest-django, pytest-cov; dados sintéticos e relógio controlado para bordas.
- **Target Platform**: Windows/PowerShell local, web server-side compatível com Linux.
- **Project Type**: extensão do app rides; preserva Features 001/002.
- **Performance Goals**: SC-005, consulta com dados preparados em até 1 minuto de demonstração; evitar N+1 por paradas, sem inventar SLA de rede.
- **Constraints**: janela fixa, fuso America/Sao_Paulo na entrada/exibição, instantes aware; nenhuma escrita de domínio; nenhum e-mail/placa/nome completo enviado nos resultados.
- **Scale/Scope**: PoC com catálogo pequeno, sem paginação obrigatória ou integração com mapas; filtrar candidatos no banco antes de avaliar ordem em memória.

## Constitution Check

| Princípio | Pré/pós desenho | Mecanismo previsto |
| --- | --- | --- |
| I — vínculo/LGPD | Conforme | Passageiro ativo, motoristas ativos, projeção pública explícita, sem histórico de buscas |
| II — integridade | Conforme ao recorte | Busca não reserva nem reduz vagas; concorrência de reservas fica em feature própria |
| III — testes/cobertura | Planejado | Matriz de rota/tempo e HTTP; PostgreSQL; >=80% de linhas/ramificações críticas com relatórios separados |
| IV — SDD | Conforme | Spec confirmada → plano → tarefas; zero código nesta rodada |
| V — rastreabilidade | Conforme | REQ/FR e mapa T017–T019 para IDs locais; prompts registrados |
| VI — stack/governança | Conforme | Stack existente; confirmação temporal referenciada sem alterar constitution |

REQ-005 principal; REQ-002, REQ-003, REQ-017 e governança REQ-018/019. Regras temporais confirmadas na spec. Homologação acadêmica, domínios, cancelamento e formalização futura de emenda constitucional não são resolvidos aqui.

## Project Structure

### Documentation

[research.md](research.md), [data-model.md](data-model.md), [contracts/web-routes.md](contracts/web-routes.md), [quickstart.md](quickstart.md), [tasks.md](tasks.md).

### Source Code (previsto, sem criação nesta rodada)

- Converter `rides/services.py` em `rides/services/offers.py`, mantendo corpo/comportamento de publish_offer; `rides/services/__init__.py` reexporta publish_offer, preservando imports existentes. Não deixar módulo e pacote homônimos simultâneos.
- `rides/services/matching_service.py`: SearchQuery, SearchResult e MatchingService.
- `rides/forms.py`: RideSearchForm. `rides/views.py`: ActivePassengerRequiredMixin e RideSearchView. `rides/urls.py`: rota de busca.
- `rides/templates/rides/search.html`, `_search_result.html`: herdam/usam layout existente, sem dependência de JavaScript para buscar.
- `tests/test_matching.py`: predicados, contrato transitório e seleção no PostgreSQL. `tests/test_ride_search.py`: formulário, projeção, renderização e HTTP.
- `scripts/check-feature003-quality.ps1`: entrega futura, relatórios `coverage-feature003.json` e `test-results-feature003.xml`, bloco de métricas próprio no README.

## Phase 0 — Research

Decisões em [research.md](research.md), baseadas nos artefatos e código locais, com revisão delegada somente leitura. Nenhum pacote novo ou API externa a homologar.

## Phase 1 — Design & Contracts

Sem migração. Contratos transitórios e campos existentes utilizados em [data-model.md](data-model.md). Interface em [contratos](contracts/web-routes.md).

MatchingService.search recebe passageiro e SearchQuery validada. Reconsulta o usuário, exige PASSAGEIRO, ATIVA e is_active. Captura now uma vez, filtra SQL por partida > now, partida entre limites inclusivos, seats > 0 e motorista MOTORISTA/ATIVA/is_active. Usa select_related para motorista/extremos e Prefetch de waypoints com point, ordenados por position. Nenhum filtro de tolerância ou autoria enviado pelo cliente governa a consulta.

Para cada candidato, formar lista de IDs [origin, paradas..., destination]. Rejeitar dado estruturalmente ambíguo (pontos repetidos) como não compatível; não reordenar nem reparar ofertas legadas. Conferir presença de ambos os pontos e índice embarque < índice desembarque. Retornar cada oferta uma vez, ordenada por departure_at, created_at, id, como SearchResult público, não como queryset de modelos entregue ao template.

Predicados de rota/tempo podem ser testados isoladamente; search aplica também autorização e elegibilidade atuais. Comparar instantes completos, sem arredondar segundos, sem simular deslocamento até paradas. GET é somente leitura de domínio; persistência técnica de sessão/mensagens Django não é histórico de busca.

## Matriz de validação

| Grupo | Cobertura |
| --- | --- |
| US1 / FR-002–FR-003 | Todas as combinações de pontos de uma rota sintética, extremos, inversão, iguais, ausentes, direta, paradas fora da ordem de PK/nome |
| US2 / FR-004–FR-006 | −30min/centro/+30min, 1 segundo fora, meia-noite, offset equivalente, instante atual, entrada inválida, parâmetro de tolerância ignorado |
| US3 / FR-001, FR-007–FR-011 | Perfis de acesso, exclusão de motorista inativo, saída passada, resultado único/ordenado, vazio/estado inicial, DTO sem segredos e sem escrita |
| Regressão | Import publish_offer compatível, testes existentes da Feature 002 e seis módulos da Feature 001 |
| Entrega | Relatórios próprios, meta 80%, roteiro visual e tempo humano SC-005 sem inferir pelo pytest |

## Complexity Tracking

Sem violações ou exceções. Transformação do módulo em pacote é preparação técnica compatível, não nova funcionalidade; documentada como T001 local. Não ampliar matching para reserva, frota, reputação ou cancelamento.