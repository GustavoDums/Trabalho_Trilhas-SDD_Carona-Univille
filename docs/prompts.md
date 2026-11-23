## P001 — Constitution inicial ## 
/speckit-constitution

Crie a constitution inicial do Carona Univille, projeto acadêmico da
Trilha 2 de Spec-Driven Development. Use o template do Spec Kit e salve
o resultado em .specify/memory/constitution.md.

O Carona Univille é uma prova de conceito web para a comunidade acadêmica.
Motoristas oferecem caronas e passageiros buscam e reservam vagas.
O escopo mínimo inclui cadastro acadêmico validado com papéis de motorista
e passageiro, oferta com origem, destino, horário, vagas e pontos de parada,
busca por rota e janela de horário, reserva sem overbooking e cancelamento
com prazo mínimo. O escopo completo inclui avaliação mútua após a viagem,
penalidades por cancelamento tardio e no-show, e caronas recorrentes.
Notificações e lista de espera automática são bônus.

Escreva a constitution em português do Brasil, com princípios verificáveis:

1. Acesso acadêmico e LGPD. Restrinja o uso à comunidade acadêmica
   com vínculo validado. Minimize a coleta de dados pessoais e de
   localização. Exija que as specs definam quem pode ver esses dados
   e para qual finalidade. Use dados fictícios nos testes e na demo.

2. Integridade das vagas. Mesmo com pedidos simultâneos, a quantidade de
   reservas confirmadas deve respeitar a capacidade da oferta. Exija
   critérios de aceite verificáveis para a última vaga, o matching por
   rota e horário, os limites de cancelamento e, no escopo completo,
   o cálculo de reputação.

3. Qualidade da entrega. Exija testes automatizados dos critérios de
   aceite, cobertura mínima de 80% e relatório versionado no repositório.
   O início do README deve trazer a quantidade real de testes e o
   percentual medido de cobertura, atualizados a cada entrega.

4. Desenvolvimento guiado pela especificação. Antes da primeira spec,
   extraia os requisitos do briefing e registre as perguntas e decisões
   da dupla. A spec descreve o comportamento e os critérios de aceite.
   O plan registra a implementação técnica. As tasks organizam o trabalho
   em fatias rastreáveis. Os documentos devem permitir recriar o sistema.

5. Rastreabilidade e histórico. Cada commit de implementação deve apontar
   para uma task, e cada task deve apontar para os requisitos que atende.
   Registre em docs/prompts.md o texto exato de cada prompt enviado,
   incluindo comandos do Spec Kit e pedidos de revisão. Associe cada
   entrada ao artefato produzido e, quando houver, à decisão da dupla.

6. Stack e governança. Registre na constitution a stack aprovada pela
   dupla. Como nenhuma escolha foi informada neste prompt, marque a stack
   como pendente. Faça o mesmo para o mecanismo de validação acadêmica,
   as regras exatas de matching e o prazo de cancelamento. Registre as
   alterações futuras da constitution com a data e o motivo da mudança.

Ao final, apresente o caminho do arquivo gerado e liste as decisões
pendentes para a dupla revisar. Encerre após gerar a constitution.

## P002 — Levantamento de requisitos ##

Crie docs/levantamento.md para a Trilha 2 — Carona Univille.
Se a pasta docs não existir, crie-a. Consulte a constitution já gerada
e use o briefing abaixo como fonte para levantar os requisitos.

Briefing:
- O Carona Univille é uma prova de conceito web em que motoristas
  oferecem caronas e passageiros reservam vagas.
- A plataforma é restrita à comunidade acadêmica, com cadastro validado.
  Dados pessoais e de localização devem seguir a LGPD.
- Escopo mínimo: cadastro com os papéis motorista e passageiro, oferta
  com origem, destino, horário, vagas e pontos de parada, busca por rota
  e janela de horário, reserva sem overbooking e cancelamento com prazo
  mínimo.
- Escopo completo: avaliação mútua após a viagem, cálculo de reputação,
  penalidade por cancelamento tardio e no-show, e caronas recorrentes.
- Bônus da trilha: notificações e lista de espera automática quando
  uma vaga é liberada.
- Os testes de aceitação verificam matching por rota e horário, limite
  de vagas sob reservas simultâneas, prazos de cancelamento e cálculo
  de reputação.
- A entrega pede constitution, specs, plans e tasks, rastreabilidade
  commit → task → requisito, testes automatizados dos critérios de aceite,
  cobertura mínima de 80% com relatório versionado, quantidade de testes
  e cobertura no início do README e pitch com demo ao vivo de até
  10 minutos, sem código nos slides.

Dê um ID estável a cada requisito (REQ-001, REQ-002...) e indique a
cláusula do briefing que o sustenta. Identifique o que pertence ao escopo
mínimo, ao escopo completo, aos bônus e às exigências gerais de entrega.

Registre as perguntas em aberto com uma proposta, um exemplo concreto
e o status "Pendente de decisão da dupla". Inclua:
- Como comprovar o vínculo acadêmico e se uma validação simulada com
  dados fictícios precisa de confirmação do professor.
- Se a mesma pessoa pode atuar nos dois papéis.
- Como comparar origem, destino, ordem das paradas e janela de horário.
- Qual é o prazo mínimo de cancelamento, qual horário serve de
  referência e como tratar o instante exato do limite.
- Quem pode ver dados de contato e pontos de embarque.
- Como definir reputação, no-show, penalidades e recorrência no
  escopo completo.

Ao final, liste as decisões que afetam a primeira spec. Preserve as
propostas como pendentes até a dupla decidir. Encerre após criar o
levantamento e apresentar um resumo das perguntas em aberto.

## P003 — Spec de cadastro acadêmico e perfis ##
/speckit-specify

Crie a primeira spec do Carona Univille, uma PoC web de caronas
restrita à comunidade acadêmica. A feature é Cadastro Acadêmico,
Validação de Vínculo e Perfis.

Use .specify/memory/constitution.md e docs/levantamento.md como
referências. Preserve a redação e a rastreabilidade dos requisitos
REQ-001, REQ-002 e REQ-003. Oferta, busca, reserva e cancelamento
serão detalhados na próxima spec.

Use as seguintes propostas para a primeira versão e identifique-as
como pendentes de confirmação da dupla:
- O cadastro solicita nome, e-mail institucional e um papel inicial
  (motorista ou passageiro). A primeira versão propõe um papel por
  conta. A atuação nos dois papéis permanece como decisão em aberto.
- Matrícula, telefone, placa e dados do veículo ficam fora do
  cadastro inicial. A spec deve indicar a finalidade e a visibilidade
  dos dados coletados.
- Contas pendentes ficam restritas ao fluxo de ativação. O acesso às
  funcionalidades de carona exige uma conta com vínculo validado.
- Para a PoC, proponha validação simulada de contas acadêmicas
  fictícias. Registre que o professor precisa confirmar se isso
  atende à restrição do enunciado. Trate @univille.br como domínio
  proposto, ainda a confirmar. O domínio por si só não ativa a conta.

Escreva histórias de usuário priorizadas e critérios de aceite em
Dado/Quando/Então. Inclua cenários para cadastro com cada papel,
e-mail fora do domínio aceito, tentativa de acesso com conta
pendente, ativação bem-sucedida para conta elegível e falha de
ativação sem liberar acesso. Vincule os cenários aos requisitos
correspondentes.

Descreva o comportamento observável. Deixe decisões sobre tokens,
envio de e-mail, banco, endpoints e stack para o plan. Ao terminar,
informe o caminho da spec gerada e liste as decisões que ainda
precisam ser confirmadas antes de avançar.

## P004 — Clarificação da spec de cadastro ##

/speckit-clarify

Revise specs/001-cadastro-validacao-perfis/spec.md à luz da constitution
e de docs/levantamento.md. Preserve a rastreabilidade aos REQ-001,
REQ-002 e REQ-003.

Faça perguntas objetivas sobre as decisões que ainda afetam o
comportamento da feature:
- Como distinguir uma conta acadêmica fictícia elegível de uma
  inelegível, mesmo quando ambas usam o domínio aceito.
- Se a conta terá um papel fixo no MVP ou poderá atuar nos dois papéis.
- Quem pode consultar o nome completo e o e-mail institucional.
- O que acontece ao tentar cadastrar novamente o mesmo e-mail.

Confira se os critérios de aceite distinguem o acesso de visitantes,
contas pendentes e contas ativas. Inclua um cenário positivo em que
uma conta ativa acessa as funcionalidades permitidas ao seu papel,
além do cenário de bloqueio para contas pendentes.

Após cada decisão da dupla, atualize a spec e registre a decisão em
docs/levantamento.md. Mantenha a aprovação da validação simulada pelo
professor e a lista de domínios institucionais reais como pendentes
até haver confirmação. Encerre após a clarificação, sem iniciar o plan.

## P004.1 — Validação simulada ##

R: B - Whitelist de testes: Manter uma lista predefinida de contas fictícias elegíveis em configuração de mock; e-mails fora dessa lista falham na validação.

## P004.2 — Papel fixo por conta ##

R: A - Papel fixo no MVP: Cada conta pertence exclusivamente a um papel (Motorista OU Passageiro), definido no cadastro e imutável no MVP.

## P004.3 — Visibilidade de nome e e-mail institucional. ##

R: A - Visibilidade em camadas (LGPD estrita): Busca aberta exibe apenas primeiro nome e inicial (ex.: "Lucas A."); nome completo revelado apenas à contraparte após reserva confirmada; e-mail institucional é estritamente confidencial e nunca exibido a terceiros.

## P004.4 — Cadastro com e-mail ##

R: B - Resposta neutra e genérica: Exibe "Não foi possível concluir o cadastro com os dados informados. Se você já possui vínculo cadastrado, tente fazer login", sem confirmar explicitamente o e-mail.

## P005 — Registrar a stack na constitution ##

/speckit-constitution

Atualize a constitution do Carona Univille com a stack aprovada pela
dupla. Use Python e Django para a aplicação web, templates Django com
HTML e CSS para a interface, PostgreSQL para persistência e pytest
com pytest-django e pytest-cov para testes e cobertura.

Registre a justificativa. A aplicação usa a autenticação e as sessões
do Django. O PostgreSQL será usado também nos testes de integração
que verificam concorrência nas reservas em uma feature posterior.

Preserve os princípios de LGPD, cobertura mínima de 80% e
rastreabilidade. Mantenha como pendentes a aceitação da validação
simulada pelo professor e a confirmação dos domínios institucionais.
Registre a revisão conforme a governança da constitution e encerre
após atualizar o documento.

## P006 — Plano técnico do cadastro ##

/speckit-plan

Gere o plano técnico de specs/001-cadastro-validacao-perfis/spec.md.
Use a stack da constitution 1.1.0 e as decisões registradas em
docs/levantamento.md. Preserve a rastreabilidade aos REQ-001, REQ-002
e REQ-003.

Detalhe o modelo de conta, a unicidade do e-mail, o papel fixo e a
transição de Pendente para Ativa. Explique como uma conta Pendente
pode entrar no fluxo de ativação sem acessar caronas. Diferencie o
status do vínculo acadêmico do campo is_active usado pelo Django.

Planeje a validação simulada com uma lista de contas fictícias.
Inclua exemplos de duas contas do mesmo domínio, uma elegível e
outra inelegível. Mantenha como pendências a aceitação da simulação
pelo professor e a confirmação dos domínios institucionais reais.

Mapeie os cenários da spec para testes automatizados. Cubra os dois
papéis, ativação aceita e recusada, acesso por estado da conta e
cadastro duplicado. No caso duplicado, planeje verificar a mensagem
neutra, a existência de uma única conta e a preservação do seu estado
e papel. Inclua a verificação de que o e-mail institucional não fica
visível para terceiros.

Documente no quickstart como preparar o ambiente no Windows com
PowerShell, configurar o PostgreSQL, carregar os dados fictícios,
rodar os testes e gerar o relatório de cobertura versionável.
Indique como obter a contagem de testes e a cobertura medida para
atualizar o início do README.

Se faltar alguma decisão funcional de login ou ativação, registre
a pergunta para a dupla. Limite o plano ao cadastro, à validação
e aos perfis. Encerre após gerar os artefatos de planejamento.

## P007 — Gerar todas as tasks ##

Gere em uma única rodada todas as tarefas necessárias para implementar
o Carona Univille. Esta rodada é apenas de planejamento.

Leia .specify/memory/constitution.md, docs/levantamento.md e as specs
e os plans existentes. Preserve os requisitos, as decisões aprovadas
e os IDs de tarefas já registrados.

Gere specs/001-cadastro-validacao-perfis/tasks.md no formato do Spec Kit,
usando a spec e o plan já revisados. Cubra configuração do ambiente,
modelo de conta, cadastro, autenticação, permissões, validação simulada,
privacidade do perfil e testes de aceite. Sinalize as tarefas que ainda
dependem das decisões sobre senha, login após o cadastro e ativação.

Gere também docs/roadmap-implementacao.md com um checklist detalhado
de todas as tarefas do sistema, cobrindo:

- MVP (REQ-001 a REQ-007) — cadastro e validação acadêmica, perfis,
  oferta com paradas, busca por rota e janela de horário, reserva
  sem overbooking e cancelamento com liberação de vaga.
- Escopo completo (REQ-008 a REQ-011) — avaliação mútua, cálculo de
  reputação, cancelamento tardio, no-show e caronas recorrentes.
- Bônus (REQ-012 e REQ-013) — notificações e lista de espera automática.
- Entrega (REQ-014 a REQ-020) — artefatos SDD, rastreabilidade,
  histórico de prompts, testes de aceite, relatório versionado de
  cobertura mínima de 80%, métricas no início do README e pitch
  com demo ao vivo de até 10 minutos e slides sem código.

Para cada tarefa, indique a feature, os requisitos, as dependências,
o resultado esperado e como verificá-lo. Dimensione cada tarefa para
que sua implementação e seus testes relacionados caibam em um commit.

Inclua testes para a ordem das paradas e os limites da janela de busca,
dois passageiros disputando a última vaga no PostgreSQL, os instantes
antes, no limite e depois do prazo de cancelamento, e exemplos
numéricos do cálculo de reputação.

Para features com spec e plan revisados, gere seu tasks.md. Para as
demais, detalhe as tarefas no roadmap e indique quais decisões precisam
ser fechadas antes de gerar o tasks.md oficial. Mantenha como pendentes
a homologação da validação simulada e os domínios institucionais reais.

Ao final, informe os arquivos gerados e as tarefas bloqueadas.
Encerre após gerar os documentos, sem implementar ou commitar.

## P008 — Consolidar tarefas por propósito ##

Consolide as tarefas do Carona Univille por propósito, mantendo
uma tarefa por commit de implementação. Trabalhe apenas no planejamento.

Leia specs/001-cadastro-validacao-perfis/tasks.md,
docs/roadmap-implementacao.md, docs/levantamento.md e os artefatos
de spec e plan disponíveis. Use a lista atual de 125 tarefas como base.

Agrupe tarefas que entreguem juntas um resultado verificável.
Exemplos de agrupamento:

- Configuração inicial do Django, dependências e configuração de testes.
- Modelo de conta, migração e testes de suas restrições.
- Cadastro dos dois papéis, validações do formulário e testes de aceite.
- Validação acadêmica simulada, dados fictícios e testes de aprovação
  e recusa.
- Reserva transacional e teste de concorrência pela última vaga.
- Cancelamento, liberação da vaga e testes no limite do prazo.
- Geração do relatório de cobertura e atualização das métricas no README.

Use 45 a 55 tarefas no total e 10 a 14 no cadastro como referências
flexíveis. Priorize tarefas com um propósito, um critério de conclusão
e um tamanho adequado para revisão em um commit. Mantenha tarefas
separadas quando tiverem resultados, dependências ou decisões distintas.

Atualize o tasks.md da feature 001 e o roadmap geral. Preserve todos
os requisitos, cenários de aceite, dependências e pendências. Mantenha
as futuras features no roadmap até que tenham spec e plan revisados.
No total geral, conte as tarefas da feature 001 uma única vez.

Preserve os IDs de tarefas já referenciadas em commits e mantenha
a rastreabilidade de cada fusão. Mostre no resumo quais IDs antigos
foram agrupados em cada nova tarefa. Mantenha as decisões pendentes
com esse status e evite incluir regras de negócio novas.

Ao final, informe a contagem antes e depois, o novo total da feature
001 e exemplos das principais fusões. Encerre após atualizar o
planejamento, sem implementar ou commitar.

## Rode o P009 — Revisão das tarefas ##

/speckit-analyze

Revise a consistência entre a constitution, a spec, o plan, o tasks.md
consolidado da feature 001 e o roadmap de implementação.

Confira três pontos:
- T001 — Se o projeto ainda não tiver testes, pytest --collect-only
  pode retornar código 5. Verifique se o critério de conclusão
  distingue falta de testes de erro de configuração.
- T002 — Confira se a regra de nome com dois termos consta na spec
  aprovada ou se apareceu durante a consolidação.
- T012 e T043 — Confira se uma tarefa prepara a medição da cobertura
  e a outra registra o resultado da entrega, ou se há duplicidade.

Confirme quais tarefas dependem das decisões sobre senha, login
e botão de ativação. Informe se existe algum bloqueio para a T001.
Entregue apenas o diagnóstico.

## P010 — Ajustar o checklist antes de implementar ##

Atualize apenas o tasks.md da feature 001 e o roadmap com os ajustes
do relatório de análise.

Na T001, use python manage.py check para verificar a configuração
do Django. No pytest --collect-only, aceite o código 5 somente
quando o resultado indicar ausência de testes, sem erros de
configuração ou coleta.

Delimite a T012 como preparação da medição e fechamento da feature
001. Defina a T043 como medição consolidada na entrega final,
reutilizando o mesmo script.

Mantenha as decisões sobre senha, login e ativação como pendentes
nas tarefas afetadas. Preserve a regra de nome com dois termos na
T002, já prevista na spec. Encerre após atualizar os documentos,
sem iniciar a implementação.

## P011 — Implementar a T001 ##

Execute somente a tarefa T001 do Carona Univille.

Área da tarefa — Feature 001, Cadastro acadêmico, validação e perfis.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Use a entrada T001 em specs/001-cadastro-validacao-perfis/tasks.md como
fonte do escopo desta rodada.

Prepare a estrutura Django, as dependências, a configuração do pytest e o
.env.example do PostgreSQL conforme a T001. Use valores fictícios no arquivo
versionado. Execute python manage.py check e pytest --collect-only. Aceite o
código 5 somente se a saída indicar ausência de testes, sem erros de
configuração ou de coleta, e a verificação do Django passar. Informe
separadamente se a conexão com o PostgreSQL foi efetivamente verificada.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.

## P012 — Implementar a T002 ##

Execute somente a tarefa T002 do Carona Univille.

Área da tarefa — Feature 001, Cadastro acadêmico, validação e perfis.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Use a entrada T002 em specs/001-cadastro-validacao-perfis/tasks.md como
fonte do escopo desta rodada.

Implemente AcademicUser e suas migrações conforme spec.md e data-model.md.
Cubra as restrições que a T002 atribui ao modelo, incluindo unicidade do
e-mail, papel fixo, estado acadêmico inicial pendente e nome com pelo menos
dois termos. Execute os testes da tarefa e verifique a migração no banco
previsto no plano.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.

OBS: A T001 está concluída e a conexão local com o PostgreSQL já foi
validada pelo Django. Use o ambiente virtual do projeto.

Siga TDD na T002: escreva e rode primeiro os testes do modelo de
conta, confirme que falham pelo comportamento esperado, depois
implemente o modelo e a migração e rode os testes novamente.
Informe os resultados e aguarde minha revisão e meu commit.

## P013 — Implementar a T003

Execute somente a tarefa T003 do Carona Univille.

Área da tarefa — Feature 001, Cadastro acadêmico, validação e perfis.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Use a entrada T003 em specs/001-cadastro-validacao-perfis/tasks.md como
fonte do escopo desta rodada.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.

## P014 — Implementar a T004

Execute somente a tarefa T004 do Carona Univille.

Área da tarefa — Feature 001, Cadastro acadêmico, validação e perfis.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Use a entrada T004 em specs/001-cadastro-validacao-perfis/tasks.md como
fonte do escopo desta rodada.

Antes de implementar campos de senha e confirmação, verifique a decisão
registrada pela dupla. Se ainda estiver provisória, informe o que precisa de
confirmação. Use o fluxo e os critérios aprovados na documentação local para
delimitar a T004.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.

## P015 — Implementar a T005

Execute somente a tarefa T005 do Carona Univille.

Área da tarefa — Feature 001, Cadastro acadêmico, validação e perfis.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Use a entrada T005 em specs/001-cadastro-validacao-perfis/tasks.md como
fonte do escopo desta rodada.

Cubra o cadastro como Motorista e como Passageiro, com estado acadêmico
inicial Pendente. Confira as decisões registradas sobre senha e login após o
cadastro antes de alterar o formulário, a view, as rotas ou o
redirecionamento previstos nesta tarefa.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.

## P016 — Implementar a T006

Execute somente a tarefa T006 do Carona Univille.

Área da tarefa — Feature 001, Cadastro acadêmico, validação e perfis.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Use a entrada T006 em specs/001-cadastro-validacao-perfis/tasks.md como
fonte do escopo desta rodada.

Verifique que a tentativa duplicada retorna a mensagem neutra aprovada,
mantém uma única conta e preserva os dados, o papel e o estado acadêmico do
registro original.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.

## P017 — Implementar a T007

Execute somente a tarefa T007 do Carona Univille.

Área da tarefa — Feature 001, Cadastro acadêmico, validação e perfis.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Use a entrada T007 em specs/001-cadastro-validacao-perfis/tasks.md como
fonte do escopo desta rodada.

Siga o recorte da T007 para a validação pela lista de contas fictícias.
Verifique os casos de elegibilidade atribuídos a esta tarefa. Os passos de
interface seguem a divisão do checklist.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.\

## P018 — Implementar a T008

Execute somente a tarefa T008 do Carona Univille.

Área da tarefa — Feature 001, Cadastro acadêmico, validação e perfis.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Use a entrada T008 em specs/001-cadastro-validacao-perfis/tasks.md como
fonte do escopo desta rodada.

Confira se a dupla aprovou o acionamento por botão único ou outra interação
registrada na spec. Cubra a ativação com a sessão e os dados previstos na
tarefa, incluindo os resultados de aprovação e recusa que constarem dos
critérios.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.

## P019 — Implementar a T009

Execute somente a tarefa T009 do Carona Univille.

Área da tarefa — Feature 001, Cadastro acadêmico, validação e perfis.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Use a entrada T009 em specs/001-cadastro-validacao-perfis/tasks.md como
fonte do escopo desta rodada.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.

## P020 — Implementar a T010

Execute somente a tarefa T010 do Carona Univille.

Área da tarefa — Feature 001, Cadastro acadêmico, validação e perfis.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Use a entrada T010 em specs/001-cadastro-validacao-perfis/tasks.md como
fonte do escopo desta rodada.

Confira se a equipe já definiu login automático ou manual após o cadastro.
Implemente somente a parte desse comportamento atribuída à T010 no checklist
local.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.


## P021 — Implementar a T011

Execute somente a tarefa T011 do Carona Univille.

Área da tarefa — Feature 001, Cadastro acadêmico, validação e perfis.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Use a entrada T011 em specs/001-cadastro-validacao-perfis/tasks.md como
fonte do escopo desta rodada.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.


## P022 — Implementar a T012

Execute somente a tarefa T012 do Carona Univille.

Área da tarefa — Feature 001, Cadastro acadêmico, validação e perfis.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Use a entrada T012 em specs/001-cadastro-validacao-perfis/tasks.md como
fonte do escopo desta rodada.

Prepare a medição de cobertura como descrita na T012. Execute a suíte de
cadastro, gere o relatório versionável e sincronize o início do README com a
contagem real e o percentual medido. Verifique o quickstart. Identifique os
números como os da Feature 001 e aplique a meta documentada de 80%.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.


## P023 — Diagnóstico da T013 e especificação da Feature 002

Execute somente a tarefa T013 do Carona Univille.

Área da tarefa — Feature 002, Oferta de caronas com paradas.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T013 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.


## P024 — Plano técnico e tarefas da Feature 002

Gere o plano técnico e as tarefas da Feature 002, sem implementar código.

Referência anexada: `docs/prompts.md`.

Skills aplicadas: speckit-plan e speckit-tasks. Contexto: spec existente, decisões
de pontos discretos e veículo na primeira oferta, constitution e código local.
Revisão delegada somente leitura, conforme workflow de planejamento; sem edição
por agente delegado. Artefatos: plan.md, research.md, data-model.md,
contracts/web-routes.md, quickstart.md e tasks.md da Feature 002. Sete tarefas
locais abertas; T013 do roadmap corresponde a Feature 002/T002, precedida por
T001 de preparação. Roadmap e referências da spec sincronizados.
Sem modelos, serviços, migrações, testes ou scripts de produto implementados.
Nenhuma suíte executada nesta rodada documental; sem staging ou commit.


## P026 — Roadmap T014 / Feature 002 T003 local

Execute somente a tarefa T014 do Carona Univille.

Área da tarefa — Feature 002, Oferta de caronas com paradas.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T014 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.


## P027 — Dependência da T015: concluir roadmap T014 / Feature 002 T004 local

Execute somente a tarefa T015 do Carona Univille.

Área da tarefa — Feature 002, Oferta de caronas com paradas.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T015 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.


## P028 — Roadmap T015 / Feature 002 T005 local

neste caso, execute somente a tarefa T015 do Carona Univille.

Área da tarefa — Feature 002, Oferta de caronas com paradas.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T015 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.

Referência anexada: `docs/prompts.md`.

Correspondência única: roadmap T015 = Feature 002/T005 local, dependência T004
concluída. Artefatos: view de consulta própria, rota, template, testes, relatórios
Feature 002, README, tasks e roadmap. Sem reserva, edição, exclusão ou cancelamento.
Alterações preexistentes preservadas; sem staging ou commit.


## P029 — Roadmap T016 / Feature 002 T006 local

Execute somente a tarefa T016 do Carona Univille.

Área da tarefa — Feature 002, Oferta de caronas com paradas.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T016 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.

Referência anexada: `docs/prompts.md`.

Correspondência única: roadmap T016 = Feature 002/T006 local; dependência T005
concluída. Artefatos: testes integrados de aceitação, relatórios Feature 002,
README, tasks e roadmap. Não houve alteração do código de produção.
Testes cobrem sessões e CSRF reais, dois autores e rollback por falha injetada.
Alterações preexistentes preservadas; sem staging ou commit.
## P030 — Diagnóstico T017 e especificação da Feature 003

Execute somente a tarefa T017 do Carona Univille.

Área da tarefa — Feature 003, Busca por rota e horário.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T017 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.

Referência anexada: `docs/prompts.md`.

### Autorização para especificar

com base neste projeto até o momento, crie a feature 3 com as informações presentes no projeto

Referência anexada: `docs/prompts.md`.

Skill aplicada: speckit-specify. Artefatos: specs/003-busca-rota-horario/spec.md,
checklists/requirements.md, referências no levantamento/roadmap e feature.json.
Duas decisões continuam pendentes: janela fixa/configurável e referência temporal.
Recomendação de ±30 minutos fixos pela saída da origem não tratada como homologada.
Sem matching implementado, sem plano/tasks e sem testes executados nesta rodada.
Sem staging ou commit.
## P031 — Confirmar regras temporais da Feature 003

pode fazer com base no que considera recomendado para o projeto

Referência anexada: `docs/prompts.md`.

Contexto da confirmação: janela recomendada de ±30 minutos fixos, bordas
inclusivas, comparando saída da origem e sem estimar passagem por parada.
Adotadas ambas as opções; spec, checklist, levantamento e roadmap sincronizados.
Sem plano/tasks, código ou testes novos. Sem staging ou commit.
## P032 — Planejamento técnico da Feature 003

gere o plano técnico e as tarefas locais

Referência anexada: `docs/prompts.md`.

Skills aplicadas: speckit-plan e speckit-tasks. Artefatos: plan.md, research.md,
data-model.md, contracts/web-routes.md, quickstart.md e tasks.md da Feature 003;
referências da spec/checklist e roadmap sincronizadas. Revisão delegada somente
leitura conforme a skill de planejamento, sem edição pelo delegado.
Regras confirmadas preservadas: ±30 minutos inclusivos pela saída da origem.
Cinco tarefas locais abertas: T017 do roadmap corresponde a T002 local, com
preparação T001 para pacote de serviços compatível; T018 a T003; T019 a T004.
Sem migração ou código de produto, testes ou scripts implementados/executados.
Alterações preexistentes preservadas; sem staging ou commit.
---

## 2026-11-22 — Preparação documental das Features 004 em diante

Prompt do usuário (integral):

> Prepare as features 004 em diante do Carona Univille para implementação. Nesta rodada, gere ou complete os arquivos de especificação, plano técnico e tarefas locais no repositório. Encerre após validar a documentação, sem implementar código, fazer staging ou criar commits.
>
> Antes de escrever, leia a constitution do projeto, docs/levantamento.md, docs/roadmap-implementacao.md e os artefatos existentes em specs/. Use as features 001 a 003 como referência de formato e preserve as alterações existentes.
>
> Escopo:
> - Feature 004 — Reserva sem overbooking, T020–T023 do roadmap.
> - Feature 005 — Cancelamento e liberação de vaga, T024–T027.
> - Features 006 a 009 — T028–T036. Resolva a distribuição das tarefas e os nomes das features pelo roadmap.
> - Features 010 e 011 — T037–T040. Inclua apenas os bônus que a dupla já confirmou no planejamento. Se a decisão estiver pendente, registre isso no resumo.
> - T041–T045 pertencem à entrega e à governança geral. Use-os como referência quando pertinente.
>
> Para cada feature no escopo, siga a estrutura e os nomes usados em specs/ e entregue:
>
> 1. spec.md — requisitos, fluxos, regras de negócio, dependências e critérios de aceitação verificáveis.
> 2. plan.md — abordagem técnica compatível com a arquitetura atual, componentes afetados, mudanças em dados ou interfaces quando aplicável, ordem de implementação e estratégia de verificação.
> 3. tasks.md — checklist com IDs locais, tarefas pequenas e executáveis, requisitos vinculados, dependências, arquivos ou áreas prováveis e critérios de conclusão.
>
> Relacione cada item aplicável do roadmap aos IDs locais do tasks.md por objetivo e requisito. Os números podem ser diferentes. Preserve os IDs locais e o estado das tarefas já existentes. Para as novas tarefas, deixe o checklist em aberto.
>
> Se as fontes divergirem ou faltar uma decisão de produto, registre a dúvida e avance nas partes que puder especificar com segurança. Ao final, confira a consistência entre spec.md, plan.md e tasks.md e liste os arquivos criados ou atualizados, o mapeamento dos IDs do roadmap para os IDs locais e as decisões pendentes.

Referência anexada: docs/prompts.md.

Skills aplicadas: speckit-specify, speckit-plan, speckit-tasks e speckit-analyze.
Artefatos: sete documentos por feature 004–009 e docs/preparacao-features-004-009.md.
Não houve confirmação nova de regras de produto ou adoção dos bônus 010/011.
Todas as 40 tarefas locais permanecem abertas, com decisões bloqueantes explícitas.
Revisão de pesquisa delegada somente leitura, conforme instrução da skill speckit-plan.

Instrução enviada ao agente de pesquisa (integral):

> Somente pesquisa/revisão de documentação, sem editar. Usuário pede preparar specs/plans/tasks Features004–009 e bônus010/011 só se confirmados, registrando pendências sem bloquear trabalho documental. Leia roadmap trechos004–011 e levantamento. Identifique conflitos entre reserva/cancelamento/avaliação/reputação/penalidades/recorrência, bônus realmente confirmados ou apenas propostos e invariantes técnicos seguros transacionais. Responda com recomendações e bloqueios de produto; não homologue propostas.

Nenhum código, migração, staging ou commit nesta rodada. Validação documental,
sem executar suíte futura nem alterar métricas existentes.


---

## 2026-11-22 — Feature 003 / roadmap T018 / T003 local e dependências autorizadas

Prompt integral:

~~~text
Execute somente a tarefa T018 do Carona Univille.

Área da tarefa — Feature 003, Busca por rota e horário.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T018 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md.

Após análise, foi informado: T018 → T003 local; T001/T002 locais ainda ausentes e divergência sobre nota. Proposta: executar primeiro T001 e T002 (roadmap T017), depois T003 (T018), mantendo nota ausente conforme spec. View/rota T004 (T019) fora do escopo.

Resposta integral do usuário:

~~~text
autorizo
~~~

Referência anexada: docs/prompts.md.

Skills aplicadas: speckit-implement (restrita às três tarefas autorizadas) e python-fact-grounded-coding. Checklist documental 16/16 aprovado; sem hooks configurados. Venv do projeto Python 3.12.10, Django 5.1.15 e PostgreSQL existentes.

T001: regressão 114; contrato de import 115 antes/depois da refatoração, sem mudança de comportamento. T002: fixture inicialmente corrigida para criar conta PENDENTE; vermelho válido 65 falhas por serviço ausente, depois 65 aprovados. T003: 27 falhas por formulário ausente, depois 27 aprovados. Regressão final 359 aprovados, sem falhas/erros/ignorados; reports coverage-feature003-t018.json e test-results-feature003-t018.xml, detalhes em specs/003-busca-rota-horario/evidence-t018.md.

Sem nova migração, view/rota de busca, nota, reserva, staging ou commit. Checklists locais T001–T003 e roadmap T017/T018 concluídos somente após evidência; T004/T005 locais permanecem pendentes. Alteração prévia em docs/prompts.md preservada.


---

## 2026-11-22 — Feature 003 / T004 local / roadmap T019

Prompt integral:

~~~text
Execute somente a tarefa T019 do Carona Univille.

Área da tarefa — Feature 003, Busca por rota e horário.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T019 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md.

Correspondência por objetivo/requisito: T019 → T004 local; dependência T003 concluída. Divergência identificada na tabela histórica do roadmap (busca paginada), enquanto plano e tarefa local não exigem paginação. Foi recomendado seguir T004 sem paginação e corrigir a referência do roadmap.

Confirmação integral do usuário:

~~~text
sim
~~~

Referência anexada: docs/prompts.md.

Skills aplicadas: speckit-implement (somente T004) e python-fact-grounded-coding. Checklist documental 16/16 aprovado, sem hooks. Ambiente venv existente; PostgreSQL real nos testes. Testes HTTP escritos/rodados antes da view/rota: 32 falhas esperadas e 31 aprovações (incluindo os 27 testes anteriores). Após implementação e correção de comparação QueryDict no próprio teste: 63 aprovados. A comparação foi ajustada para .dict(), preservando a verificação integral dos filtros.

Artefatos, regressão e medição desta rodada: specs/003-busca-rota-horario/evidence-t019.md. Sem paginação, nova migração, staging ou commit; tarefa de qualidade/demo final T005 permanece fora desta rodada. Alteração prévia em docs/prompts.md preservada.



---

## 2026-11-22 — Feature 004 / T002 local / roadmap T020

Prompt integral:

~~~text
Execute somente a tarefa T020 do Carona Univille.

Área da tarefa — Feature 004, Reserva sem overbooking.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T020 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md.

Correspondência única: T020 → T002 local, modelo RideBooking/migração. Identificado bloqueio T001 de decisões D004-01/D004-02. Recomendação apresentada: confirmação instantânea; estados CONFIRMADA/CANCELADA; uma vaga por toda a oferta; persistir pontos escolhidos do catálogo; adiar WhatsApp, sem telefone nesta tarefa. Após confirmação, registrar preparação documental e implementar somente T020/T002 com TDD.

Confirmação integral do usuário:

~~~text
confirmo
~~~

Referência anexada: docs/prompts.md.

Skills: speckit-implement restrita a T001 documental e T002 de modelo, python-fact-grounded-coding. Sem checklist adicional/hooks na Feature 004; contexto resolvido com SPECIFY_FEATURE_DIRECTORY e SPECIFY_FEATURE_NO_PERSIST, preservando ponteiro ativo. Venv Python 3.12.10/Django 5.1.15 e PostgreSQL existentes.

TDD: 49 falhas por modelo RideBooking ausente (LookupError), antes de editar produção; 49 aprovados após modelo/migração. Migração 0003_ridebooking planejada, SQL revisado e aplicada no PostgreSQL local; snapshots de contas/ofertas/pontos/paradas idênticos antes/depois, nova tabela vazia, 4 FKs e 3 restrições verificadas. Relatórios e resultados finais em specs/004-reserva-sem-overbooking/evidence-t020.md.

Sem serviço de reserva/concorrência, interface, rotas, telefone, staging ou commit. Alteração prévia em docs/prompts.md preservada.

---

## 2026-11-22 — Feature 004 / T003 local / núcleo do roadmap T021

Prompt integral:

~~~text
Execute somente a tarefa T021 do Carona Univille.

Área da tarefa — Feature 004, Reserva sem overbooking.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T021 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Implemente a proteção transacional prevista no plan. Teste dois passageiros
elegíveis tentando reservar simultaneamente a última vaga, com transações
independentes no PostgreSQL. Verifique que existe exatamente uma reserva
confirmada e que o saldo final é zero.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md.

Antes de editar, identificadas T003 local (serviço/concorrência) e T006 local (disponibilidade na busca), ambas vinculadas à T021 na tabela. Recomendado executar somente T003 nesta rodada e deixar T006 para outra rodada.

Resposta integral do usuário:

~~~text
sim, logo após pode rodar a T006 na próxima rodada
~~~

Referência anexada: docs/prompts.md.

Escopo desta rodada: somente T003; autorização da T006 fica registrada para a próxima rodada, sem executá-la aqui. Skills aplicadas: speckit-implement restrita ao recorte autorizado e python-fact-grounded-coding. Sem hooks/checklist adicional; ponteiro ativo preservado com SPECIFY_FEATURE_NO_PERSIST.

Contrato interno da função documentado antes do código. TDD: 33 falhas por booking_service ausente, depois 33 aprovações. Testes transacionais usam duas conexões com pg_backend_pid e txid_current distintos, barreira antes dos locks, uma confirmação e uma recusa, saldo zero; caso adicional cobre duplicidade concorrente do mesmo passageiro. JUnit final inclui propriedades com IDs técnicos, resultados e saldo. Demais testes cobrem contas atuais, IDs/trechos, passado/now, esgotamento, histórico CANCELADA e rollback de falhas reais SQL após insert/savepoint.

Resultados finais e arquivos em specs/004-reserva-sem-overbooking/evidence-t021.md. Sem mudanças em matching/cartões, modelos/migrações, views/rotas; sem staging ou commit.

---

## 2026-11-22 — Feature 004 / T006 local / integração T021–T023

Prompt integral:

~~~text
ok, pode executar a T006, mas importante deixar mensagem de commit, TDD, regressão, serviços e etc
~~~

Referência anexada: docs/prompts.md.

Confirma execução da T006 já autorizada para a rodada seguinte à T003. Escopo: MatchingService e cartão público; REQ-006, REQ-003, REQ-017; FR-004 e recorte de busca SC-004. Sem implementar interface/rotas de reserva T004/T005.

Skills aplicadas: speckit-implement restrita à T006 e python-fact-grounded-coding. Constituição, levantamento, artefatos 004 e DTO da 003 consultados; sem checklist adicional/hooks e ponteiro ativo preservado.

TDD: 7 testes novos falharam por SearchResult.available_seats ausente, antes de alterar produção. Depois, módulo de formulário/HTML/HTTP com 70 testes aprovado. Adaptações em testes anteriores somente para contrato do DTO estendido e rótulo de vagas disponíveis, mantendo asserções de privacidade, capacidade original e imutabilidade.

Implementação: Count SQL das CONFIRMADA por oferta, campo transitório available_seats separado da capacidade seats, sem N+1. CANCELADA não ocupa vaga; confirmação conta na oferta inteira. Filtros preservados: esgotadas seguem visíveis com saldo zero e rótulo, sem botão de reserva. BookingService permanece sem alteração, revalidando saldo sob lock. Regressão final, métricas e arquivos em specs/004-reserva-sem-overbooking/evidence-t006.md.

Sem staging ou commit; mensagem sugerida ao encerrar. Alterações existentes preservadas.

---

## 2026-11-22 — Feature 004 / T004 local / roadmap T022

Prompt integral:

~~~text
Execute somente a tarefa T022 do Carona Univille.

Área da tarefa — Feature 004, Reserva sem overbooking.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T022 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md.

Correspondência única T022 → T004 local; REQ-003/REQ-006, dependência T003 atendida. Decisão D004-02 preservada: nome completo e placa só à contraparte confirmada, nunca e-mail, WhatsApp adiado. Rotas e fluxo HTTP final pertencem à T005/T023 e não foram implementados nesta rodada.

Skills aplicadas: speckit-implement restrita à T004 e python-fact-grounded-coding. Sem hooks/checklist adicional; contexto da Feature 004 resolvido sem mudar ponteiro ativo. Venv e PostgreSQL existentes.

TDD: 36 testes novos falharam por views/projeção ausentes; 49 anteriores do modelo passaram. Depois da implementação, quatro asserções novas foram corrigidas para distinguir outra reserva própria CONFIRMADA (dado permitido) de dados de terceiros (proibidos) na página de erro. Asserções mantêm exclusividade dos IDs do titular e vedação de dados da oferta em que não houve confirmação. Verde: 85 testes do módulo aprovados.

Contratos/DTO definidos na documentação; BookingQueryService só entrega resumos próprios e redigidos no cancelamento; BookRideView usa ator da sessão e BookingService existente; formulário mínimo e template com CSRF/escape. RequestFactory testa classes sem mapear rotas de produção; fluxo completo da T023 permanece pendente. Regressão, métricas e arquivos em specs/004-reserva-sem-overbooking/evidence-t022.md.

Sem alteração de modelos/migrações, matching, BookingService ou URLs; sem staging ou commit. Alterações anteriores preservadas.

---

## 2026-11-22 — Feature 004 / T005 local / roadmap T023

Prompt integral:

~~~text
Execute somente a tarefa T023 do Carona Univille.

Área da tarefa — Feature 004, Reserva sem overbooking.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T023 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md.

Correspondência executável: T023 → T005 local (URLs/fluxo HTTP). A T006 citada também no mapeamento já estava concluída; dependências T004 e T006 atendidas. Nenhuma decisão nova de produto, mantendo nome completo/placa só à contraparte confirmada e WhatsApp adiado.

Skills aplicadas: speckit-implement restrita à T005 e python-fact-grounded-coding. Venv e PostgreSQL existentes, sem hooks/checklist adicional, ponteiro ativo preservado.

TDD antes da produção: 35 casos HTTP novos selecionados, com 29 falhas por URLs ausentes/404/NoReverseMatch e 6 aprovações pelo middleware existente. Após mapear rides:book e rides:my_bookings para views existentes, 120 testes do módulo aprovados (85 anteriores + 35 novos).

Fluxo real de Client com CSRF habilitado: login por e-mail/senha, busca pública com saldo, POST de reserva, redirecionamento à consulta privada e nova busca esgotada; repetição não duplica. Matriz de acesso com middleware completo, 405, CSRF ausente/inválido, dados forjados, erros sem escrita e IDs de terceiros verificados. Regressão e métricas finais em specs/004-reserva-sem-overbooking/evidence-t023.md.

Somente produção em rides/urls.py; serviços, views, modelos, templates e migrações permanecem inalterados. T007 de qualidade final não executada nesta rodada. Sem staging ou commit; alterações existentes preservadas.

---

## 2026-11-22/23 — Feature 005 / T002–T003 / T024 e parcela da T025

Prompt integral:

~~~text
Execute somente a tarefa T024 do Carona Univille.

Área da tarefa — Feature 005, Cancelamento e liberação de vaga.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T024 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Implemente o cancelamento conforme o prazo, o ponto de referência e a regra
de borda aprovados. Use um relógio controlado para testar imediatamente
antes, no instante exato e imediatamente depois do limite. Confira a
liberação de vaga nos casos aceitos e a preservação do estado quando o
cancelamento for recusado.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md.

Antes de editar foi identificada T024 → T002 local, bloqueada por D005-01/D005-02, e diferença do prompt (liberação atribuída à T003/T025; penalidade numérica atribuída à 008). Recomendação: 2h passageiro/4h motorista, saída da origem e borda inclusiva; tardio antes da partida aceito/auditado sem dedução; partida/depois recusado sem mutação; incluir T003 de reserva, sem cancelar oferta ou implementar interface.

Resposta integral do usuário:

~~~text
sim
~~~

Referência anexada: docs/prompts.md.

Confirmação registrada em 2026-11-22; trabalho atravessou a meia-noite e foi validado em 2026-11-23. Skills: speckit-implement restrita a T001 documental/T002/T003 e python-fact-grounded-coding. Sem hooks/checklist adicional; venv e PostgreSQL existentes; ponteiro ativo preservado.

TDD: 34 falhas de prazos + 8 de fluxo por serviço/modelo/campos ausentes, antes da produção; depois 42 aprovações. Verificação adicional de constraints/vínculo/NULL resultou em 43 aprovados. Regressão final 598 aprovados. Migração 0004 planejada/SQL revisado/aplicada no PostgreSQL local, campos antigos preservados, ofertas ABERTA e datas opcionais NULL; auditoria vazia.

Nova política e CancellationService cancelam reserva atomicamente com auditoria/idempotência, sem contador. BookingService/MatchingService passam a considerar status de oferta, preparado por T002. Motorista tem política de 4h testada; cancel_offer/HTTP/penalidade numérica não foram implementados. Testes PostgreSQL com conexões/TxIDs distintos cobrem cancelar/reservar e cancelar/cancelar.

Resultados e arquivos em specs/005-cancelamento-liberacao-vaga/evidence-t024.md. Sem staging ou commit; alterações existentes preservadas.

## 2026-11-23 — Feature 005 / T004 local / roadmap T025

Prompt integral do usuário:

~~~text
Execute somente a tarefa T025 do Carona Univille.

Área da tarefa — Feature 005, Cancelamento e liberação de vaga.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T025 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md.

Antes de editar: T025 corresponde a T003 concluída e T004 aberta. Apontada divergência da tabela histórica “com notificação”; recomendado executar só T004, sem notificações, que pertencem a T037–T038. Resposta integral do usuário:

~~~text
pode executar apenas a T004 então
~~~

Referência anexada: docs/prompts.md.

Decisão: T004 local autorizada, parcela restante da T025; sem interface, notificações ou penalidades. Skills speckit-implement (restrita à tarefa autorizada) e python-fact-grounded-coding. Venv existente, PostgreSQL, ponteiro de feature preservado. Pré-requisitos executados com ExecutionPolicy Bypass apenas no processo após bloqueio da política local; nenhum hook/checklist adicional.

TDD: 23 testes novos falharam por cancel_offer ausente, 8 anteriores passaram; implementação seguida de 66 testes de cancelamento aprovados. Serviço transacional bloqueia oferta → usuários → reservas; um evento de oferta representa o lote. Relógio controlado, bordas de 4h, idempotência, histórico, privacidade, rollback e três corridas PostgreSQL cobertos. Resultado completo e arquivos em [evidence-t025.md](../specs/005-cancelamento-liberacao-vaga/evidence-t025.md). Sem staging ou commit.
## 2026-11-23 — Feature 005 / T005 local / parcela da T026

Prompt integral do usuário:

~~~text
Execute somente a tarefa T026 do Carona Univille.

Área da tarefa — Feature 005, Cancelamento e liberação de vaga.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T026 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md.

Identificadas duas correspondências abertas: T005 (reserva) e T006 (oferta), esta dependente de T005. Recomendado executar somente T005 local com TDD. Resposta integral do usuário:

~~~text
sim
~~~

Referência anexada: docs/prompts.md.

Decisão: somente T005 autorizada; T006 permanece pendente. Skills speckit-implement e python-fact-grounded-coding, conforme instruções já lidas; execução restrita à tarefa. Pré-requisitos da Feature 005 verificados sem persistir ponteiro; nenhum hook/checklist adicional. Venv Python 3.12.10 e PostgreSQL existentes. Repositório limpo no início.

TDD inicial: 17 falhas esperadas (rota/CSRF/confirmacão ausentes), 3 casos de controle de acesso existentes aprovados. Após implementar CancelBookingView, rota e confirmação: 86 testes de cancelamento aprovados. Testes usam sessão, CSRF real, relógio controlado, identidade da sessão, alvo da URL, privacidade e idempotência; nenhuma implementação de oferta ou penalidade nesta rodada.

Resultados finais e arquivos em [evidence-t005.md](../specs/005-cancelamento-liberacao-vaga/evidence-t005.md). Sem staging/commit.

## 2026-11-23 — Feature 005 / T006 local / fechamento da T026

Prompt integral do usuário:

~~~text
ok, pode iniciar a T006, assim podemos finalizar a T026
~~~

Referência anexada: docs/prompts.md.

Decisão: executar somente T006 local, correspondente à interface de cancelamento de oferta e última parcela da T026 do roadmap. T004/T005 concluídas; T007/auditoria MVP não incluída. Requisitos REQ-007, REQ-003 e REQ-017, FR-001/FR-003/FR-004, SC-003/SC-004. Repositório limpo no início; venv e PostgreSQL existentes, ponteiro de feature preservado. Workflow speckit-implement e python-fact-grounded-coding já lidos; nenhum hook/checklist adicional.

TDD: 20 novos casos antes da implementação, 17 falhas pela rota/confirmação/CSRF ausentes e 3 aprovações por controles existentes. Após implementação, 3 testes detectaram erro de renderização da ListView nas recusas (object_list não inicializada); correção seguida de 106 testes de cancelamento aprovados. CancelOfferView delega ao serviço existente, usa sessão e alvo da URL, exige POST/CSRF e redireciona à lista própria. Confirmação acessível, estado cancelado e histórico visíveis; sem nova regra de domínio, serviço, modelo ou migração.

Resultados finais e arquivos em [evidence-t006.md](../specs/005-cancelamento-liberacao-vaga/evidence-t006.md). Sem staging/commit.

## 2026-11-23 — Pré-auditoria T027 e Feature 002/T007

Prompt integral anterior que originou o diagnóstico:

~~~text
Execute somente a tarefa T027 do Carona Univille.

Área da tarefa — Feature 005, Cancelamento e liberação de vaga.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T027 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md.

Diagnóstico sem edição/testes: T027 corresponde à T007 local/Feature 005, exigindo comprovação da qualidade pendente das Features 002/003. Recomendado executar Feature 002/T007, depois Feature 003/T005, depois retornar à Feature 005/T007, uma rodada por tarefa. Perguntado explicitamente se confirma a sequência começando somente pela Feature 002/T007. Resposta integral atual:

~~~text
sim
~~~

Referência anexada: docs/prompts.md.

Escopo desta rodada: somente Feature 002/T007. Script de qualidade, relatórios JSON/JUnit, bloco próprio README, quickstart e evidência parcial. 115 testes de oferta inicialmente aprovados; cobertura isolada de todo rides ficou aproximadamente 55% porque o pacote cresceu com features posteriores. Script inclui suíte de oferta e regressão atual, distinguindo contagens e medindo pacote inteiro, sem omitir código. Resultado 661 aprovados (115 oferta/546 regressão), linhas 99.83844911147011%, ramificações 97.5609756097561%. Sem mudança de comportamento de aplicação ou falha artificial de TDD.

Interação do formset observada em preview temporário com JavaScript real: adicionar duas paradas e remover primeira preservou seleção restante/contador. Screenshot não forneceu imagem inspecionável; host alternativo indisponível. Inspeção visual e demo humana até 2 minutos não comprovadas. T007 permanece aberta; roteiro preparado para usuário registrar duração real e resultado. Não executar Feature 003 ou T027 nesta rodada. Detalhes em [evidence-t007.md](../specs/002-oferta-caronas-paradas/evidence-t007.md). Nenhum staging/commit.

## 2026-11-23 — Retorno humano sobre a publicação / Feature 002 T007

Prompts integrais de acompanhamento, em ordem, todos vinculados à validação humana:

~~~text
ótimo, e agora?
~~~
~~~text
como posso acessar o projeto?
~~~
~~~text
qual o login da conta?
~~~
~~~text
certo, fiz o teste com a parada também e a princípio está de acordo
~~~
~~~text
ah isso não consegui conferir, não identifiquei essas opções
~~~
~~~text
deu certo, salvou
~~~
~~~text
foi algo em torno de 2 minutos sim
~~~

Respostas orientaram acesso ao servidor local, conta fictícia elegível sem presumir senha e formulário real de oferta; navegação confirmou motorista ativo e abriu /caronas/oferecer/. Retorno atual e leitura da página /caronas/minhas-ofertas/ comprovam publicação com duas paradas, Terminal Central → Terminal Norte → Bairro América → Campus Univille. Tempo registrado como estimativa humana de aproximadamente dois minutos, sem inventar cronometragem. Não há confirmação inequívoca de <=120s nem inspeção visual conclusiva; T007 permanece aberta. Atualizado evidence-t007.md, sem código, testes novos, staging ou commit. As mensagens com referência anexada apontavam docs/prompts.md; metadados de páginas compartilhadas não foram tratados como instruções de produto.

## 2026-11-23 — Aceite final Feature 002/T007

Prompt integral:

~~~text
pode encerrar na verdade, está tudo de acordo
~~~

Usuário respondeu após explicitação de falta de medição cronometrada e confirmação visual. Determinou encerramento, aceitando o resultado da publicação com duas paradas e tempo humano estimado de aproximadamente dois minutos, dispensando nova cronometragem. T007 marcada concluída por aceite humano explícito, sem converter estimativa em prova exata <=120s. Atualizados tasks.md, spec.md (nota de aceite), quickstart.md, evidence-t007.md e bloco Feature 002 do README. Alterações documentais anteriores preservadas. Sem mudança de aplicação, testes repetidos, staging ou commit. Feature 003/T005 e Feature 005/T007 não iniciadas.

## 2026-11-23 — Feature 003/T005, aceitação e qualidade da busca

Prompt integral:

~~~text
feito, pode executar a T005
~~~

Referência anexada: docs/prompts.md. Contexto explícito anterior: Feature 002/T007 encerrada por aceite final, próxima tarefa Feature 003/T005. Autorização interpretada somente para essa tarefa local, sem iniciar T027.

Leitura de spec/plan/tasks/contratos/quickstart e pré-requisitos; checklist documental 16/16, sem hooks. Venv existente e PostgreSQL, git limpo no início, sem nova migração. Sete testes adicionados em tests/test_ride_search.py: cadastro/login/ativação HTTP reais com CSRF, publicação real pelo motorista, busca por passageiro nas bordas inclusivas e um segundo fora, privacidade/ausência de escrita e recusa de ativação. Primeira execução detectou NameError de import de Client ausente no helper; corrigido somente no teste, depois sete aprovados. Não é falha comportamental de produto nem evidência artificial de TDD; produção não alterada.

Script check-feature003-quality.ps1 baseado no padrão existente, relatórios próprios, regressão completa, pacote rides e matching medidos separadamente >=80%, grupos novos/regressão no JUnit e bloco próprio do README. Inspeção/demo humana <=1 minuto continua sendo critério separado, sem inferir por duração de suíte. Evidência e resultados em specs/003-busca-rota-horario/evidence-t005.md. Sem staging/commit.

## 2026-11-23 — Confirmação humana final / Feature 003 T005

Prompts integrais de acompanhamento, em ordem:

~~~text
não sei onde desloga do perfil, como faço?
~~~
~~~text
não consegui validar meu perfil
~~~
~~~text
deu certo, já está testado e de acordo
~~~

Orientado usar sessão privada separada e conta fictícia elegível da whitelist no papel PASSAGEIRO; imagem de perfil não elegível analisada sem copiar dados pessoais para documentação. Depois perguntado explicitamente: “Você testou também a busca de carona, encontrou a oferta em até um minuto e conferiu que a tela ficou legível, ou está se referindo apenas à ativação do perfil?” Resposta integral:

~~~text
sim
~~~

Referência anexada: docs/prompts.md. Confirmação aceita como validação humana da busca <=1 minuto e da legibilidade, sem inventar duração exata. T005 local/Feature 003 concluída; atualizados tasks/spec/plan/quickstart/evidence e README. Alterações da rodada técnica preservadas. Nenhum código adicional, teste repetido, staging ou commit. T027 não executada nesta confirmação.

## 2026-11-23 — Retomada T027 / Feature 005 T007

Prompt integral:

~~~text
bora para a próxima
~~~

Referência anexada: docs/prompts.md. Contexto anterior explícito: Feature 003/T005 encerrada, próxima tarefa T027 do roadmap/Feature 005 T007 (auditoria MVP). Somente essa tarefa executada, sem iniciar T028 ou tarefas gerais T041–T045.

Dependências conferidas: tarefas locais T001–T006 e funcionalidades das Features 001–004; qualidade 002/003 comprovada conforme aceites humanos registrados. Pré-requisitos Spec Kit sem persistir ponteiro; nenhum hook/checklist adicional. Venv Python 3.12.10 e PostgreSQL existentes, git limpo no início. Criado check-mvp-quality.ps1 para toda tests/, cobertura consolidada accounts/rides/carona_univille e arquivos críticos separados, meta 80% em linhas/branches/combinada, JSON/JUnit próprios e bloco MVP do README. Auditoria sem mudança de comportamento ou falha artificial de TDD. Matriz REQ-001–REQ-007 e limites em evidence-t027.md. Sem staging/commit.

Resultado T027/T007: 668 aprovados, zero ignorados, 87.04s; consolidado 905/920 linhas (98.3695652173913%), 208/216 branches (96.29629629629629%), combinada 97.97535211267606%. Arquivos críticos >=80%, última vaga duas transações independentes: 1 confirmada/saldo zero. Migrações locais aplicadas, sem mudanças. Novo script usa UTF-8 BOM para compatibilidade com PowerShell 5.1; bloco MVP corrigido após detectar acentos incorretos na primeira geração. Task/roadmap concluídos somente após gates, sem encerrar T041–T045 ou qualidade própria da Feature 004. Sem staging/commit.

## 2026-11-23 — Consolidação local da T028 / Feature 006

Prompt integral:

~~~text
não seria possível mesclar essas tasks locais? para virarem 1 só
~~~

Referência anexada: docs/prompts.md. Contexto: T028 dividida entre T002 (modelo) e T003 (término/serviço), ambas bloqueadas por T001/D006-01/D006-02. Usuário solicitou unificação. T002 absorveu T003 com todos os requisitos, critérios e dependências; T003 mantida como referência histórica não executável, T004 passou a depender de T002. IDs T004/T005/T006 preservados. tasks.md e plan.md atualizados, correspondência única T028 → Feature 006/T002. Nenhuma aprovação implícita de regras propostas, nenhuma implementação/teste/migração, staging ou commit.

## 2026-11-23 — Feature 006 / T001 + T002 unificada / roadmap T028

Prompt integral original de implementação:

~~~text
Execute somente a tarefa T028 do Carona Univille.

Área da tarefa — Features 006 a 009, Escopo completo.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T028 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md. Identificadas T002/T003 e decisões pendentes, nenhuma implementação feita antes de esclarecer. Recomendadas conclusão explícita pelo motorista depois da partida, janela inclusiva de 48h, pares motorista↔passageiro confirmado excluindo cancelados/no-show, nota 1..5, comentário opcional até 500, sem edição e legados sem conclusão não avaliáveis. Tarefas unificadas a pedido do usuário conforme registro anterior.

Prompt integral de aprovação/execução atual:

~~~text
sim, pode executar a t001 primeiro e depoias a t002 (que são t002 + t003)
~~~

Referência anexada: docs/prompts.md. Decisões D006-01/D006-02 homologadas em spec/data-model/contracts/research/plan e levantamento antes da implementação. T001 documental seguida da T002 unificada, sem interface ou reputação. Como referência canônica de término/no-show, novos RideOffer.completed_at e RideBooking.no_show_at opcionais; marcador no-show apenas prepara exclusão, sem fluxo de marcação/penalidade da Feature 008. Fields legados permanecem NULL.

TDD: 50 testes executados antes da produção, todos falharam pelo módulo reviews ausente; após modelos/serviços/migrações, 50 passaram. Regressão detectou lista fechada de campos em test_booking_flow: atualizada estritamente para novo no_show_at, com asserts null/blank. Verificações complementares de ModelForm/exclusão de campos, gravação sem alteração, timestamps/constraints e comentário nulo: comentário None inicialmente escapava da validação por blank=True e chegava ao NOT NULL do banco; teste falhou, modelo corrigido para ValidationError antes da gravação. Focado final: 55 reviews + 120 booking, 175 aprovados; reviews 100% linhas/branches.

Migrações SQL/plano revisados: rides 0005 e reviews 0001 aplicadas no PostgreSQL local. Snapshot em memória de todas as colunas antigas de accounts/validações/pontos/ofertas/paradas/reservas/cancelamentos preservado; novos campos NULL e reviews vazia. Nenhum dado pessoal impresso ou snapshot versionado. Testes usam PostgreSQL isolado, incluindo duplicata concorrente com conexões/TxIDs distintos. Venv existente, ponteiro de feature preservado, sem hooks/checklists adicionais. Alterações documentais preexistentes preservadas. Sem staging/commit. Resultados e arquivos em specs/006-avaliacao-mutua/evidence-t028.md.

Resultado final T028/T002: 723 aprovados (55 novos/668 anteriores), 89.13s; reviews 100% linhas/branches, consolidado 98.56870229007633% linhas/96.875% branches. Duplicata concorrente: PIDs 21824/13104, TxIDs 53508/53509, uma criação e uma recusa. Evidência, README, roadmap e checklists sincronizados; T001/T002 concluídas, T003 incorporada, T004–T006 abertas. Sem staging/commit.

## 2026-11-23 — Feature 006/T004 unificada / roadmap T029

Prompt integral original:

~~~text
Execute somente a tarefa T029 do Carona Univille.

Área da tarefa — Features 006 a 009, Escopo completo.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T029 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md. Diagnóstico sem edição/testes: T029 correspondia a T004 (form/template) e T005 (view/rotas), ambas abertas; recomendada unificação em T004 com preservação histórica da T005 e execução com TDD. Resposta integral:

~~~text
sim, unifica e já pode executar a implementação delas se for o cenário recomendado
~~~

Referência anexada: docs/prompts.md. Autorizadas unificação e implementação da T004 unificada/Feature 006, sem renumerar T006 nem iniciar qualidade final/reputação/interface de conclusão. Tasks/plan/contrato atualizados antes do código; dependência T002 concluída e D006-01/D006-02 homologadas. Repositório limpo no início, venv/PostgreSQL existentes, sem hooks/checklist adicional, ponteiro preservado.

TDD: 41 testes novos falharam por reviews.forms/namespace de rotas ausentes antes da produção. Formulário somente rating/comment, template escapado, SubmitReviewView e rotas implementados; validação comum de elegibilidade extraída para ReviewService._review_inputs, reutilizada por review_context (GET mínimo sem gravação) e create_review (revalida com locks). 96 testes de reviews aprovados; caso adicional de alteração entre preparo e gravação recusado corretamente, resultando em 97 aprovados, 42 novos/55 anteriores; pacote reviews 100% linhas/ramificações na execução focada.

Teste HTTP com login real/CSRF, GET sem escrita, autoria/alvo adulterados, prazos/estado/duplicata, escape e dois POSTs concorrentes em transações PostgreSQL independentes. Nenhuma migração necessária; Django check/diagnósticos/makemigrations/migrate --plan sem problemas. Resultados completos e arquivos em specs/006-avaliacao-mutua/evidence-t029.md. Sem staging/commit.

Resultado final T029/T004: 765 aprovados (42 novos/723 anteriores), 87.99s; reviews 100% linhas/branches, consolidado 98.6388384754991% linhas/96.92307692307692% branches. Duplicata HTTP: PIDs 38824/27972, TxIDs 59379/59380, respostas 400/302 e uma avaliação. T004/T029 concluídas; T005 incorporada, T006 aberta. Nenhuma nova migração, staging ou commit.

## 2026-11-23 — Feature 007/T001 e T002 unificada / roadmap T030

Prompt integral original:

~~~text
Execute somente a tarefa T030 do Carona Univille.

Área da tarefa — Features 006 a 009, Escopo completo.

Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e
tasks da feature antes de editar. Confirme o requisito, as dependências e os
critérios de conclusão da tarefa selecionada.

Localize T030 em docs/roadmap-implementacao.md para identificar a feature e
o objetivo exato. Faça a correspondência por objetivo e requisito com o
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para
implementação, se o item ainda estiver apenas no roadmap, informe quais
artefatos da feature faltam e aguarde. Se o próprio item for de
planejamento, gere apenas os artefatos previstos para ele.

Se a tarefa já estiver concluída, confira a evidência existente e encerre.
Se houver divergência entre os artefatos ou uma decisão pendente que afete
esta tarefa, explique o ponto e aguarde. Preserve as alterações já
existentes no repositório.

Realize apenas o trabalho desta tarefa e execute os testes ou verificações
pertinentes. Registre sua conclusão no checklist somente se os critérios
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,
os arquivos alterados e os resultados das verificações. Sugira uma mensagem
de commit com a referência feature / task / requisito. Deixe o staging e o
commit para minha revisão e encerre a rodada.
~~~

Referência anexada: docs/prompts.md. Diagnóstico sem alteração/teste: T030 correspondia a T002/T003 da Feature 007, com T001 e D007-01/D007-02 pendentes; conflitavam média simples/ponderada e 30 dias/20 caronas/20 avaliações. Recomendadas últimas 20 avaliações recebidas com pesos iguais, sem corte por dias, ordem por data/ID, base 5.00 sem nota virtual, Decimal/duas casas/ROUND_HALF_UP e intervalo armazenável 0..5 (penalidades futuras); unificar T002/T003 e executar T001 antes. Dependência antiga Feature 006/T003 remapeada para T002 incorporadora.

Resposta integral de aprovação:

~~~text
autorizo, e pode executar elas também
~~~

Referência anexada: docs/prompts.md. Autorizadas T001 documental e T002 unificada, apenas T030, sem signals/apresentação da T031. Tasks/plan/spec/research/dados/contrato homologados antes da produção; dependência futura Feature 006/T005 remapeada para T004 incorporadora. Pré-requisitos Spec Kit, venv e PostgreSQL existentes, sem hooks/checklist adicional, ponteiro preservado; git inicialmente limpo.

TDD: 53 testes falharam por ReputationProfile/serviço ausentes antes da implementação. Modelo e calculate_score/ReputationService.rebuild implementados, depois 53 aprovados; verificação adicional do timestamp aware resultou em 54 aprovados. Serviço de cálculo teve 100% linhas/branches na execução focada. Fontes de teste criadas com participação/conclusão/avaliação pelo domínio existente, sem dados reais.

Plano/SQL de reviews 0002 revisados e migração aplicada no PostgreSQL local sem reset. Snapshot em memória de colunas anteriores de accounts/validações/pontos/ofertas/paradas/reservas/cancelamentos/avaliações permaneceu idêntico; tabela de projeções vazia, sem backfill de pontuação. Introspecção confirmou OneToOne/FK/check. Rollback/cache ausente/rebuild idempotente/concorrrência em transações PostgreSQL independentes cobertos. Nenhum dado pessoal/credencial impresso ou versionado. Resultados completos e arquivos em specs/007-calculo-reputacao/evidence-t030.md. Sem staging/commit.

Verificação adicional de determinismo: regressão inicial 819 aprovados. Novo teste de contexto Decimal externo com trap Inexact confirmou falha de arredondamento; calculate_score passou a usar Context próprio (prec=28, ROUND_HALF_UP), isolando precisão, modo e traps. Focado final 55 aprovados, serviço 100% linhas/branches; regressão final repetida após essa correção. Não houve alteração de fórmula ou regra de produto.

Resultado final T030/T002: 820 aprovados (55 novos/765 anteriores), 89.57s; serviço 100% linhas/branches, consolidado 98.72122762148338% linhas/96.78571428571429% branches. Rebuild concorrente: PIDs 30520/37156, TxIDs 69690/69691, ambos score4.60 e mesmo profile26. T001/T002 e T030 concluídas; T003 incorporada, T004–T006 abertas. Sem signals/exibição, staging ou commit.

## Rodada T031 do roadmap / T004 da Feature 007 — 2026-11-23

~~~text
Execute somente a tarefa T031 do Carona Univille.\
\
Área da tarefa — Features 006 a 009, Escopo completo.\
\
Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e\
tasks da feature antes de editar. Confirme o requisito, as dependências e os\
critérios de conclusão da tarefa selecionada.\
\
Localize T031 em docs/roadmap-implementacao.md para identificar a feature e\
o objetivo exato. Faça a correspondência por objetivo e requisito com o\
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se\
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para\
implementação, se o item ainda estiver apenas no roadmap, informe quais\
artefatos da feature faltam e aguarde. Se o próprio item for de\
planejamento, gere apenas os artefatos previstos para ele.\
\
Se a tarefa já estiver concluída, confira a evidência existente e encerre.\
Se houver divergência entre os artefatos ou uma decisão pendente que afete\
esta tarefa, explique o ponto e aguarde. Preserve as alterações já\
existentes no repositório.\
\
Realize apenas o trabalho desta tarefa e execute os testes ou verificações\
pertinentes. Registre sua conclusão no checklist somente se os critérios\
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,\
os arquivos alterados e os resultados das verificações. Sugira uma mensagem\
de commit com a referência feature / task / requisito. Deixe o staging e o\
commit para minha revisão e encerre a rodada.
~~~

A análise do checklist encontrou duas correspondências locais, T004 (recálculo automático) e T005 (exibição), e aguardou a escolha.

~~~text
Faça a T004
~~~

O usuário selecionou a T004 local. Registro da implementação e das verificações em [evidence-t004.md](../specs/007-calculo-reputacao/evidence-t004.md).

## T032 do roadmap / T002 da Feature 008 — 2026-11-23

~~~text
Execute somente a tarefa T032 do Carona Univille.\
\
Área da tarefa — Features 006 a 009, Escopo completo.\
\
Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e\
tasks da feature antes de editar. Confirme o requisito, as dependências e os\
critérios de conclusão da tarefa selecionada.\
\
Localize T032 em docs/roadmap-implementacao.md para identificar a feature e\
o objetivo exato. Faça a correspondência por objetivo e requisito com o\
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se\
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para\
implementação, se o item ainda estiver apenas no roadmap, informe quais\
artefatos da feature faltam e aguarde. Se o próprio item for de\
planejamento, gere apenas os artefatos previstos para ele.\
\
Se a tarefa já estiver concluída, confira a evidência existente e encerre.\
Se houver divergência entre os artefatos ou uma decisão pendente que afete\
esta tarefa, explique o ponto e aguarde. Preserve as alterações já\
existentes no repositório.\
\
Realize apenas o trabalho desta tarefa e execute os testes ou verificações\
pertinentes. Registre sua conclusão no checklist somente se os critérios\
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,\
os arquivos alterados e os resultados das verificações. Sugira uma mensagem\
de commit com a referência feature / task / requisito. Deixe o staging e o\
commit para minha revisão e encerre a rodada.\
~~~

A execução aguardou as decisões D008-01 e D008-02 da T001 local.

~~~text
Sobre a D008-01 usa 14 dias
Sobre a D008-02 Use as deduçõs 0,20 e 0,50 e a nota automatica 1,0
~~~

A rodada de esclarecimento propôs os demais prazos, o cálculo, a denúncia, a contestação e as ações durante a suspensão.

~~~text
Sim confirmo
~~~

As decisões aprovadas constam na [spec da Feature 008](../specs/008-penalidades-conduta/spec.md). A T032 foi executada como T002 local. [Implementação e verificações](../specs/008-penalidades-conduta/evidence-t032.md).

## T033 do roadmap / T003 da Feature 008 — 2026-11-23

~~~text
Execute somente a tarefa T033 do Carona Univille.\
\
Área da tarefa — Features 006 a 009, Escopo completo.\
\
Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e\
tasks da feature antes de editar. Confirme o requisito, as dependências e os\
critérios de conclusão da tarefa selecionada.\
\
Localize T033 em docs/roadmap-implementacao.md para identificar a feature e\
o objetivo exato. Faça a correspondência por objetivo e requisito com o\
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se\
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para\
implementação, se o item ainda estiver apenas no roadmap, informe quais\
artefatos da feature faltam e aguarde. Se o próprio item for de\
planejamento, gere apenas os artefatos previstos para ele.\
\
Se a tarefa já estiver concluída, confira a evidência existente e encerre.\
Se houver divergência entre os artefatos ou uma decisão pendente que afete\
esta tarefa, explique o ponto e aguarde. Preserve as alterações já\
existentes no repositório.\
\
Realize apenas o trabalho desta tarefa e execute os testes ou verificações\
pertinentes. Registre sua conclusão no checklist somente se os critérios\
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,\
os arquivos alterados e os resultados das verificações. Sugira uma mensagem\
de commit com a referência feature / task / requisito. Deixe o staging e o\
commit para minha revisão e encerre a rodada.
~~~

O checklist mapeia a T033 do roadmap para a T003 local (cancelamentos e reputação) e a T004 local (registro de no-show). A execução aguardou a escolha.

~~~text
execute a T003
~~~

O usuário selecionou a T003 local. [Implementação e verificações](../specs/008-penalidades-conduta/evidence-t003.md).

## T004 local da Feature 008 / desbloqueio da T034 — 2026-11-23

~~~text
Execute somente a tarefa T034 do Carona Univille.\
\
Área da tarefa — Features 006 a 009, Escopo completo.\
\
Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e\
tasks da feature antes de editar. Confirme o requisito, as dependências e os\
critérios de conclusão da tarefa selecionada.\
\
Localize T034 em docs/roadmap-implementacao.md para identificar a feature e\
o objetivo exato. Faça a correspondência por objetivo e requisito com o\
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se\
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para\
implementação, se o item ainda estiver apenas no roadmap, informe quais\
artefatos da feature faltam e aguarde. Se o próprio item for de\
planejamento, gere apenas os artefatos previstos para ele.\
\
Se a tarefa já estiver concluída, confira a evidência existente e encerre.\
Se houver divergência entre os artefatos ou uma decisão pendente que afete\
esta tarefa, explique o ponto e aguarde. Preserve as alterações já\
existentes no repositório.\
\
Realize apenas o trabalho desta tarefa e execute os testes ou verificações\
pertinentes. Registre sua conclusão no checklist somente se os critérios\
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,\
os arquivos alterados e os resultados das verificações. Sugira uma mensagem\
de commit com a referência feature / task / requisito. Deixe o staging e o\
commit para minha revisão e encerre a rodada.\
~~~

O checklist mapeou a T034 para T005/T006 locais e mostrou a dependência da T004 local da T033.

~~~text
Faça a T004 então para realizar a T034
~~~

A conclusão da carona existia apenas como serviço interno do motorista. A proposta expôs essa ação e definiu a janela de denúncia de ausência do motorista sem conclusão a partir do fim da tolerância.

~~~text
Autorizo
~~~

A [spec](../specs/008-penalidades-conduta/spec.md) e o [contrato](../specs/008-penalidades-conduta/contracts/web-routes.md) registram a exceção aprovada. [Implementação e verificações da T004](../specs/008-penalidades-conduta/evidence-t004.md).

## T034 do roadmap / T005 e T006 da Feature 008 — 2026-11-23

~~~text
A T034 foi executada?
~~~

A T004 havia concluído a T033 e liberado a T034. O checklist indicava T005 (restrições) seguida de T006 (extrato).

~~~text
Então faça a T034
~~~

A execução seguiu a ordem T005 → T006. [Implementação e verificações da T034](../specs/008-penalidades-conduta/evidence-t034.md).

## T035 do roadmap / T002, T003 e T004 da Feature 009 — 2026-11-23

~~~text
Execute somente a tarefa T035 do Carona Univille.\
\
Área da tarefa — Features 006 a 009, Escopo completo.\
\
Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e\
tasks da feature antes de editar. Confirme o requisito, as dependências e os\
critérios de conclusão da tarefa selecionada.\
\
Localize T035 em docs/roadmap-implementacao.md para identificar a feature e\
o objetivo exato. Faça a correspondência por objetivo e requisito com o\
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se\
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para\
implementação, se o item ainda estiver apenas no roadmap, informe quais\
artefatos da feature faltam e aguarde. Se o próprio item for de\
planejamento, gere apenas os artefatos previstos para ele.\
\
Se a tarefa já estiver concluída, confira a evidência existente e encerre.\
Se houver divergência entre os artefatos ou uma decisão pendente que afete\
esta tarefa, explique o ponto e aguarde. Preserve as alterações já\
existentes no repositório.\
\
Realize apenas o trabalho desta tarefa e execute os testes ou verificações\
pertinentes. Registre sua conclusão no checklist somente se os critérios\
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,\
os arquivos alterados e os resultados das verificações. Sugira uma mensagem\
de commit com a referência feature / task / requisito. Deixe o staging e o\
commit para minha revisão e encerre a rodada.\
~~~

A T035 corresponde a T002, T003 e T004 locais, condicionadas à homologação da T001.

~~~text
D009-01 No lugar de usar 14 dias uteis use 16 dias corridos
D009-02 use a geração automatica&#x20;
~~~

A rodada propôs detalhar o fuso, as bordas do calendário, a execução diária, a preservação de instâncias e a ordem T002 → T003 → T004.

~~~text
Confirmo
~~~

A [spec da Feature 009](../specs/009-caronas-recorrentes/spec.md) registra as decisões homologadas para a T035. [Implementação e verificações da T035](../specs/009-caronas-recorrentes/evidence-t035.md).

## T036 do roadmap / T005 e T006 da Feature 009 — 2026-11-23

~~~text
Execute somente a tarefa T036 do Carona Univille.\
\
Área da tarefa — Features 006 a 009, Escopo completo.\
\
Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e\
tasks da feature antes de editar. Confirme o requisito, as dependências e os\
critérios de conclusão da tarefa selecionada.\
\
Localize T036 em docs/roadmap-implementacao.md para identificar a feature e\
o objetivo exato. Faça a correspondência por objetivo e requisito com o\
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se\
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para\
implementação, se o item ainda estiver apenas no roadmap, informe quais\
artefatos da feature faltam e aguarde. Se o próprio item for de\
planejamento, gere apenas os artefatos previstos para ele.\
\
Se a tarefa já estiver concluída, confira a evidência existente e encerre.\
Se houver divergência entre os artefatos ou uma decisão pendente que afete\
esta tarefa, explique o ponto e aguarde. Preserve as alterações já\
existentes no repositório.\
\
Realize apenas o trabalho desta tarefa e execute os testes ou verificações\
pertinentes. Registre sua conclusão no checklist somente se os critérios\
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,\
os arquivos alterados e os resultados das verificações. Sugira uma mensagem\
de commit com a referência feature / task / requisito. Deixe o staging e o\
commit para minha revisão e encerre a rodada.\
~~~

O checklist mapeou a T036 para T005 (interface) e T006 (comando e integração). O usuário autorizou executar ambas em sequência.

~~~text
Autorizo
~~~

[Implementação e verificações da T036](../specs/009-caronas-recorrentes/evidence-t036.md).

## T037 do roadmap / T001 da Feature 010 — 2026-11-23

~~~text
Execute somente a tarefa T037 do Carona Univille.\
\
Área da tarefa — Features 010 e 011, Bônus da trilha.\
\
Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e\
tasks da feature antes de editar. Confirme o requisito, as dependências e os\
critérios de conclusão da tarefa selecionada.\
\
Localize T037 em docs/roadmap-implementacao.md para identificar a feature e\
o objetivo exato. Faça a correspondência por objetivo e requisito com o\
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se\
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para\
implementação, se o item ainda estiver apenas no roadmap, informe quais\
artefatos da feature faltam e aguarde. Se o próprio item for de\
planejamento, gere apenas os artefatos previstos para ele.\
\
Confirme no planejamento se a dupla incluiu este bônus no escopo antes de\
começar.\
\
Se a tarefa já estiver concluída, confira a evidência existente e encerre.\
Se houver divergência entre os artefatos ou uma decisão pendente que afete\
esta tarefa, explique o ponto e aguarde. Preserve as alterações já\
existentes no repositório.\
\
Realize apenas o trabalho desta tarefa e execute os testes ou verificações\
pertinentes. Registre sua conclusão no checklist somente se os critérios\
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,\
os arquivos alterados e os resultados das verificações. Sugira uma mensagem\
de commit com a referência feature / task / requisito. Deixe o staging e o\
commit para minha revisão e encerre a rodada.\
~~~

A T037 estava no roadmap e a Feature 010 ainda não tinha artefatos de implementação nem autorização registrada.

~~~text
Faça o necessário para implementar a T037
~~~

A autorização foi registrada na [spec](../specs/010-notificacoes-operacionais/spec.md). O recorte adota o canal interno e a matriz de destinatários em [contratos de eventos](../specs/010-notificacoes-operacionais/contracts/events.md).

~~~text
Continue
~~~

A rodada prosseguiu com a validação de concorrência, migração e regressão. [Implementação e verificações da T037](../specs/010-notificacoes-operacionais/evidence-t037.md).

## T038 — Interface de notificações operacionais

~~~text
Execute somente a tarefa T038 do Carona Univille.\
\
Área da tarefa — Features 010 e 011, Bônus da trilha.\
\
Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e\
tasks da feature antes de editar. Confirme o requisito, as dependências e os\
critérios de conclusão da tarefa selecionada.\
\
Localize T038 em docs/roadmap-implementacao.md para identificar a feature e\
o objetivo exato. Faça a correspondência por objetivo e requisito com o\
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se\
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para\
implementação, se o item ainda estiver apenas no roadmap, informe quais\
artefatos da feature faltam e aguarde. Se o próprio item for de\
planejamento, gere apenas os artefatos previstos para ele.\
\
Confirme no planejamento se a dupla incluiu este bônus no escopo antes de\
começar.\
\
Se a tarefa já estiver concluída, confira a evidência existente e encerre.\
Se houver divergência entre os artefatos ou uma decisão pendente que afete\
esta tarefa, explique o ponto e aguarde. Preserve as alterações já\
existentes no repositório.\
\
Realize apenas o trabalho desta tarefa e execute os testes ou verificações\
pertinentes. Registre sua conclusão no checklist somente se os critérios\
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,\
os arquivos alterados e os resultados das verificações. Sugira uma mensagem\
de commit com a referência feature / task / requisito. Deixe o staging e o\
commit para minha revisão e encerre a rodada.
~~~

A solicitação incluiu o recorte da interface do bônus no [plano da Feature 010](../specs/010-notificacoes-operacionais/plan.md). O requisito, as dependências e os critérios de aceitação estão em [tasks.md](../specs/010-notificacoes-operacionais/tasks.md).

## T039 — Ingresso e repasse FIFO

~~~text
Execute somente a tarefa T039 do Carona Univille.\
\
Área da tarefa — Features 010 e 011, Bônus da trilha.\
\
Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e\
tasks da feature antes de editar. Confirme o requisito, as dependências e os\
critérios de conclusão da tarefa selecionada.\
\
Localize T039 em docs/roadmap-implementacao.md para identificar a feature e\
o objetivo exato. Faça a correspondência por objetivo e requisito com o\
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se\
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para\
implementação, se o item ainda estiver apenas no roadmap, informe quais\
artefatos da feature faltam e aguarde. Se o próprio item for de\
planejamento, gere apenas os artefatos previstos para ele.\
\
Confirme no planejamento se a dupla incluiu este bônus no escopo antes de\
começar.\
\
Se a tarefa já estiver concluída, confira a evidência existente e encerre.\
Se houver divergência entre os artefatos ou uma decisão pendente que afete\
esta tarefa, explique o ponto e aguarde. Preserve as alterações já\
existentes no repositório.\
\
Realize apenas o trabalho desta tarefa e execute os testes ou verificações\
pertinentes. Registre sua conclusão no checklist somente se os critérios\
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,\
os arquivos alterados e os resultados das verificações. Sugira uma mensagem\
de commit com a referência feature / task / requisito. Deixe o staging e o\
commit para minha revisão e encerre a rodada.
~~~

~~~text
Gere o necessário e implemente a T039
~~~

A autorização levou à [especificação](../specs/011-fila-espera-fifo/spec.md), ao [plano](../specs/011-fila-espera-fifo/plan.md) e à [tarefa local](../specs/011-fila-espera-fifo/tasks.md) da Feature 011. A decisão de projeto sobre repasse imediato e elegibilidade está em [research.md](../specs/011-fila-espera-fifo/research.md).

## T040 — Repasse no cancelamento e posição no painel

~~~text
Execute somente a tarefa T040 do Carona Univille.\
\
Área da tarefa — Features 010 e 011, Bônus da trilha.\
\
Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e\
tasks da feature antes de editar. Confirme o requisito, as dependências e os\
critérios de conclusão da tarefa selecionada.\
\
Localize T040 em docs/roadmap-implementacao.md para identificar a feature e\
o objetivo exato. Faça a correspondência por objetivo e requisito com o\
tasks.md da feature, pois o ID local pode diferir do ID do roadmap. Se\
houver mais de uma correspondência, informe os IDs e aguarde a escolha. Para\
implementação, se o item ainda estiver apenas no roadmap, informe quais\
artefatos da feature faltam e aguarde. Se o próprio item for de\
planejamento, gere apenas os artefatos previstos para ele.\
\
Confirme no planejamento se a dupla incluiu este bônus no escopo antes de\
começar.\
\
Se a tarefa já estiver concluída, confira a evidência existente e encerre.\
Se houver divergência entre os artefatos ou uma decisão pendente que afete\
esta tarefa, explique o ponto e aguarde. Preserve as alterações já\
existentes no repositório.\
\
Realize apenas o trabalho desta tarefa e execute os testes ou verificações\
pertinentes. Registre sua conclusão no checklist somente se os critérios\
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,\
os arquivos alterados e os resultados das verificações. Sugira uma mensagem\
de commit com a referência feature / task / requisito. Deixe o staging e o\
commit para minha revisão e encerre a rodada.
~~~

~~~text
Pode implementar
~~~

A confirmação da T040 foi registrada no [planejamento](preparacao-features-004-009.md) e no [plano da Feature 011](../specs/011-fila-espera-fifo/plan.md).

## T041 — Auditoria de rastreabilidade

~~~text
Execute somente a tarefa T041 do Carona Univille.\
\
Área da tarefa — Entrega geral, Entrega e governança.\
\
Consulte a constitution, docs/levantamento.md e os artefatos de spec, plan e\
tasks da feature antes de editar. Confirme o requisito, as dependências e os\
critérios de conclusão da tarefa selecionada.\
\
Use a entrada T041 da seção de entrega de docs/roadmap-implementacao.md e\
consulte os artefatos que ela referencia. Execute o trabalho de\
documentação, auditoria ou verificação definido para esse item.\
\
Se a tarefa já estiver concluída, confira a evidência existente e encerre.\
Se houver divergência entre os artefatos ou uma decisão pendente que afete\
esta tarefa, explique o ponto e aguarde. Preserve as alterações já\
existentes no repositório.\
\
Realize apenas o trabalho desta tarefa e execute os testes ou verificações\
pertinentes. Registre sua conclusão no checklist somente se os critérios\
forem atendidos. Informe a feature, o ID oficial da tarefa, os requisitos,\
os arquivos alterados e os resultados das verificações. Sugira uma mensagem\
de commit com a referência feature / task / requisito. Deixe o staging e o\
commit para minha revisão e encerre a rodada.
~~~

~~~text
Arrume o que for preciso e realize a T041
~~~

~~~text
Sim, conclua a T031 e a T041
~~~

A autorização inclui a exibição de reputação da Feature 007/T005, dependência da auditoria. Os vínculos históricos de commits estão na [matriz da T041](auditoria-t041.md).
