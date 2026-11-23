# Quickstart de validação: Feature 009

Validar o gerador e a independência das ocorrências com a suíte da T035. A suíte da T036 cobre o formulário, o comando diário e a integração com busca e reserva.

1. Fechar decisões da [spec](spec.md), implementar dependências, usar venv e PostgreSQL existentes, sem imprimir segredos.
2. Após implementação, da raiz:

~~~powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py makemigrations --check --dry-run
.\venv\Scripts\python.exe manage.py migrate --plan
.\venv\Scripts\python.exe manage.py migrate
.\venv\Scripts\python.exe -m pytest tests/test_recurring_rides.py tests/test_recurring_flow.py tests/test_holiday_calendar.py -q --tb=short
~~~

3. Executar SC-001 a SC-004 da [spec](spec.md) com dados fictícios, incluindo a geração concorrente e o cancelamento de somente uma ocorrência. SC-005 valida as entradas da T036.
4. Concorrência requer conexões PostgreSQL independentes e testes transacionais; SQLite/mocks de lock não comprovam integridade.
5. Rodar regressão das dependências; script de qualidade da tarefa final gera JUnit e cobertura identificados por feature, >=80% de linhas e ramificações críticas; README somente com números reais. Auditoria MVP da 005 consolida REQ-001–REQ-007.
6. Em Minhas ofertas, abrir Caronas recorrentes e cadastrar uma regra com dados fictícios. Verificar as datas na listagem, depois buscar e reservar uma carona em uma sessão de passageiro.
7. Para validar a T008 com a API real, use um ambiente com acesso HTTPS a `brasilapi.com.br`. Compare a janela gerada com a data local de hoje e o 15º dia útil inclusivo. Para a virada do ano, consulte os dois calendários anuais. Os testes automatizados simulam as respostas HTTP, incluindo indisponibilidade, sem depender da rede.

## Acionamento diário

No agendador do ambiente de execução, use o diretório do projeto como pasta de trabalho, configure o ambiente Django e execute o comando uma vez por dia. A conta do processo deve ser do operador autorizado.

~~~powershell
.\venv\Scripts\python.exe manage.py generate_recurring_rides --all
~~~

Para executar em uma única regra, substitua `--all` por `--rule ID`. A janela de 15 dias úteis é calculada em America/Sao_Paulo. A rotina pode ser repetida com segurança. Se o comando relatar indisponibilidade do calendário, execute de novo após a recuperação do serviço.
