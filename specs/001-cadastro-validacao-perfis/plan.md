# Implementation Plan: Cadastro Acadêmico, Validação de Vínculo e Perfis

**Branch**: `001-cadastro-validacao-perfis` | **Date**: 2026-11-21 | **Spec**: [spec.md](file:///specs/001-cadastro-validacao-perfis/spec.md)

**Input**: Feature specification from `/specs/001-cadastro-validacao-perfis/spec.md`, alinhada à [Constitution v1.1.0](file:///.specify/memory/constitution.md) e ao [Levantamento de Requisitos](file:///docs/levantamento.md).

---

## Summary

Esta funcionalidade estabelece a fundação de identidade, controle de acesso e governança de privacidade da plataforma **Carona Univille**, implementando os requisitos `REQ-001` (Cadastro e Papéis), `REQ-002` (Validação de Vínculo Institucional) e `REQ-003` (Privacidade e LGPD).

A solução técnica baseia-se na stack homologada na Constitution 1.1.0:
- **Aplicação Web e Backend**: Python 3.12+ e Django 5.x utilizando modelo customizado `AcademicUser` (substituindo o `User` padrão).
- **Controle de Acesso**: Middleware customizado (`AcademicStatusMiddleware`) que isola estritamente contas com status `PENDENTE` na rota de ativação `/accounts/activation/`, diferenciando o status de domínio de negócio da flag técnica `is_active` do Django.
- **Validação Simulada**: Serviço desacoplado `AcademicValidationService` que consulta uma base de homologação mockada (`academic_whitelist.json`) com registros elegíveis e inelegíveis.
- **Persistência**: PostgreSQL 15+ com transações ACID e restrição de unicidade em `email`.
- **Qualidade e Testes**: Suíte automatizada com `pytest`, `pytest-django` e `pytest-cov`, garantindo cobertura mínima de 80% e mitigação ativa contra enumeração de usuários.

---

## Technical Context

- **Language/Version**: Python 3.12+
- **Primary Dependencies**: Django 5.x, `psycopg` (ou `psycopg2-binary`), `django-environ` (ou `python-dotenv`)
- **Storage**: PostgreSQL 15+ (com transações ACID atômicas; mandatório no ambiente local e nos testes de integração)
- **Testing**: `pytest`, `pytest-django`, `pytest-cov`
- **Target Platform**: Aplicação Web / Windows 11 (PowerShell) e servidores Linux
- **Project Type**: Web Application com renderização server-side (Django Templates, HTML5 e CSS)
- **Performance Goals**: Tempo de resposta de formulários e redirecionamentos < 200ms; processamento da validação simulada em < 500ms
- **Constraints**:
  - Restrição de domínio de e-mail institucional `@univille.br`
  - Conformidade inegociável com LGPD (minimização de dados cadastrais e sigilo absoluto do e-mail institucional para terceiros)
  - Cobertura de testes automatizados $\ge 80\%$ com relatório versionado
  - Zero dependência de dados reais de alunos/professores (100% dados sintéticos)
- **Scale/Scope**: PoC acadêmica demonstrável em pitch de 10 minutos, com catálogo de dados mockados e arquitetura pronta para as features de oferta e reserva

---

## Constitution Check

*GATE: Avaliação de conformidade com a Constitution v1.1.0 antes e após o design.*

| Princípio Constitucional | Status | Justificativa e Mecanismo de Aderência |
| :--- | :---: | :--- |
| **I. Acesso Acadêmico e LGPD** | **APROVADO** | Uso restrito a e-mails `@univille.br`. Minimização estrita: formulário inicial coleta apenas nome, e-mail e papel. Propriedade `display_name` exibe apenas primeiro nome e inicial ("Lucas A."). E-mail institucional é estritamente confidencial. Validação opera sobre dados fictícios (whitelist mockada). |
| **II. Integridade das Vagas e Concorrência** | **APROVADO** | PostgreSQL homologado como SGBD mandatório inclusive nos testes de integração, preparando a infraestrutura transacional ACID para os bloqueios concorrentes de reservas na Feature 2. |
| **III. Qualidade da Entrega e Testes Automatizados** | **APROVADO** | Suíte de testes com `pytest` e `pytest-cov`. Cobertura mínima de 80% configurada com relatórios estruturados (`coverage.json`). Script no quickstart para extrair contagem real e percentual medido para o topo do `README.md`. |
| **IV. Desenvolvimento Guiado por Especificação (SDD)** | **APROVADO** | Sequência rigorosa respeitada: Levantamento (`docs/levantamento.md`) $\rightarrow$ Spec (`spec.md`) $\rightarrow$ Plan (`plan.md`). Nenhuma linha de código implementada antes das tasks. |
| **V. Rastreabilidade Rigorosa e Histórico de Prompts** | **APROVADO** | Prompts registrados cronologicamente em `docs/prompts.md`. Mapeamento estrito dos cenários de teste para os requisitos `REQ-001`, `REQ-002` e `REQ-003`. |
| **VI. Stack Oficial e Governança Evolutiva** | **APROVADO** | Stack 100% aderente à Constitution 1.1.0 (Python, Django, PostgreSQL, pytest). Decisões pendentes mantidas formalmente sinalizadas. |

---

## Project Structure

A estrutura de código segue o padrão idiomático de projetos Django desacoplados:

```text
Trabalho_Trilhas-SDD_Carona-Univille/
├── carona_univille/                  # Configurações centrais do projeto Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py                   # Configuração de AUTH_USER_MODEL, DATABASES (PostgreSQL) e MIDDLEWARE
│   ├── urls.py                       # Roteamento global (/accounts/* e rotas operacionais)
│   └── wsgi.py
├── accounts/                         # Aplicação de Identidade, Autenticação, Perfis e Validação
│   ├── __init__.py
│   ├── admin.py                      # Registro de AcademicUser no Django Admin
│   ├── apps.py
│   ├── forms.py                      # AcademicRegistrationForm e formulários de autenticação
│   ├── middleware.py                 # AcademicStatusMiddleware (isolamento de contas Pendentes)
│   ├── models.py                     # AcademicUser e AcademicValidationRecord
│   ├── services.py                   # AcademicValidationService (consulta à whitelist mockada)
│   ├── urls.py                       # Rotas (/register/, /login/, /activation/, /profile/, /logout/)
│   ├── views.py                      # RegisterView, LoginView, ActivationView, ProfileView
│   ├── fixtures/
│   │   └── academic_whitelist.json   # Base mockada de homologação institucional (fictícia)
│   └── templates/
│       └── accounts/
│           ├── base.html             # Layout base com estilos CSS utilitários
│           ├── register.html         # Tela de cadastro institucional
│           ├── login.html            # Tela de autenticação com e-mail e senha
│           ├── activation.html       # Tela de validação de vínculo acadêmico
│           └── profile.html          # Painel de perfil acadêmico do usuário
├── static/
│   ├── css/
│   │   └── style.css                 # Estilos visuais da interface web
│   └── js/
├── tests/                            # Suíte de testes automatizados com pytest
│   ├── conftest.py                   # Fixtures compartilhadas (banco PostgreSQL de teste, client, usuários mock)
│   ├── test_models.py                # Testes de integridade do modelo AcademicUser (validações e display_name)
│   ├── test_registration.py          # Testes de cadastro (papéis, e-mail univille e e-mail duplicado neutro)
│   ├── test_activation.py            # Testes de validação institucional (whitelist elegível vs inelegível)
│   ├── test_access_control.py        # Testes de controle de acesso do middleware (visitante, pendente e ativo)
│   └── test_privacy_lgpd.py          # Testes de privacidade LGPD (sigilo do e-mail e exposição em camadas)
├── docs/
│   ├── levantamento.md               # Levantamento e decisões da dupla
│   └── prompts.md                    # Histórico auditável de prompts
├── specs/
│   └── 001-cadastro-validacao-perfis/
│       ├── spec.md                   # Especificação de comportamento e critérios de aceite
│       ├── plan.md                   # Este plano de implementação
│       ├── research.md               # Decisões de pesquisa técnica (Phase 0)
│       ├── data-model.md             # Modelagem de dados e transições de estado (Phase 1)
│       ├── quickstart.md             # Guia de execução rápida e validação no Windows
│       ├── contracts/
│       │   └── web-routes.md         # Contratos de rotas, formulários e respostas HTTP
│       └── checklists/
│           └── requirements.md       # Checklist de qualidade da especificação
├── manage.py
├── pytest.ini                        # Configuração do pytest com DJANGO_SETTINGS_MODULE
├── requirements.txt                  # Dependências Python homologadas
└── README.md                         # Documentação principal com indicadores de testes e cobertura
```

---

## Phase 0: Outline & Research

As decisões e justificativas técnicas detalhadas encontram-se consolidadas em [research.md](file:///specs/001-cadastro-validacao-perfis/research.md):
- **Modelo de Usuário**: Adoção de `AcademicUser` estendendo `AbstractUser` com `USERNAME_FIELD = 'email'`.
- **Diferenciação Semântica de `is_active`**: `is_active = True` permite login técnico; `academic_status` (`PENDENTE` vs `ATIVA`) governa as regras de autorização de caronas.
- **Isolamento de Contas Pendentes**: Implementação via `AcademicStatusMiddleware` que intercepta requisições e redireciona contas pendentes compulsoriamente para `/accounts/activation/`.
- **Validação Simulada**: Implementação de `AcademicValidationService` consumindo `accounts/fixtures/academic_whitelist.json`.
- **Mitigação de Enumeração**: Retorno de mensagem neutra em tentativas de cadastro com e-mail duplicado, preservando intacto o registro anterior.

---

## Phase 1: Design & Contracts

Os artefatos de design e contratos foram gerados e validados:
- **Modelo de Dados e Estados**: [data-model.md](file:///specs/001-cadastro-validacao-perfis/data-model.md) detalha campos, constraints, diagramas de transição de estado e regras de imutabilidade do papel `role`.
- **Contratos de Interface**: [contracts/web-routes.md](file:///specs/001-cadastro-validacao-perfis/contracts/web-routes.md) estabelece os métodos, rotas HTTP, payloads e códigos de resposta esperados.
- **Guia de Execução Rápida**: [quickstart.md](file:///specs/001-cadastro-validacao-perfis/quickstart.md) documenta a preparação do ambiente no Windows com PowerShell, criação do banco PostgreSQL, carregamento da fixture, execução de testes e extração de métricas de cobertura.

---

## Mapeamento de Testes Automatizados (Matriz de Rastreabilidade)

Todos os cenários de aceite descritos na especificação possuem mapeamento direto para a suíte de testes em `tests/`:

| Cenário da Spec | Requisitos | Arquivo de Teste | Comportamento Verificado pelo Teste |
| :--- | :---: | :--- | :--- |
| **Cenário 1.1** *(Cadastro Passageiro)* | `REQ-001`, `REQ-003` | `tests/test_registration.py` | Cadastro com papel `PASSAGEIRO`, e-mail `@univille.br`; valida criação da conta no PostgreSQL com `academic_status == 'PENDENTE'` e `role == 'PASSAGEIRO'`. |
| **Cenário 1.2** *(Cadastro Motorista)* | `REQ-001`, `REQ-003` | `tests/test_registration.py` | Cadastro com papel `MOTORISTA`, e-mail `@univille.br`; valida criação da conta no PostgreSQL com `academic_status == 'PENDENTE'` e `role == 'MOTORISTA'`. |
| **Cenário 1.3** *(Rejeição Forasteiro)* | `REQ-001`, `REQ-002` | `tests/test_registration.py` | Tentativa de cadastro com `@gmail.com`; valida erro de validação do formulário e ausência de gravação no banco de dados. |
| **Cenário 2.1** *(Ativação Elegível)* | `REQ-002` | `tests/test_activation.py` | Usuário com e-mail elegível na whitelist (`joao.silva@univille.br`) aciona validação; valida transição atômica para `academic_status == 'ATIVA'` e criação de log de auditoria `APROVADO`. |
| **Cenário 2.2** *(Ativação Recusada)* | `REQ-002` | `tests/test_activation.py` | Usuário com e-mail inelegível (`visitante.externo@univille.br`) aciona validação; valida permanência de `academic_status == 'PENDENTE'` e criação de log `RECUSADO`. |
| **Cenário 3.1** *(Bloqueio Pendente)* | `REQ-002`, `REQ-003` | `tests/test_access_control.py` | Usuário autenticado com `PENDENTE` tenta acessar `/caronas/` ou `/accounts/profile/`; valida interceptação pelo middleware com redirecionamento HTTP 302 para `/accounts/activation/`. |
| **Cenário 3.2** *(Acesso Conta Ativa)* | `REQ-001`, `REQ-002` | `tests/test_access_control.py` | Usuário autenticado com `ATIVA` acessa `/accounts/profile/` e áreas permitidas ao seu papel; valida resposta HTTP 200 e exibição de selo ativo. |
| **Cenário 3.3** *(Acesso Visitante)* | `REQ-002` | `tests/test_access_control.py` | Usuário anônimo tenta acessar rota protegida; valida redirecionamento HTTP 302 para `/accounts/login/`. |
| **Cenário 4.1** *(E-mail Duplicado)* | `REQ-001`, `REQ-003` | `tests/test_registration.py` | Submissão de cadastro com e-mail já existente; valida: (1) exibição da mensagem neutra/genérica; (2) existência de exatamente 1 registro no PostgreSQL (`count() == 1`); (3) preservação estrita do `academic_status`, da senha e do papel original (sem sobrescrita). |
| **Cenário 4.2** *(Privacidade LGPD)* | `REQ-003` | `tests/test_privacy_lgpd.py` | Valida que a propriedade `display_name` formata apenas primeiro nome e inicial ("Lucas A.") e que o endereço de e-mail institucional NUNCA é renderizado em HTML de listagens públicas ou exposto para terceiros. |

---

## Decisões Funcionais Pendentes para Alinhamento da Dupla

### Decisão confirmada — T005 (2026-11-22)

O cadastro concluído redireciona para `/accounts/login/`, sem autenticação
automática, conforme confirmação do usuário. A T005 entrega a view e a rota
de cadastro; a tela e a rota de login pertencem à T010. Até essa tarefa,
o destino do redirecionamento ainda não dispõe de uma página implementada.

Durante a elaboração do plano técnico, as seguintes questões operacionais de interface foram mapeadas e permanecem registradas para deliberação da dupla antes ou durante a implementação:

1. **Definição da Senha de Acesso Inicial**:
   - *Situação*: A spec estabelece o cadastro de Nome, E-mail e Papel.
   - *Opção Recomendada no Plano*: O próprio formulário de cadastro inclui os campos `password` e `password_confirm`, permitindo que o usuário crie sua credencial de acesso imediatamente.
   - *Alternativa*: Cadastro sem senha, gerando um link com token de ativação para definição de senha no primeiro acesso (requer serviço simulado de envio).
   - *Status*: `Confirmado pelo usuário em 2026-11-22: password e password_confirm obrigatórios, igualdade entre campos e validadores de senha do Django`.

2. **Interface da Tela de Ativação (`/accounts/activation/`)**:
   - *Situação*: Como o usuário aciona a validação simulada com a whitelist?
   - *Opção Recomendada no Plano*: A tela de ativação exibe os dados cadastrados (Nome, E-mail `@univille.br`) e um botão de ação único: *"Validar Vínculo Institucional"*. Ao clicar, o sistema consulta a whitelist usando o próprio e-mail da sessão autenticada.
   - *Alternativa*: Solicitar que o usuário digite novamente sua matrícula institucional no formulário de ativação para testar o vínculo.
   - *Status*: `Pendente de confirmação da dupla (Opção de botão único adotada provisoriamente no plano)`.

---

## Pendências Constitucionais Mantidas

Conforme exigido pela governança da Constitution 1.1.0:
- **`TODO(VALIDACAO_ACADEMICA)`**: A aprovação formal do professor orientador quanto à validade acadêmica da simulação com whitelist permanece pendente de alinhamento em aula.
- **`TODO(DOMINIOS_INSTITUCIONAIS)`**: O domínio `@univille.br` está implementado como padrão; a inclusão de subdomínios adicionais reais permanece pendente de homologação.

---
*Artefato de planejamento técnico aprovado e pronto para a geração de tarefas atômicas com `/speckit-tasks`.*
