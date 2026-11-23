# Implementation Plan: Oferta de caronas com paradas

**Feature**: 002-oferta-caronas-paradas | **Date**: 2026-11-22 | **Spec**: [spec.md](spec.md)
**Branch**: não criada ou alterada nesta rodada; identificação por `.specify/feature.json`.
**Input**: REQ-004, REQ-002 e REQ-003. Somente planejamento e tarefas, sem código implementado.

## Summary

Adicionar app `rides` ao projeto existente. `RoutePoint` mantém catálogo de pontos; `RideOffer` conserva autoria, extremos, saída, vagas e snapshot do veículo; `Waypoint` mantém paradas intermediárias em sequência. Formulário e serviço publicam atomicamente; views permitem somente motorista ativo e consulta de suas próprias ofertas. Sem mapas, frota independente, edição ou cancelamento.

## Technical Context

- **Language/Version**: Python 3.12+, ambiente `venv` existente.
- **Primary Dependencies**: Django 5.1.x instalado, ORM/Auth/Sessions/Templates existentes; nenhuma dependência nova prevista.
- **Storage**: PostgreSQL 15+, inclusive nos testes. Reutilizar `.env`; não registrar segredos.
- **Testing**: pytest, pytest-django, pytest-cov, TDD obrigatório por tarefa conforme constitution. Dados sintéticos.
- **Target Platform**: Windows/PowerShell local, aplicação web server-side compatível com Linux.
- **Project Type**: monólito Django, integrado ao middleware acadêmico da Feature 001.
- **Performance Goals**: demonstrar publicação com duas paradas e conferência em até 2 minutos (SC-005); não estabelecer SLA artificial de rede.
- **Constraints**: somente MOTORISTA/ATIVA; meta >=80% de linhas e ramificações críticas; placa restrita ao autor; e-mail não renderizado; migrações reprodutíveis.
- **Scale/Scope**: PoC com catálogo pequeno; vagas sem teto de negócio adicional, respeitando representação técnica em inteiro de 64 bits.

## Constitution Check

| Princípio | Antes e após desenho | Evidência prevista |
| --- | --- | --- |
| I — vínculo e minimização | Conforme | Serviço e views verificam motorista ativo; sem telefone/coordenadas; snapshots e filtro por autor |
| II — integridade | Conforme ao escopo | Publicação integral em transação; reservas e concorrência de última vaga fora desta feature |
| III — testes/cobertura | Planejado | Critérios mapeados abaixo; PostgreSQL e relatórios próprios da Feature 002; não reutilizar métricas da Feature 001 |
| IV — cadeia SDD | Conforme | Spec existente → este plano → tarefas; nenhuma implementação nesta rodada |
| V — rastreabilidade | Conforme | Mapa roadmap/local em tasks, REQ/FR por tarefa e registro em docs/prompts.md |
| VI — stack/governança | Conforme | Stack atual; pendências constitucionais mantidas, sem alterar constitution |

Não há violação a justificar. Homologação docente e domínios adicionais permanecem pendentes. Escolher pontos discretos não encerra janela de matching ou regras de cancelamento.

## Project Structure

### Documentation (this feature)

`plan.md`, [research.md](research.md), [data-model.md](data-model.md), [contracts/web-routes.md](contracts/web-routes.md), [quickstart.md](quickstart.md), [tasks.md](tasks.md).

### Source Code (repository root; previsto, ainda não criado)

- `rides/__init__.py`, `apps.py`, `models.py`, `forms.py`, `services.py`, `views.py`, `urls.py`.
- `rides/migrations/0001_initial.py`: estrutura; `0002_seed_route_points.py`: catálogo por migração de dados.
- `rides/templates/rides/offer_create.html`, `my_offers.html`: herdam `accounts/base.html`.
- `carona_univille/settings.py`: registrar rides; `carona_univille/urls.py`: incluir rotas específicas sem remover o placeholder `/caronas/`.
- `tests/test_rides_offer.py`: modelos, serviço, formulário e HTTP; fixtures específicas no próprio módulo para não alterar fixtures da Feature 001 sem necessidade.
- `scripts/check-feature002-quality.ps1`: medição futura separada; relatórios `coverage-feature002.json`, `test-results-feature002.xml` e bloco próprio no README.

**Structure Decision**: app separado de identidade, sem repositório intermediário, SPA ou dependência externa.

## Phase 0 — Research

Decisões e alternativas em [research.md](research.md). Uma revisão delegada somente leitura confirmou o desenho e os limites entre invariantes SQL e validação da aplicação. Nenhuma escolha tecnológica pendente.

## Phase 1 — Design & Contracts

Modelo canônico em [data-model.md](data-model.md). Interface HTML em [contratos](contracts/web-routes.md). Catálogo inicial é criado pela migração de dados, não por catálogo externo carregado automaticamente.

Publicação recebe autor da sessão e pontos em lista ordenada. Dentro de `transaction.atomic`, reconsulta/bloqueia o AcademicUser, verifica is_active, role e academic_status, valida dados completos e horário estritamente futuro, cria oferta e paradas. Falha reverte tudo. Não aceitar `driver`, `position` ou status como autoridade do POST.

`save()` dos modelos chama `full_clean()` para campos/regras locais; horário futuro e elegibilidade do motorista são avaliados somente em inserções e novamente no serviço. Não usar CHECK com NOW(), nem exigir saída futura ao ler oferta histórica. Escritas em lote ou SQL não substituem a fronteira de publicação; limites documentados no modelo de dados.

## Testes e rastreabilidade

| Escopo | Critérios | Verificação |
| --- | --- | --- |
| Modelos e catálogo | FR-001, FR-003–FR-007; SC-001/002 | FK, UNIQUE, CHECK, sequência, permissões de criação, horários nos limites, snapshot |
| Publicação | US1.1–1.4; FR-001–FR-008 | Direta/com paradas, autoria da sessão, 403 passageiro, bloqueios anônimo/pendente, rollback |
| Validação e veículo | US2.1–2.3 | Ausências, espaços, vagas fracionárias, ponto externo/repetido, erro sem gravação, reutilização própria |
| Consulta | US3.1–3.3; FR-009–FR-011 | Ordenação, vazio, isolamento por autor, sem e-mail/placa na lista, sem ações de edição |
| Entrega | SC-001–SC-005 | Regressão Feature 001, métricas separadas, roteiro sintético com tempo humano registrado |

## Complexity Tracking

Sem exceções constitucionais. Catálogo persistente mínimo e snapshot na oferta evitam criar gestão de frota. Não há tarefas de produto executadas nesta entrega documental.