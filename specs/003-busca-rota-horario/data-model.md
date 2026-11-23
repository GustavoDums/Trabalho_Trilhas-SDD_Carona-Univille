# Data Model — Feature 003

Nenhuma entidade persistente nova ou migração prevista. Contratos transitórios definidos em `rides/services/matching_service.py`. Esta é a fonte canônica dos campos e restrições das tarefas de busca.

## SearchQuery (dataclass frozen)

| Campo canônico | Tipo e regra |
| --- | --- |
| SearchQuery.boarding_id | int positivo de PK RoutePoint existente; rejeitar bool, vazio, fracionário e ID ausente do catálogo |
| SearchQuery.alighting_id | int positivo de RoutePoint existente, distinto de boarding_id; mesmas regras de entrada |
| SearchQuery.desired_at | datetime aware obrigatório; preservar instante, data e segundos; não impor regra de futuro ao pedido |

A dataclass valida tipos, IDs positivos/distintos e fuso; serviço valida existência atual no catálogo. Formulário converte IDs com ModelChoiceField e horário com DateTimeField no fuso America/Sao_Paulo antes de construir SearchQuery. Nenhum campo tolerance/window ou author. Chaves extras do GET não modificam a janela fixa.

## SearchResult (dataclass frozen, projeção explícita)

| Campo canônico | Tipo e regra |
| --- | --- |
| SearchResult.offer_id | int positivo da oferta compatível, único na coleção retornada |
| SearchResult.driver_display_name | str retornada por AcademicUser.display_name; nunca full_name ou email |
| SearchResult.itinerary | tuple[str, ...], nomes de origem/paradas/destino na sequência real, ao menos dois itens; escapar na renderização |
| SearchResult.departure_at | datetime aware da saída da origem; exibir data/hora no fuso indicado |
| SearchResult.seats | int positivo, vagas ofertadas, sem deduzir reservas inexistentes |
| SearchResult.vehicle_model | str do snapshot da oferta, sem placa |
| SearchResult.vehicle_color | str do snapshot da oferta, sem outros dados de veículo |

Não incluir usuário/modelo completo, nome completo, email, placa, nota de reputação ou contato. Não oferecer as_dict/serializer que acrescente atributos do modelo. O serviço constrói DTOs só após validar candidato. Limites textuais das fontes vêm de seus modelos existentes, sem novos limites de produto.

## Campos existentes consultados (somente leitura)

| Campo canônico | Origem/regra de uso |
| --- | --- |
| RoutePoint.id | Identidade do catálogo da Feature 002, não comparação por nome |
| RoutePoint.name | Rótulo dos pontos para resultado |
| RideOffer.id | Identidade e desempate final |
| RideOffer.driver | Motorista atual: is_active=True, role=MOTORISTA, academic_status=ATIVA |
| RideOffer.origin | Primeiro ID no itinerário |
| RideOffer.destination | Último ID no itinerário |
| RideOffer.departure_at | > now e entre desired_at−30min e desired_at+30min, ambos inclusivos |
| RideOffer.seats | >0 para aparecer |
| RideOffer.created_at | Desempate após saída |
| RideOffer.vehicle_model | Fonte de projeção pública |
| RideOffer.vehicle_color | Fonte de projeção pública |
| Waypoint.offer | Relação para prefetch das paradas |
| Waypoint.point | Identidade/nome do ponto intermediário |
| Waypoint.position | Ordenação das paradas; nunca ordenar pelo nome ou ID |
| AcademicUser.id | Reconsulta do passageiro e identidade interna do motorista |
| AcademicUser.role | Passageiro para consultar, motorista para ofertante elegível |
| AcademicUser.academic_status | ATIVA para ambos |
| AcademicUser.is_active | True para ambos |
| AcademicUser.display_name | Abreviação pública existente |

Nenhuma restrição ou campo das Features 001/002 é alterado. Validações transitórias não se apresentam como constraints SQL. Placa/full_name/email podem existir no armazenamento, mas não integram SearchResult.

## Regras da coleção

Itinerário de IDs precisa conter pontos distintos para ser interpretado sem ambiguidade; dado legado malformado não vira resultado por aproximação. Para consulta válida, ambos os IDs devem existir na mesma lista e boarding_index < alighting_index. Zero paradas é válido. Cada oferta gera no máximo um resultado. Ordenação final: RideOffer.departure_at, created_at, id.

Somente ofertas futuras/positivas e motorista ativo entram no conjunto. Query não cria registros de busca, reservas ou alterações de domínio; autenticação técnica e sessões Django permanecem existentes.