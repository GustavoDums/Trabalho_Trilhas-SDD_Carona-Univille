# Contratos: Cálculo matemático de reputação

**Status**: cálculo/rebuild entregues na [T002](../evidence-t030.md), recálculo por signal integrado na T004 e projeção nas rotas de perfil e busca entregue na [T005](../evidence-t005.md).

Não cria endpoint de alteração pública da nota. Signal/serviço interno recebe user_id e instante aware; devolve projeção decimal. Templates de perfil e resultado de busca recebem score pronto e formato acessível; cliente não escolhe pontuação/pesos. Rebuild autorizado por comando administrativo futuro apenas se necessário à política aprovada.

## Regras comuns

Identidade vem da sessão, não de campo oculto. Ação mutante exige POST/CSRF, salvo CLI administrativo documentado. Views delegam aos serviços, que também autorizam. Negativas não divulgam dados de terceiros. Escapar texto; sem e-mail/placa em atributos ou JSON públicos. Conflitos de domínio não retornam sucesso fictício nem stacktrace. Nomes propostos serão fixados na tarefa de decisão. Sem notificações externas nesta feature.

## Leitura da nota na T005

- `GET /accounts/profile/` mostra a nota da sessão. Parâmetros de identidade adicionais não selecionam terceiros.
- `GET /caronas/buscar/` inclui a nota do motorista em cada resultado compatível. A busca mantém o nome abreviado e os dados públicos previstos na Feature 003.
- As telas exibem a nota decimal em texto com uma estrela decorativa. Quando a projeção está ausente, exibem 5,00. A nota registrada de 0,00 é exibida normalmente.

## Homologação e recorte — 2026-11-23

Usuário aprovou D007-01/D007-02 e autorizou T001 seguida da T002 unificada (antigas T002/T003, roadmap T030). D007-01: média aritmética simples das últimas 20 avaliações recebidas, cada avaliação com o mesmo peso mesmo na mesma viagem; sem janela de 30 dias. Selecionar created_at <= instante de referência e ordenar created_at DESC, id DESC, limit 20. A 21ª expulsa a mais antiga, não agrupar por oferta.

D007-02: novato 5.00 apenas quando conjunto vazio; base não entra como nota virtual. Calcular com Decimal e arredondar somente resultado final para duas casas com ROUND_HALF_UP, independente do contexto Decimal do chamador. [5,5,4,5,4]=4.60; [5,5,5,1]=4.00 (exatamente três notas 5 anteriores). Profile aceita 0.00..5.00; cálculo de notas 1..5 não gera zero, limite inferior prepara futura integração de penalidades da 008, não implementada agora.

ReputationProfile é projeção reconstruível sem substituir RideReview. Rebuild é serviço interno explícito, não endpoint; signals/atualização automática e exibição pública ficam T031. Referências anteriores a pendências/propostas divergentes são históricas e substituídas por esta homologação. Nenhuma aprovação de pesos, expiração por dias ou penalidades foi inferida.
API canônica de cálculo/rebuild em data-model.md; exceções ValidationError para IDs/fontes/instantes/score inválidos. Nenhum endpoint ou signal novo nesta T030. Rebuild explícito é interno e não exige conta ativa para reconstruir histórico.
