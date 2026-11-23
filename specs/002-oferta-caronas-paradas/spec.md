# Feature Specification: Oferta de caronas com paradas

**Feature Branch**: `002-oferta-caronas-paradas` (identificador da feature; nenhuma branch criada)
**Created**: 2026-11-22
**Status**: Draft — especificação pronta para revisão e planejamento
**Input**: “pode fazer a feature 2 então”, após recomendação de definir itinerário por marcos, coletar veículo na primeira oferta e criar apenas a especificação.

## Contexto, decisões e rastreabilidade

Esta feature atende a **REQ-004** de [levantamento](../../docs/levantamento.md), com **REQ-002** (motorista com vínculo ativo) e **REQ-003** (minimização e privacidade), conforme a [constitution](../../.specify/memory/constitution.md).

A autorização desta rodada adota as recomendações discutidas: itinerário discreto e ordenado de bairros/marcos conhecidos de Joinville, sem coordenadas ou mapas; modelo, cor e placa exigidos na primeira publicação de oferta, sem acrescentar esses dados ao cadastro acadêmico. A placa fica privada, com eventual liberação à contraparte somente após reserva confirmada em feature futura.

Correspondência com o [roadmap](../../docs/roadmap-implementacao.md): T013 (identidade da oferta e paradas), T014 (publicação), T015 (consulta das próprias ofertas) e T016 (aceitação). Esses IDs continuam sendo referências do roadmap; os IDs oficiais locais e sua correspondência constam em [tasks.md](tasks.md). A T013 não foi implementada nesta rodada.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Publicar oferta com itinerário (Priority: P1)

Como motorista com vínculo ativo, quero informar meu trajeto, horário e vagas para disponibilizar uma oferta acadêmica com paradas na ordem da viagem.

**Why this priority**: Entrega o núcleo de REQ-004 e a informação necessária às futuras busca e reserva.

**Independent Test**: Publicar uma oferta sintética e consultá-la novamente, verificando autoria, trajeto, horário, vagas e veículo.

**Acceptance Scenarios**:

1. **Given** motorista ativo com veículo informado, **When** publica Terminal Central → Bairro América → Campus Univille com saída futura e 3 vagas, **Then** uma oferta é criada, vinculada ao motorista autenticado, com uma parada intermediária na posição correta. (REQ-004; FR-001–FR-006)
2. **Given** motorista ativo, **When** publica origem e destino distintos sem paradas intermediárias, **Then** a oferta é aceita com itinerário direto. (REQ-004; FR-003)
3. **Given** visitante, conta pendente ou passageiro ativo, **When** tenta publicar, **Then** nenhuma oferta é criada; visitante segue para login, pendente para ativação e passageiro recebe recusa de permissão. (REQ-002; FR-001)
4. **Given** motorista ativo, **When** envia autoria de outra conta, **Then** a autoria continua sendo exclusivamente a conta autenticada. (REQ-002, REQ-003; FR-002)

### User Story 2 - Informar veículo e corrigir dados inválidos (Priority: P2)

Como motorista, quero registrar os dados mínimos do veículo e corrigir erros antes da publicação, evitando ofertas incompletas ou inconsistentes.

**Why this priority**: Identifica o transporte e assegura que a oferta publicada represente uma viagem utilizável.

**Independent Test**: Submeter dados válidos e inválidos e confirmar que uma falha não cria oferta ou paradas parciais.

**Acceptance Scenarios**:

1. **Given** motorista sem veículo informado, **When** tenta publicar sem modelo, cor ou placa, **Then** recebe os erros dos campos faltantes e nenhuma oferta é publicada; ao completar os campos, pode publicar. (REQ-004, REQ-003; FR-007)
2. **Given** formulário preenchido, **When** vagas são zero, negativas ou fracionárias, horário não é futuro, origem e destino coincidem ou um ponto está vazio, **Then** os dados são rejeitados com orientação e sem publicação parcial. (REQ-004; FR-004–FR-006, FR-008)
3. **Given** várias paradas, **When** uma delas é inválida, **Then** a oferta inteira é rejeitada, mantendo os demais valores não sensíveis disponíveis para correção. (REQ-004; FR-008)

### User Story 3 - Consultar minhas ofertas com privacidade (Priority: P3)

Como motorista ativo, quero rever minhas ofertas e a sequência das paradas, sem acessar dados privados de outros motoristas.

**Why this priority**: Permite confirmar o resultado da publicação e oferece gestão inicial da autoria.

**Independent Test**: Criar ofertas para dois motoristas sintéticos e verificar que cada um consulta somente as próprias.

**Acceptance Scenarios**:

1. **Given** motorista com duas ofertas, **When** abre minhas ofertas, **Then** vê ambas em ordem crescente de saída, com origem, paradas na sequência, destino, horário, vagas e modelo/cor; nenhuma oferta alheia aparece. (REQ-004, REQ-003; FR-009)
2. **Given** motorista sem ofertas, **When** abre a consulta, **Then** vê estado vazio e indicação de como publicar. (REQ-004; FR-009)
3. **Given** motorista consultando suas ofertas, **When** envia identificador de outro motorista, **Then** o conjunto exibido continua restrito à própria conta; e-mails e placas alheios nunca aparecem. (REQ-003; FR-010)

### Edge Cases

- Espaços externos são ignorados; origem, destino e paradas usam um catálogo comum de pontos, evitando variações textuais para o mesmo local.
- Pontos não pertencentes ao catálogo são rejeitados. Não são coletados endereços residenciais exatos ou localização contínua.
- Origem e destino precisam ser distintos; pontos repetidos em qualquer posição do itinerário são rejeitados nesta versão, que não contempla circuitos.
- Zero paradas é válido. A ordem escolhida é preservada após publicação e nova consulta; não é reordenada alfabeticamente.
- Saída exatamente no instante da submissão é inválida: a partida precisa ser estritamente futura. O usuário vê o fuso de referência de Joinville.
- Uma vaga significa um passageiro, excluindo o motorista. Não há reservas nesta feature; vagas disponíveis inicialmente equivalem às ofertadas.
- Campos obrigatórios vazios ou somente com espaços são rejeitados. Valores de vaga não inteiros são rejeitados, mesmo quando visualmente numéricos.
- Uma falha ao concluir publicação não deixa oferta, veículo associado àquela oferta ou paradas parcialmente publicadas.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: Somente conta autenticada de papel MOTORISTA e vínculo ATIVA pode publicar e consultar suas ofertas; demais estados recebem o tratamento descrito em US1. (REQ-002)
- **FR-002**: A autoria deriva exclusivamente da conta autenticada, sem aceitar substituição enviada pelo usuário. (REQ-002, REQ-003)
- **FR-003**: Cada oferta contém origem, destino e zero ou mais paradas intermediárias, formando uma sequência única e ordenada. (REQ-004)
- **FR-004**: Pontos são selecionados de catálogo discreto de bairros/marcos públicos de Joinville, são distintos no itinerário e não podem estar vazios. (REQ-004, REQ-003)
- **FR-005**: Cada oferta contém data e horário de saída estritamente futuros, apresentados no fuso de Joinville. (REQ-004)
- **FR-006**: Vagas ofertadas são um inteiro positivo de lugares para passageiros; o motorista não ocupa uma dessas vagas. (REQ-004)
- **FR-007**: Antes da primeira publicação, modelo, cor e placa do veículo precisam ser informados. Cada oferta publicada conserva os dados do veículo utilizado nela; uma oferta posterior pode reutilizar dados previamente informados sem alterar ofertas anteriores. (REQ-004, REQ-003)
- **FR-008**: Publicação grava a oferta completa ou não publica nada. Dados inválidos recebem erros específicos, sem publicação parcial. (REQ-004)
- **FR-009**: Motoristas consultam somente suas ofertas, ordenadas por saída crescente e, em empate, ordem de criação, com itinerário na sequência e vagas ofertadas. A lista vazia é informativa. (REQ-004)
- **FR-010**: E-mail institucional nunca é exibido a terceiros. A placa só é acessível ao próprio motorista nesta feature; eventual acesso da contraparte depende de reserva confirmada em feature futura. (REQ-003)
- **FR-011**: A consulta de próprias ofertas não permite editar, excluir ou cancelar ofertas nesta versão. Busca, matching, reserva e cancelamento são features separadas. (REQ-004; limite de escopo)

### Key Entities *(include if feature involves data)*

- **Oferta de carona**: autoria acadêmica, origem, destino, saída, vagas para passageiros, dados do veículo e paradas ordenadas. Representa uma publicação única.
- **Parada intermediária**: ponto público e posição na oferta; pertence a uma única oferta.
- **Ponto de itinerário**: referência de bairro ou marco no catálogo compartilhado, com identidade estável e nome de exibição.
- **Dados do veículo da oferta**: modelo, cor e placa estritamente necessários à identificação do transporte. A organização técnica desses dados será definida no plano.

### Visibilidade e finalidade dos dados

| Dado | Finalidade | Acesso nesta feature | Limite para features futuras |
| --- | --- | --- | --- |
| Origem, destino, paradas, saída e vagas | Descrever viagem e capacidade | Motorista autor ativo | Consulta por acadêmicos ativos será tratada na busca |
| Modelo e cor | Identificar transporte | Motorista autor ativo | Podem aparecer na busca futura |
| Placa | Identificação após confirmação | Somente motorista autor | Contraparte apenas após reserva confirmada |
| Nome do motorista | Autoria e segurança | Nome próprio na gestão | Pré-reserva somente nome abreviado; completo após confirmação |
| E-mail institucional | Identidade da conta | Uso interno da sessão | Nunca exibido a terceiros |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das ofertas válidas nos cenários de teste conservam autor, horário, vagas, veículo e ordem integral do itinerário após nova consulta.
- **SC-002**: 100% das tentativas inválidas e não autorizadas previstas nos cenários são recusadas sem publicação parcial.
- **SC-003**: 100% das consultas de minhas ofertas excluem ofertas de outros motoristas, inclusive ao manipular identificadores enviados.
- **SC-004**: Nenhum cenário expõe e-mail institucional ou placa a terceiros; todos os testes e demonstrações usam dados fictícios.
- **SC-005**: Na demonstração com dados já definidos, um motorista consegue publicar uma oferta com duas paradas e conferir a sequência em até 2 minutos.

## Assumptions

- A Feature 001 fornece identidade, papel fixo e estado acadêmico; suas decisões permanecem vigentes.
- A autorização para iniciar esta especificação adotou os dois padrões recomendados: pontos discretos e dados do veículo antes da primeira publicação. Regras adicionais abaixo são premissas desta versão para revisão, não alegações de decisões anteriores da dupla.
- Catálogo inicial pequeno, com pontos públicos conhecidos e sem entrada livre. Sua composição e identificadores serão documentados no planejamento, sem dependência de serviço de mapas.
- Itinerários sem repetição de pontos; vagas positivas sem teto arbitrário de produto nesta especificação. Não há estimativa automática de percurso ou horário individual por parada; regras de matching e tolerância continuam pendentes para a Feature 003.
- Uma oferta tem um veículo; não há gestão independente de frota, comprovação documental de veículo ou validação contra cadastros reais. Placa deve estar preenchida; convenções de normalização serão detalhadas no plano sem prometer verificação externa.
- Retenção, edição e cancelamento não ganham novos fluxos nesta rodada. Não há coleta de telefone, avaliações, penalidades, recorrência, notificações ou lista de espera.
- As pendências constitucionais de validação simulada e domínios institucionais continuam abertas. A escolha de pontos discretos nesta feature não resolve a janela de matching nem prazos de cancelamento.
- A especificação foi produzida antes do planejamento. Plano, modelo de dados técnico, contratos e tarefas locais estão agora documentados nesta pasta, sem implementação da T013 do roadmap.
## Aceite final do usuário — 2026-11-23

Após esclarecer a ausência de cronometragem exata e confirmação visual, o usuário determinou: “pode encerrar na verdade, está tudo de acordo”. Essa aprovação encerra a inspeção visual e aceita, para esta rodada, o relato humano de aproximadamente dois minutos sem exigir nova execução cronometrada. T007 concluída por aceite explícito, com ressalva documental: não existe medição exata que demonstre <=120s. Não converter estimativa em duração exata ou duração de teste automatizado.

Os registros parciais anteriores são históricos e substituídos por este aceite quanto ao estado da tarefa. Resultado técnico: 661 testes aprovados (115 oferta/546 regressão), linhas 99.83844911147011%, ramificações 97.5609756097561%. Encerramento documental, sem rerodar testes, staging ou commit. Feature 003/T005 e Feature 005/T007 não iniciadas.
