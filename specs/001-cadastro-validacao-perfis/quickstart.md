# Guia de Inicialização Rápida e Validação (Quickstart)

**Feature**: `001-cadastro-validacao-perfis`  
**Data**: 2026-11-21  
**Ambiente**: Windows 11 com PowerShell

Este guia descreve o passo a passo para configurar o ambiente de desenvolvimento, inicializar o banco de dados PostgreSQL, carregar a base fictícia de testes, executar a suíte automatizada de testes, gerar os relatórios de cobertura versionáveis e atualizar os indicadores de qualidade no `README.md`.

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
Copy-Item .env.example .env

# 2. Criar a base de dados principal e a base de testes via psql (ou pgAdmin)
# Ajuste 'postgres' para o seu usuário do PostgreSQL, se aplicável:
psql -U postgres -c "CREATE DATABASE carona_univille_db;"
psql -U postgres -c "CREATE DATABASE carona_univille_test_db;"

# 3. Executar as migrações estruturais do Django
python manage.py migrate

# 4. Carregar os dados fictícios da whitelist acadêmica de homologação
python manage.py loaddata accounts/fixtures/academic_whitelist.json
```

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

## 5. Execução dos Testes Automatizados e Geração de Cobertura

Conforme exigido pelo **Princípio III da Constitution**, a base de código deve manter cobertura mínima de 80% e gerar relatórios versionados no repositório.

### 5.1. Executar a Suíte de Testes
```powershell
# Executa todos os testes com saída verbosa
pytest -v
```

### 5.2. Gerar Relatório de Cobertura Versionável
```powershell
# Executa testes gerando relatório em terminal, em JSON e em HTML
pytest --cov=accounts --cov-report=term-missing --cov-report=json:coverage.json --cov-report=html:htmlcov
```

---

## 6. Extração de Métricas para Atualização Contínua do `README.md`

O topo do arquivo `README.md` deve exibir a quantidade real de testes executados com sucesso e o percentual exato medido de cobertura. Utilize o seguinte script no PowerShell para obter os valores exatos:

```powershell
# Script de extração de métricas de qualidade
$covData = Get-Content coverage.json | ConvertFrom-Json
$percent = [math]::Round($covData.totals.percent_covered, 2)
$testCount = (pytest -q --collect-only | Select-String "test").Count

Write-Host "================ METRICAS DE QUALIDADE ================" -ForegroundColor Cyan
Write-Host "Total de Testes Automatizados: $testCount" -ForegroundColor Green
Write-Host "Cobertura de Testes Medida:    $percent%" -ForegroundColor Green
Write-Host "========================================================" -ForegroundColor Cyan
```

### Atualização do Cabeçalho do `README.md`
Copie as métricas extraídas para a seção de badges / indicadores do `README.md`:

```markdown
# Carona Univille

![Testes](https://img.shields.io/badge/testes-12%20passando-brightgreen)
![Cobertura](https://img.shields.io/badge/cobertura-85.4%25-brightgreen)

> **Métricas da Entrega Atual (v1.1.0)**:
> - **Testes Automatizados**: 12 executados com 100% de sucesso
> - **Cobertura Medida**: 85.4% (Meta mínima da Constitution: 80%)
```

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
   - Verificar a visualização pública do perfil de `Lucas Aluno`.
   - Esperado: Nome abreviado como `Lucas A.` e e-mail institucional não renderizado.
