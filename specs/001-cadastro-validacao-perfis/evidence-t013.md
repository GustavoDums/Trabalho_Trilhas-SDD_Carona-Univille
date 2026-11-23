# Evidência da Feature 001 / T013 local — revisão visual

**Data** 2026-11-23 · **Requisitos** REQ-001, REQ-002, REQ-003, REQ-014, REQ-015, REQ-017, REQ-018 e REQ-019.

Cadastro e login passaram a usar um painel institucional e formulários com rótulos persistentes. O layout compartilhado aplica navegação por papel, foco visível, cartões, mensagens e estados consistentes às áreas de perfil, caronas, avaliações e avisos. A interface usa uma folha de estilos local. Formulários, campos, ações com CSRF, validações e dados de sessão usam os contratos existentes.

## Verificações

- Cadastro revisado no Edge em 1440 px e 390 px. Login revisado em 390 px. A largura do conteúdo permaneceu dentro da janela e os campos visíveis conservaram rótulos associados.
- A busca autenticada foi revisada em 1440 px e 390 px, com uma oferta aberta e uma esgotada. Minhas ofertas e Meu perfil foram revisados em 390 px. A navegação mostrou o papel da sessão e indicou a página atual.
- Os 93 testes focados de cadastro, acesso e notificações passaram. A regressão inicial detectou duas verificações de busca dependentes da abertura do cartão. O seletor `article[data-offer-id]` foi preservado, e os 196 testes focados de busca, ofertas e fila passaram em seguida.
- `manage.py check` passou e `findstatic accounts/carona.css` confirmou a localização da folha de estilos.
- A suíte consolidada no PostgreSQL passou com 992 testes, sem falhas ou ignorados. Cobertura combinada de 98.49023090586145%, em linhas de 98.96401308615049% e em ramificações de 96.41148325358851%. Os resultados foram conferidos no [README](../../README.md), no [JSON](../../coverage.json) e no [JUnit](../../test-results-t043.xml).

## Reprodução

~~~powershell
python manage.py check
python manage.py findstatic accounts/carona.css
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-quality-metrics.ps1 -Consolidado
~~~
