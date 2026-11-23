# Research: Caronas recorrentes

## Fontes e estado observado

[constitution](../../.specify/memory/constitution.md), [levantamento](../../docs/levantamento.md), [roadmap](../../docs/roadmap-implementacao.md) e [registro de preparação](../../docs/preparacao-features-004-009.md). Publicação atômica, pacote rides/services e cancelamento já estão disponíveis.

## Decisões técnicas propostas

**Decisão**: manter Django, PostgreSQL, templates e pytest. **Motivo**: stack constitucional e ambiente existente. **Alternativas rejeitadas**: frameworks novos, SQLite para provar concorrência, filas e fornecedores externos.

**Decisão**: preservar capacidade original, histórico e projeções reconstruíveis, com idempotência transacional. **Motivo**: evitar perda de auditoria e efeitos duplicados. **Alternativa rejeitada**: contadores sem fonte de verdade e validação apenas na view.

## Decisões homologadas

A T035 forneceu o gerador reutilizado pela interface e pelo comando interno da T036. A T008 revisou o horizonte para 15 dias úteis em America/Sao_Paulo. A geração continua automática na criação da regra e na rotina diária. [D009-01 e D009-02](spec.md).

O contrato de feriados da BrasilAPI aceita o ano e a UF. A consulta com `uf=SC` retorna as datas nacionais e estaduais fornecidas pela API, incluindo datas móveis. A integração usa a biblioteca padrão do Python, mantém o cache por ano e envia somente o ano e a UF. Feriados municipais e calendário acadêmico ficam fora dessa fonte. [Documentação da BrasilAPI](https://brasilapi.com.br/docs#tag/Feriados-Nacionais).
