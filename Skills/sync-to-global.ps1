#!/usr/bin/env pwsh
# Sync-SkillsToGlobal.ps1
# Copies all SKILL.md files from local repo Skills/ to global opencode config
# Source of truth: E:/repos/trading_notes/Skills/
# Target: C:/Users/Manumafe/.config/opencode/skills/

$ErrorActionPreference = "Stop"

$sourceRoot = "E:/repos/trading_notes/Skills"
$targetRoot = "C:/Users/Manumafe/.config/opencode/skills"

# Mapping of local folder names to global skill names
$skillMappings = @{
    "forex_factory_high_impact_fetch" = "forex-factory-high-impact-fetch"
    "forex_factory_bank_holiday_fetch" = "forex-factory-bank-holiday-fetch"
    "key_levels_in_range" = "key_levels_in_range"
}

$synced = 0
$errors = 0

foreach ($mapping in $skillMappings.GetEnumerator()) {
    $localDir = Join-Path $sourceRoot $mapping.Key
    $globalDir = Join-Path $targetRoot $mapping.Value
    $sourceFile = Join-Path $localDir "SKILL.md"
    $targetFile = Join-Path $globalDir "SKILL.md"

    if (-not (Test-Path $sourceFile)) {
        Write-Warning "Source not found: $sourceFile"
        $errors++
        continue
    }

    # Ensure target directory exists
    if (-not (Test-Path $globalDir)) {
        New-Item -ItemType Directory -Path $globalDir | Out-Null
        Write-Host "Created directory: $globalDir" -ForegroundColor Cyan
    }

    # Copy the file
    Copy-Item -Path $sourceFile -Destination $targetFile -Force
    Write-Host "Synced: $($mapping.Key) -> $($mapping.Value)" -ForegroundColor Green
    $synced++
}

Write-Host "`nDone. Synced: $synced, Errors: $errors" -ForegroundColor Yellow
