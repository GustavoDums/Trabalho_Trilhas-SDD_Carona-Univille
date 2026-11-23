# Trilha 2 — Carona Univille: Levantamento de Requisitos e Decisões Prévias

Este documento formaliza o levantamento de requisitos funcionais, não funcionais e de governança para o projeto **Carona Univille** (Prova de Conceito web para a comunidade acadêmica da Univille), elaborado no âmbito da Trilha 2 de *Spec-Driven Development* (SDD).

As definições aqui contidas estão estritamente alinhadas aos princípios da [Constitution do Projeto](file:///.specify/memory/constitution.md) e ao briefing oficial da trilha.

---

## 1. Quadro Consolidado de Requisitos

Cada requisito possui um identificador estável (`REQ-xxx`), a cláusula de sustentação no briefing e o seu enquadramento de escopo.

### 1.1. Escopo Mínimo (MVP — Obrigatório)

| ID | Título | Cláusula do Briefing / Constitution | Descrição do Requisito |
| :--- | :--- | :--- | :--- |
| **REQ-001** | Cadastro Acadêmico e Papéis | *"cadastro com os papéis motorista e passageiro"* | O sistema DEVE permitir o cadastro de membros da comunidade acadêmica da Univille, viabilizando a atuação nos papéis de motorista e passageiro. |
| **REQ-002** | Validação de Vínculo Institucional | *"A plataforma é restrita à comunidade acadêmica, com cadastro validado."* | O acesso e a participação em caronas DEVEM ser condicionados à validação de vínculo acadêmico ativo (alunos, docentes ou técnicos da Univille). |
| **REQ-003** | Privacidade e Minimização (LGPD) | *"Dados pessoais e de localização devem seguir a LGPD."* / Princípio I | A coleta de dados pessoais e de localização DEVE ser estritamente mínima. A visualização de dados de contato e itinerário sensível deve respeitar níveis de acesso por papel. Testes e demonstrações DEVEM utilizar unicamente dados fictícios. |
| **REQ-004** | Oferta de Caronas | *"oferta com origem, destino, horário, vagas e pontos de parada"* | O motorista DEVE conseguir cadastrar uma oferta de carona contendo: ponto de origem, destino final, data/horário de saída, capacidade de vagas e pontos de parada intermediários ao longo do percurso. |
| **REQ-005** | Busca por Rota e Horário | *"busca por rota e janela de horário"* | O passageiro DEVE conseguir buscar caronas especificando ponto de embarque, ponto de desembarque e uma janela de horário desejada. |
| **REQ-006** | Reserva sem Overbooking sob Concorrência | *"reserva sem overbooking"* / *"limite de vagas sob reservas simultâneas"* / Princípio II | O sistema DEVE garantir controle estrito de concorrência e integridade transacional: mesmo com múltiplos pedidos simultâneos para a última vaga, a capacidade ofertada NUNCA DEVE ser excedida. |
| **REQ-007** | Cancelamento com Prazo Mínimo | *"cancelamento com prazo mínimo"* / *"prazos de cancelamento"* | Motoristas e passageiros DEVEM poder cancelar caronas ou reservas com base em um prazo antecedente mínimo regulamentar, respeitando regras de horário limite. |

### 1.2. Escopo Completo (Extensão)

| ID | Título | Cláusula do Briefing / Constitution | Descrição do Requisito |
| :--- | :--- | :--- | :--- |
| **REQ-008** | Avaliação Mútua Pós-Viagem | *"avaliação mútua após a viagem"* | Após a conclusão do horário previsto da carona, motorista e passageiros confirmados DEVEM poder registrar avaliação recíproca com nota quantitativa e comentário descritivo opcional. |
| **REQ-009** | Cálculo Determinístico de Reputação | *"cálculo de reputação"* / Princípio II | O sistema DEVE calcular a reputação de cada usuário de forma pública, matemática e transparente, atualizando-a a cada avaliação recebida ou infração computada. |
| **REQ-010** | Penalidades por Cancelamento Tardio e No-Show | *"penalidade por cancelamento tardio e no-show"* | O sistema DEVE registrar cancelamentos fora do prazo mínimo e faltas sem aviso prévio (*no-show*), aplicando penalidades automáticas na pontuação de reputação ou bloqueio temporário de ações. |
| **REQ-011** | Caronas Recorrentes | *"caronas recorrentes"* | O motorista DEVE poder configurar ofertas de carona recorrentes (ex.: segundas e quartas no mesmo horário), gerando instâncias de carona de forma programada e independente. |

### 1.3. Bônus da Trilha (Diferenciais)

| ID | Título | Cláusula do Briefing / Constitution | Descrição do Requisito |
| :--- | :--- | :--- | :--- |
| **REQ-012** | Sistema de Notificações | *"Bônus da trilha: notificações"* | O sistema DEVE enviar avisos visuais ou por mensagens sobre eventos críticos: confirmação de reserva, cancelamento pelo motorista/passageiro e lembrete antes da partida. |
| **REQ-013** | Fila de Espera Automática | *"Bônus da trilha: ... e lista de espera automática quando uma vaga é liberada."* | Quando todas as vagas de uma carona estiverem ocupadas, passageiros interessados DEVEM poder entrar em uma lista de espera. Caso haja cancelamento, a vaga DEVE ser repassada automaticamente ao próximo passageiro da fila (ordem FIFO). |

### 1.4. Exigências Gerais de Entrega e Engenharia de Software

| ID | Título | Cláusula do Briefing / Constitution | Descrição do Requisito |
| :--- | :--- | :--- | :--- |
| **REQ-014** | Artefatos Formais SDD | *"A entrega pede constitution, specs, plans e tasks"* / Princípio IV | O ciclo de desenvolvimento DEVE seguir rigorosamente a metodologia Spec-Driven Development: Levantamento/Decisões → `spec.md` → `plan.md` → `tasks.md` → Implementação. |
| **REQ-015** | Rastreabilidade Bidirecional | *"rastreabilidade commit → task → requisito"* / Princípio V | Todo commit de código DEVE referenciar a task correspondente (`feat(T-xxx): ...`), e toda task DEVE apontar formalmente para o requisito (`REQ-xxx`) que atende. |
| **REQ-016** | Registro de Auditoria de Prompts | Princípio V da Constitution | O arquivo `docs/prompts.md` DEVE conter o registro textual idêntico de todos os prompts, comandos e instruções submetidos a assistentes de IA, associados aos artefatos gerados e às decisões da dupla. |
| **REQ-017** | Testes Automatizados dos Critérios de Aceite | *"testes automatizados dos critérios de aceite"* / Princípio III | Os critérios de aceite críticos (concorrência na última vaga, matching de rota/horário, prazos de cancelamento e reputação) DEVEM possuir testes automatizados ponta a ponta/integração. |
| **REQ-018** | Cobertura Mínima de 80% e Relatório | *"cobertura mínima de 80% com relatório versionado"* / Princípio III | A suíte de testes DEVE cobrir no mínimo 80% das linhas e caminhos lógicos do código de produção, com o relatório analítico mantido versionado no repositório. |
| **REQ-019** | Indicadores de Qualidade no README | *"quantidade de testes e cobertura no início do README"* / Princípio III | O topo do arquivo `README.md` DEVE apresentar a contagem real de testes bem-sucedidos e o percentual exato medido de cobertura, atualizados a cada entrega. |
| **REQ-020** | Apresentação em Pitch com Live Demo | *"pitch com demo ao vivo de até 10 minutos, sem código nos slides."* | A entrega final DEVE contemplar um pitch de até 10 minutos com demonstração ao vivo da plataforma em funcionamento, sendo vedada a exibição de código-fonte nos slides de suporte. |

---

## 2. Registro de Perguntas em Aberto e Propostas Técnicas

Abaixo estão detalhadas as dúvidas e definições em aberto que necessitam de alinhamento pela dupla antes ou durante as etapas de especificação e planejamento técnico.

### Pergunta 1: Comprovação do Vínculo Acadêmico e Validação Simulada
- **Contexto**: A plataforma é de uso exclusivo da comunidade da Univille, mas trata-se de uma Prova de Conceito (PoC) acadêmica com dados fictícios.
- **Dúvida**: Como comprovar o vínculo acadêmico no cadastro e se uma validação simulada com dados fictícios precisa de confirmação/validação prévia do professor?
- **Proposta**:
  1. *Regra de Cadastro*: Exigir que o e-mail cadastrado possua domínio oficial da instituição (`@univille.br` ou `@univille.edu.br`).
  2. *Validação Simulada (PoC)*: Implementar um serviço mock de validação onde o sistema gera um código/token de ativação (visível em console de depuração, log ou em tela de ativação de teste), dispensando a necessidade de integração com servidores reais da Univille.
  3. *Alinhamento com o Professor*: Consultar o docente para homologar formalmente que a validação baseada em mock + e-mail `@univille.br` atende integralmente aos critérios de avaliação da Trilha 2, mantendo aderência ao Princípio I (dados estritamente fictícios).
- **Exemplo Concreto**: O usuário preenche nome `Ana Silva`, matrícula `202401999` e e-mail `ana.silva@univille.br`. O sistema valida a terminação do e-mail institucional. Na validação de vínculo simulada, se `ana.silva@univille.br` constar na whitelist de testes da PoC, a conta é ativada. Se cadastrar `visitante@univille.br` (inexistente na whitelist), a validação falha e a conta permanece `Pendente`.
- **Decisão da Dupla (Sessão 2026-11-18)**: Adotada a **Opção B (Whitelist de Testes)**: a diferenciação determinística entre contas acadêmicas elegíveis e inelegíveis para a PoC será feita via lista predefinida de e-mails/registros mockados de teste.
- **Status**: `Decidido pela dupla (Opção B) | Pendente de confirmação com o professor`

---

### Pergunta 2: Atuação nos Dois Papéis (Motorista e Passageiro)
- **Contexto**: Estudantes e colaboradores da universidade podem ofertar carona em alguns dias e buscar carona em outros.
- **Dúvida**: A mesma pessoa pode atuar nos dois papéis com a mesma conta de usuário?
- **Proposta**:
  1. *Conta Única com Papéis Híbridos*: O usuário cadastra-se uma única vez e possui um perfil com capacidades de Motorista e de Passageiro. Para ativar o modo motorista, deve registrar previamente os dados básicos do veículo (modelo, cor e placa fictícia).
  2. *Incompatibilidades Temporais e Integridade*:
     - Um usuário NUNCA PODE reservar vaga em uma carona ofertada por ele mesmo.
     - Um usuário NÃO DEVE poder confirmar reserva como passageiro em uma carona cujo horário coincida ou se sobreponha a uma carona em que ele já esteja atuando como motorista ou passageiro.
- **Exemplo Concreto**: Lucas cadastra-se no sistema selecionando o papel "Motorista" para ofertar caronas na PoC. Para testar o papel "Passageiro", a dupla utiliza outra conta mockada da whitelist (ex.: `mariana@univille.br`). A alternância dinâmica de papéis na mesma conta é vedada no MVP para garantir simplicidade e foco na integridade das reservas.
- **Decisão da Dupla (Sessão 2026-11-18)**: Adotada a **Opção A (Papel fixo no MVP)**: cada conta é criada com um papel imutável (motorista OU passageiro). A capacidade híbrida fica postergada como evolução pós-MVP.
- **Status**: `Decidido pela dupla (Opção A — Papel fixo no MVP) | Evolução híbrida postergada`

---

### Pergunta 3: Algoritmo de Matching (Rota, Ordem das Paradas e Janela de Horário)
- **Contexto**: A busca precisa conectar motoristas e passageiros de maneira precisa e determinística para os testes automatizados.
- **Dúvida**: Como comparar origem, destino, ordem das paradas intermediárias e a janela de horário?
- **Proposta**:
  1. *Modelo de Rota Discreta*: Em vez de exigir APIs complexas de mapas externos (que introduzem latência e custos), a PoC pode operar sobre uma lista ordenada de pontos/marcos conhecidos (ex.: bairros e terminais urbanos de Joinville).
  2. *Regra de Ordem Sequencial*: Uma carona é compatível com o pedido do passageiro se, e somente se:
     - O ponto de embarque solicitado coincide com a origem ou com um ponto de parada intermediário $P_i$;
     - O ponto de desembarque solicitado coincide com um ponto posterior $P_j$ ou o destino final da carona;
     - A ordem sequencial é estritamente crescente na rota ($i < j$).
  3. *Janela de Horário*: O passageiro informa o horário desejado $H_{desejado}$ e uma tolerância de janela (padrão de $\pm 30$ minutos). A carona é compatível se o horário estimado de passagem pelo ponto de embarque estiver contido no intervalo $[H_{desejado} - 30\text{min}, H_{desejado} + 30\text{min}]$.
- **Exemplo Concreto**: O motorista oferece a rota: `Terminal Central (07:00)` $\rightarrow$ `Bairro América (07:15)` $\rightarrow$ `Campus Univille (07:35)`.
  - Passageiro A busca `Bairro América` $\rightarrow$ `Campus Univille` às `07:20` ($\pm 15$ min): **Compatível** (ordem válida e horário dentro da janela de 07:05 a 07:35).
  - Passageiro B busca `Campus Univille` $\rightarrow$ `Terminal Central` às `07:10`: **Incompatível** (sentido inverso ao trajeto).
  - Passageiro C busca `Terminal Central` $\rightarrow$ `Campus Univille` às `08:30`: **Incompatível** (fora da janela de tolerância de horário).
- **Status**: `Pendente de decisão da dupla`

---

### Pergunta 4: Prazos e Regras Limite de Cancelamento
- **Contexto**: Cancelamentos repentinos prejudicam a previsibilidade da viagem tanto para quem conduz quanto para quem pega carona.
- **Dúvida**: Qual é o prazo mínimo de cancelamento, qual horário serve de referência oficial e como tratar o instante exato do limite (tratamento de borda)?
- **Proposta**:
  1. *Prazo Mínimo do Passageiro*: Até 2 horas (120 minutos) antes do horário de partida da carona (cancelamento sem penalidade).
  2. *Prazo Mínimo do Motorista*: Até 4 horas (240 minutos) antes do horário de partida da carona (para dar tempo hábil de os passageiros se reorganizarem).
  3. *Horário de Referência*: O horário oficial de partida da carona na origem, sincronizado no fuso horário do servidor em UTC.
  4. *Tratamento de Borda no Minuto Exato*: A condição para cancelamento tempestivo (gratuito) é estritamente inclusiva com relação ao delta de tempo: $\Delta t \ge \text{prazo\_mínimo}$.
     - Se o cancelamento ocorrer até o segundo zero do limite, é tempestivo.
     - A partir do primeiro segundo posterior ($< 120$ minutos restantes), é classificado como cancelamento tardio.
- **Exemplo Concreto**: Carona agendada para saída às `18:00:00`.
  - Se o passageiro cancelar às `15:59:59` (restam 2h 00m 01s): Cancelamento Tempestivo (vaga liberada, sem registros negativos).
  - Se o passageiro cancelar às `16:00:00` (restam exatamente 2h 00m 00s): Cancelamento Tempestivo.
  - Se o passageiro cancelar às `16:00:01` (restam 1h 59m 59s): Cancelamento Tardio (vaga liberada, registra penalidade de cancelamento tardio no perfil do passageiro).
- **Status**: `Pendente de decisão da dupla`

---

### Pergunta 5: Privacidade e LGPD na Exposição de Contato e Localização
- **Contexto**: A Constitution (Princípio I) exige transparência de permissões e minimização de exposição de dados pessoais.
- **Dúvida**: Quem tem permissão para visualizar dados de contato (telefone, e-mail) e os pontos exatos de embarque/desembarque?
- **Proposta**:
  1. *Fase de Consulta Aberta (Pré-reserva)*:
     - Dados Visíveis: Primeiro nome e inicial do motorista (ex.: "Guilherme S."), avaliação média em estrelas, modelo e cor do veículo, pontos públicos de rota e horário previsto.
     - Dados Ocultos: Placa do veículo, e-mail, telefone/WhatsApp e endereços residenciais exatos.
  2. *Fase de Reserva Confirmada (Pós-reserva)*:
     - Liberação Recíproca: Motorista e passageiro com vaga confirmada recebem acesso mútuo ao telefone de contato (WhatsApp) e ao e-mail institucional para coordenação do embarque.
     - Placa do veículo é revelada ao passageiro confirmado para segurança na identificação presencial.
  3. *Privacidade entre Passageiros*:
     - Passageiros da mesma carona NÃO têm acesso ao telefone ou e-mail de outros passageiros (apenas visualizam nome público ou indicação de "vaga ocupada").
- **Exemplo Concreto**: Ao pesquisar no aplicativo, o usuário visualiza: *"Motorista: Marcos R. (4.9 ★) - Ônix Branco - Saída: Terminal Norte - Vagas: 2"*. Ao ter sua reserva confirmada, o painel do passageiro passa a exibir: *"Nome do motorista: Marcos Ribeiro | Placa: ABC-3E21 | Ponto combinado: Saída dos fundos do terminal"*. O e-mail institucional nunca é exibido a terceiros.
- **Decisão da Dupla (Sessão 2026-11-18)**: Adotada a **Opção A (Visibilidade em camadas - LGPD estrita)**: busca aberta exibe apenas primeiro nome e inicial do sobrenome; nome completo é revelado unicamente à contraparte após reserva confirmada; e-mail institucional é estritamente confidencial.
- **Status**: `Decidido pela dupla (Opção A — Visibilidade em Camadas e E-mail Confidencial)`

---

### Pergunta 6: Regras do Escopo Completo (Reputação, No-Show, Penalidades e Recorrência)
- **Contexto**: O escopo completo introduz regras de governança de comportamento e facilidades para caronas de rotina semanal.
- **Dúvida**: Como calcular a reputação, como caracterizar formalmente o *no-show*, quais são as penalidades e como funcionam as caronas recorrentes?
- **Proposta**:
  1. *Cálculo de Reputação*: Média ponderada das notas atribuídas (1 a 5 estrelas) nos últimos 30 dias ou últimas 20 caronas, garantindo que o histórico reflita o comportamento recente.
  2. *Caracterização de No-Show (Não comparecimento)*:
     - Ocorrência quando o motorista ou passageiro não aparece no ponto de encontro após tolerância estrita de 10 minutos após o horário agendado.
     - A parte prejudicada registra no sistema a ausência da contraparte em até 2 horas após a viagem.
  3. *Sistema de Penalidades*:
     - *Cancelamento Tardio*: Redução de 0.2 na pontuação geral de reputação.
     - *No-Show*: Atribuição automática de nota equivalente a 1 estrela e redução de 0.5 na reputação. Três ocorrências de no-show bloqueiam o usuário temporariamente por 14 dias.
  4. *Caronas Recorrentes*:
     - O motorista cadastra uma regra de recorrência (ex.: "Segunda, Quarta e Sexta às 07:15").
     - O sistema instancia automaticamente as ofertas para os próximos 14 dias úteis.
     - Cada carona gerada é autônoma: se o motorista cancelar a viagem de segunda-feira, as de quarta e sexta permanecem válidas e inalteradas.
- **Exemplo Concreto**: Matheus oferece carona recorrente nas terças e quintas. Em uma quinta-feira, o passageiro Pedro reservou vaga mas não apareceu no ponto até 07:25 (tolerância de 10 min expirada). Matheus confirma a saída e registra *"No-Show de Pedro"*. O sistema calcula a penalidade, deduz 0.5 pontos da reputação de Pedro e cancela sua reserva sem direito a reembolso de reputação.
- **Status**: `Pendente de decisão da dupla`

---

## 3. Decisões Homologadas para a Primeira Spec (Sessão 2026-11-18)

As seguintes deliberações foram acordadas pela dupla e integradas à [Spec 001](file:///specs/001-cadastro-validacao-perfis/spec.md):

1. **Validação de Vínculo na PoC**: Adotada **Opção B (Whitelist de Testes)**. Contas mockadas elegíveis ativam o vínculo; e-mails ausentes na lista de homologação mantêm a conta pendente. A validação perante os critérios da disciplina permanece `Pendente de alinhamento com o professor`.
2. **Modelo de Papéis no MVP**: Adotada **Opção A (Papel Fixo por Conta)**. Cada conta no MVP é exclusivamente motorista OU passageiro, simplificando a modelagem e testes. Perfil híbrido postergado para o pós-MVP.
3. **Privacidade e LGPD**: Adotada **Opção A (Visibilidade em Camadas)**. Primeiro nome e inicial na busca aberta; nome completo liberado apenas entre motorista e passageiro após reserva confirmada; e-mail institucional estritamente confidencial.
4. **Tratamento de E-mail Duplicado**: Adotada **Opção B (Mensagem Neutra e Genérica)**. Prevenção ativa contra enumeração de usuários, orientando o usuário a tentar login sem vazar a existência do cadastro.
5. **Domínios Institucionais**: `@univille.br` definido como domínio primário da PoC. A inclusão de subdomínios adicionais reais permanece `Pendente de confirmação da dupla`.

---
*Documento gerado como base de sustentação metodológica para o Spec-Driven Development da Trilha 2.*

## 4. Decisões para a Feature 002 (2026-11-22)

Após a recomendação de preparar a especificação antes da implementação, o usuário
autorizou iniciar a Feature 002 adotando itinerário discreto e dados de veículo
na primeira oferta. Registro detalhado em [spec.md](../specs/002-oferta-caronas-paradas/spec.md).

- **Itinerário da oferta**: lista ordenada de bairros ou marcos públicos de Joinville, sem coordenadas ou mapas externos. Esta decisão resolve o formato dos pontos para REQ-004; não fecha a janela de horário ou o algoritmo de matching da Feature 003.
- **Veículo**: modelo, cor e placa exigidos antes da primeira publicação, sem ampliar o cadastro acadêmico inicial. Modelo e cor poderão aparecer em busca futura; placa permanece privada, com liberação à contraparte somente após reserva confirmada.
- **Recorte autorizado desta rodada**: especificação e checklist de qualidade. Plano, tarefas e implementação ainda não iniciados. Premissas complementares estão separadas das decisões anteriores na especificação.
- **Pendências mantidas**: homologação docente da validação acadêmica simulada, domínios adicionais, matching e cancelamento seguem sua governança própria.

## 5. Preparação da Feature 003 (2026-11-22)

Solicitada a criação da especificação com base no estado atual do projeto.
[Rascunho](../specs/003-busca-rota-horario/spec.md) reutiliza catálogo, ofertas e ordem de paradas da Feature 002 e acesso acadêmico da Feature 001.

- Regra de ordem proposta no levantamento: embarque anterior ao desembarque (`i < j`), com pontos do mesmo catálogo e sem busca por coordenadas.
- A janela de ±30 minutos aparece no roadmap; a escolha fixa/configurável continua pendente. O exemplo anterior de ±15 minutos não é homologação de parametrização pelo usuário.
- O projeto registra saída da origem, sem horário individual por parada. Deve ser confirmado se a PoC compara a saída (com aviso) ou se exigirá dados de passagem antes de implementar a busca.
- Recomendação do agente: ±30 minutos fixos, inclusivos, pela saída da origem. **Ainda não aprovada pela dupla** nesta rodada.
- Reputação não implementada não será fabricada no cartão de busca. Privacidade continua estrita: nome abreviado, sem nome completo, placa ou e-mail para terceiros.
- Nenhum código, plano ou tasks da Feature 003 implementado/gerado; TODO(REGRAS_MATCHING) e demais pendências da constitution preservados.

### Confirmação das regras temporais da Feature 003 (2026-11-22)

Atualiza as pendências da seção 5: após a recomendação apresentada, o usuário autorizou o uso das opções recomendadas para o projeto.

- Janela fixa de ±30 minutos, com os dois extremos inclusivos; sem campo para tolerância customizável.
- Comparar a saída da origem, inclusive para embarque intermediário. Informar claramente que não há previsão de horário de passagem na parada.
- Exemplo: pedido 08:00 inclui saídas 07:30 e 08:30; exclui 07:29:59 e 08:30:01, respeitando também a regra de partida futura.
- Estas decisões substituem as alternativas temporais ainda provisórias registradas anteriormente para a Feature 003. Não mudam o modelo de ofertas nem encerram homologação acadêmica, domínios ou cancelamento.
- Spec e checklist atualizados; plano/tasks e implementação continuam para etapas posteriores. Nenhuma emenda da constitution foi realizada nesta rodada.
### Confirmação de reserva e dados da Feature 004 (2026-11-22)

Decisão explícita do usuário: confirmação instantânea, estados CONFIRMADA/CANCELADA; uma reserva ocupa uma vaga durante toda a oferta, sem reutilização por trecho. Persistir os pontos de embarque/desembarque escolhidos do catálogo, em ordem do itinerário. WhatsApp adiado, sem coleta de telefone nesta tarefa; e-mail continua confidencial. As tarefas posteriores poderão liberar nome completo e placa somente à contraparte confirmada.
D004-01/D004-02 resolvidas; escopo atual: modelo e migração da [T002 local / roadmap T020](../specs/004-reserva-sem-overbooking/tasks.md). Serviço/concorrência e interface permanecem tarefas seguintes.

### Confirmação de cancelamento — Feature 005 (2026-11-22)

Usuário confirmou: passageiro 2h, motorista 4h, referência na saída da origem, comparação aware em UTC e borda inclusiva (antecedência >= prazo). Cancelamento tardio antes da partida é aceito com auditoria; na partida/depois, recusado sem mutação. Dedução numérica fica na Feature 008.
Autorizadas nesta rodada T002 local/T024 e T003 local (parcela de reserva da T025) para verificar liberação idempotente e concorrência. Cancelamento de oferta e interface excluídos. Estas decisões substituem as propostas pendentes correspondentes do levantamento; a constitution não é emendada nesta rodada.

### Remoção do painel do motorista — Feature 005/T008 local (2026-11-23)

A lixeira vermelha no canto de cada cartão de **Minhas ofertas** retira a carona do painel após confirmação. Oferta cancelada sai diretamente. Oferta aberta segue D005-01 e D005-02 para cancelamento e sai do painel na mesma operação. O histórico de reservas, cancelamentos e ocorrências recorrentes é preservado. [Especificação e critérios de aceite](../specs/005-cancelamento-liberacao-vaga/spec.md).

### Homologação de avaliações — Feature 006 (2026-11-23)

Usuário aprovou D006-01/D006-02 e autorizou T001 documental seguida da T002 unificada (antigas T002/T003, roadmap T028). Motorista registra conclusão pelo relógio servidor após partida; sem conclusão, não há avaliação. Janela inclusiva de 48h após conclusão; somente motorista↔passageiro confirmado, ativos/habilitados; excluir cancelados/no-show. Nota inteira 1..5, comentário opcional até 500 caracteres, sem edição e sem duplicata por direção/contraparte. Legados permanecem sem conclusão; não inventar chegada. Sem penalidade/reputação ou interface nesta rodada. Referência canônica em specs/006-avaliacao-mutua/spec.md e data-model.md; constitution não emendada nesta rodada.

### Homologação de reputação — Feature 007 (2026-11-23)

D007-01/D007-02 aprovadas pelo usuário: média simples das últimas 20 avaliações recebidas, pesos iguais inclusive na mesma viagem, sem corte de 30 dias; ordenação created_at/id decrescentes até referência inclusiva. Novato 5.00 sem nota virtual; Decimal com ROUND_HALF_UP em duas casas no final. Profile admite 0.00..5.00 para futura integração de penalidades, não aplicada nesta rodada. Exemplos: [5,5,4,5,4]=4.60 e [5,5,5,1]=4.00, este último exatamente três notas 5 anteriores. T001 documental e T002 unificada (antigas T002/T003, roadmap T030) autorizadas; signals e apresentação ficam T031. Essas regras substituem propostas anteriores conflitantes de pesos/30 dias/20 caronas. Constitution não emendada nesta rodada.

### Homologação de penalidades — Feature 008 (2026-11-23)

D008-01 e D008-02 confirmadas pelo usuário. Três no-shows distintos em 30 dias geram suspensão de 14 dias. Cancelamento tardio deduz 0,20. No-show contribui com uma nota 1,0 na média e deduz 0,50 após o cálculo. O prazo de denúncia, a elegibilidade, a contestação e as ações permitidas durante a suspensão constam na [spec da Feature 008](../specs/008-penalidades-conduta/spec.md). O recorte autorizado é a modelagem e os testes da T032, correspondente à T002 local.

Na T004 local da Feature 008, o usuário autorizou expor a conclusão ao motorista titular. Para denunciar a ausência do motorista sem conclusão registrada, o passageiro confirmado dispõe de 2 horas a partir do fim da tolerância de 10 minutos. [Contrato HTTP](../specs/008-penalidades-conduta/contracts/web-routes.md).

### Homologação de recorrência — Feature 009 (2026-11-23)

D009-02 mantém a geração automática na criação da regra e na rotina diária, com revalidação do titular. A T035 entrega modelos, serviço e independência do cancelamento. A T036 conecta o gerador às entradas automáticas.

A revisão de D009-01 na Feature 009/T008 define 15 dias úteis a partir da data local em America/Sao_Paulo. Hoje conta se for útil. Sábados, domingos e os feriados nacionais e de Santa Catarina fornecidos pela BrasilAPI ficam fora da contagem. Dentro da janela, o motorista continua escolhendo os dias da semana e as partidas devem ser estritamente futuras. Ocorrências existentes são preservadas. [Política vigente](../specs/009-caronas-recorrentes/spec.md).

### Recorte de notificações — Feature 010 (2026-11-23)

O usuário autorizou o trabalho necessário à T037. O recorte adota avisos internos para confirmação de reserva e cancelamentos. A consulta é a T038. O prazo e o acionamento dos lembretes de partida do REQ-012 ficam para definição própria. [Especificação e critérios](../specs/010-notificacoes-operacionais/spec.md).
