# Data Model — Feature 002

Fonte canônica de campos e restrições para as tarefas. Todos os modelos em `rides/models.py`, PK `BigAutoField`. Campos obrigatórios: null=False/blank=False, salvo indicação. Limites textuais são limites técnicos, não validação externa de identidade.

## RoutePoint

| Campo canônico | Tipo e restrições |
| --- | --- |
| RoutePoint.id | bigint PK automático |
| RoutePoint.code | SlugField(80), UNIQUE, obrigatório, código estável; catálogo administrado por migração |
| RoutePoint.name | CharField(100), trim, não vazio após trim |

Sem endpoint de criação/edição pelo motorista. Catálogo inicial em research.md; códigos são identidade, rótulos podem conter acentos. Referências a pontos inexistentes são rejeitadas por FK. Não excluir ponto referenciado (PROTECT).

## RideOffer

| Campo canônico | Tipo e restrições |
| --- | --- |
| RideOffer.id | bigint PK automático |
| RideOffer.driver | FK settings.AUTH_USER_MODEL, PROTECT, related_name=ride_offers; em criação exige is_active=True, role=MOTORISTA e academic_status=ATIVA |
| RideOffer.origin | FK RoutePoint, PROTECT, related_name=origin_offers; obrigatório |
| RideOffer.destination | FK RoutePoint, PROTECT, related_name=destination_offers; obrigatório e diferente de origin |
| RideOffer.departure_at | DateTimeField timezone-aware, obrigatório, estritamente maior que timezone.now() na publicação; igualdade rejeitada; histórico não revalidado pelo simples decorrer do tempo |
| RideOffer.seats | PositiveBigIntegerField, inteiro entre 1 e 9223372036854775807 (limite da representação), exclui motorista; não truncar números fracionários |
| RideOffer.vehicle_model | CharField(100), trim, não vazio; snapshot da oferta |
| RideOffer.vehicle_color | CharField(50), trim, não vazio; snapshot da oferta |
| RideOffer.vehicle_plate | CharField(20), trim/uppercase, não vazio; sem regex nacional, sem UNIQUE global; snapshot privado |
| RideOffer.created_at | DateTimeField(auto_now_add=True), não editável |

Meta.ordering: departure_at, created_at, id. Index em driver/departure_at para consulta própria. CHECK `ride_seats_positive` (seats>=1); CHECK `ride_endpoints_distinct` (origin_id != destination_id). FKs e NOT NULL nativos; limites de varchar nativos. Modelo chama full_clean no save; regras de elegibilidade e tempo em inserção, sem tentar revalidar tempo em consultas ou manutenção histórica. Usuário que perde vínculo deixa de criar/consultar; suas ofertas antigas não são automaticamente apagadas ou canceladas nesta feature.

## Waypoint

| Campo canônico | Tipo e restrições |
| --- | --- |
| Waypoint.id | bigint PK automático |
| Waypoint.offer | FK RideOffer, CASCADE, related_name=waypoints; obrigatório |
| Waypoint.point | FK RoutePoint, PROTECT; obrigatório, distinto dos extremos da oferta |
| Waypoint.position | PositiveIntegerField, 1..2147483647; ordem intermediária, atribuída pelo servidor |

UNIQUE `(offer, position)` (`waypoint_offer_position_unique`); UNIQUE `(offer, point)` (`waypoint_offer_point_unique`); CHECK position>=1 (`waypoint_position_positive`); ordering=position. Save chama full_clean para impedir ponto igual a extremo. Ordem contígua 1..N é garantida no serviço para a publicação integral, não por CHECK entre linhas. Zero paradas é válido; não criar Waypoint para origem/destino.

## Agregado e transação

Itinerário lógico = origin + waypoints ordenados + destination. Todos os pontos devem ser distintos. Serviço valida lista completa, referências, ausência de itens vazios e ordem, gera posições contíguas e salva tudo dentro de uma única transação. Recebe conta da sessão, reconsulta/bloqueia AcademicUser e verifica elegibilidade imediatamente antes de publicar. Modelo não conhece sessão: a validação de identidade recebida ocorre na view/serviço.

Snapshot pertence à oferta; reutilizar significa copiar valores da última oferta do próprio autor para o formulário, depois gravar nova cópia. Não atualizar a anterior. Não criar modelo de frota nem migrations em accounts.

## Limites de garantia

Constraints SQL cobrem somente as regras estruturais indicadas. Papel/estado do motorista, tempo futuro, normalização, extremos versus paradas e contiguidade dependem de validação da aplicação. bulk_create, update e SQL direto não são caminhos públicos de publicação; não prometer que executam clean/save. Serviço não usa bulk_create para contornar validações de Waypoint. Testes precisam distinguir clean/save de constraints SQL.

Não há campos de reserva, vagas restantes calculadas, status de cancelamento ou horários por parada nesta versão.