# Contratos: Avaliação mútua pós-viagem

**Status**: decisões homologadas e serviços T002 implementados ([evidência](../evidence-t028.md)); HTTP proposto para T004/T005.

GET/POST /avaliacoes/caronas/<offer_id>/usuarios/<reviewed_id>/nova/ em reviews/urls.py, sessão acadêmica ativa, contraparte validada no servidor. Form contém rating e comment; reviewer nunca é campo editável. GET exibe formulário, POST grava uma vez e redireciona; recusa de elegibilidade não revela dados do alvo.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Nomes propostos serão fixados na tarefa de decisão. Sem notificações externas nesta feature.

## Homologação D006-01/D006-02 — 2026-11-23

Usuário aprovou as recomendações e autorizou T001 documental seguida da T002 unificada (antigas T002/T003). D006-01 CONFIRMADA: motorista titular ativo registra explicitamente conclusão após a partida (instante >= departure_at), relógio do servidor aware em UTC. RideOffer.completed_at opcional representa o término informado, não previsão de chegada nem detecção automática. Repetição autorizada preserva a primeira data. Oferta CANCELADA não pode ser concluída; ofertas legadas recebem NULL e não permitem avaliação sem conclusão registrada.

D006-02 CONFIRMADA: janela fechada [completed_at, completed_at+48h], ambos extremos inclusivos; bloquear antes e depois. Somente motorista↔passageiro com reserva CONFIRMADA na mesma oferta, ambos habilitados/com vínculo ativo; excluir cancelados e no-show. Uma avaliação por oferta/avaliador/avaliado, nota inteira 1..5, comentário opcional até 500 caracteres, sem edição. Sem passageiro↔passageiro, autoavaliação, reputação, penalidade ou interface nesta rodada.

Referências a decisões pendentes nas seções anteriores representam o estado histórico e são substituídas por esta homologação. T002 abrange domínio/migrações/serviços/testes; formulários e rotas permanecem T004/T005.
Serviços internos e locks definidos em data-model.md; PermissionDenied para ator/contraparte inelegível, ValidationError para alvo, estado, janela, nota ou duplicata. Contrato HTTP acima permanece futuro (T004/T005), sem rota de conclusão nesta T002.
