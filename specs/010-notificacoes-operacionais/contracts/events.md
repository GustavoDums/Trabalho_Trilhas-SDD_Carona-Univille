# Contrato de eventos

| Origem | Destinatários | Momento |
| --- | --- | --- |
| Nova reserva confirmada | Titular da reserva e motorista | Depois do savepoint de inserção da reserva |
| Cancelamento individual | Titular da reserva e motorista | Depois do evento de auditoria e da aplicação das regras de conduta |
| Cancelamento de oferta | Motorista titular e passageiros das reservas confirmadas selecionadas para a transição | Depois do evento de auditoria da oferta e da aplicação das regras de conduta |

Os três gatilhos são internos e fazem parte da transação da operação original. Um evento repetido preserva os avisos existentes. O cancelamento de uma oferta usa um único evento de origem para todos os destinatários.

A consulta e a marcação de leitura são da T038. Os contratos de leitura devem limitar consulta, contagem e mutação ao titular identificado pela sessão.
