# T045 — Roteiro e ensaio da demonstração ao vivo

**Área** Entrega geral · **Requisito** REQ-020 · **Dependências concluídas** T043 e T044 · **Data do ensaio** 2026-11-23.

[Slides do pitch](pitch-carona-univille.pptx) · [Tempo dos slides](evidencia-t044.md) · [Medição da entrega](evidencia-t043.md).

## Preparação

Use uma base PostgreSQL nova e exclusiva da demonstração, com as migrações aplicadas e o servidor local em modo multithread. Configure `DB_NAME`, `DB_HOST`, `DB_PORT`, `DB_USER` e `DB_PASSWORD` para essa base, conforme o [quickstart](../specs/001-cadastro-validacao-perfis/quickstart.md). O catálogo de pontos é instalado pelas migrações. Use apenas os três perfis fictícios abaixo e uma senha de demonstração criada durante a preparação.

| Sessão | Conta fictícia | Papel |
| --- | --- | --- |
| Navegador principal | `mariana.motorista@univille.br` | Motorista |
| Perfil de navegador separado | `joao.silva@univille.br` | Passageiro 1 |
| Outro perfil de navegador separado | `lucas.aluno@univille.br` | Passageiro 2 |

Antes do pitch, deixe os dois passageiros cadastrados, ativados e conectados em sessões separadas, com a mesma senha fictícia para a disputa. Deixe o cadastro da motorista para a apresentação. A partir da raiz do projeto, com o ambiente virtual ativado:

~~~powershell
python manage.py migrate
python manage.py runserver 127.0.0.1:8000 --noreload
~~~

## Apresentação

Reserve 3:00 para os slides e 0:15 de transição. O roteiro abaixo tem alvo de 5:10 para o aplicativo, somando 8:25 com os slides e deixando 1:35 de margem até o limite. Os tempos desta tabela orientam a apresentação.

No navegador, abra `http://127.0.0.1:8000/accounts/register/` para o cadastro. Os atalhos das etapas seguintes são `/caronas/oferecer/`, `/caronas/buscar/` e `/caronas/minhas-reservas/` no mesmo servidor.

| Tempo no aplicativo | Ação | O que mostrar |
| --- | --- | --- |
| 0:00–1:45 | Cadastre a motorista, faça login e abra a validação acadêmica. Clique em **Validar Vínculo Institucional**. | Antes da validação, a conta está pendente. Após validar, o perfil indica vínculo ativo. Explique que a PoC usa um catálogo fictício. |
| 1:45–2:40 | Em **Oferecer carona**, publique Terminal Central → Terminal Norte → Bairro América → Campus Univille, com uma vaga, veículo fictício e saída amanhã. | **Minhas ofertas** preserva a ordem das duas paradas. Anote o ID em **Cancelar oferta**. |
| 2:40–3:20 | Na sessão de um passageiro, busque Terminal Norte → Campus Univille na data e no horário publicados. | O cartão da oferta mostra uma vaga disponível no trecho. |
| 3:20–4:15 | Use o comando de disputa abaixo com o ID da oferta. Após o resultado, atualize a busca e **Minhas reservas** na sessão vencedora. | Duas sessões enviaram a solicitação em paralelo. Uma recebeu confirmação e a outra recebeu esgotamento. O saldo exibido é zero. |
| 4:15–5:10 | Na sessão vencedora, abra **Minhas reservas**, expanda **Cancelar reserva** e confirme. Atualize a busca na outra sessão. | O histórico mantém a reserva cancelada e a busca volta a mostrar uma vaga disponível. |

O comando abaixo apresenta a disputa real pelo formulário HTTP de reserva. Use o terminal para mostrar o resultado e o navegador para mostrar a busca e o painel. Substitua `1` pelo ID da oferta publicada. A senha digitada no terminal fica oculta.

~~~powershell
python scripts/rehearse-live-demo.py --disputar 1
~~~

## Ensaio cronometrado

Com outra base nova e migrada, execute abaixo. O script cadastra, autentica e ativa as três contas via HTTP com CSRF, publica a oferta, busca o trecho em duas sessões, dispara dois POSTs concorrentes usando uma barreira e cancela a reserva da sessão vencedora. Os IDs e o saldo são verificados pelas páginas reais retornadas pelo servidor.

~~~powershell
python scripts/rehearse-live-demo.py
~~~

Executado contra o Django em `127.0.0.1:58045` com `--porta 58045` e PostgreSQL 16.15. A preparação do banco e a abertura do servidor ocorreram antes do início do relógio.

| Etapa verificada | Tempo |
| --- | --- |
| Cadastro, login e ativação de três contas | 6,41 s |
| Publicação com duas paradas | 0,30 s |
| Busca por trecho e horário | 0,17 s |
| Duas tentativas, uma confirmação, uma recusa e saldo zero | 0,35 s |
| Cancelamento e vaga novamente disponível | 0,27 s |
| **Fluxo web completo** | **7,50 s** |

Uma consulta ao PostgreSQL confirmou três vínculos ativos, uma oferta com uma vaga e duas paradas ordenadas, uma reserva cancelada e zero reservas confirmadas após o ensaio. O modo `--disputar` também foi executado com as duas sessões fictícias e produziu uma confirmação e uma recusa.

Os 38 testes selecionados em `tests/test_concurrency_booking.py` e `tests/test_cancellation_flow.py` passaram no PostgreSQL com o filtro `-k "concurrency or serializes"`. `git diff --check` passou.

O tempo medido corresponde ao fluxo web automatizado no aplicativo em execução. O tempo de fala e cliques no navegador é uma estimativa da apresentação.
