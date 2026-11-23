# Data Model: Cálculo matemático de reputação

D007-01/D007-02 homologadas em 2026-11-23, T001/T002 unificada autorizadas.

## Campos canônicos

- ReputationProfile.user: OneToOne AUTH_USER_MODEL PROTECT, related_name reputation_profile, obrigatório/único. Sem criação automática em cadastro ou avaliação nesta T030; rebuild explícito cria se ausente.
- ReputationProfile.score: DecimalField(max_digits=3, decimal_places=2), default Decimal('5.00'), validadores e CheckConstraint intervalo inclusivo 0.00..5.00. Rejeitar float/bool, NaN/infinito e precisão além de duas casas na validação, sem truncar silenciosamente. Zero é armazenamento permitido para futura penalidade; média atual não aplica penalidades.
- ReputationProfile.computed_at: DateTimeField aware opcional null/blank, default None; None indica profile ainda não reconstruído. Rebuild grava exatamente instante de referência capturado uma vez, convertido a UTC.

Sem contador novo. Profile é cache reconstruível; histórico canônico é RideReview. Migração cria tabela vazia, sem backfill de notas ou alteração de usuários/avaliações existentes.

## Fórmula e seleção

calculate_score(ratings) recebe conjunto já selecionado com até 20 notas inteiras 1..5; rejeita bool/float/texto/fração e mais de 20 itens. Vazio retorna Decimal('5.00'). Média exata em Decimal com contexto local de precisão 28 e quantize('0.01', ROUND_HALF_UP) somente ao final. A base inicial não entra na média.

ReputationService.rebuild(*, user_id, at=None) é operação interna atômica. Se at ausente captura timezone.now uma vez após lock do usuário; exige datetime aware e normaliza UTC. Bloquear AcademicUser, inclusive quando profile ausente; depois profile. Ler RideReview recebidas (reviewed_user_id), created_at <= referência, order_by('-created_at','-id')[:20]. Cada avaliação conta, inclusive múltiplos passageiros da mesma oferta, sem peso por viagem ou expiração de 30 dias. Não reclassificar retrospectivamente avaliações imutáveis por mudanças atuais de vínculo/cancelamento. Calcular novamente das fontes persistidas, nunca somar delta.

Atualizar/criar profile e computed_at na mesma transação; reexecução com fontes/referência iguais preserva score e mesmo profile. Serviço pode reconstruir instante histórico explícito, restrito a chamador interno; não há entrada HTTP de user_id/score/at. Fontes não são alteradas. Lock do usuário serializa dois rebuilds e protege cache ausente; constraint OneToOne complementa a API. SQL/bulk não são API de domínio.

Na T004 da T031, inserir RideReview recalcula a projeção na mesma transação. O signal ignora fixtures raw e saves de avaliações já existentes. A projeção em busca/perfil pertence à T005 da T031. A Feature 008 integra penalidades.
