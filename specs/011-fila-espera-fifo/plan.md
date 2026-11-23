# Implementation Plan: Fila de Espera Automática com Repasse FIFO

**Feature** 011-fila-espera-fifo · [Especificação](spec.md)

## Summary

A T039 acrescenta ingresso a partir da busca e serviço transacional que confirma uma única vaga por chamada. A T040 chama o serviço no cancelamento e exibe a posição.

## Technical Context

Python 3.12+, Django 5.1, PostgreSQL e pytest. Reutilizar o formulário de trecho, a validação da reserva, os serviços de conduta e de reserva e os avisos da Feature 010.

## Constitution Check

A sessão fornece o titular e o formulário usa CSRF. O bloqueio da oferta serializa ingresso, reserva e repasse. Chaves únicas protegem fila e reserva. Os testes usam dados fictícios em PostgreSQL e a entrega registra resultados e cobertura.

Na T040, o cancelamento bloqueia primeiro a oferta e depois as contas envolvidas, incluindo os candidatos da fila, em ordem crescente de ID. Cancelamento, auditoria, penalidade, repasse e avisos pertencem à mesma transação. O painel consulta posições somente para o passageiro da sessão, em ofertas abertas e futuras.

## Project Structure

[Decisões](research.md), [dados](data-model.md), [contrato](contracts/web-routes.md), [validação](quickstart.md) e [tarefas](tasks.md).

O modelo e a migração ficam no app rides. A regra de fila fica em rides/services/waitlist_service.py. Rotas, views e templates de rides apresentam o ingresso. Os critérios de T039 ficam em tests/test_waitlist.py.

A integração da T040 fica em `rides/services/cancellation_service.py`, com a posição em `rides/services/waitlist_service.py`, `rides/views.py` e `rides/templates/rides/my_bookings.html`. Os critérios de T040 ficam em `tests/test_waitlist_flow.py`.

## Complexity Tracking

Um registro por titular e oferta na fila corrente. O identificador gerado sob o bloqueio da oferta estabelece a ordem de entrada. O serviço de reservas continua responsável pela criação transacional e seus efeitos existentes.
