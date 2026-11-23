# Research — Feature 003

**Data**: 2026-11-22. Fontes: spec confirmada, constitution, levantamento e código local. Pesquisa técnica de integração, sem alterações de produto.

## Estrutura dos serviços

**Decision**: converter services.py para pacote services, com offers.py e matching_service.py. Reexportar publish_offer no __init__ para manter `from rides.services import publish_offer`.
**Rationale**: o roadmap prevê serviço em submódulo, mas já existe módulo homônimo. Resolver antes do matching, com regressão e sem mudança de comportamento.
**Alternatives considered**: criar arquivo e diretório homônimos (ambiguidade/imports); renomear todos os consumidores (quebra desnecessária); colocar matching junto à publicação (mistura responsabilidades).

## Ordem e tempo

**Decision**: comparar IDs de pontos na sequência armazenada e saída da origem em intervalo fixo ±30 minutos, inclusivo, conforme confirmação do usuário.
**Rationale**: não há horários por parada. Não fabricar passagem/ETA; aviso obrigatório na interface.
**Alternatives considered**: tolerância configurável e previsão por parada (não escolhidas); ordenação por rótulo ou PK (muda o trajeto).

Capturar now uma vez por busca; usar instantes aware e preservar precisão de segundos. Com data desejada passada ainda pode haver saída futura dentro da janela; não adicionar rejeição de data desejada passada. Partida igual a now é excluída. Tempo/catálogo são validados no contrato, não por nova tabela.

## Consulta e projeção pública

**Decision**: seleção SQL temporal/eligibilidade, prefetch de paradas/pontos, ordem avaliada em memória sobre candidatos, saída como DTO imutável sem usuário completo, placa ou e-mail.
**Rationale**: simples para PoC e auditável; evita N+1 e vazamento de campos acidentais pelo contexto da busca.
**Alternatives considered**: múltiplos joins para cada posição (duplicação e complexidade), passar RideOffer completo ao cartão (risco de exposição acidental).

Não usar cache de resultados nesta etapa; uma nova consulta reavalia vínculos e tempo. Não incluir nota de reputação: não existe fonte implementada. O objeto request.user existe no contexto técnico Django, mas o cartão recebe exclusivamente o DTO; não serializar contexto técnico ou usuário em HTML/JSON.

## Interface e qualidade

**Decision**: formulário GET com IDs do catálogo e datetime-local; sem campo de tolerância, sem POST ou reserva. Estado inicial, inválido, vazio e resultados distintos.
**Rationale**: busca reproduzível, sem escrita de domínio; cliente não escolhe autor ou amplia permissões.
**Alternatives considered**: POST para consulta e histórico persistente (sem requisito), filtros silenciosamente relaxados (viola critérios).

Relatórios próprios Feature 003; medir código novo de matching/forms/view sem diluir com código não relacionado. Regressão das features anteriores permanece obrigatória, com contagem separada. Coverage não mede templates: privacidade exige inspeção do HTML renderizado e dos campos do DTO.