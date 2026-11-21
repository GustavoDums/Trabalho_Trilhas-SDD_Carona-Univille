# Interface Contracts: Rotas Web e Formulários

**Feature**: `001-cadastro-validacao-perfis`  
**Data**: 2026-11-21  
**Status**: Concluído

Este documento estabelece os contratos de interface das rotas web, formulários de entrada, códigos de resposta HTTP e regras de controle de acesso para o módulo de identidade acadêmica.

---

## 1. Tabela de Rotas e Políticas de Acesso

| Rota / Endpoint | Método | Controle de Acesso | Descrição Funcional | Template Associado |
| :--- | :---: | :--- | :--- | :--- |
| `/accounts/register/` | `GET`, `POST` | Público (Visitante) | Formulário de criação de conta institucional. | `accounts/register.html` |
| `/accounts/login/` | `GET`, `POST` | Público (Visitante) | Autenticação com e-mail institucional e senha. | `accounts/login.html` |
| `/accounts/activation/` | `GET`, `POST` | Autenticado (`PENDENTE` ou `ATIVA`) | Interface de validação de vínculo acadêmico simulado. | `accounts/activation.html` |
| `/accounts/profile/` | `GET` | Autenticado (`ATIVA`) | Painel do perfil acadêmico do usuário. | `accounts/profile.html` |
| `/accounts/logout/` | `POST` | Autenticado | Encerramento da sessão Django. | Redirecionamento 302 |
| `/caronas/*` | Qualquer | Autenticado (`ATIVA`) | Rotas de carona (mockadas/reservadas para a Feature 2). | Interceptado por Middleware |

---

## 2. Contratos Detalhados por Rota

### 2.1. Rota: `/accounts/register/`

#### Requisição `GET`
- **Comportamento**: Renderiza o formulário de cadastro.
- **Resposta**: `200 OK`, HTML com campos `full_name`, `email`, `role`, `password`, `password_confirm`.

#### Requisição `POST`
- **Payload esperado**:
  ```html
  full_name: "Lucas Aluno"
  email: "lucas.aluno@univille.br"
  role: "PASSAGEIRO"  <!-- ou "MOTORISTA" -->
  password: "senha_segura_123"
  password_confirm: "senha_segura_123"
  csrfmiddlewaretoken: "..."
  ```
- **Respostas Possíveis**:
  - **Sucesso (Novo Cadastro)**:
    - Status: `302 Found` $\rightarrow$ Redireciona para `/accounts/login/` (ou efetua auto-login e redireciona para `/accounts/activation/`).
    - Estado no banco: Usuário criado com `academic_status = 'PENDENTE'`, `is_active = True`.
    - Mensagem flash: *"Cadastro realizado com sucesso! Conclua a validação do seu vínculo acadêmico para ativar sua conta."*
  - **Falha de Domínio (REQ-002)**:
    - Status: `200 OK` (re-renderiza o formulário).
    - Erro no campo `email`: *"O endereço de e-mail deve obrigatoriamente pertencer ao domínio acadêmico @univille.br."*
  - **Falha de E-mail Duplicado (Mitigação de Enumeração)**:
    - Status: `200 OK` (re-renderiza o formulário).
    - Erro não-campo (alerta geral): *"Não foi possível concluir o cadastro com os dados informados. Se você já possui vínculo cadastrado, tente fazer login."*
    - Estado no banco: Nenhuma alteração no registro existente; contagem mantida em 1.

---

### 2.2. Rota: `/accounts/login/`

#### Requisição `POST`
- **Payload esperado**:
  ```html
  email: "lucas.aluno@univille.br"
  password: "senha_segura_123"
  csrfmiddlewaretoken: "..."
  ```
- **Respostas Possíveis**:
  - **Sucesso com Conta Pendente**:
    - Status: `302 Found` $\rightarrow$ Redireciona para `/accounts/activation/`.
  - **Sucesso com Conta Ativa**:
    - Status: `302 Found` $\rightarrow$ Redireciona para `/accounts/profile/` (ou dashboard operacional).
  - **Credenciais Inválidas**:
    - Status: `200 OK` com erro: *"E-mail ou senha incorretos."*

---

### 2.3. Rota: `/accounts/activation/`

#### Requisição `GET`
- **Acesso**: Apenas usuários autenticados.
- **Comportamento**: Exibe o status atual do usuário (`PENDENTE` ou `ATIVA`), orientações da PoC sobre a whitelist de testes e um botão de ação *"Validar Vínculo Institucional"*.

#### Requisição `POST`
- **Comportamento**: Dispara o `AcademicValidationService` passando `request.user.email`.
- **Respostas Possíveis**:
  - **Vínculo Confirmado (E-mail na Whitelist Elegível)**:
    - Status: `302 Found` $\rightarrow$ Redireciona para `/accounts/profile/`.
    - Efeito: `academic_status` transiciona de `'PENDENTE'` para `'ATIVA'`. Criação de `AcademicValidationRecord` com `simulation_result = 'APROVADO'`.
    - Mensagem flash: *"Vínculo institucional com a Univille homologado com sucesso! Sua conta está ativa."*
  - **Vínculo Não Confirmado (E-mail fora da Whitelist)**:
    - Status: `200 OK` (permanece na tela de ativação).
    - Efeito: `academic_status` permanece `'PENDENTE'`. Criação de `AcademicValidationRecord` com `simulation_result = 'RECUSADO'`.
    - Mensagem de erro: *"Não foi possível comprovar o vínculo institucional para este e-mail na base acadêmica simulada. Verifique se seu cadastro consta na lista de homologação da PoC."*

---

### 2.4. Rota: `/accounts/profile/`

#### Requisição `GET`
- **Acesso**: Apenas usuários autenticados com `academic_status == 'ATIVA'`.
- **Contrato de Exibição (LGPD)**:
  - Exibe: Nome Completo do próprio usuário (`user.full_name`).
  - Exibe: Papel Acadêmico (`user.get_role_display()`).
  - Exibe: Status do Vínculo (`Ativo`).
  - Painel de Privacidade: Mostra como o usuário é apresentado a terceiros na busca de caronas: `user.display_name` (ex.: `"Lucas A."`). Informa que o e-mail institucional é mantido em sigilo estrito.

---

## 3. Contrato do Middleware de Interceptação (`AcademicStatusMiddleware`)

O middleware avalia o fluxo de requisições de acordo com a seguinte tabela de decisão:

| Estado do Usuário | URL Solicitada | Ação do Middleware | Código HTTP |
| :--- | :--- | :--- | :---: |
| Anônimo / Visitante | `/accounts/login/`, `/accounts/register/`, `/static/*` | Permite passagem normal. | `200` |
| Anônimo / Visitante | `/accounts/profile/`, `/caronas/*` | Redireciona para `/accounts/login/` com parâmetro `?next=...`. | `302` |
| Autenticado (`PENDENTE`) | `/accounts/activation/`, `/accounts/logout/`, `/static/*` | Permite passagem normal. | `200` |
| Autenticado (`PENDENTE`) | `/accounts/profile/`, `/caronas/*`, `/` | Intercepta e redireciona compulsoriamente para `/accounts/activation/`. | `302` |
| Autenticado (`ATIVA`) | Qualquer rota permitida ao seu papel | Permite passagem normal. | `200` |
