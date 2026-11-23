# Contrato de eventos

| Origem | Destinatários | Momento |
| --- | --- | --- |
| Nova reserva confirmada | Titular da reserva e motorista | Depois do savepoint de inserção da reserva |
| Cancelamento individual | Titular da reserva e motorista | Depois do evento de auditoria e da aplicação das regras de conduta |
| Cancelamento de oferta | Motorista titular e passageiros das reservas confirmadas selecionadas para a transição | Depois do evento de auditoria da oferta e da aplicação das regras de conduta |

Os três gatilhos são internos e fazem parte da transação da operação original. Um evento repetido preserva os avisos existentes. O cancelamento de uma oferta usa um único evento de origem para todos os destinatários.

## Consulta e leitura na T038

| Ação | Contrato |
| --- | --- |
| Sino na navegação | A sessão com vínculo ativo vê o total de avisos não lidos do titular, inclusive zero. |
| `GET /notificacoes/` | Lista apenas avisos do titular, do mais recente ao mais antigo, com tipo do evento, referência da carona, data e estado de leitura. A resposta privada usa `Cache-Control: no-store`. |
| `POST /notificacoes/<id>/ler/` | Exige sessão acadêmica, titularidade e token CSRF. Registra o primeiro instante de leitura e redireciona à lista. Um ID de terceiro ou inexistente recebe HTTP 404. |
