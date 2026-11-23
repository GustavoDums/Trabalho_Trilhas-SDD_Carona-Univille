# Feature 001 / T012 e entrega geral / T043. PowerShell 5.1+.
[CmdletBinding()]
param(
    [switch]$Consolidado,
    [string]$PythonPath
)

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = if ($PythonPath) { $PythonPath } else { Join-Path $projectRoot 'venv/Scripts/python.exe' }
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw 'Informe um Python com as dependencias do projeto conforme o quickstart.'
}
$python = (Resolve-Path -LiteralPath $python).Path

$scope = 'Feature 001 / T012'
$marker = 'feature-001-quality'
$sources = @('accounts', 'carona_univille.views')
$tests = @(
    'tests/test_models.py', 'tests/test_foundation.py',
    'tests/test_registration.py', 'tests/test_activation.py',
    'tests/test_access_control.py', 'tests/test_privacy_lgpd.py'
)
$coverageFile = 'coverage-feature001-t012.json'
$junitFile = 'test-results.xml'
$reproduce = 'powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-quality-metrics.ps1'
$mode = 'feature001'
if ($Consolidado) {
    $scope = 'Entrega geral / T043'
    $marker = 't043-quality'
    $sources = @('accounts', 'rides', 'reviews', 'notifications', 'carona_univille')
    $tests = @('tests')
    $coverageFile = 'coverage.json'
    $junitFile = 'test-results-t043.xml'
    $reproduce += ' -Consolidado'
    $mode = 'consolidado'
}
$coverageArgs = @($sources | ForEach-Object { "--cov=$_" })

Push-Location -LiteralPath $projectRoot
try {
    & $python -m pytest @tests @coverageArgs --cov-branch --cov-fail-under=80 --cov-report=term-missing "--cov-report=json:$coverageFile" "--junitxml=$junitFile"
    if ($LASTEXITCODE -ne 0) {
        throw "A suite ou a meta combinada de $scope falhou (codigo $LASTEXITCODE). Consulte a saida do pytest. README nao atualizado."
    }

    # Envie apenas os totais ao PowerShell 5.1, que rejeita algumas chaves do JSON detalhado.
    $metricsCode = @'
import json
from pathlib import Path
import sys

with open(sys.argv[1], encoding='utf-8') as source:
    report = json.load(source)

def percentages(data):
    lines = 100 * data['covered_lines'] / data['num_statements'] if data['num_statements'] else 100
    branches = 100 * data['covered_branches'] / data['num_branches'] if data['num_branches'] else 100
    return lines, branches, data['percent_covered']

totals = report['totals']
if not totals['num_statements']:
    raise SystemExit('Relatorio de cobertura sem linhas medidas.')
lines, branches, combined = percentages(totals)
below = []
if min(lines, branches, combined) < 80:
    below.append(f'Total: linhas {lines}%; ramificacoes {branches}%; combinada {combined}%')
critical = 0
if sys.argv[2] == 'consolidado':
    for filename, file in report['files'].items():
        path = Path(filename.replace(chr(92), '/'))
        data = file['summary']
        if 'migrations' in path.parts or not data['num_statements']:
            continue
        if path.parts[0] in {'accounts', 'rides', 'reviews', 'notifications'} or path.as_posix() == 'carona_univille/views.py':
            critical += 1
            measured = percentages(data)
            if min(measured) < 80:
                below.append(f'{path}: linhas {measured[0]}%; ramificacoes {measured[1]}%; combinada {measured[2]}%')
if below:
    raise SystemExit('Cobertura abaixo de 80%:\n' + '\n'.join(below))

print(json.dumps(dict(
    covered_lines=totals['covered_lines'], num_statements=totals['num_statements'],
    covered_branches=totals['covered_branches'], num_branches=totals['num_branches'],
    lines=str(totals.get('percent_statements_covered', lines)),
    branches=str(totals.get('percent_branches_covered', branches)),
    combined=str(combined), critical=critical,
)))
'@
    $metricsJson = & $python -c $metricsCode $coverageFile $mode
    if ($LASTEXITCODE -ne 0) { throw "Falha de validacao de $coverageFile. README nao atualizado." }
    $metrics = $metricsJson | ConvertFrom-Json

    [xml]$junit = Get-Content -LiteralPath $junitFile -Raw -Encoding UTF8
    $cases = @($junit.SelectNodes('//testcase'))
    $passed = @($cases | Where-Object { -not $_.SelectSingleNode('failure|error|skipped') }).Count
    $skipped = @($cases | Where-Object { $_.SelectSingleNode('skipped') }).Count
    if ($passed -eq 0) { throw 'Nenhum teste aprovado na execucao.' }

    $dateText = Get-Date -Format 'yyyy-MM-dd'
    $sourceText = $sources -join ', '
    $readmePath = Join-Path $projectRoot 'README.md'
    $readme = [IO.File]::ReadAllText($readmePath)
    $newline = if ($readme.Contains([string][char]13 + [char]10)) { [string][char]13 + [char]10 } else { [string][char]10 }
    $blockLines = @(
        "<!-- $($marker):start -->"
        "$scope — **$passed testes aprovados**, $skipped ignorados. Meta: **80%**."
        "Cobertura combinada de $sourceText — **$($metrics.combined)%**."
        "Linhas: $($metrics.covered_lines)/$($metrics.num_statements) (**$($metrics.lines)%**). Ramificações: $($metrics.covered_branches)/$($metrics.num_branches) (**$($metrics.branches)%**)."
        if ($Consolidado) {
            "Escopo de 11 features. Meta atingida globalmente e nos $($metrics.critical) módulos críticos."
        }
        "Relatórios: [$coverageFile]($coverageFile) e [$junitFile]($junitFile). Medição: $dateText."
        ('Reproduzir: ' + [char]96 + $reproduce + [char]96 + '.')
        "<!-- $($marker):end -->"
    )
    $block = $blockLines -join $newline
    $pattern = "(?s)<!-- $($marker):start -->.*?<!-- $($marker):end -->"
    $count = [regex]::Matches($readme, $pattern).Count
    if ($count -gt 1 -or ($count -eq 0 -and -not $Consolidado)) { throw "Verifique o bloco $marker no README." }
    $updated = if ($count -eq 1) {
        [regex]::Replace($readme, $pattern, [Text.RegularExpressions.MatchEvaluator]{ param($match) $block })
    } else {
        $readme.Insert($readme.IndexOf([char]10) + 1, $newline + $block + $newline)
    }
    [IO.File]::WriteAllText($readmePath, $updated, [Text.UTF8Encoding]::new($false))
    Write-Host "$($scope): $passed aprovados; cobertura $($metrics.combined)%; meta 80% atendida em linhas e ramificacoes."
}
finally { Pop-Location }
