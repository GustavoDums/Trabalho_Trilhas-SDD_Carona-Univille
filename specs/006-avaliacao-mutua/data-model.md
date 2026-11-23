# Data Model: Avaliação mútua pós-viagem

D006-01/D006-02 confirmadas em 2026-11-23; implementação T002 unificada, sem interface.

## Campos canônicos

- RideOffer.completed_at: DateTimeField aware opcional null/blank, default NULL; servidor grava ao concluir, apenas motorista titular ativo e instante >= departure_at. CheckConstraint: NULL ou >= departure_at e status ABERTA. Não criar estado CONCLUIDA nem alterar capacidade. Histórico legado mantém NULL.
- RideBooking.no_show_at: DateTimeField aware opcional null/blank, default NULL; marcador de inelegibilidade preparado para integração futura da Feature 008. Esta tarefa não cria fluxo de marcação, penalidade ou reputação. Não inferir no-show da ausência de avaliação; legados mantêm NULL. API de marcação e auditoria pertencem à 008 e deverão seguir lock global.
- RideReview.offer: FK RideOffer PROTECT, related_name reviews.
- RideReview.reviewer / reviewed_user: FK AUTH_USER_MODEL PROTECT, related_names reviews_written/reviews_received.
- RideReview.rating: PositiveSmallIntegerField, validadores 1..5, rejeitar bool/fracionário antes da conversão; CheckConstraint intervalo.
- RideReview.comment: CharField max_length=500, blank=True, default vazio; normalizar espaços externos. Limite varchar(500) no PostgreSQL; não alegar CheckConstraint adicional de tamanho.
- RideReview.created_at: DateTimeField aware obrigatório, default timezone.now, não editável; serviço captura relógio uma vez e passa instante da operação.

UniqueConstraint (offer, reviewer, reviewed_user); CheckConstraint reviewer != reviewed_user. Modelo valida nota, comentário e imutabilidade de avaliações salvas. FKs preservam histórico. Regras de elegibilidade entre linhas pertencem a ReviewService, não são garantias de insert SQL isolado.

## Serviços e transações

ReviewService.complete_offer(*, user, offer_id, clock=None) retorna RideOffer; ReviewService.create_review(*, user, offer_id, reviewed_user_id, rating, comment='', clock=None) retorna RideReview. Bloquear oferta → usuários por PK → reserva participante. Reconsultar atores ATIVA/is_active e papéis fixos. Só motorista↔passageiro confirmado; no_show_at não nulo, reserva/oferta canceladas ou conclusão ausente recusam. Janela UTC fechada de 48h; relógio aware injetável capturado uma vez. Duplicata é recusada, sem editar avaliação existente. Falha de gravação reverte tudo; constraint única protege duplicata concorrente.

Criação direta/bulk/SQL não é API de domínio; SQL protege invariantes locais, serviços protegem relações e autorização. Alteração de avaliação persistida recusada pelo modelo; nenhuma API de edição. Migrações aditivas preservam todos os dados anteriores, novos timestamps NULL e tabela vazia. Verificar SQL/plano e aplicar no PostgreSQL local sem reset, além do banco de testes.

## Projeção autorizada — T029/T004

ReviewService.review_context(*, user, offer_id, reviewed_user_id, clock=None) consulta elegibilidade compartilhada com create_review e retorna somente counterpart_name (display_name abreviado), departure_at e completed_at. Não devolve ORM de usuário, e-mail ou placa. Ofertas, usuários e reserva são reconsultados/bloqueados na mesma ordem; GET não altera dados de domínio. create_review revalida independentemente da consulta anterior, incluindo unicidade. Nenhum schema novo nesta T004.
