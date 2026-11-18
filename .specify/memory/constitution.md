<!--
# Relatório de Impacto de Sincronização (Sync Impact Report)
- Mudança de versão: 1.0.0 -> 1.1.0 (Emenda de Governança - Definição da Stack Tecnológica Oficial)
- Princípios modificados / ampliados:
  - VI. Stack Oficial e Governança Evolutiva: homologação formal da stack técnica aprovada pela dupla (Python, Django, PostgreSQL, pytest, pytest-django, pytest-cov).
- Seções adicionadas / reestruturadas:
  - Stack Tecnológica Aprovada e Justificativa Arquitetural: formalização dos componentes de software, estratégias de autenticação/sessão e transações ACID para concorrência de reservas.
  - Histórico de Emendas à Constituição: registro formal de alterações conforme processo de governança.
- Resolução de Pendências:
  - TODO(STACK_TECNICA): Concluído e homologado.
- Pendências Mantidas:
  - TODO(VALIDACAO_ACADEMICA): Confirmação com o professor orientador quanto à validação simulada com dados fictícios.
  - TODO(DOMINIOS_INSTITUCIONAIS): Confirmação de subdomínios institucionais adicionais além de @univille.br.
  - TODO(REGRAS_MATCHING): Parâmetros exatos de rota e janela de horário (posterguem para a spec de caronas).
  - TODO(PRAZO_CANCELAMENTO): Prazos de cancelamento (posterguem para a spec de caronas).
-->

# Carona Univille Constitution

## Core Principles

### I. Acesso Acadêmico e Proteção de Dados (LGPD)
- **Restrição de Acesso**: O sistema DEVE ser de uso exclusivo da comunidade acadêmica da Univille (alunos, professores e funcionários). Toda conta DEVE possuir vínculo acadêmico validado e ativo para interagir com o sistema, seja no papel de motorista ou de passageiro.
- **Minimização de Dados (LGPD)**: O sistema DEVE coletar exclusivamente os dados estritamente necessários para a operação das caronas (identificação institucional, rota e horário). Dados sensíveis ou de localização contínua NÃO DEVEM ser coletados.
- **Transparência e Controle de Acesso**: Toda especificação funcional (spec) DEVE definir explicitamente quais papéis têm visibilidade sobre cada dado pessoal e de localização, bem como a finalidade explícita de tal exposição.
- **Dados Sintéticos em Testes e Demo**: Em todos os ambientes de desenvolvimento, testes automatizados e demonstrações, DEVEM ser utilizados unicamente dados fictícios/sintéticos. Dados reais de membros da comunidade acadêmica NUNCA DEVEM ser versionados ou empregados em testes.

### II. Integridade das Vagas e Concorrência
- **Prevenção Absoluta de Overbooking**: O sistema DEVE garantir integridade transacional mesmo sob condições de concorrência com requisições simultâneas. O total de reservas confirmadas NUNCA DEVE ultrapassar a capacidade de vagas ofertadas pelo motorista.
- **Garantia Transacional ACID**: As operações de reserva DEVEM utilizar transações atômicas com bloqueio pessimista ou controle estrito de concorrência no banco de dados relacional (PostgreSQL), serializando pedidos simultâneos para a última vaga.
- **Critérios de Aceite Verificáveis**: Toda especificação de reserva, matching e cancelamento DEVE conter critérios de aceite testáveis cobrindo:
  1. Concorrência na disputa pela última vaga disponível (garantindo que exatamente uma reserva seja confirmada e as excedentes rejeitadas sem inconsistências).
  2. Matching determinístico por rota (origem, destino e pontos de parada) e janela de horário de tolerância.
  3. Prazos e limites de cancelamento de reservas e ofertas.
  4. Cálculo de reputação e aplicação de penalidades por cancelamento tardio ou no-show (no escopo completo).

### III. Qualidade da Entrega e Testes Automatizados
- **Testes Automatizados Obrigatórios**: Todos os critérios de aceite descritos nas especificações DEVEM possuir testes automatizados correspondentes (abrangendo testes de unidade, integração e contratos de interface).
- **Cobertura Mínima de 80%**: A base de código DEVE manter cobertura de testes automatizados de no mínimo 80% em linhas e ramificações lógicas críticas de negócio.
- **Relatório Versionado**: O relatório de execução e cobertura de testes DEVE ser gerado via ferramentas padronizadas (`pytest-cov`) e mantido versionado no repositório a cada ciclo de entrega.
- **Visibilidade Contínua no README**: O topo do arquivo `README.md` DEVE obrigatoriamente exibir a quantidade real de testes executados com sucesso e o percentual exato medido de cobertura, devendo ser atualizados a cada entrega ou pull request.

### IV. Desenvolvimento Guiado por Especificação (Spec-Driven Development)
- **Ordem de Execução de Artefatos**: O desenvolvimento DEVE seguir rigorosamente a cadeia `Briefing & Decisões` → `spec.md` → `plan.md` → `tasks.md` → `Implementação`. Nenhum código de produção DEVE ser implementado sem uma task correspondente previamente descrita.
- **Alinhamento Prévio da Dupla**: Antes da elaboração da primeira especificação (`spec.md`), a dupla DEVE analisar o briefing, extrair os requisitos e documentar formalmente as perguntas levantadas e as decisões acordadas.
- **Papel dos Artefatos**:
  - `spec.md`: descreve o comportamento esperado do sistema e os critérios de aceite verificáveis, sem acoplamento a implementações técnicas.
  - `plan.md`: documenta a arquitetura técnica, modelo de dados, contratos de API e estratégia de suporte.
  - `tasks.md`: divide o plano em tarefas atômicas, sequenciadas e rastreáveis.
- **Reprodutibilidade do Sistema**: Os artefatos de especificação e planejamento DEVEM possuir detalhamento suficiente para permitir que qualquer desenvolvedor recrie o sistema do zero com fidelidade aos requisitos.

### V. Rastreabilidade Rigorosa e Histórico de Prompts
- **Rastreabilidade de Código e Commits**: Cada commit de implementação DEVE fazer referência explícita ao identificador da task entregue (ex.: `feat(T-001): ...`). Cada task DEVE obrigatoriamente referenciar os requisitos e critérios de aceite aos quais atende.
- **Auditoria de Prompts em `docs/prompts.md`**: É MANDATÓRIO registrar no arquivo `docs/prompts.md` o texto exato e integral de todo prompt enviado a agentes de IA, incluindo:
  - Comandos do Spec Kit (ex.: `/speckit-specify`, `/speckit-plan`).
  - Instruções de refinamento, revisão e correção.
  - O artefato produzido ou alterado em decorrência do comando.
  - O registro da decisão conjunta tomada pela dupla associada a essa ação, quando houver.

### VI. Stack Oficial e Governança Evolutiva
- **Adesão Estrita à Stack Homologada**: Todo o desenvolvimento DEVE utilizar exclusivamente a stack tecnológica aprovada e documentada nesta constitution (Python, Django, PostgreSQL e ecossistema pytest).
- **Sinalização Explícita de Pendências**: Decisões técnicas ou de negócio pendentes DEVEM constar formalmente nesta constitution com marcador de pendência, evitando presunções individuais.
- **Registro Histórico de Mudanças**: Qualquer alteração futura nesta constitution DEVE ser acompanhada de registro formal contendo data, autor(es), nova versão semântica e motivação detalhada da mudança.

---

## Escopo do Produto e Limites do Sistema

O sistema Carona Univille é concebido como uma Prova de Conceito (PoC) web para mobilidade acadêmica, estruturado nas seguintes faixas de escopo:

1. **Escopo Mínimo (MVP / Obrigatório)**:
   - Cadastro acadêmico com validação institucional e distinção de papéis (motorista e passageiro).
   - Oferta de caronas contendo ponto de origem, destino, horário de saída, número de vagas e pontos de parada intermediários.
   - Busca de caronas por compatibilidade de rota e janela de horário de tolerância.
   - Reserva de vagas com garantia transacional contra overbooking.
   - Cancelamento de reserva ou oferta com validação de prazo mínimo antecedente.

2. **Escopo Completo (Extensão)**:
   - Avaliação mútua entre motoristas e passageiros após a conclusão da viagem.
   - Mecanismo de penalidades e impacto na reputação por cancelamento tardio ou no-show (não comparecimento).
   - Oferta e reserva de caronas recorrentes (dias e horários fixos da semana).

3. **Bônus (Opcionais)**:
   - Notificações de confirmação, cancelamento e avisos operacionais.
   - Lista de espera automática para caronas lotadas, com reserva automática mediante desistência.

---

## Stack Tecnológica Aprovada e Justificativa Técnica

A dupla deliberou e homologou a seguinte stack tecnológica oficial para o projeto:

| Camada | Tecnologia Homologada | Justificativa Arquitetural e Técnica |
| :--- | :--- | :--- |
| **Aplicação Web / Backend** | **Python (3.12+) & Django** | Ecossistema maduro, seguro e altamente produtivo para desenvolvimento ágil orientado a especificações. O Django fornece ORM robusto com suporte a transações atômicas nativas (`transaction.atomic`), além de proteção integrada contra ameaças web comuns (CSRF, XSS, SQLi). |
| **Autenticação & Sessões** | **Django Auth & Sessions** | Utilização dos módulos nativos `django.contrib.auth` e `django.contrib.sessions`. Permite controle unificado de autenticação acadêmica, isolamento de estados (visitante, conta pendente e conta ativa) e gerenciamento de perfis sem dependência de bibliotecas externas complexas. |
| **Interface / Frontend** | **Templates Django (HTML5 + CSS)** | Renderização *server-side* sem a complexidade acidental de compilação de frameworks SPA (React/Vue). Garante entrega enxuta, alta performance de carregamento, simplicidade nos testes de aceitação e facilidade para live demo de 10 minutos. |
| **Banco de Dados / Persistência** | **PostgreSQL** | Sistema de gerenciamento de banco de dados relacional mandatório para produção e para os **testes de integração de concorrência**. Suporta transações estritas com isolamento ACID e bloqueios (`SELECT ... FOR UPDATE`), garantindo a integridade inegociável da última vaga e prevenção absoluta de overbooking (Princípio II). |
| **Testes Automatizados & Cobertura** | **pytest, pytest-django e pytest-cov** | Padrão da comunidade Python para testes expressivos, fixtures reutilizáveis e parametrização de cenários BDD/Gherkin. O `pytest-cov` garante a medição determinística da cobertura de testes (meta $\ge 80\%$) com relatórios estruturados e versionados. |

> [!IMPORTANT]
> O **PostgreSQL** é componente obrigatório da infraestrutura de testes de integração, especialmente para a suíte que validará o comportamento transacional sob requisições concorrentes na disputa de vagas (requisito do escopo mínimo).

---

## Diretrizes Técnicas e Decisões Pendentes da Dupla

As seguintes decisões de governança e de negócio permanecem registradas como **PENDENTES**:

1. **TODO(VALIDACAO_ACADEMICA)**:
   - *Status*: PENDENTE (Aguardando confirmação do professor orientador).
   - *Descrição*: Homologação formal com o docente responsável para confirmar se a abordagem de validação simulada com whitelist de contas fictícias atende integralmente à restrição de acesso acadêmico estipulada no briefing da disciplina.

2. **TODO(DOMINIOS_INSTITUCIONAIS)**:
   - *Status*: PENDENTE (Aguardando confirmação da dupla).
   - *Descrição*: Definição se a restrição institucional considerará estritamente o domínio `@univille.br` ou se admitirá também subdomínios institucionais adicionais (ex.: `@univille.edu.br`).

3. **TODO(REGRAS_MATCHING)**:
   - *Status*: PENDENTE (Aguardando especificação da Feature de Caronas).
   - *Descrição*: Parâmetros do algoritmo de matching de rotas (lista de marcos/bairros discretos vs. raio geográfico) e intervalo de tolerância da janela de horário ($\pm 30$ min).

4. **TODO(PRAZO_CANCELAMENTO)**:
   - *Status*: PENDENTE (Aguardando especificação da Feature de Caronas).
   - *Descrição*: Prazos mínimos antecedentes para cancelamento sem penalidades (proposta de 2h para passageiro e 4h para motorista, com critério de borda inclusivo).

---

## Governança do Projeto

- **Supremacia Constitucional**: As diretrizes desta constitution têm autoridade soberana sobre qualquer código, ferramenta ou preferência individual. PRs e artefatos em desconformidade NÃO DEVEM ser aceitos.
- **Processo de Emenda**: Alterações a esta constitution exigem consenso prévio da dupla e atualização de versão segundo versionamento semântico:
  - **MAJOR**: Alterações ou remoções incompatíveis de princípios ou escopo essencial.
  - **MINOR**: Inclusão de novos princípios, resolução de decisões arquiteturais pendentes (ex.: definição da stack) ou ampliação de diretrizes.
  - **PATCH**: Correções de grafia, formatação e esclarecimentos sem alteração de regra de negócio.
- **Validação de Conformidade**: Cada ciclo de especificação, planejamento e revisão de código deve auditar o alinhamento com os princípios aqui estabelecidos.

### Histórico de Emendas à Constituição

| Versão | Data (ISO) | Autor(es) | Tipo de Mudança | Justificativa / Resumo |
| :---: | :---: | :---: | :---: | :--- |
| **1.0.0** | 2026-11-18 | Dupla Trilha 2 | Ratificação Inicial | Criação da constitution com os 6 princípios norteadores, escopo e governança inicial. |
| **1.1.0** | 2026-11-18 | Dupla Trilha 2 | Minor Bump | Homologação da stack técnica oficial (Python, Django, PostgreSQL, pytest, pytest-django, pytest-cov), detalhamento da arquitetura de concorrência com PostgreSQL e preservação das pendências acadêmicas. |

---

**Version**: 1.1.0 | **Ratified**: 2026-11-18 | **Last Amended**: 2026-11-18
