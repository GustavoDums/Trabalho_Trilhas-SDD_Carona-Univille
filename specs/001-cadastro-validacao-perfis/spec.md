# Feature Specification: Cadastro Acadêmico, Validação de Vínculo e Perfis

**Feature Branch**: `001-cadastro-validacao-perfis`  
**Created**: 2026-11-18  
**Status**: Draft  
**Input**: User description: "Cadastro Acadêmico, Validação de Vínculo e Perfis para a PoC Carona Univille, com regras de minimização LGPD, validação simulada e controle de acesso para contas pendentes."

---

## Contexto e Rastreabilidade de Requisitos

Esta especificação define o comportamento observável da funcionalidade inicial do **Carona Univille**, correspondendo à porta de entrada da plataforma (identidade e acesso).

As regras aqui estabelecidas implementam diretamente os seguintes requisitos formais do [Levantamento de Requisitos](file:///docs/levantamento.md) e da [Constitution](file:///.specify/memory/constitution.md):
- **REQ-001 (Cadastro Acadêmico e Papéis)**: Cadastro exclusivo para membros da Univille com distinção de papéis iniciais (motorista e passageiro).
- **REQ-002 (Validação de Vínculo Institucional)**: Restrição de uso à comunidade com vínculo comprovado e controle de acesso para contas não ativadas.
- **REQ-003 (Privacidade e Minimização - LGPD)**: Coleta estrita dos dados mínimos necessários para a PoC, transparência de visibilidade e finalidade, além de dados estritamente fictícios nos testes.

> [!NOTE]
> As funcionalidades de **Oferta de Caronas** (`REQ-004`), **Busca por Rota e Horário** (`REQ-005`), **Reserva sem Overbooking** (`REQ-006`) e **Cancelamento com Prazo Mínimo** (`REQ-007`) são dependentes desta especificação e serão detalhadas na próxima spec do escopo mínimo.

---

## Clarifications

### Session 2026-11-22 — T008
- Q: Como o usuário aciona a validação de vínculo? → A: Botão único “Validar Vínculo Institucional”, sem campos adicionais. A validação usa exclusivamente o e-mail da sessão autenticada; e-mails ou identificadores enviados no POST não selecionam outra conta. Confirmado pelo usuário. Aprovação redireciona ao perfil; recusa mantém a tela e o estado PENDENTE, com auditoria em ambos os casos.

### Session 2026-11-22 — T004
- Q: O cadastro inicial deve incluir senha e confirmação? → A: Sim. O usuário confirmou a inclusão de `password` e `password_confirm`, ambos obrigatórios, com validação de igualdade e os validadores de senha configurados no Django. Esses campos são credenciais técnicas adicionais aos dados acadêmicos mínimos de FR-001; a confirmação não é persistida e a senha é armazenada somente como hash. Na T005, o usuário confirmou em 2026-11-22 o redirecionamento para /accounts/login/ sem autenticação automática.

### Session 2026-11-18
- Q: Quais campos compõem o formulário de cadastro nesta primeira versão? → A: Apenas nome completo, e-mail institucional e a seleção de um papel inicial (motorista ou passageiro). Matrícula, telefone, placa e dados do veículo foram postergados para preservar a minimização de dados (LGPD).
- Q: Como tratar a duplicidade de papéis (usuário motorista e passageiro)? → A: Na v1, cada conta é associada a um único papel inicial. A capacidade de atuação híbrida (mesmo usuário atuar como motorista e passageiro) permanece como decisão em aberto para deliberação da dupla.
- Q: O domínio de e-mail `@univille.br` ativa automaticamente o usuário? → A: Não. O domínio `@univille.br` é apenas uma pré-condição de formato para submissão cadastral. Toda conta recém-criada assume o status `Pendente` e só atinge o status `Ativa` após a conclusão bem-sucedida do fluxo de validação de vínculo institucional.
- Q: Como funciona a validação institucional na PoC? → A: Por meio de um fluxo de validação simulado com dados acadêmicos fictícios. Foi registrado que a dupla deve obter a confirmação do professor orientador sobre a aderência dessa simulação ao briefing da disciplina.
- Q: Como distinguir uma conta acadêmica fictícia elegível de uma inelegível quando ambas usam o domínio aceito @univille.br? → A: O simulador de validação de vínculo acadêmico utiliza uma lista prévia de homologação (whitelist de testes com registros mockados). E-mails institucionais fictícios presentes na lista são validados com sucesso (elegíveis); e-mails institucionais fora da lista são rejeitados pelo simulador com vínculo não comprovado (inelegíveis).
- Q: A conta de usuário terá um papel fixo no MVP ou poderá atuar nos dois papéis na mesma conta? → A: Papel fixo no MVP (Opção A). Cada conta acadêmica cadastrada pertence exclusivamente a um único papel (Motorista OU Passageiro), selecionado no cadastro e imutável durante o MVP. Para a PoC e testes dos dois fluxos, são utilizadas contas distintas da whitelist. A atuação híbrida fica postergada para evolução futura.
- Q: Quem tem permissão para visualizar o nome completo e o e-mail institucional de um usuário na plataforma? → A: Visibilidade em camadas (LGPD estrita - Opção A). Em buscas abertas e listagens públicas, exibe-se apenas o primeiro nome e inicial do sobrenome (ex.: "Lucas A."). O nome completo é revelado à contraparte exclusivamente após a confirmação de uma reserva de carona. O e-mail institucional é estritamente confidencial, não sendo exibido a outros usuários em nenhuma hipótese.
- Q: Qual comportamento observável o sistema deve apresentar quando houver uma tentativa de cadastro com um e-mail institucional que já possui conta registrada? → A: Resposta neutra e genérica (Opção B). O sistema rejeita a criação da conta e exibe mensagem neutra: "Não foi possível concluir o cadastro com os dados informados. Se você já possui vínculo cadastrado, tente fazer login", sem confirmar explicitamente se o endereço já existe na base de dados, prevenindo enumeração de usuários e respeitando a privacidade.

---

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Cadastro Inicial com Papel Acadêmico (Priority: P1)

Como membro da comunidade acadêmica da Univille, quero realizar meu cadastro informando meu nome, meu e-mail institucional e meu papel desejado (motorista ou passageiro), para que eu possa iniciar o processo de acesso à plataforma de caronas.

**Why this priority**: É a porta de entrada indispensável para qualquer interação com o sistema. Sem a criação da identidade acadêmica, nenhuma outra funcionalidade pode ser utilizada.

**Independent Test**: Pode ser testado de forma totalmente autônoma preenchendo o formulário de cadastro e verificando a criação da conta com os dados fornecidos e status `Pendente`, sem depender de nenhum fluxo de carona.

**Acceptance Scenarios**:

1. **Cenário 1.1 — Cadastro com sucesso no papel Passageiro (REQ-001, REQ-003)**:
   - **Dado** que um estudante não cadastrado acessa a tela de cadastro,
   - **Quando** preenche o nome "Lucas Aluno", o e-mail institucional "lucas.aluno@univille.br" e seleciona o papel "Passageiro",
   - **Então** o sistema cria o registro da conta com status `Pendente`,
   - **E** exibe uma mensagem de confirmação de cadastro orientando o usuário a realizar a validação de seu vínculo institucional para ativar a conta.

2. **Cenário 1.2 — Cadastro com sucesso no papel Motorista (REQ-001, REQ-003)**:
   - **Dado** que um colaborador não cadastrado acessa a tela de cadastro,
   - **Quando** preenche o nome "Mariana Motorista", o e-mail institucional "mariana.motorista@univille.br" e seleciona o papel "Motorista",
   - **Então** o sistema cria o registro da conta com status `Pendente`,
   - **E** exibe uma mensagem de confirmação de cadastro orientando a usuária a concluir a validação de vínculo acadêmico.

3. **Cenário 1.3 — Rejeição de cadastro com e-mail fora do domínio acadêmico aceito (REQ-001, REQ-002)**:
   - **Dado** que um visitante acessa a tela de cadastro,
   - **Quando** tenta cadastrar o nome "Carlos Visitante", o e-mail pessoal "carlos@gmail.com" e qualquer papel,
   - **Então** o sistema bloqueia o envio do formulário,
   - **E** exibe uma mensagem de erro indicando que o acesso é restrito à comunidade acadêmica e que é obrigatório o uso de e-mail institucional `@univille.br`.

---

### User Story 2 - Validação de Vínculo e Ativação de Conta (Priority: P2)

Como usuário acadêmico cadastrado com conta pendente, quero realizar o procedimento de validação de vínculo institucional (simulado para a PoC), para que minha conta se torne ativa e eu possa ter acesso às funcionalidades do meu papel no Carona Univille.

**Why this priority**: Garante o cumprimento do Princípio I da Constitution e do REQ-002, assegurando que apenas membros com vínculo institucional comprovado possam participar de caronas.

**Independent Test**: Pode ser testado isoladamente fornecendo entradas válidas e inválidas para contas com status `Pendente`, validando a transição de estado para `Ativa` ou a manutenção do bloqueio.

**Acceptance Scenarios**:

1. **Cenário 2.1 — Ativação bem-sucedida para conta elegível no ambiente simulado (REQ-002)**:
   - **Dado** que existe uma conta de passageiro ou motorista com status `Pendente` cujo e-mail institucional consta na lista de homologação acadêmica da PoC (whitelist de testes),
   - **Quando** o usuário executa o fluxo de validação de vínculo acadêmico,
   - **Então** o sistema valida positivamente o vínculo institucional via simulador,
   - **E** atualiza o status da conta de `Pendente` para `Ativa`,
   - **E** exibe mensagem de boas-vindas liberando o acesso ao ambiente operacional correspondente ao seu papel.

2. **Cenário 2.2 — Falha na validação de vínculo sem liberação de acesso (REQ-002)**:
   - **Dado** que existe uma conta com status `Pendente` cujo e-mail institucional NÃO consta na lista de homologação acadêmica da PoC (inelegível na whitelist),
   - **Quando** o usuário tenta executar a validação de vínculo,
   - **Então** o sistema recusa a ativação,
   - **E** informa que o vínculo institucional não pôde ser comprovado,
   - **E** mantém o status da conta como `Pendente`, sem conceder acesso às áreas protegidas de caronas.

---

### User Story 3 - Controle de Acesso e Restrição de Contas Pendentes (Priority: P3)

Como sistema de carona acadêmico, quero controlar o acesso com base no estado do usuário (visitante, conta pendente ou conta ativa), garantindo que apenas membros com vínculo ativado interajam com as funcionalidades de carona correspondentes ao seu papel.

**Why this priority**: Evita que visitantes ou usuários não homologados consigam interagir com rotas, motoristas ou passageiros, garantindo ao mesmo tempo que contas ativas acessem seus recursos operacionais com segurança.

**Independent Test**: Pode ser testado tentando navegar para rotas públicas e protegidas simulando os três estados de usuário: visitante anônimo, usuário com conta `Pendente` e usuário com conta `Ativa`.

**Acceptance Scenarios**:

1. **Cenário 3.1 — Tentativa de acesso a funcionalidades com conta pendente (REQ-002, REQ-003)**:
   - **Dado** que um usuário autenticado possui sua conta com status `Pendente`,
   - **Quando** tenta acessar qualquer funcionalidade de carona (como consultar rotas, ofertar carona ou visualizar dados da comunidade),
   - **Então** o sistema intercepta a requisição,
   - **E** impede a visualização de qualquer dado de caronas ou usuários,
   - **E** redireciona o usuário compulsoriamente para a tela com instruções e ações de ativação de vínculo acadêmico.

2. **Cenário 3.2 — Acesso autorizado para conta com vínculo ativo (REQ-001, REQ-002)**:
   - **Dado** que um usuário autenticado possui sua conta com status `Ativa` com o papel "Passageiro" (ou "Motorista"),
   - **Quando** acessa a plataforma de caronas,
   - **Então** o sistema concede acesso imediato ao painel principal e às funcionalidades permitidas para o seu papel (busca e reserva de vagas para passageiro; criação e gestão de ofertas para motorista),
   - **E** exibe seu perfil acadêmico com indicador de vínculo validado.

3. **Cenário 3.3 — Tentativa de acesso direto por visitante não autenticado (REQ-002)**:
   - **Dado** que um visitante anônimo (não autenticado) tenta acessar diretamente uma página interna de caronas ou perfil,
   - **Quando** a requisição é processada,
   - **Então** o sistema bloqueia o acesso ao conteúdo protegido,
   - **E** redireciona o visitante para a página de identificação (login / cadastro institucional).

---

### Edge Cases

- **Tentativa de cadastro com e-mail já cadastrado**: O sistema deve recusar o cadastro emitindo uma mensagem neutra e genérica ("Não foi possível concluir o cadastro com os dados informados. Se você já possui vínculo cadastrado, tente fazer login"), sem confirmar a existência prévia do e-mail na base, prevenindo enumeração de contas e vazamento de informações.
- **Campos com espaços em branco ou vazios**: O formulário deve exigir que o nome completo contenha pelo menos dois termos (prenome e sobrenome) e rejeitar envios com strings vazias ou formadas apenas por espaços.
- **Formato inválido antes do domínio**: Submissões como `@univille.br` ou `nome..invalido@univille.br` devem ser interceptadas com erro de validação sintática antes de qualquer tentativa de persistência.
- **Tentativa de validação repetida de conta já ativa**: Se um usuário com conta `Ativa` tentar acionar novamente o fluxo de ativação, o sistema deve informar que sua conta já está ativada e direcioná-lo ao painel principal do seu papel.

---

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: O sistema DEVE permitir a criação de novas contas acadêmicas solicitando exclusivamente: Nome Completo, E-mail Institucional e Papel Inicial (Motorista ou Passageiro). *(Rastreabilidade: REQ-001, REQ-003)*
- **FR-002**: O sistema DEVE validar sintaticamente que o endereço de e-mail informado pertença ao domínio institucional proposto `@univille.br`, rejeitando qualquer outro domínio com mensagem explicativa. *(Rastreabilidade: REQ-001, REQ-002)*
- **FR-003**: Toda nova conta criada DEVE assumir compulsoriamente o status inicial `Pendente`. *(Rastreabilidade: REQ-002)*
- **FR-004**: O sistema DEVE disponibilizar um fluxo simulado de validação de vínculo acadêmico para fins de demonstração da PoC, operando sobre uma lista predefinida (whitelist de testes) de registros institucionais fictícios elegíveis. E-mails constantes na whitelist têm sua validação aprovada; e-mails ausentes são recusados como inelegíveis. *(Rastreabilidade: REQ-002, Princípio I)*
- **FR-005**: O sistema DEVE transicionar o status da conta para `Ativa` apenas após a confirmação satisfatória do vínculo acadêmico na validação simulada. *(Rastreabilidade: REQ-002)*
- **FR-006**: O sistema DEVE bloquear o acesso de qualquer conta com status `Pendente` a funcionalidades de busca, oferta ou reserva de caronas, mantendo o usuário confinado à interface de ativação. *(Rastreabilidade: REQ-002)*
- **FR-007**: O sistema DEVE garantir a unicidade de cadastro por e-mail institucional, impedindo contas duplicadas e emitindo mensagem neutra e genérica em caso de tentativa de duplicidade, sem expor a existência prévia do registro. *(Rastreabilidade: REQ-001, REQ-003)*
- **FR-008**: No escopo do MVP, cada conta DEVE estar associada exclusivamente a um único papel imutável (`Motorista` OU `Passageiro`), definido no cadastro. A alternância dinâmica de papéis na mesma conta é vedada no MVP. *(Rastreabilidade: REQ-001)*

---

### Key Entities

- **ContaAcademica**:
  - *Identificador Único*: Referência única da conta.
  - *NomeCompleto*: Nome do membro acadêmico (mínimo de prenome e sobrenome).
  - *EmailInstitucional*: Endereço corporativo/acadêmico terminado no domínio aceito (`@univille.br`).
  - *Papel*: Papel inicial selecionado (`Motorista` ou `Passageiro`).
  - *StatusConta*: Estado de validação do cadastro (`Pendente` ou `Ativa`).
  - *DataCriacao*: Data e hora de submissão do cadastro.
- **RegistroValidacaoVinculo**:
  - *Identificador*: Referência do evento de validação.
  - *ContaReferenciada*: Associação à ContaAcademica.
  - *ResultadoSimulacao*: Indicador do resultado do teste de vínculo (`Aprovado` ou `Recusado`).
  - *DataProcessamento*: Registro temporal da validação simulada.

---

### Privacidade e Governança de Dados (LGPD)

Em estrita consonância com o **Princípio I da Constitution** e o **REQ-003**, os dados coletados nesta funcionalidade possuem finalidades e visibilidades claramente delimitadas:

| Dado Coletado | Finalidade de Coleta | Visibilidade / Acesso | Justificativa de Minimização (LGPD) |
| :--- | :--- | :--- | :--- |
| **Nome Completo** | Identificação do usuário na comunidade acadêmica e segurança interpessoal. | Visível publicamente apenas como primeiro nome e inicial do sobrenome (ex.: "Lucas A."). Nome completo acessível apenas internamente ou após reserva confirmada na carona. | Evita exposição desnecessária na fase de navegação aberta. |
| **E-mail Institucional** | Comprovação do vínculo institucional Univille e canal de ativação/segurança. | Privado. Não é exibido em buscas públicas ou listagens gerais. | Protege a privacidade contra varreduras e spam; usado unicamente para vínculo e autenticação. |
| **Papel Selecionado** | Configuração dos fluxos de tela e permissões (motorista ou passageiro). | Público dentro do contexto de uso da plataforma. | Dado estritamente operacional indispensável para o modelo de caronas. |
| **Matrícula / Telefone / Veículo** | *Fora do escopo inicial da v1.* | Não coletados nesta funcionalidade. | Respeito à minimização estrita da v1; telefone e dados do veículo serão coletados no momento apropriado (ao cadastrar carona ou confirmar reserva). |

---

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das submissões de cadastro com e-mails pertencentes a domínios não acadêmicos são rejeitadas antes de qualquer gravação ou avanço de fluxo.
- **SC-002**: 100% das contas recém-criadas iniciam compulsoriamente com o status `Pendente`, com 0% de vazamento de acesso a funcionalidades operacionais de caronas antes da ativação.
- **SC-003**: No ambiente de demonstração da PoC, um usuário acadêmico fictício consegue concluir o preenchimento do cadastro inicial e a validação simulada em menos de 1 minuto.
- **SC-004**: 100% dos cenários de teste automatizados para critérios de aceite dos papéis Motorista e Passageiro executam com dados fictícios garantidos (zero dependência de dados reais).

---

## Assumptions

- **Ambiente de Demonstração e Testes**: A validação de vínculo institucional será demonstrada com cenários pré-configurados de contas fictícias elegíveis e inelegíveis no ambiente de teste/demo.
- **Domínio Institucional Primário**: Assume-se o domínio `@univille.br` como o padrão para a comunidade acadêmica (docentes, discentes e colaboradores). A inclusão de subdomínios como `@univille.edu.br` pode ser incorporada caso deliberado pela dupla.
- **Exclusividade de Papel na v1**: Assume-se temporariamente que um usuário escolhe um único papel no cadastro, postergando a alternância dinâmica de papéis para uma revisão futura.
- **Faseamento de Dados do Veículo**: Assume-se que o motorista não precisa cadastrar veículo no momento da criação da conta, apenas quando for efetivamente publicar uma oferta de carona (próxima spec).

---

## Decisões Pendentes de Confirmação da Dupla e do Professor

Antes do início da fase de planejamento técnico (`plan.md`) e da implementação, os seguintes pontos permanecem formalmente registrados como pendentes de deliberação:

1. **Confirmação com o Professor Orientador**:
   - *Ponto*: A validação simulada de vínculo institucional com contas e dados fictícios atende integralmente à restrição de acesso acadêmico estipulada no enunciado da Trilha 2?
   - *Status*: `Pendente de alinhamento com o professor`.
2. **Confirmação do Domínio Institucional Aceito**:
   - *Ponto*: O domínio aceito no cadastro deve ser exclusivamente `@univille.br` ou deve aceitar também `@univille.edu.br` e/ou outros subdomínios da instituição?
   - *Status*: `Pendente de decisão da dupla`.
3. **Evolução para Perfil Híbrido (Dois Papéis na Mesma Conta)**:
   - *Ponto*: A versão seguinte deve permitir que um mesmo usuário transite livremente entre os papéis de motorista e passageiro mantendo o mesmo cadastro?
   - *Status*: `Decidido pela dupla para o MVP (Papel Fixo por Conta - Opção A) | Evolução para perfil híbrido postergada para pós-MVP`.
4. **Momento de Coleta do Telefone / WhatsApp**:
   - *Ponto*: O telefone para coordenação de embarque deve ser solicitado na ativação do perfil ou apenas na primeira reserva/oferta de carona?
   - *Status*: `Pendente de decisão da dupla`.
