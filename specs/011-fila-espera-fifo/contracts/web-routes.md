# Ingresso e repasse

- O resultado lotado na busca oferece o POST `/caronas/<offer_id>/fila/` com os IDs de embarque e desembarque selecionados. O POST exige vínculo ativo no papel de passageiro e CSRF. A identidade vem da sessão.
- O ingresso aceito redireciona para minhas reservas com mensagem de confirmação. Ingresso repetido mantém a entrada original. Erros de dados ou disponibilidade retornam 400 com a causa e violações de acesso retornam 403 ou redirecionam conforme a sessão.
- `WaitlistService.promote_next(offer_id=...)` processa no máximo uma vaga na transação da oferta e retorna a reserva confirmada ou `None`. A chamada que conecta o cancelamento a esse contrato pertence à T040.
- Na T040, `POST /caronas/reservas/<booking_id>/cancelar/` chama o repasse dentro da transação de um cancelamento novo. A confirmação usa o aviso da Feature 010. O reenvio do cancelamento conserva o resultado anterior.
- `GET /caronas/minhas-reservas/` mostra apenas as entradas do passageiro da sessão em ofertas abertas e futuras. A posição é contada a partir de 1 na fila atual da oferta. A tela usa a referência da carona, o trecho e o horário de saída.
