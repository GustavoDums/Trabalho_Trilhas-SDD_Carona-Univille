# Feature 002 / T007 / REQ-004, REQ-018, REQ-019. PowerShell 5.1+.
[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $projectRoot 'venv/Scripts/python.exe'
if (-not (Test-Path -LiteralPath $python)) { throw 'Use o venv do projeto.' }
Push-Location -LiteralPath $projectRoot
try {
    # rides inclui features posteriores: medir todo o pacote com regressao,
    # separando a suite de oferta no JUnit, sem excluir codigo da medicao.
    & $python -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-fail-under=80 --cov-report=term-missing --cov-report=json:coverage-feature002.json --junitxml=test-results-feature002.xml
    if ($LASTEXITCODE -ne 0) { throw 'Testes/cobertura falharam; README preservado.' }
    $metricsJson = & $python -c "import json; print(json.dumps(json.load(open('coverage-feature002.json'))['totals']))"
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao ler cobertura.' }
    $metrics = $metricsJson | ConvertFrom-Json
    $linePercent = 100.0 * $metrics.covered_lines / $metrics.num_statements
    $branchPercent = if ($metrics.num_branches -gt 0) { 100.0 * $metrics.covered_branches / $metrics.num_branches } else { 100.0 }
    if ($linePercent -lt 80 -or $branchPercent -lt 80) { throw 'Linhas ou ramificacoes abaixo de 80%; README preservado.' }
    [xml]$junit = Get-Content -LiteralPath 'test-results-feature002.xml' -Raw -Encoding UTF8
    $cases = @($junit.SelectNodes('//testcase'))
    $passed = @($cases | Where-Object { -not $_.SelectSingleNode('failure|error|skipped') }).Count
    $skipped = @($cases | Where-Object { $_.SelectSingleNode('skipped') }).Count
    $offerPassed = @($cases | Where-Object { $_.classname -match '(^|\.)test_rides_offer$' -and -not $_.SelectSingleNode('failure|error|skipped') }).Count
    if ($offerPassed -eq 0) { throw 'Suite de oferta ausente; README preservado.' }
    $regression = $passed - $offerPassed
    $culture = [Globalization.CultureInfo]::InvariantCulture
    $combinedText = ([double]$metrics.percent_covered).ToString('R', $culture)
    $lineText = $linePercent.ToString('R', $culture)
    $branchText = $branchPercent.ToString('R', $culture)
    $dateText = Get-Date -Format 'yyyy-MM-dd'
    $block = @"
<!-- feature-002-quality:start -->
Feature 002 / T007 — **$offerPassed testes de oferta aprovados**, $regression de regressão; total $passed aprovados, $skipped ignorados. Medição: $dateText.
Cobertura do pacote técnico atual ``rides/`` com regressão: **$combinedText%** combinada; linhas $($metrics.covered_lines)/$($metrics.num_statements) ($lineText%); ramificações $($metrics.covered_branches)/$($metrics.num_branches) ($branchText%). Meta: 80% em cada medida. Estes percentuais incluem as features posteriores de rides.
Relatórios: [coverage-feature002.json](coverage-feature002.json), [test-results-feature002.xml](test-results-feature002.xml). Reproduzir: ``powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-feature002-quality.ps1``.
Demonstração humana SC-005 e inspeção visual são evidências separadas; este script não as aprova nem conclui T007 automaticamente. [Evidência](specs/002-oferta-caronas-paradas/evidence-t007.md).
<!-- feature-002-quality:end -->
"@
    $readmePath = Join-Path $projectRoot 'README.md'
    $readme = [IO.File]::ReadAllText($readmePath)
    $pattern = '(?s)<!-- feature-002-quality:start -->.*?<!-- feature-002-quality:end -->'
    if ([regex]::Matches($readme, $pattern).Count -ne 1) { throw 'Esperado um bloco feature-002-quality.' }
    $readme = [regex]::Replace($readme, $pattern, [Text.RegularExpressions.MatchEvaluator]{ param($match) $block })
    [IO.File]::WriteAllText($readmePath, $readme, [Text.UTF8Encoding]::new($false))
    Write-Host "Feature 002: $offerPassed oferta + $regression regressao; linhas $lineText%; branches $branchText%. Demo humana nao avaliada."
}
finally { Pop-Location }
