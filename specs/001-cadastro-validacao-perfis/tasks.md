# Tasks: Cadastro Acadêmico, Validação de Vínculo e Perfis

**Input**: Design documents from `/specs/001-cadastro-validacao-perfis/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/web-routes.md`, `quickstart.md`)  
**Prerequisites**: `spec.md` (revisada), `plan.md` (revisado), `data-model.md`, `contracts/web-routes.md`, `research.md`  
**Constitution**: Alinhado à [Constitution v1.1.0](file:///.specify/memory/constitution.md) (Python 3.12+, Django 5, PostgreSQL, pytest, pytest-cov $\ge 80\%$, LGPD e rastreabilidade)  
**Consolidação**: 12 tarefas agrupadas por propósito verificável, dimensionadas para 1 commit de implementação cada (consolidado a partir das 34 tarefas preliminares).

---

## Phase 1: Setup (Infraestrutura do Projeto e Ambiente)

**Purpose**: Inicialização completa do projeto Django, dependências, configuração do pytest e variáveis de ambiente com PostgreSQL.

- [ ] T001 Inicializar projeto Django `carona_univille/`, dependências em `requirements.txt`, configuração do pytest em `pytest.ini` e variáveis de ambiente PostgreSQL em `.env.example` e `carona_univille/settings.py`; verificar a configuração do Django com `python manage.py check` e o pytest com `pytest --collect-only` (aceitando código de saída 5 unicamente quando indicar ausência de testes coletados, sem erros de configuração ou coleta) *(Consolidação: T001, T002, T003, T004)*

---

## Phase 2: Foundational (Estrutura Central de Identidade e Persistência)

**Purpose**: Modelagem de dados, migrações, fixture mockada e infraestrutura de templates e fixtures de teste.

**⚠️ CRITICAL**: Nenhuma história de usuário pode ser iniciada antes da conclusão desta fase.

- [ ] T002 Implementar o modelo `AcademicUser` em `accounts/models.py` herdando de `AbstractUser` com `USERNAME_FIELD = 'email'`, gerando a migração inicial em `accounts/migrations/0001_initial.py` e testes unitários em `tests/test_models.py`, validando as restrições de `data-model.md`: `AcademicUser.email` (UNIQUE), `AcademicUser.role` (MOTORISTA/PASSAGEIRO imutável), `AcademicUser.academic_status` (PENDENTE/ATIVA) e `AcademicUser.full_name` (mínimo 2 palavras) *(Consolidação: T005, T007, T011)*
- [ ] T003 [P] Criar o modelo `AcademicValidationRecord` em `accounts/models.py`, a base mockada em `accounts/fixtures/academic_whitelist.json`, o template base em `accounts/templates/accounts/base.html` e fixtures de banco e cliente em `tests/conftest.py` *(Consolidação: T006, T008, T009, T010)*

**Checkpoint**: Fundação de identidade pronta e testada — a implementação das histórias de usuário pode iniciar.

---

## Phase 3: User Story 1 - Cadastro Inicial com Papel Acadêmico (Priority: P1) 🎯 MVP

**Goal**: Permitir que membros da Univille se cadastrem informando nome, e-mail institucional `@univille.br` e papel inicial (`PASSAGEIRO` ou `MOTORISTA`), nascendo com status `PENDENTE`, com proteção contra duplicidade e rejeição de domínios externos.

**Independent Test**: Submeter formulário em `/accounts/register/` e comprovar gravação com status `PENDENTE` no PostgreSQL para motorista e passageiro; comprovar erro em e-mail fora de `@univille.br`; comprovar resposta neutra e preservação de dados em tentativa de cadastro duplicado.

- [ ] T004 [P] [US1] Implementar o formulário `AcademicRegistrationForm` em `accounts/forms.py` com validações de domínio `@univille.br` e nome completo (mínimo 2 termos), template `accounts/templates/accounts/register.html` e testes de validação em `tests/test_registration.py` *(Nota: Decisão pendente da dupla — inclusão de campos password e password_confirm) (Consolidação: T014, T016 e parte de T012)*
- [ ] T005 [US1] Implementar a view `RegisterView` em `accounts/views.py`, rotas em `accounts/urls.py` e testes de aceitação em `tests/test_registration.py` para cadastro com papéis `PASSAGEIRO` e `MOTORISTA` gerando contas com status PENDENTE *(Nota: Decisão pendente da dupla — fluxo pós-cadastro: auto-login para ativação vs redirecionamento para login) (Consolidação: T012, T015, T017)*
- [ ] T006 [US1] Implementar proteção contra enumeração na `RegisterView` em `accounts/views.py` e testes em `tests/test_registration.py` validando que e-mail duplicado exibe mensagem neutra, mantém exatamente 1 registro no PostgreSQL e preserva o status e papel originais *(Consolidação: T013 e lógica neutra de T015)*

**Checkpoint**: User Story 1 totalmente funcional, independente e testável via suíte automatizada.

---

## Phase 4: User Story 2 - Validação de Vínculo e Ativação de Conta (Priority: P2)

**Goal**: Permitir que usuários com contas pendentes validem seu vínculo institucional na PoC através de simulação contra a whitelist de homologação, transicionando o status para `ATIVA` se elegíveis ou mantendo `PENDENTE` se inelegíveis.

**Independent Test**: Autenticar conta pendente, acionar a validação institucional em `/accounts/activation/` e verificar que contas presentes na whitelist tornam-se `ATIVA`, enquanto contas ausentes permanecem `PENDENTE`.

- [ ] T007 [P] [US2] Implementar o serviço desacoplado `AcademicValidationService` em `accounts/services.py` consultando `accounts/fixtures/academic_whitelist.json` com transação atômica e testes unitários em `tests/test_activation.py` (contas elegíveis vs inelegíveis) *(Consolidação: T018, T020)*
- [ ] T008 [US2] Implementar a view `ActivationView` em `accounts/views.py`, template `accounts/templates/accounts/activation.html`, rota `/accounts/activation/` e testes de integração em `tests/test_activation.py` validando transição para `ATIVA` com auditoria ou recusa mantendo `PENDENTE` *(Nota: Decisão pendente da dupla — interface com botão único vs campos adicionais) (Consolidação: T019, T021, T022, T023)*

**Checkpoint**: User Stories 1 e 2 funcionais e integradas de forma independente.

---

## Phase 5: User Story 3 - Controle de Acesso e Restrição de Contas Pendentes (Priority: P3)

**Goal**: Confinar contas pendentes na interface de ativação impedindo acesso a caronas, liberar acesso operacional para contas ativas conforme seu papel e garantir a privacidade e minimização da LGPD no perfil (nome abreviado e e-mail institucional confidencial).

**Independent Test**: Verificar que visitantes são redirecionados para login; que usuários `PENDENTE` são redirecionados compulsoriamente para `/accounts/activation/` ao tentar acessar caronas; que usuários `ATIVA` acessam normalmente seu perfil; e que o e-mail institucional não é exposto a terceiros.

- [ ] T009 [US3] Implementar o middleware `AcademicStatusMiddleware` em `accounts/middleware.py`, registrá-lo em `carona_univille/settings.py` e escrever testes de integração em `tests/test_access_control.py` para bloqueio de visitante e redirecionamento compulsório de contas pendentes *(Consolidação: T024, T026, T027)*
- [ ] T010 [US3] Implementar views `LoginView` e `ProfileView` em `accounts/views.py`, templates `login.html` e `profile.html` e testes de privacidade em `tests/test_privacy_lgpd.py` validando exibição de `user.display_name` ("Lucas A.") e sigilo estrito do e-mail *(Consolidação: T025, T028, T029)*
- [ ] T011 [US3] Criar view placeholder `/caronas/` em `carona_univille/views.py` e testes em `tests/test_access_control.py` comprovando bloqueio a pendentes e liberação para contas ativas *(Consolidação: T030 e asserções complementares de T024)*

**Checkpoint**: Todas as histórias de usuário da Feature 001 implementadas, isoladas e protegidas.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de qualidade, conformidade com a Constitution e documentação versionada.

- [ ] T012 [P] Preparar infraestrutura de medição de qualidade criando o script `scripts/check-quality-metrics.ps1`, executar a suíte de testes de `accounts/` gerando relatório inicial `coverage.json` comprovando cobertura $\ge 80\%$ da Feature 001, registrar contagem e cobertura iniciais no topo do `README.md` e validar o roteiro do `quickstart.md` *(Consolidação: T031, T032, T033, T034)*

---

## Dependencies & Execution Order

### Phase Dependencies
- **Phase 1 (Setup)**: `T001` sem dependências — inicia imediatamente.
- **Phase 2 (Foundational)**: `T002` e `T003` dependem de `T001`. **Bloqueia todas as User Stories**.
- **Phase 3 (User Story 1 - P1)**: `T004`, `T005`, `T006` dependem de `T002` e `T003`.
- **Phase 4 (User Story 2 - P2)**: `T007` e `T008` dependem da conclusão da Phase 2 e integram com a US1.
- **Phase 5 (User Story 3 - P3)**: `T009`, `T010`, `T011` dependem de `T002`, US1 e US2.
- **Phase 6 (Polish)**: `T012` depende da conclusão de todas as histórias da Feature 001.

### Dependências Funcionais Pendentes de Homologação
- **T004 (Senha no Cadastro)**: Inclui provisoriamente campos de senha e confirmação, aguardando alinhamento formal da dupla sobre a inclusão de senha no cadastro inicial.
- **T005 (Fluxo Pós-Cadastro)**: Aguarda definição da dupla se o cadastro autentica imediatamente para conduzir à ativação ou redireciona para a tela de login.
- **T008 (Interface de Ativação)**: Implementa ativação através de botão único de ação, aguardando alinhamento da dupla sobre a necessidade de campos adicionais (ex.: confirmação explícita de matrícula).
- **TODO(VALIDACAO_ACADEMICA)**: A validação simulada contra lista fictícia em JSON (`academic_whitelist.json`) permanece como proposta pendente de homologação pelo professor orientador.
- **TODO(DOMINIOS_INSTITUCIONAIS)**: Confirmação de eventuais subdomínios institucionais adicionais além de `@univille.br` permanece pendente com a instituição.

---

## Parallel Opportunities

- **Phase 2**: `T003` pode rodar em paralelo com `T002` após a definição da estrutura base.
- **User Story 1**: `T004` pode ser iniciado em paralelo com a estrutura da view `T005`.
- **User Story 2**: `T007` (serviço) pode ser implementado antes ou em paralelo com `T008` (interface web).
- **User Story 3**: `T010` (perfil/LGPD) pode ser implementado em paralelo com `T009` (middleware de redirecionamento).
