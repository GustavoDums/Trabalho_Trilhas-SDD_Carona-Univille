# Guia de Inicialização Rápida e Validação (Quickstart)

**Feature**: `001-cadastro-validacao-perfis`  
**Data**: 2026-11-21  
**Ambiente**: Windows 11 com PowerShell

Este guia descreve o passo a passo para configurar o ambiente de desenvolvimento, inicializar o banco de dados PostgreSQL, conferir o catálogo fictício de testes, executar a suíte automatizada de testes, gerar os relatórios de cobertura versionáveis e atualizar os indicadores de qualidade no `README.md`.

---

## 1. Pré-Requisitos de Ambiente

- **Python**: Versão 3.12 ou superior instalada e acessível no `PATH`.
- **PostgreSQL**: Servidor PostgreSQL 15+ ativo localmente na porta padrão `5432` (serviço do Windows ou container Docker).
- **Git**: Para controle de versão e rastreabilidade dos commits.

---

## 2. Preparação do Ambiente no Windows (PowerShell)

Abra o terminal do PowerShell na raiz do projeto (`Trabalho_Trilhas-SDD_Carona-Univille`):

```powershell
# 1. Criar o ambiente virtual Python
python -m venv venv

# 2. Ativar o ambiente virtual no PowerShell
.\venv\Scripts\Activate.ps1

# 3. Atualizar o pip e instalar as dependências da stack oficial
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 3. Configuração do Banco de Dados PostgreSQL

Certifique-se de que o serviço do PostgreSQL está em execução. No PowerShell, configure o arquivo de ambiente e crie o banco de dados:

```powershell
# 1. Copiar o arquivo de exemplo de variáveis de ambiente
if (-not (Test-Path .env)) { Copy-Item .env.example .env }

# 2. Criar a base de dados principal e a base de testes via psql (ou pgAdmin)
# Ajuste 'postgres' para o seu usuário do PostgreSQL, se aplicável:
psql -U postgres -c "CREATE DATABASE carona_univille_db;"
# O pytest-django cria e remove o banco de testes automaticamente.

# 3. Executar as migrações estruturais do Django
python manage.py migrate

# 4. Conferir a sintaxe do catálogo fictício de homologação
python -m json.tool accounts/fixtures/academic_whitelist.json
```

A whitelist é um catálogo JSON consumido em memória pelo serviço de validação
(T007), conforme `data-model.md`. Não é uma fixture do ORM Django e não deve ser
carregada com `loaddata`. A T003 fornece o catálogo; nenhuma conta é criada ou
ativada automaticamente a partir dele.

---

## 4. Execução da Aplicação Web para Demonstração Manual

```powershell
# Iniciar o servidor local de desenvolvimento
python manage.py runserver
```

Acesse no navegador:
- Cadastro Institucional: `http://localhost:8000/accounts/register/`
- Autenticação: `http://localhost:8000/accounts/login/`
- Validação de Vínculo: `http://localhost:8000/accounts/activation/`

---

## 5. Medição reproduzível da Feature 001

Na raiz do projeto, usando o ambiente virtual já instalado:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-quality-metrics.ps1
```

O script usa `venv/Scripts/python.exe` e executa os seis arquivos de testes
explicitamente associados à Feature 001 (modelos, fundação, cadastro, ativação,
controle de acesso e privacidade). A cobertura inclui `accounts/` e a view
placeholder de `carona_univille/views.py`. Não representa cobertura de features futuras.

A execução gera dois relatórios versionáveis:

- `coverage.json`: linhas, ramificações e percentual combinado do pytest-cov.
- `test-results.xml`: resultado JUnit da execução real, usado para contar aprovados
  e ignorados, sem estimar a contagem por `--collect-only`.

O pytest aplica `--cov-branch --cov-fail-under=80`. O script também exige
**80% separadamente em linhas e ramificações** e propaga falhas com saída não zero.
Somente após sucesso ele sincroniza o bloco marcado no início do `README.md`,
preservando o restante do documento. Uma falha não atualiza as métricas do README.
Os relatórios devem ser revisados e incluídos no commit pela dupla.

## 6. Verificações do ambiente e dos fluxos

```powershell
.\venv\Scripts\python.exe manage.py check
.\venv\Scripts\python.exe manage.py migrate --check
.\venv\Scripts\python.exe -m json.tool accounts/fixtures/academic_whitelist.json
```

A suíte exercita os cenários abaixo pelo cliente HTTP Django e pelo ORM no
PostgreSQL de testes. O usuário do banco precisa de permissão para criar o banco
de testes; o pytest-django gerencia sua criação e remoção. Não use dados reais.
Não é necessário recriar ambiente, sobrescrever `.env` ou criar bancos existentes
para repetir a medição.

Para uma inspeção manual, inicie o servidor conforme a seção 4. Cadastre uma conta
fictícia, incluindo senha e confirmação; o cadastro leva ao login **sem autenticação
automática**. Faça login com essa credencial para abrir a ativação. O botão único
valida o e-mail da sessão, sem matrícula ou outros campos. O catálogo não cria contas.
Não há listagem pública de perfis nesta feature nem fluxo de logout implementado.
Use sessões privadas distintas do navegador para demonstrar contas diferentes.

---
## 7. Roteiro de Validação dos Cenários da Spec 001

Execute os seguintes testes ponta a ponta (manuais ou automatizados) para validar a entrega:

1. **Cenário 1 (Cadastro de Passageiro Elegível)**:
   - Cadastrar `lucas.aluno@univille.br` com papel `Passageiro`.
   - Esperado: Conta criada com `academic_status = 'PENDENTE'`.
2. **Cenário 2 (Cadastro de Motorista Elegível)**:
   - Cadastrar `mariana.motorista@univille.br` com papel `Motorista`.
   - Esperado: Conta criada com `academic_status = 'PENDENTE'`.
3. **Cenário 3 (Rejeição de Domínio Forasteiro)**:
   - Tentar cadastrar `visitante@gmail.com`.
   - Esperado: Bloqueio imediato com mensagem de erro de domínio acadêmico.
4. **Cenário 4 (Tentativa de Cadastro Duplicado)**:
   - Tentar cadastrar novamente `lucas.aluno@univille.br`.
   - Esperado: Mensagem neutra/genérica informando para tentar login; contagem no banco mantida em 1 registro.
5. **Cenário 5 (Confinamento de Conta Pendente)**:
   - Fazer login com conta pendente e tentar acessar `/caronas/`.
   - Esperado: Redirecionamento 302 imediato para `/accounts/activation/`.
6. **Cenário 6 (Ativação com Sucesso - Whitelist Elegível)**:
   - Na tela de ativação de `lucas.aluno@univille.br`, clicar em "Validar Vínculo Institucional".
   - Esperado: Transição para `academic_status = 'ATIVA'` e redirecionamento para o perfil com selo de ativo.
7. **Cenário 7 (Falha na Ativação - Inelegível)**:
   - Cadastrar `estudante.inexistente@univille.br` e acionar validação.
   - Esperado: Recusa pelo simulador, manutenção do status `PENDENTE` e permanência na tela de ativação.
8. **Cenário 8 (Privacidade e LGPD)**:
   - Autenticar a própria conta ativa de `Lucas Aluno` e abrir `/accounts/profile/`.
   - Esperado: nome completo próprio, prévia abreviada `Lucas A.` e e-mail institucional não renderizado. Visitantes e pendentes são redirecionados; não existe perfil público nesta feature.
