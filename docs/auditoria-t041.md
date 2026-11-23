# T041 — Auditoria de rastreabilidade da entrega

**Requisitos** REQ-014 e REQ-015 · **Data** 2026-11-23 · **Escopo** Entrega geral.

## Resultado da inspeção

A base auditada foi `15eb425c7588390e3a55b9bf3ff2271a5614f1e1`, com 52 commits alcançáveis. A matriz inclui os 45 que alteram a aplicação, sua configuração, testes ou scripts de qualidade. Todos os 45 apontam para tarefas identificáveis e requisitos formais. Um usa o prefixo literal `feat(Txxx):`. Os outros 44 usam prefixos com feature e tarefa local, como `feat(011/T002):` e `fix(001/T006):`. O registro dessa equivalência preserva o histórico publicado e segue o requisito de identificação explícita do [Princípio V](../.specify/memory/constitution.md) e do [REQ-015](levantamento.md).

Os itens T002–T012 da Feature 001 foram confrontados com o checklist local e seus registros de validação. A T031 reúne o recálculo automático já entregue no commit `0ef95da` e a exibição da nota autorizada nesta rodada, validada com 992 testes. Os 40 itens anteriores à T041 constam como concluídos no roadmap. [Checklist da Feature 001](../specs/001-cadastro-validacao-perfis/tasks.md) · [Evidência da exibição](../specs/007-calculo-reputacao/evidence-t005.md).

A matriz confere os commits existentes na base indicada. A exibição da nota está na árvore de trabalho para revisão e deve ser registrada com a referência `T031 / Feature 007 / T005 local / REQ-009 / REQ-003 / REQ-017`.

## Critério e reprodução

Para commits históricos, a identidade é a combinação de feature e tarefa local declarada no assunto ou no corpo. O prefixo com apenas a tarefa é resolvido pela feature declarada na própria mensagem. Para commits novos de funcionalidade, usar `feat(Txxx): ...` com a tarefa do roadmap no prefixo e a feature, a tarefa local e os requisitos na mensagem. Correções, testes e scripts podem usar `fix`, `test` ou `chore` com as mesmas referências.

```powershell
git log --oneline 15eb425c7588390e3a55b9bf3ff2271a5614f1e1
git log --format="%h %s" 15eb425c7588390e3a55b9bf3ff2271a5614f1e1 -- accounts rides reviews notifications carona_univille manage.py requirements.txt .env.example tests scripts pytest.ini
git show -s --format="%B" 559617b
git diff --check
```

A lista por caminho inclui migrações, interfaces, testes e scripts de qualidade. Os sete commits fora do recorte alteram documentação, planejamento, relatórios ou a instalação do Spec Kit. Para verificar uma linha da matriz, use `git show --stat <hash>` e compare a mensagem e os arquivos com o checklist apontado. Cada identificador local é resolvido no checklist da feature correspondente.

## Matriz de commits

Os requisitos abaixo são os que aparecem na mensagem de cada commit. O checklist vinculado registra os critérios de aceite e pode listar requisitos transversais adicionais. O travessão indica uma tarefa de qualidade local sem item próprio no roadmap.

| Commit | Tarefa local | Roadmap | Requisitos na mensagem |
| --- | --- | --- | --- |
| `e040cde` | [001 / T001](../specs/001-cadastro-validacao-perfis/tasks.md) | T001 | REQ-014, REQ-018 |
| `298fe70` | [001 / T002](../specs/001-cadastro-validacao-perfis/tasks.md) | T002 | REQ-001, REQ-002, REQ-003 |
| `0046d73` | [001 / T003](../specs/001-cadastro-validacao-perfis/tasks.md) | T003 | REQ-002, REQ-003 |
| `90dd17f` | [001 / T004](../specs/001-cadastro-validacao-perfis/tasks.md) | T004 | REQ-001, REQ-002 |
| `b849e31` | [001 / T005](../specs/001-cadastro-validacao-perfis/tasks.md) | T005 | REQ-001, REQ-002 |
| `fd52490` | [001 / T006](../specs/001-cadastro-validacao-perfis/tasks.md) | T006 | REQ-001, REQ-003 |
| `7f0174c` | [001 / T007](../specs/001-cadastro-validacao-perfis/tasks.md) | T007 | REQ-002 |
| `b1dfd78` | [001 / T008](../specs/001-cadastro-validacao-perfis/tasks.md) | T008 | REQ-002 |
| `a0a6908` | [001 / T009](../specs/001-cadastro-validacao-perfis/tasks.md) | T009 | REQ-002, REQ-003 |
| `7ee8960` | [001 / T010](../specs/001-cadastro-validacao-perfis/tasks.md) | T010 | REQ-002, REQ-003 |
| `70a7fde` | [001 / T011](../specs/001-cadastro-validacao-perfis/tasks.md) | T011 | REQ-002 |
| `fc8f586` | [001 / T012](../specs/001-cadastro-validacao-perfis/tasks.md) | T012 | REQ-018, REQ-019 |
| `1838b1d` | [002 / T001–T002](../specs/002-oferta-caronas-paradas/tasks.md) | T013 | REQ-004, REQ-002, REQ-003 |
| `f7fc24a` | [002 / T003](../specs/002-oferta-caronas-paradas/tasks.md) | T014 | REQ-004 |
| `ba63751` | [002 / T004](../specs/002-oferta-caronas-paradas/tasks.md) | T014 | REQ-004, REQ-003 |
| `feb142c` | [002 / T005](../specs/002-oferta-caronas-paradas/tasks.md) | T015 | REQ-004, REQ-003 |
| `ff36e3a` | [002 / T006](../specs/002-oferta-caronas-paradas/tasks.md) | T016 | REQ-004, REQ-017 |
| `559617b` | [003 / T001–T003](../specs/003-busca-rota-horario/tasks.md) | T017–T018 | REQ-003, REQ-005 |
| `f00377d` | [003 / T004](../specs/003-busca-rota-horario/tasks.md) | T019 | REQ-005, REQ-017 |
| `cfdb815` | [004 / T002](../specs/004-reserva-sem-overbooking/tasks.md) | T020 | REQ-006 |
| `7f637da` | [004 / T003](../specs/004-reserva-sem-overbooking/tasks.md) | T021 | REQ-006 |
| `6b15523` | [004 / T006](../specs/004-reserva-sem-overbooking/tasks.md) | T021 e T023 | REQ-006 |
| `acd63f1` | [004 / T004](../specs/004-reserva-sem-overbooking/tasks.md) | T022 | REQ-003, REQ-006 |
| `06911b4` | [004 / T005](../specs/004-reserva-sem-overbooking/tasks.md) | T023 | REQ-006, REQ-017 |
| `f890327` | [005 / T002–T003](../specs/005-cancelamento-liberacao-vaga/tasks.md) | T024–T025 | REQ-007 |
| `79e8f0d` | [005 / T004](../specs/005-cancelamento-liberacao-vaga/tasks.md) | T025 | REQ-007, REQ-003, REQ-017 |
| `7082c11` | [005 / T005](../specs/005-cancelamento-liberacao-vaga/tasks.md) | T026 | REQ-007, REQ-003, REQ-017 |
| `d2f3496` | [005 / T006](../specs/005-cancelamento-liberacao-vaga/tasks.md) | T026 | REQ-007, REQ-003, REQ-017 |
| `c020c86` | [002 / T007](../specs/002-oferta-caronas-paradas/tasks.md) | — | REQ-004, REQ-018, REQ-019 |
| `21c40dc` | [003 / T005](../specs/003-busca-rota-horario/tasks.md) | — | REQ-005, REQ-003, REQ-017, REQ-018, REQ-019 |
| `a27249f` | [005 / T007](../specs/005-cancelamento-liberacao-vaga/tasks.md) | T027 | REQ-001–REQ-007, REQ-014–REQ-019 |
| `03acb7f` | [006 / T002](../specs/006-avaliacao-mutua/tasks.md) | T028 | REQ-008, REQ-003, REQ-017 |
| `485346d` | [006 / T004](../specs/006-avaliacao-mutua/tasks.md) | T029 | REQ-008, REQ-003, REQ-017 |
| `77fb847` | [007 / T002](../specs/007-calculo-reputacao/tasks.md) | T030 | REQ-009, REQ-003, REQ-017 |
| `0ef95da` | [007 / T004](../specs/007-calculo-reputacao/tasks.md) | T031 (recálculo) | REQ-003, REQ-009, REQ-017 |
| `d6b6087` | [008 / T002](../specs/008-penalidades-conduta/tasks.md) | T032 | REQ-010, REQ-003, REQ-017 |
| `29a9eab` | [008 / T003](../specs/008-penalidades-conduta/tasks.md) | T033 | REQ-007, REQ-010 |
| `488b0d7` | [008 / T004](../specs/008-penalidades-conduta/tasks.md) | T033 | REQ-010, REQ-003, REQ-017 |
| `07e8f0f` | [008 / T005–T006](../specs/008-penalidades-conduta/tasks.md) | T034 | REQ-010, REQ-003, REQ-017 |
| `c481af4` | [009 / T002–T004](../specs/009-caronas-recorrentes/tasks.md) | T035 | REQ-011, REQ-003, REQ-017 |
| `401f8ea` | [009 / T005–T006](../specs/009-caronas-recorrentes/tasks.md) | T036 | REQ-011, REQ-003, REQ-017 |
| `7391f22` | [010 / T001](../specs/010-notificacoes-operacionais/tasks.md) | T037 | REQ-012, REQ-003, REQ-017 |
| `e37f92e` | [010 / T002](../specs/010-notificacoes-operacionais/tasks.md) | T038 | REQ-012 / REQ-002 / REQ-003 / REQ-017 |
| `fc79494` | [011 / T001](../specs/011-fila-espera-fifo/tasks.md) | T039 | REQ-013 / REQ-017 |
| `15eb425` | [011 / T002](../specs/011-fila-espera-fifo/tasks.md) | T040 | REQ-007 / REQ-013 / REQ-017 |
