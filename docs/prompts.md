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

Referência anexada: `docs/prompts.md`.

### Resolução do quickstart

O agente recomendou corrigir a referência a perfil público para perfil próprio
com prévia abreviada e substituir a contagem por coleta por resultados efetivos.
Resposta do usuário:

pode fazer o recomendado

Referência anexada: `docs/prompts.md`.

Artefatos: script de qualidade, quickstart, relatórios de cobertura e execução,
README e tasks. Comportamento da aplicação preservado; alterações preexistentes
preservadas. Sem staging ou commit.