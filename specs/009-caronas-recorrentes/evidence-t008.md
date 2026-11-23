# Feature 009 / T008 local — Calendário de recorrência

**Data** 2026-11-23 · **Requisitos** REQ-011, REQ-003, REQ-014, REQ-017–REQ-019 · **Decisão** D009-01 revisada.

| Critério | Verificação |
| --- | --- |
| 15 dias úteis | A contagem usa a data local e pula fins de semana e feriados. O limite é inclusivo. Os testes verificam a virada de mês, os dias selecionados e a exclusão de partidas já atingidas. |
| Virada de ano e cache | A integração simulada consulta os anos envolvidos uma vez, reutiliza as respostas válidas e pula feriados em dezembro e janeiro. Uma data de feriado que cai no sábado já está fora da contagem de fins de semana. |
| API real | O cliente do Django consultou 2026 e 2027 com `uf=SC`. A janela iniciada em 21/12/2026 terminou em 12/01/2027. |
| Formulário e comando | As entradas geram as mesmas datas. Na indisponibilidade do calendário, a criação da regra retorna 503, o comando retorna erro e a listagem mantém as caronas já geradas. |
| Integridade | Reexecutar conserva os vínculos das ofertas publicadas. O serviço mantém os testes de concorrência, rollback e cancelamento independente. |
| Django e PostgreSQL | `manage.py check`, `makemigrations --check --dry-run` e `migrate --check` passaram. |

Os três arquivos de teste de recorrência e calendário aprovaram **62 testes** no PostgreSQL, incluindo os casos da T008. [Roteiro de reprodução](quickstart.md).

A suíte consolidada aprovou **1.005 testes**, com zero falhas e zero ignorados. A cobertura combinada foi de **98,56%**, com **99,01% de linhas** e **96,54% de ramificações**. A meta de 80% foi atingida globalmente e nos 38 módulos críticos. [JSON](../../coverage.json) · [JUnit](../../test-results-t043.xml) · [README](../../README.md).
