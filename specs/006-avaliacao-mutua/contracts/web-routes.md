# Contratos: Avaliação mútua pós-viagem

**Status**: decisões homologadas e serviços T002 implementados ([evidência](../evidence-t028.md)); HTTP T004 unificada implementado/verificado ([evidência](../evidence-t029.md)).

GET/POST /avaliacoes/caronas/<offer_id>/usuarios/<reviewed_id>/nova/ em reviews/urls.py, sessão acadêmica ativa, contraparte validada no servidor. Form contém rating e comment; reviewer nunca é campo editável. GET exibe formulário, POST grava uma vez e redireciona; recusa de elegibilidade não revela dados do alvo.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Nomes propostos serão fixados na tarefa de decisão. Sem notificações externas nesta feature.

## Homologação D006-01/D006-02 — 2026-11-23

Usuário aprovou as recomendações e autorizou T001 documental seguida da T002 unificada (antigas T002/T003). D006-01 CONFIRMADA: motorista titular ativo registra explicitamente conclusão após a partida (instante >= departure_at), relógio do servidor aware em UTC. RideOffer.completed_at opcional representa o término informado, não previsão de chegada nem detecção automática. Repetição autorizada preserva a primeira data. Oferta CANCELADA não pode ser concluída; ofertas legadas recebem NULL e não permitem avaliação sem conclusão registrada.

D006-02 CONFIRMADA: janela fechada [completed_at, completed_at+48h], ambos extremos inclusivos; bloquear antes e depois. Somente motorista↔passageiro com reserva CONFIRMADA na mesma oferta, ambos habilitados/com vínculo ativo; excluir cancelados e no-show. Uma avaliação por oferta/avaliador/avaliado, nota inteira 1..5, comentário opcional até 500 caracteres, sem edição. Sem passageiro↔passageiro, autoavaliação, reputação, penalidade ou interface nesta rodada.

Referências a decisões pendentes nas seções anteriores representam o estado histórico e são substituídas por esta homologação. T002 abrange domínio/migrações/serviços/testes; formulários e rotas permanecem T004/T005.
Serviços internos e locks definidos em data-model.md; PermissionDenied para ator/contraparte inelegível, ValidationError para alvo, estado, janela, nota ou duplicata. Contrato HTTP acima permanece futuro (T004/T005), sem rota de conclusão nesta T002.

## T029 / T004 unificada — contrato HTTP aprovado para implementação

Nome reviews:submit_review, GET/POST /avaliacoes/caronas/<offer_id>/usuarios/<reviewed_id>/nova/. Somente contas ativas/habilitadas dos papéis motorista/passageiro. Revisar elegibilidade da contraparte, término, janela e duplicata antes de apresentar formulário e novamente ao gravar. GET não cria avaliação. IDs de oferta/avaliado vêm da URL, avaliador da sessão; campos extras do POST não substituem identidade/tempo. Form contém somente rating e comment; comentário escapado em erros.

GET válido 200; POST válido 302 fixo para /accounts/profile/, mensagem neutra, sem eco de comentário/placa/e-mail. Erros de formulário 400 preservam entrada escapada; ValidationError de alvo/estado/janela/duplicata retorna erro genérico 400, sem dados do alvo nem formulário; PermissionDenied permanece 403. Sessão anônima/inativa segue login, pendente segue ativação. Métodos distintos de GET/POST retornam 405 para usuário elegível; CSRF obrigatório para POST.

ReviewService.review_context retorna dados mínimos autorizados (nome abreviado e instantes) sem gravação; compartilha a validação de create_review, que continua transacional e revalida tudo na gravação. Não há edição de avaliação, notificação, reputação ou nova rota de conclusão nesta T029.
