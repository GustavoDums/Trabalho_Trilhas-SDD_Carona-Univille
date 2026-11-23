# Feature 005 / T007 local / roadmap T027 / REQ-001--REQ-007, REQ-014--REQ-019.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot 'venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Use o venv do projeto conforme quickstart.' }
Push-Location -LiteralPath $projectRoot
try {
    & $python manage.py check
    if ($LASTEXITCODE -ne 0) { throw 'Django check falhou.' }
    & $python manage.py makemigrations --check --dry-run
    if ($LASTEXITCODE -ne 0) { throw 'Ha alteracoes de schema sem migracao.' }
    & $python manage.py migrate --check
    if ($LASTEXITCODE -ne 0) { throw 'Ha migracoes locais pendentes; revisar sem reset.' }
    & $python -m pytest tests -q --tb=short --cov=accounts --cov=rides --cov=carona_univille --cov-branch --cov-fail-under=80 --cov-report=term-missing --cov-report=json:coverage-mvp.json --junitxml=test-results-mvp.xml
    if ($LASTEXITCODE -ne 0) { throw 'Suite/cobertura MVP falhou; README preservado.' }
    $metricsCode = @"
import json
r = json.load(open('coverage-mvp.json'))
def checked(s, name):
    lines = 100*s['covered_lines']/s['num_statements'] if s['num_statements'] else 100
    branches = 100*s['covered_branches']/s['num_branches'] if s['num_branches'] else 100
    if min(lines, branches, s['percent_covered']) < 80:
        raise SystemExit(name+' abaixo de 80% em linhas, branches ou combinada')
    return dict(lines=lines, branches=branches, combined=s['percent_covered'])
totals = checked(r['totals'], 'MVP')
critical = {}
for path, data in r['files'].items():
    path = path.replace(chr(92), '/')
    if (path.startswith('accounts/') and path.endswith(('models.py','forms.py','middleware.py','services.py','views.py'))) or (path.startswith('rides/') and ('/services/' in path or path.endswith(('models.py','forms.py','views.py')))):
        critical[path] = checked(data['summary'], path)
print(json.dumps(dict(totals=r['totals'], measured=totals, critical=critical)))
"@
    $metricsJson = & $python -c $metricsCode
    if ($LASTEXITCODE -ne 0) { throw 'Meta critica nao atendida; README preservado.' }
    $report = $metricsJson | ConvertFrom-Json
    [xml]$junit = Get-Content -LiteralPath 'test-results-mvp.xml' -Raw -Encoding UTF8
    $cases = @($junit.SelectNodes('//testcase'))
    $passed = @($cases | Where-Object { -not $_.SelectSingleNode('failure|error|skipped') }).Count
    $skipped = @($cases | Where-Object { $_.SelectSingleNode('skipped') }).Count
    if ($passed -eq 0 -or $skipped -ne 0) { throw 'Auditoria exige suite completa sem casos ignorados; README preservado.' }
    $culture = [Globalization.CultureInfo]::InvariantCulture
    $combined = ([double]$report.measured.combined).ToString('R', $culture)
    $lines = ([double]$report.measured.lines).ToString('R', $culture)
    $branches = ([double]$report.measured.branches).ToString('R', $culture)
    $dateText = Get-Date -Format 'yyyy-MM-dd'
    $block = @"
<!-- mvp-quality:start -->
MVP / Feature 005 / T007 local / roadmap T027 — **$passed testes aprovados**, $skipped ignorados; REQ-001–REQ-007. Medição: $dateText.
Cobertura consolidada de ``accounts/``, ``rides/`` e ``carona_univille/``: **$combined%** combinada; linhas $($report.totals.covered_lines)/$($report.totals.num_statements) (**$lines%**); ramificações $($report.totals.covered_branches)/$($report.totals.num_branches) (**$branches%**). Meta: >=80% combinada, linhas e ramificações, também por módulo crítico de negócio.
Relatórios: [coverage-mvp.json](coverage-mvp.json), [test-results-mvp.xml](test-results-mvp.xml), [auditoria](specs/005-cancelamento-liberacao-vaga/evidence-t027.md).
Reproduzir: ``powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-mvp-quality.ps1``. Métricas consolidadas; não são testes exclusivos da Feature 005. T041–T045 e tarefas de qualidade próprias de outras features não são concluídas automaticamente.
<!-- mvp-quality:end -->
"@
    $path = Join-Path $projectRoot 'README.md'
    $readme = [IO.File]::ReadAllText($path)
    $pattern = '(?s)<!-- mvp-quality:start -->.*?<!-- mvp-quality:end -->'
    $count = [regex]::Matches($readme, $pattern).Count
    if ($count -gt 1) { throw 'Bloco MVP duplicado; README preservado.' }
    if ($count -eq 1) { $readme = [regex]::Replace($readme, $pattern, [Text.RegularExpressions.MatchEvaluator]{ param($match) $block }) }
    else { $readme = $readme.Insert($readme.IndexOf([char]10)+1, [Environment]::NewLine+$block+[Environment]::NewLine) }
    [IO.File]::WriteAllText($path, $readme, [Text.UTF8Encoding]::new($false))
    Write-Host "MVP: $passed aprovados; linhas $lines%; branches $branches%; modulos criticos >=80%."
}
finally { Pop-Location }
