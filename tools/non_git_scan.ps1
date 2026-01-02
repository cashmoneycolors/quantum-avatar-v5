param(
  [string[]]$Roots = @(
    "C:\workspace",
    "C:\workspaces",
    "C:\cashmoneycolors",
    "C:\cashmoneycolors_projects",
    "C:\Users\cashm\Documents",
    "D:\"
  ),
  [int]$MaxResults = 400,
  [string]$ReportPath = "c:\\Users\\cashm\\quantum-avatar-v5\\non-git-scan_roots_20260102_clean.md"
)

$ErrorActionPreference = 'Stop'

$markerNames = @(
  "pyproject.toml","requirements.txt","setup.py","Pipfile","poetry.lock",
  "package.json","pnpm-lock.yaml","yarn.lock",
  "Cargo.toml","go.mod","pom.xml","build.gradle","gradlew",
  "Gemfile","composer.json",
  "Makefile"
)

$markerGlobs = @("*.sln","*.csproj","*.fsproj","*.vbproj")

$excludeDirNames = @(
  ".git",
  "node_modules",
  ".venv","venv",
  "__pycache__",
  ".pytest_cache", ".mypy_cache",
  ".ruff_cache",
  ".idea", ".vscode",
  ".vs",
  "CopilotIndices",
  "FileContentIndex",
  "dist","build","target","out","bin","obj",
  ".next", ".nuxt",
  "$RECYCLE.BIN",
  "System Volume Information",
  "AppData","Program Files","Program Files (x86)","Windows","ProgramData",
  ".lmstudio", ".conan",
  "Norton sandbox"
)

function Is-ExcludedDirName([string]$name) {
  foreach ($x in $excludeDirNames) {
    if ($name -ieq $x) { return $true }
  }
  return $false
}

function Try-Get-MarkersInDir([string]$dir) {
  $found = New-Object System.Collections.Generic.List[string]

  foreach ($m in $markerNames) {
    if (Test-Path -LiteralPath (Join-Path $dir $m)) {
      $found.Add($m)
    }
  }

  foreach ($g in $markerGlobs) {
    $hit = Get-ChildItem -LiteralPath $dir -File -Filter $g -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($hit) { $found.Add($hit.Name) }
  }

  return $found
}

$rootsExisting = $Roots | Where-Object { Test-Path -LiteralPath $_ }

# path -> @{ path=...; last=...; markers=@{name=$true} }
$hits = @{}

foreach ($root in $rootsExisting) {
  Write-Host "Scanning root: $root"

  $stack = New-Object System.Collections.Generic.Stack[string]
  $stack.Push($root)

  while ($stack.Count -gt 0) {
    $current = $stack.Pop()

    # prune: if current is a git repo, skip it entirely
    if (Test-Path -LiteralPath (Join-Path $current ".git")) {
      continue
    }

    $markers = Try-Get-MarkersInDir $current
    if ($markers.Count -gt 0) {
      # record hit
      if (-not $hits.ContainsKey($current)) {
        $hits[$current] = @{ path=$current; last=(Get-Date 0); markers=@{} }
      }
      $hit = $hits[$current]

      foreach ($m in $markers) {
        $hit.markers[$m] = $true
        try {
          $lm = (Get-Item -LiteralPath (Join-Path $current $m) -ErrorAction SilentlyContinue).LastWriteTime
          if ($lm -and $lm -gt $hit.last) { $hit.last = $lm }
        } catch {}
      }
    }

    # descend
    try {
      $children = Get-ChildItem -LiteralPath $current -Directory -Force -ErrorAction SilentlyContinue
    } catch {
      $children = @()
    }

    foreach ($c in $children) {
      if (Is-ExcludedDirName $c.Name) { continue }
      $stack.Push($c.FullName)
    }
  }
}

$results = @(
  $hits.GetEnumerator() | ForEach-Object {
  $v = $_.Value
  [pscustomobject]@{
    path = $v.path
    last = $v.last
    markers = ($v.markers.Keys | Sort-Object) -join ','
  }
  } | Sort-Object last -Descending
)

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# Non-Git Kandidaten Scan (clean)")
$lines.Add("Erstellt: $(Get-Date -Format s)")
$lines.Add("")
$lines.Add("## Roots")
foreach ($r in $rootsExisting) { $lines.Add($r) }
$lines.Add("")
$lines.Add("## Treffer (sortiert nach LastWriteTime)")

$take = [Math]::Min($MaxResults, $results.Count)
$i = 0
foreach ($row in $results) {
  if ($i -ge $take) { break }
  $lines.Add("- $($row.path) | last=$($row.last) | markers=$($row.markers)")
  $i++
}
$lines.Add("")
$lines.Add("Total Treffer: $($results.Count)")

$dirOut = Split-Path -Parent $ReportPath
if (-not (Test-Path -LiteralPath $dirOut)) { New-Item -ItemType Directory -Path $dirOut | Out-Null }
$lines | Set-Content -LiteralPath $ReportPath -Encoding UTF8

Write-Host "Wrote report: $ReportPath"
Write-Host "Top 20:";
$results | Select-Object -First 20 path,last,markers | Format-Table -AutoSize | Out-String | Write-Host
