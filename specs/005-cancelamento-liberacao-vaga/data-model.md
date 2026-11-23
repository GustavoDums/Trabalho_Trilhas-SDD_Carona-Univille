# Data Model: Cancelamento e liberação de vaga

**Status**: D005-01/D005-02 confirmadas pelo usuário em 2026-11-22; T002/T003 implementadas e verificadas em 2026-11-23 ([evidência](evidence-t024.md)). T004 implementada em 2026-11-23 ([evidência](evidence-t025.md)); HTTP pendente.

## Campos e restrições canônicas

A extensão T008 adiciona `RideOffer.removed_from_driver_at`, instante opcional com fuso. A migração `rides.0008_rideoffer_removed_from_driver_at` inicia o campo como nulo nas ofertas existentes. `MyOffersView` seleciona apenas as ofertas do titular com o campo nulo. O serviço grava a remoção sob o mesmo lock da oferta após confirmar seu estado cancelado. Reservas, eventos de cancelamento e referências de ocorrências recorrentes continuam apontando para a oferta.

| Campo | Tipo/regra |
| --- | --- |
| RideOffer.status | CharField max_length=9, ABERTA/CANCELADA, default ABERTA; CheckConstraint enum; ofertas existentes recebem ABERTA |
| RideOffer.cancelled_at | DateTimeField aware opcional (null/blank), default None; efetivação do cancelamento de oferta pertence à T004 |
| RideBooking.cancelled_at | DateTimeField aware opcional; cancelamento efetivo grava o instante capturado; histórico anterior pode continuar None |
| CancellationRecord.id | BigAutoField |
| CancellationRecord.actor | FK obrigatória AcademicUser, PROTECT, cancellation_records; autoria vem do ator autenticado |
| CancellationRecord.offer | FK obrigatória RideOffer, PROTECT, cancellation_records |
| CancellationRecord.booking | FK opcional RideBooking, PROTECT, cancellation_records; quando informada, deve pertencer à offer; None representa futura transição da oferta |
| CancellationRecord.occurred_at | DateTimeField aware obrigatório, mesmo instante da transição |
| CancellationRecord.classification | CharField max_length=10, TEMPESTIVO/TARDIO; choices e CheckConstraint |

UniqueConstraint parcial por booking não nula e por offer quando booking é nula: um evento por transição efetiva. Repetição de reserva CANCELADA não gera evento nem atualiza datas, mesmo após a partida; legado cancelado sem auditoria não tem evento inventado. Não apagar histórico por cascata.

Django full_clean valida timestamps aware; campo opcional admite None. Não exigir cancelled_at de reservas CANCELADA legadas nem inventar data. CancellationRecord valida vínculo booking.offer. Restrições locais no PostgreSQL complementam o serviço.

## Política aprovada

Passageiro: antecedência >=2h é TEMPESTIVO; motorista: >=4h é TEMPESTIVO. Referência única: RideOffer.departure_at na origem. Comparar instantes completos em UTC; borda inclusiva. Antes da partida e abaixo do prazo: TARDIO aceito com auditoria. Na partida ou depois: recusar sem mutação. Sem dedução numérica, nota automática ou suspensão; penalidade futura pertence à Feature 008.

## Estado e capacidade

CONFIRMADA→CANCELADA e cancelled_at/auditoria são gravados no mesmo atomic. Repetição é idempotente. RideOffer.seats continua capacidade original; saldo deriva apenas de CONFIRMADA. Não incrementar contador. Modelo/status de oferta são preparados nesta T002; fechar oferta e cancelar reservas em lote pertence à T004. BookingService e MatchingService devem recusar/excluir status CANCELADA desde a inclusão do campo, sem implementar a transição de oferta.

## Migração

Criar campos e tabela vazia de auditoria preservando todos os campos anteriores. Estado padrão ABERTA para ofertas legadas, datas opcionais None. Verificar plano/SQL, aplicar no PostgreSQL local sem reset e conferir snapshots dos campos antigos, FKs/constraints e migração registrada.

## Serviço e locks

Cancelamento suportado somente por CancellationService; criação direta/bulk/SQL não é API de domínio. Ordem comum com BookingService: oferta → usuários por PK → reservas por PK. Resolver referência da reserva inicialmente sem lock, depois revalidar reserva/autor após locks. Capturar relógio uma vez dentro da transação para transição; nenhum relógio de navegador decide prazo. Auditoria e alteração de estado revertem juntas em erro.
