# Ingresso e repasse

- O resultado lotado na busca oferece o POST `/caronas/<offer_id>/fila/` com os IDs de embarque e desembarque selecionados. O POST exige vínculo ativo no papel de passageiro e CSRF. A identidade vem da sessão.
- O ingresso aceito redireciona para minhas reservas com mensagem de confirmação. Ingresso repetido mantém a entrada original. Erros de dados ou disponibilidade retornam 400 com a causa e violações de acesso retornam 403 ou redirecionam conforme a sessão.
- `WaitlistService.promote_next(offer_id=...)` processa no máximo uma vaga na transação da oferta e retorna a reserva confirmada ou `None`. A chamada que conecta o cancelamento a esse contrato pertence à T040.
