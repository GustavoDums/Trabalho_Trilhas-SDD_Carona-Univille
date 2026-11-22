# Feature 001 / T012 / REQ-018, REQ-019. PowerShell 5.1+.
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot 'venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Crie o ambiente virtual venv conforme o quickstart.' }

Push-Location -LiteralPath $projectRoot
try {
    $featureTests = @(
        'tests/test_models.py', 'tests/test_foundation.py',
        'tests/test_registration.py', 'tests/test_activation.py',
        'tests/test_access_control.py', 'tests/test_privacy_lgpd.py'
    )
    & $python -m pytest @featureTests --cov=accounts --cov=carona_univille.views --cov-branch --cov-fail-under=80 --cov-report=term-missing --cov-report=json:coverage.json --junitxml=test-results.xml
    if ($LASTEXITCODE -ne 0) { throw "A suite da Feature 001 falhou (codigo $LASTEXITCODE). README nao atualizado." }

    # Extrai apenas totais: ConvertFrom-Json do PS 5.1 rejeita chaves vazias
    # presentes em algumas versoes do relatorio completo do coverage.py.
    $metricsJson = & $python -c "import json; print(json.dumps(json.load(open('coverage.json'))['totals']))"
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao ler coverage.json.' }
    $metrics = $metricsJson | ConvertFrom-Json
    $linePercent = 100.0 * $metrics.covered_lines / $metrics.num_statements
    $branchPercent = if ($metrics.num_branches -gt 0) { 100.0 * $metrics.covered_branches / $metrics.num_branches } else { 100.0 }
    if ($linePercent -lt 80 -or $branchPercent -lt 80) {
        throw 'Feature 001 abaixo de 80% em linhas ou ramificacoes. README nao atualizado.'
    }

    [xml]$junit = Get-Content -LiteralPath 'test-results.xml' -Raw -Encoding UTF8
    $cases = @($junit.SelectNodes('//testcase'))
    $passed = @($cases | Where-Object { -not $_.SelectSingleNode('failure|error|skipped') }).Count
    $skipped = @($cases | Where-Object { $_.SelectSingleNode('skipped') }).Count
    if ($passed -eq 0) { throw 'Nenhum teste aprovado na execucao.' }

    $culture = [Globalization.CultureInfo]::InvariantCulture
    $combinedText = ([double]$metrics.percent_covered).ToString('R', $culture)
    $lineText = $linePercent.ToString('R', $culture)
    $branchText = $branchPercent.ToString('R', $culture)
    $dateText = Get-Date -Format 'yyyy-MM-dd'
    $block = @"
<!-- feature-001-quality:start -->
Feature 001 / T012 — $passed testes aprovados; $skipped ignorados. Meta: **80%**.
Cobertura combinada de ``accounts/`` e ``carona_univille/views.py``: **$combinedText%**.
Linhas: $($metrics.covered_lines)/$($metrics.num_statements) ($lineText%); ramificações: $($metrics.covered_branches)/$($metrics.num_branches) ($branchText%).
Relatórios: [coverage.json](coverage.json) e [test-results.xml](test-results.xml). Medição: $dateText.

Reproduzir: ``powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-quality-metrics.ps1``.
<!-- feature-001-quality:end -->
"@
    $readmePath = Join-Path $projectRoot 'README.md'
    $readme = [IO.File]::ReadAllText($readmePath)
    $pattern = '(?s)<!-- feature-001-quality:start -->.*?<!-- feature-001-quality:end -->'
    if ([regex]::Matches($readme, $pattern).Count -ne 1) { throw 'README deve conter um unico bloco feature-001-quality.' }
    $updated = [regex]::Replace($readme, $pattern, [Text.RegularExpressions.MatchEvaluator]{ param($match) $block })
    [IO.File]::WriteAllText($readmePath, $updated, [Text.UTF8Encoding]::new($false))
    Write-Host "Feature 001: $passed aprovados; cobertura $combinedText%; meta 80% atendida em linhas e ramificacoes."
}
finally { Pop-Location }
