[CmdletBinding()]
param(
    [switch]$Offline,
    [string]$PythonExe = ""
)

$repoRoot = Split-Path -Parent $PSScriptRoot
Set-Location -LiteralPath $repoRoot

if (-not $PythonExe) {
    $venvPy = Join-Path $repoRoot ".venv\Scripts\python.exe"
    if (Test-Path -LiteralPath $venvPy -PathType Leaf) {
        $PythonExe = $venvPy
    }
    else {
        $PythonExe = "python"
    }
}

if ($Offline) {
    $env:HF_HUB_OFFLINE = "1"
    $env:TRANSFORMERS_OFFLINE = "1"
}

& $PythonExe -m compileall -q quantum_avatar
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

& $PythonExe -m unittest discover -s quantum_avatar/tests -p "test_*.py" -t .
exit $LASTEXITCODE
