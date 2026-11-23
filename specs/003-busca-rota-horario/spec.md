# Feature Specification: Busca por rota e horário

**Feature Branch**: `003-busca-rota-horario` (identificador; nenhuma branch criada)
**Created**: 2026-11-22
**Status**: Draft — regras temporais confirmadas, pronta para planejamento
**Input**: “com base neste projeto até o momento, crie a feature 3 com as informações presentes no projeto”.

## Contexto e rastreabilidade

Requisito principal **REQ-005**, apoiado por **REQ-002** (acesso acadêmico), **REQ-003** (privacidade) e **REQ-017** (testes de matching), conforme [levantamento](../../docs/levantamento.md) e [constitution](../../.specify/memory/constitution.md).

A Feature 001 fornece identidade, papel fixo e ativação. A [Feature 002](../002-oferta-caronas-paradas/spec.md) fornece ofertas, catálogo comum de pontos públicos, origem/destino, paradas ordenadas, horário de saída e veículo. A busca consulta essas informações sem criar reservas ou modificar ofertas.

O [roadmap](../../docs/roadmap-implementacao.md) atribui T017 ao algoritmo e testes de ordem/janela, T018 ao formulário e cartões privados e T019 à busca integrada. Os IDs oficiais locais e a correspondência com o roadmap constam em [tasks.md](tasks.md). Nenhuma dessas implementações é entregue por esta especificação.

## Clarifications

### Session 2026-11-22
- Após recomendação explícita de ±30 minutos fixos com bordas inclusivas e comparação pela saída da origem, o usuário autorizou: “pode fazer com base no que considera recomendado para o projeto”. Ambas as opções são adotadas. Não há horário estimado por parada, campo de tolerância ajustável ou implementação entregue nesta rodada.
## User Scenarios & Testing *(mandatory)*

### User Story 1 - Encontrar trajeto compatível (Priority: P1)

Como passageiro com vínculo ativo, quero selecionar embarque, desembarque e horário desejado para encontrar ofertas cujo trajeto percorra esses pontos na ordem correta.

**Why this priority**: Entrega a busca por rota de REQ-005, reutilizando ofertas já publicadas.

**Independent Test**: Preparar ofertas sintéticas com rotas distintas e comparar resultados para embarques/desembarques nos extremos e nas paradas.

**Acceptance Scenarios**:

1. **Given** oferta Terminal Central → Terminal Norte → Bairro América → Campus Univille, **When** passageiro busca Terminal Norte → Campus Univille e a oferta satisfaz a regra temporal confirmada, **Then** a oferta aparece; a posição do embarque é anterior à do desembarque. (FR-001–FR-004)
2. **Given** a mesma oferta, **When** busca Bairro América → Terminal Norte, **Then** a oferta não aparece, mesmo se o horário for compatível. (FR-003)
3. **Given** a mesma oferta, **When** busca origem → destino ou uma parada anterior → outra posterior, **Then** o trajeto é compatível, sujeito ao filtro de horário. (FR-003)
4. **Given** trajeto direto sem paradas, **When** busca sua origem → destino, **Then** a oferta pode aparecer sem exigir uma parada intermediária. (FR-003)
5. **Given** pontos iguais, ausentes ou não pertencentes ao catálogo, **When** solicita busca, **Then** recebe erro de entrada e nenhuma lista de dados privados é exposta. (FR-002)

### User Story 2 - Filtrar pela janela de horário (Priority: P2)

Como passageiro, quero limitar resultados ao horário desejado e compreender qual horário da oferta está sendo comparado.

**Why this priority**: Um trajeto correto fora da janela não atende ao pedido; a referência temporal precisa ser explícita para não induzir erro.

**Independent Test**: Usar instantes controlados e ofertas no centro, nos limites e imediatamente fora da janela. Critérios numéricos usam a janela fixa de ±30 minutos e a saída da origem, confirmadas pelo usuário.

**Acceptance Scenarios**:

1. **Given** horário desejado 08:00 e janela fixa de ±30 minutos, **When** horários de referência são 07:30, 08:00 e 08:30, **Then** todos são temporalmente compatíveis, com limites inclusivos. (FR-004)
2. **Given** a mesma janela, **When** horários de referência são 07:29:59 ou 08:30:01, **Then** ambos são incompatíveis. (FR-004)
3. **Given** busca atravessando meia-noite, **When** uma oferta pertence ao dia anterior/seguinte mas seu instante está dentro da janela, **Then** a comparação considera a data completa, sem cortar a janela no início/fim do dia. (FR-006)
4. **Given** embarque intermediário, **When** a busca usa saída da origem como referência confirmada, **Then** a interface informa que não é previsão de passagem na parada. Não estima nem compara horário de passagem no ponto intermediário. (FR-005)
5. **Given** horário inválido ou ausente, **When** pesquisa, **Then** recebe erro explicativo, sem converter silenciosamente para outro instante. (FR-002, FR-006)

### User Story 3 - Consultar resultados com privacidade (Priority: P3)

Como passageiro ativo, quero ver as informações necessárias para comparar ofertas sem receber dados confidenciais do motorista.

**Why this priority**: Dá utilidade à busca sem romper as regras de minimização já adotadas.

**Independent Test**: Conferir conteúdo dos resultados de dois motoristas e acesso de visitante, pendente e motorista.

**Acceptance Scenarios**:

1. **Given** várias ofertas compatíveis, **When** busca, **Then** aparecem em ordem crescente do horário de saída, com desempate por criação e identificador da oferta, preservando a ordem real das paradas. Cada oferta aparece uma única vez. (FR-007)
2. **Given** oferta compatível, **When** o cartão é exibido, **Then** mostra nome abreviado do motorista, trajeto, data/horário de saída, vagas ofertadas, modelo/cor e a referência temporal da busca; não contém nome completo, e-mail nem placa em texto, atributos ocultos ou dados incorporados. (FR-008)
3. **Given** nenhuma oferta compatível, **When** busca, **Then** vê estado vazio e pode ajustar a consulta, sem receber ofertas incompatíveis como se fossem resultados. (FR-009)
4. **Given** visitante ou conta pendente, **When** tenta pesquisar, **Then** vai ao login ou ativação, respectivamente; motorista ativo recebe recusa de permissão na busca destinada ao papel PASSAGEIRO. (FR-001)
5. **Given** um motorista deixou de ter vínculo ativo ou oferta já partiu, **When** passageiro pesquisa, **Then** essa oferta não aparece, ainda que trajeto e janela coincidam. (FR-010)

### Edge Cases

- Itinerário lógico é origem + paradas intermediárias na posição registrada + destino. Não ordenar pontos por nome ou identificador; igualdade de nomes não substitui identidade do catálogo.
- Embarque e desembarque precisam existir no mesmo itinerário e satisfazer `i < j`. Ordem invertida, mesmo ponto e ponto ausente não são compatíveis. Destino final não pode ser embarque sem ponto posterior.
- Zero paradas é uma oferta válida. Várias combinações compatíveis dentro da mesma oferta não a duplicam no resultado.
- Comparar data e horário completos no fuso apresentado, America/Sao_Paulo; duas representações do mesmo instante precisam produzir a mesma classificação.
- Partida exatamente no instante atual não é futura e não aparece. A disponibilidade é consultada novamente a cada busca; não se promete reserva ou manutenção da oferta vista.
- Não existe campo de tolerância customizável nesta versão. A janela de ±30 minutos é fixa; parâmetros enviados pelo cliente não ampliam nem reduzem essa janela.
- Nenhuma busca altera ofertas, paradas, usuários ou cria reservas. Vagas são as ofertadas; ainda não há cálculo de lugares reservados.
- Não fabricar avaliação/reputação: o roadmap menciona nota, mas essa informação depende das features posteriores de avaliação/reputação, que ainda não existem.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: A busca desta feature DEVE ser acessível somente a contas autenticadas, tecnicamente habilitadas, de papel PASSAGEIRO e vínculo ATIVA. Visitante vai ao login, pendente à ativação e motorista ativo recebe recusa de permissão. (REQ-002, REQ-005)
- **FR-002**: O passageiro DEVE informar embarque e desembarque distintos do catálogo existente e data/horário desejado válidos; entradas inválidas recebem erros específicos e não expõem resultados indevidos. (REQ-005)
- **FR-003**: Uma oferta só é compatível por rota se contém ambos os pontos no itinerário e a posição de embarque é estritamente menor que a de desembarque, incluindo extremos e zero ou mais paradas. (REQ-005, REQ-017)
- **FR-004**: A oferta DEVE satisfazer a janela fixa e inclusiva de 30 minutos antes até 30 minutos depois do instante desejado: H_desejado − 30 min ≤ H_saida_origem ≤ H_desejado + 30 min. Não há tolerância configurável pelo usuário. (REQ-005, REQ-017)
- **FR-005**: O horário comparado DEVE ser a saída da origem da oferta, inclusive quando o embarque escolhido é intermediário. A interface DEVE informar explicitamente que a janela é relativa à saída da origem e não representa previsão de passagem na parada. (REQ-005, REQ-003)
- **FR-006**: A janela DEVE comparar instantes completos com data e fuso, incluindo limites e mudanças de dia. Formulário e resultados informam o fuso de Joinville. (REQ-005)
- **FR-007**: Resultados DEVEM ser únicos por oferta e ordenados por saída crescente, depois criação e identificador; a apresentação do itinerário conserva a sequência das paradas. (REQ-005)
- **FR-008**: Cartões DEVEM mostrar somente nome abreviado, trajeto público, saída, vagas ofertadas e modelo/cor. Não expor nome completo, e-mail ou placa do motorista; não inventar nota de reputação. (REQ-003)
- **FR-009**: A interface DEVE distinguir estado inicial ainda não pesquisado de consulta válida sem resultados, permitindo corrigir filtros. (REQ-005)
- **FR-010**: Somente ofertas com partida estritamente futura, vagas ofertadas positivas e motorista tecnicamente habilitado com papel MOTORISTA e vínculo ATIVA podem aparecer. (REQ-002, REQ-005)
- **FR-011**: Busca DEVE ser somente leitura; não inclui reserva, confirmação, contato, cancelamento ou notificação. A existência de resultado não garante vaga reservada. (REQ-005; limite de escopo)

### Key Entities *(include if feature involves data)*

- **Consulta de busca**: embarque, desembarque, instante desejado e janela temporal, sem persistência obrigatória de histórico de buscas.
- **Oferta consultável**: oferta da Feature 002 com dados de autoria, itinerário, saída, vagas e modelo/cor; nenhum novo tipo de viagem é introduzido.
- **Itinerário ordenado**: pontos do catálogo e suas posições no trajeto; identidade compartilhada com a Feature 002.
- **Resultado de compatibilidade**: oferta que satisfaz simultaneamente rota, tempo e elegibilidade. Não representa reserva.

### Visibilidade dos dados

| Dado | Finalidade | Visibilidade nesta feature |
| --- | --- | --- |
| Embarque, desembarque e instante desejado | Executar consulta | Passageiro que pesquisa; não criar histórico público |
| Trajeto, saída, vagas e modelo/cor | Comparar ofertas | Passageiro ativo na lista de resultados |
| Nome abreviado do motorista | Identificar autoria sem exposição integral | Passageiro ativo |
| Nome completo, e-mail e placa | Fora da necessidade da busca | Não enviados nos resultados, inclusive conteúdo oculto |
| Nota de reputação | Evolução posterior | Ausente até implementação da feature própria |

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 100% das combinações sintéticas de pontos de teste são classificadas corretamente pela regra `i < j`, inclusive rota direta, extremos e ordem invertida.
- **SC-002**: 100% dos cenários de centro, bordas inclusivas e um segundo fora da janela são classificados corretamente, inclusive ao atravessar meia-noite.
- **SC-003**: Nenhum teste de resultados revela nome completo, e-mail ou placa a terceiros; todos os dados de teste/demo são fictícios.
- **SC-004**: 100% das tentativas de acesso proibido são bloqueadas e nenhuma busca cria ou altera oferta ou reserva.
- **SC-005**: Em demonstração com filtros preparados e ofertas sintéticas, um passageiro conclui a consulta e identifica se há trajeto compatível em até 1 minuto.

## Assumptions

- Reutilizar as decisões vigentes das Features 001 e 002: papel fixo por conta, ativação, catálogo discreto e paradas ordenadas. Não ampliar acesso híbrido por suposição.
- O cadastro de ofertas registra apenas saída da origem, sem horário por parada. O exemplo de passagem no levantamento é proposta, não capacidade existente. O usuário confirmou a saída da origem como referência da PoC, com aviso explícito de que não há previsão por parada.
- Janela confirmada: ±30 minutos fixos, inclusivos. O exemplo anterior de ±15 minutos no levantamento é histórico e não rege esta feature; tolerância customizável fica fora desta versão.
- Uma consulta válida sem resultados retorna estado vazio; não relaxa filtros automaticamente. Não exigir horário desejado futuro como nova restrição: a elegibilidade temporal dos resultados já exclui partidas não futuras.
- Reputação, vagas reservadas e liberação de contato dependem de features posteriores. Não implementar nem prometer esses comportamentos nesta especificação.
- A decisão de estrutura de serviço e sua integração com a publicação existente pertence ao planejamento técnico, preservando o comportamento da Feature 002.
- Esta rodada entrega apenas spec e checklist. As duas confirmações foram registradas; plano, contratos técnicos, modelo de dados da consulta e tasks estão documentados nesta pasta, sem implementação. T017–T019 do roadmap permanecem abertas.
- Pendências constitucionais de homologação acadêmica simulada, domínios e cancelamento não são resolvidas por esta feature. As regras de matching desta spec foram confirmadas e alinhadas ao levantamento/roadmap. O texto da constitution não é emendado nesta rodada; seu marcador histórico deve ser considerado junto desta decisão documentada.