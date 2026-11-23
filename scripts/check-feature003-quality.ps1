# Feature 003 / T005 / REQ-005, REQ-003, REQ-017, REQ-018, REQ-019. PowerShell 5.1+.
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
    & $python -m pytest tests -q --tb=short --cov=rides --cov-branch --cov-fail-under=80 --cov-report=term-missing --cov-report=json:coverage-feature003.json --junitxml=test-results-feature003.xml
    if ($LASTEXITCODE -ne 0) { throw 'Testes/cobertura falharam; README preservado.' }
    $metricsJson = & $python -c "import json; print(json.dumps(json.load(open('coverage-feature003.json'))['totals']))"
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao ler cobertura.' }
    $metrics = $metricsJson | ConvertFrom-Json
    $linePercent = 100.0 * $metrics.covered_lines / $metrics.num_statements
    $branchPercent = if ($metrics.num_branches -gt 0) { 100.0 * $metrics.covered_branches / $metrics.num_branches } else { 100.0 }
    if ($linePercent -lt 80 -or $branchPercent -lt 80) { throw 'Linhas ou ramificacoes abaixo de 80%; README preservado.' }
    $matchingJson = & $python -c "import json; r=json.load(open('coverage-feature003.json')); print(json.dumps(next(v['summary'] for k,v in r['files'].items() if k.replace(chr(92),'/').endswith('services/matching_service.py'))))"
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao ler matching.' }
    $matching = $matchingJson | ConvertFrom-Json
    $matchingLines = 100.0 * $matching.covered_lines / $matching.num_statements
    $matchingBranches = if ($matching.num_branches -gt 0) { 100.0 * $matching.covered_branches / $matching.num_branches } else { 100.0 }
    if ($matchingLines -lt 80 -or $matchingBranches -lt 80) { throw 'Matching abaixo de 80%; README preservado.' }
    & $python -c "import xml.etree.ElementTree as E; p='test-results-feature003.xml'; t=E.parse(p); s=t.getroot().find('testsuite'); props=s.find('properties'); props=E.SubElement(s,'properties') if props is None else props; cases=s.findall('testcase'); n=sum(c.get('name','').startswith('test_acceptance_search_') for c in cases); E.SubElement(props,'property',name='feature003_new_tests',value=str(n)); E.SubElement(props,'property',name='previous_regression_tests',value=str(len(cases)-n)); t.write(p,encoding='utf-8',xml_declaration=True)"
    if ($LASTEXITCODE -ne 0) { throw 'Falha ao registrar grupos JUnit.' }
    [xml]$junit = Get-Content -LiteralPath 'test-results-feature003.xml' -Raw -Encoding UTF8
    $cases = @($junit.SelectNodes('//testcase'))
    $passed = @($cases | Where-Object { -not $_.SelectSingleNode('failure|error|skipped') }).Count
    $skipped = @($cases | Where-Object { $_.SelectSingleNode('skipped') }).Count
    $offerPassed = @($cases | Where-Object { $_.classname -match '(^|\.)(test_ride_search|test_matching)$' -and -not $_.SelectSingleNode('failure|error|skipped') }).Count
    if ($offerPassed -eq 0) { throw 'Suite de busca ausente; README preservado.' }
    $newTests = @($cases | Where-Object { $_.name -like 'test_acceptance_search_*' }).Count
    $previousTests = $passed - $newTests
    $regression = $passed - $offerPassed
    $culture = [Globalization.CultureInfo]::InvariantCulture
    $combinedText = ([double]$metrics.percent_covered).ToString('R', $culture)
    $lineText = $linePercent.ToString('R', $culture)
    $branchText = $branchPercent.ToString('R', $culture)
    $dateText = Get-Date -Format 'yyyy-MM-dd'
    $block = @"
<!-- feature-003-quality:start -->
Feature 003 / T005 — **$offerPassed testes de busca/matching aprovados**, $regression de regressão; total $passed aprovados, $skipped ignorados. Medição: $dateText.
Cobertura do pacote técnico atual ``rides/`` com regressão: **$combinedText%** combinada; linhas $($metrics.covered_lines)/$($metrics.num_statements) ($lineText%); ramificações $($metrics.covered_branches)/$($metrics.num_branches) ($branchText%). Meta: 80% em cada medida. Estes percentuais incluem as features posteriores de rides.
Matching separado: $matchingLines% linhas e $matchingBranches% ramificações. Novos nesta tarefa: $newTests; regressão anterior: $previousTests (grupos no JUnit).
Relatórios: [coverage-feature003.json](coverage-feature003.json), [test-results-feature003.xml](test-results-feature003.xml). Reproduzir: ``powershell -NoProfile -ExecutionPolicy Bypass -File scripts/check-feature003-quality.ps1``.
Demonstração humana SC-005 (até 1 minuto) e inspeção visual são evidências separadas; este script não as aprova nem conclui T005 automaticamente. [Evidência](specs/003-busca-rota-horario/evidence-t005.md).
<!-- feature-003-quality:end -->
"@
    $readmePath = Join-Path $projectRoot 'README.md'
    $readme = [IO.File]::ReadAllText($readmePath)
    $pattern = '(?s)<!-- feature-003-quality:start -->.*?<!-- feature-003-quality:end -->'
    if ([regex]::Matches($readme, $pattern).Count -gt 1) { throw 'Bloco feature-003 duplicado.' }
    if ([regex]::Matches($readme, $pattern).Count -eq 0) { $readme = $readme.Insert($readme.IndexOf([char]10)+1, [Environment]::NewLine+$block+[Environment]::NewLine) }
    $readme = [regex]::Replace($readme, $pattern, [Text.RegularExpressions.MatchEvaluator]{ param($match) $block })
    [IO.File]::WriteAllText($readmePath, $readme, [Text.UTF8Encoding]::new($false))
    Write-Host "Feature 003: $offerPassed busca + $regression regressao; linhas $lineText%; branches $branchText%. Demo humana nao avaliada."
}
finally { Pop-Location }
