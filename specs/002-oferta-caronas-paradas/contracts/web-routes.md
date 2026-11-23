# Contratos HTML — Feature 002

Contrato previsto para implementação, não endpoints já disponíveis. Sessão Django e CSRF obrigatórios em POST. Não há API JSON pública.

## Acesso comum

| Estado | GET/POST de oferta e GET de minhas ofertas |
| --- | --- |
| Visitante | 302 para `/accounts/login/?next=...`, conforme middleware |
| Autenticado PENDENTE | 302 para `/accounts/activation/` |
| Passageiro ATIVA | 403, sem dados privados ou escrita |
| Motorista ATIVA e tecnicamente habilitado | Prossegue |

As duas views usam verificação própria de motorista ativo além do middleware. O serviço repete a regra no momento da publicação. Falta de CSRF pode produzir 403 antes das regras acima; nenhum caso escreve dados.

## `/caronas/oferecer/` — `rides:offer-create`

GET 200: `rides/offer_create.html`, campos `origin`, `destination` (IDs do catálogo), `departure_at` (datetime-local interpretado no fuso America/Sao_Paulo), `seats`, `vehicle_model`, `vehicle_color`, `vehicle_plate` e formset `waypoints`.

Formset: management form `waypoints-TOTAL_FORMS` e `waypoints-INITIAL_FORMS`; linhas `waypoints-0-point`, `waypoints-1-point` etc. Cada linha enviada precisa de ponto válido; zero linhas representa trajeto direto. Adicionar/remover linha antes do envio mantém DOM e índices consecutivos; não há campo de posição aceito como autoridade. Botões locais não enviam o formulário. Sem biblioteca externa, código mínimo em `rides/static/rides/offer.js`. CSRF em campo oculto. Erro de management form é erro de formulário, sem escrita.

Se o motorista já publicou, GET pré-preenche os três dados do veículo da sua última oferta; não copia trajeto, horário ou vagas. Primeira oferta exige preenchimento manual. Nunca consultar veículo de outro motorista para pré-preencher.

POST válido: serviço recebe `request.user`, dados validados e lista de pontos na ordem. Ignorar campos extras como `driver`, `user_id`, `position`, status ou IDs de ofertas anteriores. Publicar exatamente uma oferta completa e suas paradas. Resposta 302 para `/caronas/minhas-ofertas/` com mensagem “Oferta de carona publicada com sucesso.”

POST inválido: 200, reapresentar formulário e erros de campo/formset sem gravações parciais. Campos não sensíveis preservados; placa deve ser limpa do formulário reapresentado e digitada novamente, com orientação. Campo inválido não pode virar erro 500. Falhas inesperadas de infraestrutura propagam-se com rollback, sem mensagem de sucesso nem alegação de publicação concluída.

Regras de campos: [data-model.md](../data-model.md). Saída igual/agora é inválida; erro específico de horário. Vagas fracionárias não são arredondadas. Repetição de pontos, inclusive extremos, é erro do itinerário. Catálogo não permite criar ponto por POST.

## `/caronas/minhas-ofertas/` — `rides:my-offers`

GET 200: `rides/my_offers.html`. Consulta filtrada pelo motorista autenticado; ignora filtros de autoria enviados. Ordenação por departure_at, created_at, id. Prefetch de waypoints com point e select_related de extremos evita consulta por parada.

Cada item mostra origem → paradas na posição → destino, data/horário no fuso informado, vagas ofertadas e modelo/cor. Não mostra e-mail nem placa, sequer como atributo oculto; a placa continua disponível somente ao autor pelo formulário de reutilização, sem listagem pública. Sem ofertas: “Você ainda não publicou ofertas de carona.” e link de criação.

POST, PUT, PATCH e DELETE na lista: 405 para motorista autorizado. Não fornecer edição, exclusão ou cancelamento. Não aceitar ID de oferta alheia para detalhamento, pois não existe rota de detalhe nesta versão.

## Integração existente

Preservar `/caronas/` e seu placeholder. Incluir `rides.urls` sob `/caronas/` no URLconf principal; padrões de rides contêm apenas `oferecer/` e `minhas-ofertas/`. Não alterar cadastro, login manual, ativação ou perfil. Os testes da T009 usam URLconf próprio; testes desta feature devem usar o URLconf real.
