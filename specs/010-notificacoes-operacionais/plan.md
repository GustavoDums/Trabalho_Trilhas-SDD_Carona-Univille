# Implementation Plan: Notificações operacionais

**Feature**: 010-notificacoes-operacionais  
**Data**: 2026-11-23  
**Spec**: [spec.md](spec.md)

## Summary

Implementar T037 com app Django de avisos internos e integração transacional à confirmação de reserva e ao cancelamento. O mesmo evento conserva seus avisos em tentativas repetidas.

A T038 entrega a interface de avisos internos prevista no planejamento do bônus e solicitada pelo usuário. O sino indica a quantidade de avisos não lidos na navegação. A lista usa os avisos persistidos pela T037 e a marcação usa uma atualização condicional para preservar o primeiro instante de leitura.

## Technical Context

Python 3.12+, Django 5.1, PostgreSQL, pytest, pytest-django e pytest-cov. Reutiliza AcademicUser, BookingService, CancellationService e os modelos de auditoria. A leitura pela interface pertence à T038.

## Constitution Check

- Dados fictícios nos testes e destinatário privado. Avisos de eventos não carregam placa, e-mail nem texto livre.
- A escrita faz parte da transação da operação. A chave única no PostgreSQL protege os avisos sob concorrência.
- Executar testes de aceitação e regressão e registrar as métricas medidas no README.
- O escopo autorizado para T037 e T038 está registrado na spec. Regras de canal, destinatários e limites estão em [research.md](research.md). A interface identifica o titular pela sessão acadêmica e protege a mutação com CSRF.
- Dependências T002, T021 e T025 já implementadas. Preservar a ordem de locks de oferta e contas.

## Project Structure

### Documentation

[Dados](data-model.md), [contratos](contracts/events.md), [validação](quickstart.md) e [tarefas](tasks.md).

### Source Code

- `notifications/models.py`, `notifications/apps.py` e `notifications/migrations/` registram os avisos.
- `notifications/services.py` recebe somente eventos internos e materializa os destinatários.
- `rides/services/booking_service.py` e `rides/services/cancellation_service.py` chamam o serviço depois da transição bem-sucedida.
- `notifications/views.py`, `notifications/urls.py` e `notifications/templates/notifications/list.html` entregam a consulta e a marcação. `notifications/context_processors.py` fornece a contagem ao template-base de `accounts`.
- `tests/test_notifications.py` verifica destinatários, reprocessamento, concorrência, recusas, rollback, sessão, contador, privacidade e leitura em PostgreSQL.

## Complexity Tracking

Uma tabela com referências ao evento original e constraints de unicidade, sem fila, fornecedor ou processo externo.
