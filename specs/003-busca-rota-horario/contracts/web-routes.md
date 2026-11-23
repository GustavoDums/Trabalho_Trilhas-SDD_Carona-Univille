# Contratos — Busca por rota e horário

Contratos de serviço, formulário e endpoint implementados/verificados nas T001–T004 locais; [evidência HTTP](../evidence-t019.md). Qualidade/demo final T005 pendente. Nenhuma nova tabela, escrita de domínio ou API pública JSON.

## Serviço interno

- `MatchingService.search(*, passenger, query: SearchQuery)` retorna tuple de SearchResult; consulta sempre somente leitura.
- Valida passageiro reconsultado no banco (PASSAGEIRO/ATIVA/is_active) e existência dos pontos; não confia no papel enviado pelo cliente. Falta de permissão gera PermissionDenied; consulta inválida gera ValidationError com nomes de campos canônicos.
- Predicados testáveis isoladamente: `route_matches(offer, query)` para IDs/ordem e `time_matches(departure_at, desired_at)` para janela fixa inclusiva. Elegibilidade de partida futura e do motorista é parte da seleção de search, não estimativa de trajeto.
- Saída do serviço segue [data-model.md](../data-model.md). Não devolver queryset/instância de usuário ou oferta ao cartão; exceções não incluem valores privados.
- Preservar a assinatura/import de publish_offer durante transformação de módulo em pacote; mudar somente imports relativos necessários (`..models` em offers.py). Mocks que referem símbolos internos movidos precisam de ajuste sem reduzir as asserções existentes.

## `/caronas/buscar/` — `rides:search`

| Estado | Resultado |
| --- | --- |
| Visitante | 302 login com next |
| Conta pendente | 302 ativação |
| Motorista ativo | 403 |
| Passageiro ativo e habilitado | GET permitido |

Não alterar as regras existentes do middleware. Mixin ActivePassengerRequiredMixin cuida do papel e flag; serviço repete verificação para impedir uso interno indevido. Conta tecnicamente desabilitada não autentica pelo fluxo normal.

### GET inicial

Sem parâmetros: 200 com formulário não vinculado, `searched=False` e resultados vazios, sem mensagem de “nenhuma oferta encontrada” e sem listar ofertas automaticamente. Campos obrigatórios `boarding_id`, `alighting_id`, `desired_at`; ModelChoiceFields do catálogo e datetime-local. Exibir America/Sao_Paulo.

### GET com parâmetros

Exemplo sintético: `?boarding_id=1&alighting_id=3&desired_at=2026-12-01T08%3A00`. IDs são exemplos; usar IDs reais do catálogo em testes/guias.

Qualquer query string cria tentativa de consulta (`searched=True`). Campos ausentes, iguais, inexistentes ou horário inválido: 200 com erros de campo, sem resultados; não chamar matching com entrada inválida. Formulário preserva filtros enviados. `tolerance`, `window`, `driver`, `user_id` ou outros extras não são campos do formulário nem alteram permissões ou ±30 minutos.

Consulta válida: 200 com DTOs autorizados. No topo e junto ao horário, informar: **“Janela fixa de ±30 minutos em relação à saída da origem. Não representa previsão de passagem nas paradas.”**

Cartão `rides/_search_result.html`: nome abreviado, itinerário público na ordem, data/hora de saída, vagas disponíveis, modelo/cor. Evolução Feature 004/T006: SearchResult.seats preserva capacidade e SearchResult.available_seats informa saldo; zero exibe Vagas esgotadas, sem retirar a oferta compatível. A disponibilidade pode mudar até a confirmação. Escapar rótulos. Não incluir e-mail, nome completo, placa, nota, JSON oculto ou botão de reserva. No contexto de resultados, apenas DTO público; contexto técnico de request/session não deve ser serializado.

Sem resultados válidos: “Nenhuma oferta compatível com os filtros informados.” Não substituir por viagens aproximadas nem relaxar janela. Mostrar filtros para nova busca.

Ordenação por saída/criação/id e uma ocorrência por oferta. Saída exatamente agora não aparece; ambos os limites da janela são incluídos se também forem futuros. O horário desejado pode ser passado: a consulta ainda filtra partidas futuras dentro da janela, sem nova proibição do campo.

### Outros métodos

POST, PUT, PATCH e DELETE: 405 para passageiro autorizado. Não criar histórico, reserva ou alteração de oferta. Comparações de banco nos testes excluem manutenção técnica de sessão Django quando pertinente, mas incluem integralmente ofertas, paradas e contas de domínio.

## Formulário antes da view

A tarefa de formulário/cartões pode testar renderização isolada com SearchResult sintético e RequestFactory, sem antecipar endpoint. Rota e autorização HTTP pertencem à tarefa local T004, correspondente à T019 do roadmap.
