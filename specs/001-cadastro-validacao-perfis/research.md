# Phase 0 Research: Cadastro Acadêmico, Validação de Vínculo e Perfis

**Feature**: `001-cadastro-validacao-perfis`  
**Data**: 2026-11-21  
**Status**: Concluído (Decisões Técnicas Consolidadas)

---

## 1. Modelo de Identidade e Autenticação (Django Custom User)

### Decisão
Substituir o modelo padrão `User` do Django por um modelo customizado `AcademicUser`, herdando de `django.contrib.auth.models.AbstractUser`.
- `USERNAME_FIELD = 'email'` (identificação via e-mail institucional).
- Remoção do campo `username` padrão ou espelhamento automático do e-mail.
- Adição dos campos `role` (papel fixo: `'MOTORISTA'` ou `'PASSAGEIRO'`) e `academic_status` (vínculo acadêmico: `'PENDENTE'` ou `'ATIVA'`).

### Justificativa
O modelo `AbstractUser` fornece toda a infraestrutura madura do Django: hashing seguro de senhas (PBKDF2), gerenciamento de sessões, controle de tentativas de login e permissões nativas, eliminando código boilerplate. Configurar o e-mail como identificador primário desde a primeira migração é uma recomendação oficial do Django, evitando migrações complexas no futuro.

### Alternativas Consideradas
- **Modelo `OneToOneField` associado ao `User` padrão**: Rejeitado pois adiciona overhead de queries `JOIN`, necessita de signals `post_save` suscetíveis a falhas e mantém o campo `username` legado ativo.
- **`AbstractBaseUser` do zero**: Rejeitado por demandar reimplementação manual de gerenciadores de autenticação, permissões e campos básicos sem benefício para a PoC.

---

## 2. Diferenciação entre `academic_status` e `is_active` do Django

### Decisão
Manter `is_active = True` por padrão no Django para contas recém-criadas e utilizar o campo customizado de domínio `academic_status` para o ciclo de vida institucional:
- `is_active` (Booleano técnico do Django): Flag de habilitação da conta no framework de autenticação.
- `academic_status` (Domínio Carona Univille): Enum `PENDENTE` vs `ATIVA`.

### Justificativa
Se o campo `is_active` nativo do Django for definido como `False`, o framework impede qualquer autenticação e criação de sessão (`authenticate()` retorna `None`). Para que um usuário recém-cadastrado consiga efetuar login técnico e navegar até a interface de validação (`/ativacao/`), sua sessão precisa ser válida no Django. A restrição de acesso a caronas é, portanto, uma regra de negócio de autorização, e não de bloqueio de credenciais.

### Alternativas Consideradas
- **Utilizar `is_active = False` com ativação exclusivamente externa via e-mail/token**: Rejeitado pois exigiria infraestrutura de servidor SMTP funcional e impediria que o usuário realizasse a ativação simulada diretamente na interface da PoC web.

---

## 3. Controle de Acesso e Isolamento de Contas Pendentes (`AcademicStatusMiddleware`)

### Decisão
Implementar o middleware `accounts.middleware.AcademicStatusMiddleware`.
- **Visitantes não autenticados**: Ao tentarem acessar rotas protegidas, são redirecionados para `/login/`.
- **Usuários autenticados com `academic_status == 'PENDENTE'`**: Têm acesso liberado unicamente a uma lista de rotas autorizadas:
  - `/ativacao/` (tela e submissão de validação de vínculo institucional)
  - `/logout/` (encerramento da sessão)
  - URLs estáticas (`/static/*`)
  Qualquer tentativa de navegação para outras áreas do sistema (ex.: `/caronas/`, `/perfil/`, dashboard) é interceptada com redirecionamento HTTP 302 para `/ativacao/`, acompanhada de mensagem informativa.
- **Usuários com `academic_status == 'ATIVA'`**: Navegação irrestrita às funcionalidades permitidas para o seu papel.

### Justificativa
Centralizar o bloqueio no middleware garante conformidade incondicional com o Princípio I e com o `REQ-002`, evitando que novos endpoints no futuro esqueçam de adicionar verificações manuais de status.

### Alternativas Consideradas
- **Decorators de View (`@academic_active_required`) em cada view**: Rejeitado por introduzir risco de falha humana caso um desenvolvedor esqueça de anotar uma nova view.
- **Django Groups / Permissions nativas**: Rejeitado por adicionar complexidade de configuração sem ganho prático para um estado binário (`PENDENTE` / `ATIVA`).

---

## 4. Validação Institucional Simulada (Whitelist de Testes)

### Decisão
Implementar o serviço `AcademicValidationService` desacoplado, que consulta um catálogo de homologação de membros acadêmicos em formato JSON (`accounts/fixtures/academic_whitelist.json`).
- O serviço recebe o e-mail institucional e verifica sua presença e status no catálogo.
- Se o registro existir com status elegível, o serviço retorna sucesso e registra o evento em `AcademicValidationRecord`, atualizando `academic_status` para `'ATIVA'`.
- Se o e-mail não constar no catálogo ou estiver com status inelegível, a validação retorna falha e a conta permanece `'PENDENTE'`.

### Exemplos Concretos de Validação
- **Conta Elegível**: `joao.silva@univille.br` consta na whitelist como estudante com matrícula ativa $\rightarrow$ validação aprovada $\rightarrow$ status atualizado para `'ATIVA'`.
- **Conta Inelegível**: `visitante.externo@univille.br` possui domínio `@univille.br`, mas NÃO consta na whitelist $\rightarrow$ validação recusada $\rightarrow$ status permanece `'PENDENTE'`.

### Justificativa
Permite testes de aceitação 100% determinísticos, atende à decisão deliberada pela dupla (Opção B) e isola o mecanismo de validação para que possa ser substituído futuramente por um provedor OAuth2 ou LDAP real sem impacto no restante da aplicação.

### Alternativas Consideradas
- **Validação por código estático digitado em tela (ex.: "123456")**: Descartado pela dupla na rodada de clarificação em favor da whitelist mockada.
- **Regex no e-mail**: Descartado pois não permitiria testar rejeição de contas do mesmo domínio `@univille.br`.

---

## 5. Tratamento de Cadastro Duplicado e Mitigação de Enumeração de Usuários

### Decisão
No formulário de cadastro (`AcademicRegistrationForm`), quando um e-mail já cadastrado for submetido:
- A tentativa de inserção é rejeitada sem expor detalhes internos.
- A interface exibe a mensagem neutra: *"Não foi possível concluir o cadastro com os dados informados. Se você já possui vínculo cadastrado, tente fazer login."*
- O banco de dados mantém inalterado o registro original: o papel, a senha e o status (`academic_status`) anteriores permanecem estritamente preservados.

### Justificativa
Atende diretamente à deliberação da dupla (Opção B) e aos princípios de segurança defensiva da LGPD, impedindo que agentes maliciosos realizem enumeração para descobrir quais alunos ou professores utilizam a plataforma.

### Alternativas Consideradas
- **Mensagem direta "Este e-mail já existe"**: Rejeitada por permitir enumeração pública de membros cadastrados.

---

## 6. Infraestrutura de Banco de Dados e Testes

### Decisão
- **Banco de Dados**: PostgreSQL 15+ para ambiente local e testes de integração.
- **Suíte de Testes**: `pytest`, `pytest-django`, `pytest-cov`.
- Configuração do `pytest.ini` para carregar as configurações do Django e utilizar banco PostgreSQL de teste transacional.

### Justificativa
Cumpre a Constitution 1.1.0 e o Princípio II. O PostgreSQL é indispensável para validar transações ACID e bloqueios pessimistas (`select_for_update`), que serão mandatórios na feature seguinte (concorrência de reservas). Utilizar PostgreSQL nos testes garante paridade estrita de comportamento.
