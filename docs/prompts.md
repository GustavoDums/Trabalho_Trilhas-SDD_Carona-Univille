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


---

## P005 — Emenda à Constitution com a Stack Aprovada ##

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

- **Artefato Alterado**: `.specify/memory/constitution.md`
- **Versão Resultante**: `1.1.0` (Minor Bump)
- **Decisões Associadas**: Homologação da stack oficial (Python 3.12+, Django, Django Templates HTML/CSS, PostgreSQL, pytest, pytest-django, pytest-cov). Manutenção pendente de aprovação do professor e domínios reais.
