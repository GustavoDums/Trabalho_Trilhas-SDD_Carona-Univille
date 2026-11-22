# Tasks: Cadastro Acadêmico, Validação de Vínculo e Perfis

**Input**: Design documents from `/specs/001-cadastro-validacao-perfis/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/web-routes.md`, `quickstart.md`)  
**Prerequisites**: `spec.md` (revisada), `plan.md` (revisado), `data-model.md`, `contracts/web-routes.md`, `research.md`  
**Constitution**: Alinhado à [Constitution v1.1.0](file:///.specify/memory/constitution.md) (Python 3.12+, Django 5, PostgreSQL, pytest, pytest-cov $\ge 80\%$, LGPD e rastreabilidade)  
**Consolidação**: 12 tarefas agrupadas por propósito verificável, dimensionadas para 1 commit de implementação cada (consolidado a partir das 34 tarefas preliminares).

---

## Phase 1: Setup (Infraestrutura do Projeto e Ambiente)

**Purpose**: Inicialização completa do projeto Django, dependências, configuração do pytest e variáveis de ambiente com PostgreSQL.

- [x] T001 Inicializar projeto Django `carona_univille/`, dependências em `requirements.txt`, configuração do pytest em `pytest.ini` e variáveis de ambiente PostgreSQL em `.env.example` e `carona_univille/settings.py`; verificar a configuração do Django com `python manage.py check` e o pytest com `pytest --collect-only` (aceitando código de saída 5 unicamente quando indicar ausência de testes coletados, sem erros de configuração ou coleta) *(Consolidação: T001, T002, T003, T004)*

---

## Phase 2: Foundational (Estrutura Central de Identidade e Persistência)

**Purpose**: Modelagem de dados, migrações, fixture mockada e infraestrutura de templates e fixtures de teste.

**⚠️ CRITICAL**: Nenhuma história de usuário pode ser iniciada antes da conclusão desta fase.

- [x] T002 Implementar o modelo `AcademicUser` em `accounts/models.py` herdando de `AbstractUser` com `USERNAME_FIELD = 'email'`, gerando a migração inicial em `accounts/migrations/0001_initial.py` e testes unitários em `tests/test_models.py`, validando as restrições de `data-model.md`: `AcademicUser.email` (UNIQUE), `AcademicUser.role` (MOTORISTA/PASSAGEIRO imutável), `AcademicUser.academic_status` (PENDENTE/ATIVA) e `AcademicUser.full_name` (mínimo 2 palavras) *(Consolidação: T005, T007, T011)*
- [x] T003 [P] Criar o modelo `AcademicValidationRecord` em `accounts/models.py`, a base mockada em `accounts/fixtures/academic_whitelist.json`, o template base em `accounts/templates/accounts/base.html` e fixtures de banco e cliente em `tests/conftest.py` *(Consolidação: T006, T008, T009, T010)*

**Checkpoint**: Fundação de identidade pronta e testada — a implementação das histórias de usuário pode iniciar.

---

## Phase 3: User Story 1 - Cadastro Inicial com Papel Acadêmico (Priority: P1) 🎯 MVP

**Goal**: Permitir que membros da Univille se cadastrem informando nome, e-mail institucional `@univille.br` e papel inicial (`PASSAGEIRO` ou `MOTORISTA`), nascendo com status `PENDENTE`, com proteção contra duplicidade e rejeição de domínios externos.

**Independent Test**: Submeter formulário em `/accounts/register/` e comprovar gravação com status `PENDENTE` no PostgreSQL para motorista e passageiro; comprovar erro em e-mail fora de `@univille.br`; comprovar resposta neutra e preservação de dados em tentativa de cadastro duplicado.

- [x] T004 [P] [US1] Implementar o formulário `AcademicRegistrationForm` em `accounts/forms.py` com validações de domínio `@univille.br` e nome completo (mínimo 2 termos), template `accounts/templates/accounts/register.html` e testes de validação em `tests/test_registration.py` *(Decisão confirmada em 2026-11-22: incluir password e password_confirm, validar igualdade e aplicar os validadores de senha do Django) (Consolidação: T014, T016 e parte de T012)*
- [x] T005 [US1] Implementar a view `RegisterView` em `accounts/views.py`, rotas em `accounts/urls.py` e testes de aceitação em `tests/test_registration.py` para cadastro com papéis `PASSAGEIRO` e `MOTORISTA` gerando contas com status PENDENTE *(Decisão confirmada em 2026-11-22: redirecionar para /accounts/login/ sem autenticação automática) (Consolidação: T012, T015, T017)*
- [x] T006 [US1] Implementar proteção contra enumeração na `RegisterView` em `accounts/views.py` e testes em `tests/test_registration.py` validando que e-mail duplicado exibe mensagem neutra, mantém exatamente 1 registro no PostgreSQL e preserva o status e papel originais *(Consolidação: T013 e lógica neutra de T015)*

**Checkpoint**: User Story 1 totalmente funcional, independente e testável via suíte automatizada.

---

## Phase 4: User Story 2 - Validação de Vínculo e Ativação de Conta (Priority: P2)

**Goal**: Permitir que usuários com contas pendentes validem seu vínculo institucional na PoC através de simulação contra a whitelist de homologação, transicionando o status para `ATIVA` se elegíveis ou mantendo `PENDENTE` se inelegíveis.

**Independent Test**: Autenticar conta pendente, acionar a validação institucional em `/accounts/activation/` e verificar que contas presentes na whitelist tornam-se `ATIVA`, enquanto contas ausentes permanecem `PENDENTE`.

- [x] T007 [P] [US2] Implementar o serviço desacoplado `AcademicValidationService` em `accounts/services.py` consultando `accounts/fixtures/academic_whitelist.json` com transação atômica e testes unitários em `tests/test_activation.py` (contas elegíveis vs inelegíveis) *(Consolidação: T018, T020)*
- [x] T008 [US2] Implementar a view `ActivationView` em `accounts/views.py`, template `accounts/templates/accounts/activation.html`, rota `/accounts/activation/` e testes de integração em `tests/test_activation.py` validando transição para `ATIVA` com auditoria ou recusa mantendo `PENDENTE` *(Decisão confirmada em 2026-11-22: botão único usando o e-mail da sessão, sem campos adicionais) (Consolidação: T019, T021, T022, T023)*

**Checkpoint**: User Stories 1 e 2 funcionais e integradas de forma independente.

---

## Phase 5: User Story 3 - Controle de Acesso e Restrição de Contas Pendentes (Priority: P3)

**Goal**: Confinar contas pendentes na interface de ativação impedindo acesso a caronas, liberar acesso operacional para contas ativas conforme seu papel e garantir a privacidade e minimização da LGPD no perfil (nome abreviado e e-mail institucional confidencial).

**Independent Test**: Verificar que visitantes são redirecionados para login; que usuários `PENDENTE` são redirecionados compulsoriamente para `/accounts/activation/` ao tentar acessar caronas; que usuários `ATIVA` acessam normalmente seu perfil; e que o e-mail institucional não é exposto a terceiros.

- [x] T009 [US3] Implementar o middleware `AcademicStatusMiddleware` em `accounts/middleware.py`, registrá-lo em `carona_univille/settings.py` e escrever testes de integração em `tests/test_access_control.py` para bloqueio de visitante e redirecionamento compulsório de contas pendentes *(Consolidação: T024, T026, T027)*
- [x] T010 [US3] Implementar views `LoginView` e `ProfileView` em `accounts/views.py`, templates `login.html` e `profile.html` e testes de privacidade em `tests/test_privacy_lgpd.py` validando exibição de `user.display_name` ("Lucas A.") e sigilo estrito do e-mail *(Consolidação: T025, T028, T029)*
- [x] T011 [US3] Criar view placeholder `/caronas/` em `carona_univille/views.py` e testes em `tests/test_access_control.py` comprovando bloqueio a pendentes e liberação para contas ativas *(Consolidação: T030 e asserções complementares de T024)*

**Checkpoint**: Todas as histórias de usuário da Feature 001 implementadas, isoladas e protegidas.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Verificação de qualidade, conformidade com a Constitution e documentação versionada.

- [x] T012 [P] Preparar infraestrutura de medição de qualidade criando o script `scripts/check-quality-metrics.ps1`, executar a suíte de testes de `accounts/` gerando relatório inicial `coverage.json` comprovando cobertura $\ge 80\%$ da Feature 001, registrar contagem e cobertura iniciais no topo do `README.md` e validar o roteiro do `quickstart.md` *(Consolidação: T031, T032, T033, T034)*

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
- **T004 (Senha no Cadastro)**: Confirmada pelo usuário em 2026-11-22: senha e confirmação obrigatórias, com validação de igualdade e validadores de senha do Django.
- **T005 (Fluxo Pós-Cadastro)**: Confirmado em 2026-11-22: redirecionar para /accounts/login/ sem autenticação automática.
- **T008 (Interface de Ativação)**: Botão único aprovado em 2026-11-22, usando exclusivamente o e-mail da sessão autenticada, sem campos adicionais.
- **TODO(VALIDACAO_ACADEMICA)**: A validação simulada contra lista fictícia em JSON (`academic_whitelist.json`) permanece como proposta pendente de homologação pelo professor orientador.
- **TODO(DOMINIOS_INSTITUCIONAIS)**: Confirmação de eventuais subdomínios institucionais adicionais além de `@univille.br` permanece pendente com a instituição.

---

## Parallel Opportunities

- **Phase 2**: `T003` pode rodar em paralelo com `T002` após a definição da estrutura base.
- **User Story 1**: `T004` pode ser iniciado em paralelo com a estrutura da view `T005`.
- **User Story 2**: `T007` (serviço) pode ser implementado antes ou em paralelo com `T008` (interface web).
- **User Story 3**: `T010` (perfil/LGPD) pode ser implementado em paralelo com `T009` (middleware de redirecionamento).

## Evidência de conclusão — T002 (2026-11-22)

- Dependência T001 satisfeita. Escopo: modelo de identidade; REQ-001, REQ-002 e REQ-003; FR-001, FR-003, FR-007 (unicidade no banco) e FR-008.
- TDD no ambiente virtual Python 3.12.10 / Django 5.1.15: 24 testes falharam antes da implementação (modelo ainda era `auth.User`, sem campos acadêmicos); os mesmos 24 testes passaram após o modelo e a migração.
- `python -m pytest tests/test_models.py --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`: 24 aprovados; cobertura combinada 93,6842105263158%, linhas 75/79 e ramificações 14/16. Relatório em [coverage.json](../../coverage.json).
- Verificados: e-mail único no PostgreSQL, login por e-mail, papéis válidos e imutáveis no `save()`, status inicial obrigatoriamente PENDENTE, nome com pelo menos dois termos, validação institucional e propriedades de domínio.
- `python manage.py check`: nenhum problema. `python manage.py makemigrations --check --dry-run`: nenhuma alteração pendente.
- `python manage.py migrate --noinput`: migração inicial aplicada no PostgreSQL local `carona_univille_db`; `showmigrations accounts`: `[X] 0001_initial`. Introspecção confirmou a tabela `accounts_academicuser` e o índice UNIQUE nativo de `email`. O pytest também aplicou as migrações no banco de testes PostgreSQL.
- As regras de nome, choices e estado inicial são validadas ao salvar; a imutabilidade segue o `save()` previsto no modelo de dados. Operações ORM em lote e SQL direto não executam essas validações Python; a unicidade permanece garantida no banco.
- Demais tarefas permanecem abertas. Staging e commit reservados à revisão do usuário.

## Evidência de conclusão — T003 (2026-11-22)

- Dependência T001 satisfeita; identidade da T002 disponível. Infraestrutura para REQ-002 (FR-004 e auditoria de validação) e REQ-003 (dados sintéticos e minimização).
- Criados `AcademicValidationRecord`, migração `0002_academicvalidationrecord`, catálogo JSON fictício, template base e fixtures compartilhadas de usuários e clientes. O banco de testes e o cliente anônimo reutilizam as fixtures `db` e `client` do pytest-django; clientes autenticados têm sessões independentes.
- Validada a persistência de APROVADO e RECUSADO, vínculo reverso, timestamp automático, campos obrigatórios, formato de e-mail, choices e exclusão em cascata. Criar auditoria não ativa a conta; o serviço de ativação permanece na T007.
- Validados os quatro registros do catálogo e a herança do template com escape de conteúdo. Catálogo mantido conforme `data-model.md`; quickstart corrigido para não usar `loaddata`, conforme resolução autorizada pelo usuário.
- Testes: 10 novos da T003 e 24 de regressão da T002, todos aprovados no PostgreSQL. Comando: `venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_foundation.py --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
- Cobertura combinada: 94,5945945945946%; linhas 91/95 e ramificações 14/16. Relatório em [coverage.json](../../coverage.json) e métricas atualizadas no README.
- `manage.py check`: nenhum problema; `makemigrations --check --dry-run`: nenhuma alteração pendente. `migrate --noinput`: nova migração aplicada em `carona_univille_db`; `showmigrations accounts` confirmou `[X] 0002_academicvalidationrecord`. Introspecção confirmou os campos e a FK para `accounts_academicuser` no PostgreSQL.
- T004–T012 não executadas. Sem staging ou commit.

## Evidência de conclusão — T004 (2026-11-22)

- Dependências T002 e T003 concluídas. REQ-001 e REQ-002, com minimização de REQ-003: formulário de nome completo, e-mail institucional, papel, senha e confirmação; template e testes de validação. Decisão sobre senha confirmada pelo usuário e registrada na spec e no plano.
- Formulário usa validações do modelo para nome com pelo menos dois termos e domínio exato `@univille.br`; valida igualdade de senhas e aplica os quatro validadores configurados no Django. Apenas os campos autorizados compõem o formulário; senha armazenada como hash e confirmação não persistida.
- Template herda o layout base, inclui CSRF, labels, instruções e erros; senhas não são reapresentadas após erro. Verificado por renderização automatizada, sem rota ou servidor nesta tarefa.
- Testes novos: 18 aprovados. Regressão com T002–T003: 52 aprovados no PostgreSQL, no ambiente virtual Python 3.12.10 / Django 5.1.15. Antes da implementação, a coleta detectou a ausência de `accounts.forms`.
- Comando: `venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_foundation.py tests/test_registration.py --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
- Cobertura de `forms.py`: 100% de linhas e ramificações. Cobertura combinada de `accounts/`: 96,02649006622516%; linhas 125/129 e ramificações 20/22. Relatório em [coverage.json](../../coverage.json).
- `manage.py check`: nenhum problema. `makemigrations --check --dry-run`: nenhuma alteração de esquema necessária. Diagnósticos do editor sem erros nos arquivos Python novos.
- View, rotas, redirecionamento pós-cadastro (T005) e resposta neutra de duplicidade (T006) permanecem fora desta rodada. Nenhum staging ou commit realizado.

## Evidência de conclusão — T005 (2026-11-22)

- Dependências T002 e T003 atendidas; formulário T004 disponível, com senha e confirmação aprovadas. Escopo REQ-001 e REQ-002, cenários 1.1, 1.2 e rejeição do cenário 1.3. Fluxo aprovado pelo usuário: redirecionamento para `/accounts/login/`, sem autenticação automática.
- Criados `RegisterView` e `accounts/urls.py`; integrado `/accounts/register/` ao roteamento principal. GET renderiza o formulário e POST válido cria conta PENDENTE com mensagem de sucesso. Formulário e regras de senha preservados.
- Oito novos testes HTTP: GET, ambos os papéis persistidos no PostgreSQL, ausência de autenticação automática, mensagem e destino do redirecionamento, entradas inválidas e CSRF. Tentativa de injetar status ATIVA ou privilégios administrativos é ignorada. Dados sintéticos exclusivamente.
- Ciclo de verificação: oito testes falharam antes pela ausência do namespace da rota; após implementação, suíte de T002–T005 com 60 testes aprovados. `venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_foundation.py tests/test_registration.py --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
- Cobertura de views e rotas de accounts: 100%; combinada 96,3855421686747%, linhas 140/144 e ramificações 20/22. Relatório em [coverage.json](../../coverage.json).
- `manage.py check`: nenhum problema. `makemigrations --check --dry-run`: nenhuma alteração pendente. Editor sem diagnósticos nos arquivos verificados.
- Limite desta entrega: o destino `/accounts/login/` será implementado na T010; os testes verificam o 302 sem seguir para uma tela ainda indisponível. Tratamento neutro de duplicidade permanece na T006. Nenhum staging ou commit.

## Evidência de conclusão — T006 (2026-11-22)

- Dependências T002 e T003 atendidas; formulário e view de T004 e T005 disponíveis. Escopo: REQ-001, REQ-003 e FR-007, proteção de duplicidade e preservação da conta original. Nenhuma decisão pendente afeta esta tarefa.
- `RegisterView` substitui o erro de unicidade por erro geral neutro: “Não foi possível concluir o cadastro com os dados informados. Se você já possui vínculo cadastrado, tente fazer login.” Erros não relacionados permanecem disponíveis. Sem login automático ou mensagem de sucesso em duplicidade.
- Gravação protegida por savepoint; duplicidade detectada no `save()` ou na UNIQUE nativa do PostgreSQL retorna a mesma mensagem. Outros erros de integridade e domínio são propagados. Nenhuma alteração de modelo, formulário ou esquema.
- Nove novos testes: quatro combinações de papel MOTORISTA/PASSAGEIRO e estado PENDENTE/ATIVA; erros mistos; rejeição pela UNIQUE real; duplicidade detectada durante save; propagação de duas falhas não relacionadas. Comparação de todos os campos persistidos confirma preservação de nome, e-mail, papel, status, hash de senha, flags e timestamps, mantendo exatamente uma conta.
- Seis testes iniciais falharam antes da correção. Suíte final de T002–T006: 69 aprovados no PostgreSQL, usando o ambiente virtual do projeto. Comando: `venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_foundation.py tests/test_registration.py --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
- Cobertura combinada: 95,16908212560386%; linhas 169/175 e ramificações 28/32 (87,5%). Relatório em [coverage.json](../../coverage.json), métricas no README.
- `manage.py check`: nenhum problema; `makemigrations --check --dry-run`: nenhuma alteração pendente. Editor sem erros nos arquivos Python alterados; `git diff --check` sem erros.
- Limite da verificação: a janela entre pré-validação e gravação foi simulada de modo determinístico; a rejeição de unicidade foi executada no PostgreSQL real, sem disparar requisições simultâneas. Não se afirma indistinguibilidade de tempo ou resposta entre cadastro novo e duplicado, além da mensagem neutra aprovada.
- T007 e posteriores não executadas; sem staging ou commit.

## Evidência de conclusão — T007 (2026-11-22)

- Dependências de Phase 2 (T002 e T003) satisfeitas. REQ-002, FR-004 e FR-005, cenários 2.1 e 2.2: consulta do catálogo JSON fictício sem interface HTTP. A homologação docente da abordagem simulada permanece pendente, sem mudança das decisões de negócio.
- `AcademicValidationService.validate(email)` consulta a conta persistida e retorna booleano. Transação atômica e bloqueio da conta mantêm atualização de estado e auditoria no mesmo commit. Elegível torna-se ATIVA com APROVADO; ausente ou explicitamente inelegível permanece PENDENTE com RECUSADO. Repetição em conta ativa não duplica auditoria.
- Treze testes novos: três e-mails elegíveis em ambos os papéis; e-mail ausente e registro inelegível em ambos os papéis; repetição de validação; rollback ao falhar auditoria; catálogo JSON inválido sem ativação. Todos os dados são sintéticos. Papel, senha e flag técnica de autenticação preservados.
- Antes da implementação, a coleta falhou pela ausência de `accounts.services`. Verificação final no ambiente virtual Python 3.12.10 / Django 5.1.15: 82 testes aprovados no PostgreSQL, incluindo regressão de T002–T006.
- Comando: `venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_foundation.py tests/test_registration.py tests/test_activation.py --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
- Serviço: 100% de linhas e ramificações; cobertura combinada de `accounts/`: 95,65217391304348%, linhas 188/194 e ramificações 32/36. Relatório em [coverage.json](../../coverage.json), métricas no README.
- `manage.py check`: nenhum problema; `makemigrations --check --dry-run`: nenhuma alteração pendente. Diagnósticos do editor sem erros. Não houve mudança de esquema.
- T008 e posteriores não executadas. View, template, botão, rotas e identificação pela sessão permanecem para a T008. Nenhuma afirmação de teste de requisições concorrentes; sem staging ou commit.

## Evidência de conclusão — T008 (2026-11-22)

- Dependências T002, T003 e T007 atendidas, cadastro disponível. REQ-002, FR-004 e FR-005, cenários 2.1 e 2.2 e repetição de conta ativa. Botão único, sem campos adicionais, aprovado pelo usuário e registrado na spec e no plano.
- `ActivationView` e `/accounts/activation/` exigem sessão autenticada. GET exibe somente os dados da própria conta e orientações sobre a simulação, sem alterar estado. POST passa exclusivamente `request.user.email` ao serviço; parâmetros enviados não selecionam outra conta.
- Aprovação gera auditoria APROVADO e estado ATIVA, mensagem contratada e redirecionamento para `/accounts/profile/`. Recusa gera RECUSADO, mantém PENDENTE e renderiza a mensagem contratada na mesma tela. Conta já ativa redireciona com aviso, sem nova auditoria.
- Doze testes novos: GET/POST anônimos, GET sem efeitos, aprovação/recusa/ausência nos dois papéis com tentativa de injetar outra identidade, GET/POST já ativo e CSRF real (rejeição sem token e aprovação com token).
- Antes da implementação, os 12 testes falharam pela rota ausente. A primeira regressão detectou deslocamento indevido de um método de cadastro durante a edição; corrigido antes da verificação final. Suíte final: 94 testes aprovados no PostgreSQL, usando o ambiente virtual Python 3.12.10 / Django 5.1.15.
- Comando: `venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_foundation.py tests/test_registration.py tests/test_activation.py --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
- Cobertura combinada 96,04743083003953%; linhas 207/213 e ramificações 36/40 (90%). Relatório em [coverage.json](../../coverage.json), métricas no README.
- `manage.py check`: nenhum problema; `makemigrations --check --dry-run`: nenhuma alteração de esquema. Editor sem erros nos arquivos Python verificados. Template validado por renderização nos testes HTTP.
- Limites: autenticação nos testes criada pelas sessões Django; login e perfil permanecem na T010 e os testes não seguem os redirecionamentos para essas páginas ainda ausentes. Middleware da T009 não implementado. Homologação docente da simulação continua pendente. Sem staging ou commit.

## Evidência de conclusão — T009 (2026-11-22)

- Dependências T002, US1 e US2 atendidas. REQ-002, REQ-003 e FR-006; cenários 3.1 e 3.3. Implementado `AcademicStatusMiddleware`, registrado após AuthenticationMiddleware e MessageMiddleware.
- Visitantes acessam login, cadastro e arquivos estáticos; demais caminhos redirecionam ao login com `next`. Pendentes são encaminhados à ativação com aviso, exceto ativação, logout e arquivos estáticos. Ativos passam ao controle da view, sem concessão adicional de papéis.
- Exceções de ativação/logout usam caminhos exatos; `/accounts/activation/extra/` não contorna a proteção. Prefixo de estáticos inclui separador e não libera `/static-privado/`. Interceptação ocorre antes da view protegida, sem exposição do conteúdo sintético de teste.
- 36 testes novos: visitantes GET/POST, pendentes nos dois papéis, POST protegido, exceções sem ciclos, rotas públicas, passagem de ativos e ordem do middleware. URLconf e views de prova existem exclusivamente no teste, sem antecipar perfil ou página de caronas de T010/T011.
- Antes da implementação: 26 falhas e 10 testes aprovados. Após implementação, suíte de T002–T009: 130 testes aprovados no PostgreSQL, usando o ambiente virtual Python 3.12.10 / Django 5.1.15.
- Comando: `venv/Scripts/python.exe -m pytest tests/test_models.py tests/test_foundation.py tests/test_registration.py tests/test_activation.py tests/test_access_control.py --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
- Middleware: 100% de linhas e ramificações. Cobertura combinada 96,46643109540636%; linhas 229/235 e ramificações 44/48. Relatório em [coverage.json](../../coverage.json), métricas no README.
- `manage.py check`: nenhum problema. `makemigrations --check --dry-run`: nenhuma alteração pendente. Editor sem erros nos arquivos verificados; `git diff --check` sem erros.
- Login e logout efetivos e perfil não foram implementados nesta tarefa; as exceções foram verificadas com rotas de teste. T010 e posteriores permanecem abertas. Alterações preexistentes preservadas; sem staging ou commit.

## Evidência de conclusão — T010 (2026-11-22)

- Dependências T002, US1 e US2 concluídas; middleware T009 disponível. REQ-002 e REQ-003, cenário 3.2 e privacidade em camadas. Login manual após cadastro confirmado na T005 e preservado; nenhuma decisão pendente afeta o escopo.
- Implementados `LoginView`, formulário de autenticação com e-mail e senha pelo backend Django, `ProfileView`, rotas e templates. Login válido leva pendentes à ativação e ativos ao perfil. Destino definido pelo estado acadêmico, sem aceitar redirecionamento externo via `next`. Credenciais inválidas, inexistentes ou tecnicamente desabilitadas recebem o mesmo erro genérico aprovado.
- Perfil consulta somente a sessão, exibe nome completo próprio, papel, vínculo Ativo e prévia `display_name` (Lucas A.). E-mail não renderizado; parâmetros de outra conta não alteram a identidade exibida. Visitantes e pendentes não acessam o perfil.
- Dezesseis testes novos: renderização do login; login nos dois papéis/estados; erros genéricos e ausência de credenciais; privacidade nos dois papéis; bloqueios do perfil; CSRF; login de usuário ativo sem ciclo; fluxo completo cadastro → login manual → ativação → perfil nos dois papéis.
- Antes da implementação, 13 testes iniciais falharam pela ausência das rotas. Após implementação, os 13 passaram; acrescentados três cenários de campos obrigatórios e fluxo completo. Verificação final: 146 testes aprovados no PostgreSQL, no ambiente virtual Python 3.12.10 / Django 5.1.15.
- Comando: `venv/Scripts/python.exe -m pytest tests --cov=accounts --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
- Cobertura combinada 96,81528662420382%; linhas 256/262 e ramificações 48/52. Formulários: 100% de linhas e ramificações. Relatório em [coverage.json](../../coverage.json), métricas no README.
- `manage.py check`: nenhum problema; `makemigrations --check --dry-run`: nenhuma alteração pendente. Editor sem erros nos arquivos verificados. Templates verificados pela renderização HTTP, sem inspeção visual em navegador.
- Ajustada somente a precedência das rotas de prova no URLconf de `test_access_control.py`, mantendo os testes isolados de middleware após a introdução das rotas reais. Sem mudança das regras do middleware ou do cadastro.
- Não existem listagens públicas nesta feature; a privacidade foi verificada no perfil próprio e na prévia abreviada, sem alegar teste de listagens de caronas futuras. T011/T012 não executadas. Logout fora do escopo desta tarefa. Alterações preexistentes preservadas; sem staging ou commit.

## Evidência de conclusão — T011 (2026-11-22)

- Dependências T002, US1 e US2 concluídas; middleware T009 disponível. Escopo REQ-002 e FR-006, cenários 3.1 e 3.2: placeholder `/caronas/` com acesso somente a contas ativas.
- Criada view mínima em `carona_univille/views.py` e rota nomeada `caronas` no URLconf principal. Resposta de texto informa que as funcionalidades serão disponibilizadas posteriormente, sem dados pessoais. Nenhuma operação de oferta, busca, reserva ou cancelamento implementada.
- Seis testes novos em `tests/test_access_control.py`, usando o URLconf real do projeto: resolução da rota para a view correta, visitante redirecionado ao login, pendentes redirecionados à ativação nos dois papéis e ativos recebendo HTTP 200 nos dois papéis. As views de prova da T009 permanecem isoladas.
- Antes da implementação: três falhas (rota ausente e HTTP 404 para ativos), três aprovações (bloqueios já garantidos pelo middleware). Após implementação, suíte final: 152 testes aprovados no PostgreSQL, com o ambiente virtual Python 3.12.10 / Django 5.1.15.
- Comando: `venv/Scripts/python.exe -m pytest tests --cov=accounts --cov=carona_univille.views --cov-branch --cov-report=term-missing --cov-report=json:coverage.json`.
- View placeholder: 100% de linhas. Medição ampliada para incluir a nova view além de `accounts/`: cobertura combinada 96,84542586750788%, linhas 259/265 e ramificações 48/52. Relatório em [coverage.json](../../coverage.json), métricas no README.
- `manage.py check`: nenhum problema; `makemigrations --check --dry-run`: nenhuma alteração pendente. Editor sem erros nos arquivos verificados; `git diff --check` sem erros.
- Critérios da T011 atendidos. T012 não executada. Alterações preexistentes preservadas; sem staging ou commit.

## Evidência de conclusão — T012 (2026-11-22)

- Dependências T001–T011 concluídas. REQ-018 e REQ-019, Princípio III: medição reproduzível da Feature 001, relatório versionável e indicadores reais no início do README. Nenhuma mudança de comportamento da aplicação.
- Criado `scripts/check-quality-metrics.ps1`, compatível com PowerShell 5.1, usando exclusivamente o Python do venv do projeto. Executa explicitamente os seis arquivos da Feature 001, mede `accounts/` e a view placeholder e gera `coverage.json` e `test-results.xml`.
- Aplica `--cov-branch --cov-fail-under=80` e exige adicionalmente no mínimo 80% separadamente em linhas e ramificações. Falha de execução ou meta impede atualização do README. Contagem vem dos casos efetivamente aprovados no JUnit, sem usar coleta como resultado de execução. Atualização limitada ao bloco marcado de métricas.
- Execução final do script: saída 0, 152 aprovados e 0 ignorados no PostgreSQL. Cobertura combinada 96,84542586750788%; linhas 259/265 (97,73584905660377%) e ramificações 48/52 (92,3076923076923%). Meta 80% atendida. README atualizado automaticamente e consistência com os dois relatórios conferida.
- Comando reproduzível: `powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-quality-metrics.ps1`. A primeira execução passou nos testes mas falhou na leitura final do JSON por aspas do PowerShell; corrigido e repetido integralmente com sucesso. Script salvo com BOM UTF-8 para compatibilidade de acentos no PowerShell 5.1; análise sintática sem erros.
- Quickstart corrigido conforme autorização do usuário: perfil próprio com prévia abreviada, sem perfil público nesta feature; resultados reais em lugar de contagem por coleta e exemplos numéricos; login manual e botão de ativação já aprovados; proteção de `.env` existente; criação do banco de testes gerida pelo pytest-django.
- Verificação do quickstart no ambiente existente: `manage.py check` sem problemas, `migrate --check` sem pendências, catálogo validado por `json.tool`. Suíte cobriu cadastro nos dois papéis, rejeição de domínio, duplicidade, confinamento, aprovação/recusa de ativação e privacidade; fluxo HTTP completo de cadastro → login manual → ativação → perfil validado. Ambiente não recriado; credenciais não sobrescritas; sem inspeção visual manual ou medição humana de tempo de demo.
- Artefatos versionáveis preparados para revisão, sem staging ou commit. Alteração preexistente de `docs/prompts.md` preservada. `git diff --check` sem erros. Pendências de homologação docente e domínios adicionais continuam registradas, sem decisão nova nesta tarefa.
