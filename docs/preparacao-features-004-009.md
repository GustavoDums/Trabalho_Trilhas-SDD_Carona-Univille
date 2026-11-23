# Preparação documental — Features 004 a 009

Data: 2026-11-22. Escopo: especificação, plano e tarefas; nenhuma implementação, migração, medição, staging ou commit.

## Arquivos entregues

Cada diretório contém spec.md, plan.md, tasks.md, research.md, data-model.md, contracts/web-routes.md e quickstart.md (42 arquivos):
- [004 — Reserva de vagas sem overbooking](../specs/004-reserva-sem-overbooking/spec.md): [plano](../specs/004-reserva-sem-overbooking/plan.md), [tarefas](../specs/004-reserva-sem-overbooking/tasks.md), [dados](../specs/004-reserva-sem-overbooking/data-model.md), [pesquisa](../specs/004-reserva-sem-overbooking/research.md), [contrato](../specs/004-reserva-sem-overbooking/contracts/web-routes.md), [quickstart](../specs/004-reserva-sem-overbooking/quickstart.md).
- [005 — Cancelamento e liberação de vaga](../specs/005-cancelamento-liberacao-vaga/spec.md): [plano](../specs/005-cancelamento-liberacao-vaga/plan.md), [tarefas](../specs/005-cancelamento-liberacao-vaga/tasks.md), [dados](../specs/005-cancelamento-liberacao-vaga/data-model.md), [pesquisa](../specs/005-cancelamento-liberacao-vaga/research.md), [contrato](../specs/005-cancelamento-liberacao-vaga/contracts/web-routes.md), [quickstart](../specs/005-cancelamento-liberacao-vaga/quickstart.md).
- [006 — Avaliação mútua pós-viagem](../specs/006-avaliacao-mutua/spec.md): [plano](../specs/006-avaliacao-mutua/plan.md), [tarefas](../specs/006-avaliacao-mutua/tasks.md), [dados](../specs/006-avaliacao-mutua/data-model.md), [pesquisa](../specs/006-avaliacao-mutua/research.md), [contrato](../specs/006-avaliacao-mutua/contracts/web-routes.md), [quickstart](../specs/006-avaliacao-mutua/quickstart.md).
- [007 — Cálculo matemático de reputação](../specs/007-calculo-reputacao/spec.md): [plano](../specs/007-calculo-reputacao/plan.md), [tarefas](../specs/007-calculo-reputacao/tasks.md), [dados](../specs/007-calculo-reputacao/data-model.md), [pesquisa](../specs/007-calculo-reputacao/research.md), [contrato](../specs/007-calculo-reputacao/contracts/web-routes.md), [quickstart](../specs/007-calculo-reputacao/quickstart.md).
- [008 — Penalidades por cancelamento tardio e no-show](../specs/008-penalidades-conduta/spec.md): [plano](../specs/008-penalidades-conduta/plan.md), [tarefas](../specs/008-penalidades-conduta/tasks.md), [dados](../specs/008-penalidades-conduta/data-model.md), [pesquisa](../specs/008-penalidades-conduta/research.md), [contrato](../specs/008-penalidades-conduta/contracts/web-routes.md), [quickstart](../specs/008-penalidades-conduta/quickstart.md).
- [009 — Caronas recorrentes](../specs/009-caronas-recorrentes/spec.md): [plano](../specs/009-caronas-recorrentes/plan.md), [tarefas](../specs/009-caronas-recorrentes/tasks.md), [dados](../specs/009-caronas-recorrentes/data-model.md), [pesquisa](../specs/009-caronas-recorrentes/research.md), [contrato](../specs/009-caronas-recorrentes/contracts/web-routes.md), [quickstart](../specs/009-caronas-recorrentes/quickstart.md).

## Mapeamento oficial por objetivo e requisito

IDs Txxx da coluna local pertencem exclusivamente à feature indicada. Preparação T001 local não corresponde à implementação funcional de outro requisito.

| Roadmap | Feature / requisito | IDs locais |
| --- | --- | --- |
| T020 | 004 / REQ-006; modelo de reserva | T002 |
| T021 | 004 / REQ-006; concorrência e disponibilidade | T003, T006 |
| T022 | 004 / REQ-003, REQ-006; interface privada | T004 |
| T023 | 004 / REQ-006; rotas e fluxo | T005, T006 |
| T024 | 005 / REQ-007; política temporal e auditoria | T002 |
| T025 | 005 / REQ-006, REQ-007; liberação e oferta | T003, T004 |
| T026 | 005 / REQ-007; interfaces de cancelamento | T005, T006 |
| T027 | 005 / REQ-014–REQ-019; auditoria MVP | T007 |
| T028 | 006 / REQ-008; modelo e elegibilidade | T002, T003 |
| T029 | 006 / REQ-008; formulário/view/rotas | T004, T005 |
| T030 | 007 / REQ-009; modelo e cálculo | T002, T003 |
| T031 | 007 / REQ-003, REQ-009; recálculo e projeção | T004, T005 |
| T032 | 008 / REQ-010; modelo e efeitos | T002 |
| T033 | 008 / REQ-007, REQ-010; cancelamento/no-show | T003, T004 |
| T034 | 008 / REQ-010; suspensão/extrato | T005, T006 |
| T035 | 009 / REQ-011; regra, geração, independência | T002, T003, T004 |
| T036 | 009 / REQ-011; formulário e CLI | T005, T006 |

São 40 tarefas locais abertas: 004=7, 005=7, 006=6, 007=6, 008=7, 009=7. Cada feature inclui preparação T001 e qualidade final; não são implementação executada nesta rodada.

## Decisões pendentes

### Feature 004

- **D004-01**: Confirmar reserva instantânea versus aceite do motorista. CONFIRMADA/CANCELADA no roadmap pressupõe fluxo instantâneo; se houver aceite, rever estados, ocupação e critérios antes da implementação.
- **D004-02**: Confirmar coleta, finalidade e visibilidade do WhatsApp: não existe telefone na conta. E-mail nunca será divulgado. Definir também seleção/persistência de embarque e desembarque; não introduzir reutilização de vaga por trecho.

### Feature 005

- **D005-01**: Confirmar 2h para passageiro, 4h para motorista, referência na saída da origem e borda inclusiva. São propostas, não critérios aprovados.
- **D005-02**: Definir se cancelamento tardio é aceito com sanção ou recusado, e comportamento após partida. T024 pede penalidade computada, cuja fórmula pertence à 008; aqui haverá somente evento auditável até a integração aprovada.

### Feature 006

- **D006-01**: Definir término verificável da viagem: oferta contém somente departure_at. Levantamento fala em conclusão do horário previsto, mas não há chegada prevista. Não equiparar partida a término. Escolher referência e responsável pelo registro antes de alterar dados.
- **D006-02**: Confirmar janela proposta de 48h, bordas, elegibilidade de cancelados/no-show e pares permitidos (proposta: motorista↔passageiro, nunca passageiro↔passageiro); fixar limite do comentário e edição/revisão.

### Feature 007

- **D007-01**: Resolver média simples versus ponderada (pesos ausentes), janela de 30 dias versus 20 caronas versus 20 avaliações; definir agregação por viagem com múltiplos passageiros e ordenação de desempate.
- **D007-02**: Homologar nota inicial 5.00, limites da pontuação, precisão/arredondamento e os exemplos numéricos do roadmap. Exemplo 4.00 pressupõe exatamente três notas 5 anteriores, não qualquer usuário com média 5.

### Feature 008

- **D008-01**: Resolver suspensão de 7 dias (roadmap) versus 14 dias (levantamento), limiar proposto de 3 faltas em 30 dias, tolerância proposta de 10min e denúncia até 2h; definir referência para paradas sem ETA.
- **D008-02**: Homologar deduções -0.20/-0.50, nota automática 1 e sua combinação sem dupla punição acidental; definir autor autorizado, evidência, contestação, limites da nota e ações bloqueadas durante suspensão.

### Feature 009

- **D009-01**: A proposta inicial de 14 dias úteis foi sucedida pela política de 15 dias úteis com calendário da BrasilAPI na Feature 009/T008. [Decisão vigente](../specs/009-caronas-recorrentes/spec.md).
- **D009-02**: Definir geração manual/periódica, autorização do comando e edição/desativação da regra. Proposta técnica: comando manual idempotente na PoC, sem scheduler externo; mudanças não alteram instâncias existentes.

## Bônus condicionados à confirmação

Não foi localizada aprovação explícita da dupla para adotar os bônus; existência no roadmap ou autorização genérica para recomendações não prova adoção. Conforme solicitação atual, não foram criados artefatos completos para:
- Feature 010 — Sistema de Notificações Operacionais, T037/T038, REQ-012. Falta confirmar adoção, canal (painel ou e-mail simulado), lembretes e gatilhos.
- Feature 011 — Fila de Espera Automática com Repasse FIFO, T039/T040, REQ-013. Falta confirmar adoção, repasse imediato ou prazo de aceite e tratamento de candidatos inelegíveis.

Esses IDs não têm correspondência local criada nesta rodada. Features 004–009 não dependem dos bônus.

**Atualização em 2026-11-23**. O usuário autorizou fazer o necessário para implementar a T037. A Feature 010 passou a ter [artefatos do Spec Kit](../specs/010-notificacoes-operacionais/spec.md) com avisos no próprio sistema. A autorização se refere à T037.

**Recorte T038**. A solicitação de execução da T038 inclui a interface de consulta e leitura do bônus da Feature 010 no escopo. A T038 depende do registro de avisos entregue na T037. [Plano da Feature 010](../specs/010-notificacoes-operacionais/plan.md).

**Recorte T039**. O usuário autorizou preparar a Feature 011 e executar a T039. O plano adota confirmação imediata e repasse ao primeiro passageiro ainda elegível, conforme as regras de reserva. [Plano da Feature 011](../specs/011-fila-espera-fifo/plan.md).

**Recorte T040**. O usuário autorizou integrar o repasse ao cancelamento e exibir a posição ao passageiro titular. As dependências T024 e T039 estão concluídas. [Plano da Feature 011](../specs/011-fila-espera-fifo/plan.md).

## Divergências e limites de implementação

- Roadmap diz fechar decisões antes de tasks.md. A instrução atual autoriza documentar as partes seguras e dúvidas: gerados checklists preliminares com T001 bloqueante, sem tratar decisões como homologadas.
- T025 usa incremento de vagas; RideOffer.seats representa capacidade original. Plano adota disponibilidade derivada de reservas confirmadas, sem incrementar capacidade.
- T024 pede penalidade computada antes da Feature 008: 005 registra classificação/evento; dedução depende da 008. Aceite final dessa parte requer política e integração aprovadas.
- T030 mistura média simples/ponderada e caronas/avaliações; exemplos ficam condicionais.
- T032 propõe 7 dias; levantamento propõe 14. Nenhum prazo escolhido.
- Contato WhatsApp e término de viagem não existem no modelo atual. Propostas não são campos já implementados.
- Feature 003 ainda está documental, inclusive transformação de rides/services.py em pacote. Dependências registradas não são prova de conclusão.
- T041/T042 são auditorias gerais de commits/prompts; T043 consolida métricas finais; T044/T045 são pitch/demo. Não criar tarefas locais para concluí-las aqui. A referência de T043 a todas as 11 features depende de confirmação dos bônus e deve ser conciliada no planejamento da entrega.

## Verificação documental e próximo passo

Conferir requisitos/SC/decisões entre spec, plan e tasks; existência dos documentos/links; IDs locais únicos, checkboxes novos abertos e cobertura T020–T036; git diff --check e preservação de fontes anteriores. Não rodar pytest ou migrações para produzir evidência fictícia de documentos.

Próximo passo: dupla homologar decisões por feature, atualizar os contratos condicionais e executar uma tarefa local por rodada. Não há declaração de prontidão integral enquanto os gates de produto permanecerem abertos.


## Resultado da conferência desta rodada

- 42 documentos nas seis features; spec/plan/tasks e quatro artefatos auxiliares em cada uma.
- 40 checkboxes abertos, sem IDs repetidos dentro da feature; todos os FR e campos canônicos citados pelas tarefas.
- Mapeamento completo dos 17 itens T020–T036; T037–T040 explicitamente adiados por ausência de confirmação.
- Links relativos resolvidos, contextos e pré-requisitos Spec Kit conferidos nas seis features sem persistir outro ponteiro ativo.
- Nenhum teste de produto ou migração executado; comandos do quickstart descrevem validação futura.
- Revisão semântica: 12 decisões de produto pendentes (duas por feature), com gates explícitos. Não há declaração de implementação integralmente pronta.
- Fontes e alterações anteriores preservadas; somente novos documentos e acréscimo de auditoria de prompts nesta rodada.
