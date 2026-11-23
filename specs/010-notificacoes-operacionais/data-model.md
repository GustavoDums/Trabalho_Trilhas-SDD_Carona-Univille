# Modelo de dados

`Notification` guarda destinatário acadêmico, tipo, origem, data de criação e leitura opcional. Há três tipos, confirmação de reserva, cancelamento individual e cancelamento de oferta.

- Confirmação aponta para a reserva criada. Cancelamento aponta para o evento `CancellationRecord` correspondente. Todas as referências são protegidas contra exclusão acidental.
- A restrição de tipo e origem exige reserva para confirmação ou registro de cancelamento para os dois tipos de cancelamento, exclusivamente.
- Uma restrição única por destinatário e reserva protege confirmações. Outra por destinatário e registro protege cancelamentos.
- `read_at` começa nulo. A indexação permite consulta por destinatário em ordem decrescente de criação. A T038 usa a sessão e a validação de titularidade para escrever o estado de leitura.
- O modelo não copia dados de contato, nome, placa ou mensagens de texto livre.
