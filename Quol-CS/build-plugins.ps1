# build-plugins.ps1
# Builds all plugins and copies output to the main Quol bin/Plugins/<PluginId>/ folder.
# Usage: .\build-plugins.ps1 [-Configuration Debug|Release] [-PluginName <FolderName>]

param(
    [string]$Configuration = "Debug",
    [string]$PluginName = ""
)

$ErrorActionPreference = "Stop"
$ScriptDir  = $PSScriptRoot
$PluginsDir = Join-Path $ScriptDir "Plugins"
$ArtifactsDir = Join-Path $ScriptDir "artifacts"
$QuolBin    = Join-Path $ScriptDir "Quol\bin\$Configuration\net10.0"
$TargetBase = Join-Path $QuolBin "Plugins"

Write-Host ""
Write-Host "=== Quol Plugin Builder ===" -ForegroundColor Cyan
Write-Host "Configuration : $Configuration"
Write-Host "Plugin filter  : $(if ([string]::IsNullOrWhiteSpace($PluginName)) { "<all>" } else { $PluginName })"
Write-Host "Artifacts dir  : $ArtifactsDir"
Write-Host "Target bin    : $QuolBin"
Write-Host ""

# ── 1. Build Quol host first so Quol.dll is up to date ──────────────────────
Write-Host ">> Building Quol host..." -ForegroundColor Yellow
dotnet build (Join-Path $ScriptDir "Quol\Quol.csproj") -c $Configuration --nologo -v quiet
if ($LASTEXITCODE -ne 0) { Write-Error "Quol host build failed."; exit 1 }
Write-Host "   Host built OK" -ForegroundColor Green

# ── 2. Discover all plugin projects in Plugins\ ──────────────────────────────
$pluginProjects = Get-ChildItem -Path $PluginsDir -Recurse -Filter "*.csproj"

if (-not [string]::IsNullOrWhiteSpace($PluginName)) {
    $pluginProjects = $pluginProjects | Where-Object {
        $_.BaseName -ieq $PluginName -or (Split-Path $_.DirectoryName -Leaf) -ieq $PluginName
    }
}

if ($pluginProjects.Count -eq 0) {
    if ([string]::IsNullOrWhiteSpace($PluginName)) {
        Write-Host "No plugin projects found in $PluginsDir" -ForegroundColor DarkYellow
        exit 0
    }

    Write-Error "Plugin '$PluginName' was not found under $PluginsDir"
    exit 1
}

foreach ($proj in $pluginProjects) {
    $pluginName = $proj.BaseName          # e.g. PluginOne
    $projDir    = $proj.DirectoryName

    Write-Host ""
    Write-Host ">> Building $pluginName..." -ForegroundColor Yellow
    dotnet build $proj.FullName -c $Configuration --nologo -v quiet
    if ($LASTEXITCODE -ne 0) { Write-Error "$pluginName build failed."; exit 1 }

    # ── 3. Copy plugin output to Quol bin\Plugins\<name>\ ────────────────────
    $pluginBin    = Join-Path $ArtifactsDir "bin\$pluginName\$Configuration\net10.0"
    $pluginTarget = Join-Path $TargetBase $pluginName

    New-Item -ItemType Directory -Path $pluginTarget -Force | Out-Null

    # Copy DLL
    $dll = Join-Path $pluginBin "$pluginName.dll"
    if (Test-Path $dll) {
        Copy-Item $dll $pluginTarget -Force
        Write-Host "   Copied $pluginName.dll" -ForegroundColor DarkGray
    }

    # Copy config.json if present
    $cfg = Join-Path $pluginBin "config.json"
    if (Test-Path $cfg) {
        Copy-Item $cfg $pluginTarget -Force
        Write-Host "   Copied config.json" -ForegroundColor DarkGray
    }

    # Copy any extra assets (e.g. images, fonts) — exclude framework DLLs
    Get-ChildItem -Path $pluginBin -File |
        Where-Object { $_.Extension -notin @(".dll", ".pdb", ".json") } |
        ForEach-Object {
            Copy-Item $_.FullName $pluginTarget -Force
            Write-Host "   Copied $($_.Name)" -ForegroundColor DarkGray
        }

    Write-Host "   $pluginName -> Plugins\$pluginName\" -ForegroundColor Green
}

Write-Host ""
Write-Host "=== All plugins built and deployed ===" -ForegroundColor Cyan
Write-Host ""
