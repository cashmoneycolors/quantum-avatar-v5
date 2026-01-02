param(
  [string[]]$Roots = @(
    "C:\workspace",
    "C:\workspaces",
    "C:\cashmoneycolors",
    "C:\cashmoneycolors_projects",
    "C:\Users\cashm\Documents",
    "D:\"
  ),
  [int]$MaxResults = 300,
  [int]$MaxDepth = 12,
  [string]$ReportPath = "C:\\Users\\cashm\\quantum-avatar-v5\\inventory_$(Get-Date -Format yyyyMMdd_HHmmss).md"
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
  ".pytest_cache", ".mypy_cache", ".ruff_cache",
  ".idea", ".vscode", ".vs",
  "CopilotIndices", "FileContentIndex",
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

function Get-GitLastCommitIso([string]$repoPath) {
  try {
    $t = (git -C $repoPath log -1 --format=%cI 2>$null)
    if ($t) { return [string]$t }
  } catch {}
  return ""
}

$rootsExisting = $Roots | Where-Object { Test-Path -LiteralPath $_ }

$gitRepos = @{}     # repoPath -> @{ path=...; lastCommit=... }
$nonGitProjects = @{} # projectPath -> @{ path=...; last=...; markers=@{...} }

foreach ($root in $rootsExisting) {
  Write-Host "Scanning root: $root"

  $stack = New-Object System.Collections.Generic.Stack[object]
  $stack.Push(@($root, 0))

  while ($stack.Count -gt 0) {
    $item = $stack.Pop()
    $current = [string]$item[0]
    $depth = [int]$item[1]

    if ($depth -gt $MaxDepth) { continue }

    # If this is a git repo, record and do not descend.
    if (Test-Path -LiteralPath (Join-Path $current ".git")) {
      if (-not $gitRepos.ContainsKey($current)) {
        $gitRepos[$current] = @{ path=$current; lastCommit=(Get-GitLastCommitIso $current) }
      }
      continue
    }

    # Record non-git project markers (but continue descending, there may be nested projects).
    $markers = Try-Get-MarkersInDir $current
    if ($markers.Count -gt 0) {
      if (-not $nonGitProjects.ContainsKey($current)) {
        $nonGitProjects[$current] = @{ path=$current; last=(Get-Date 0); markers=@{} }
      }
      $hit = $nonGitProjects[$current]

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
      $stack.Push(@($c.FullName, ($depth + 1)))
    }
  }
}

$gitRows = @(
  $gitRepos.GetEnumerator() | ForEach-Object {
    [pscustomobject]@{
      path = $_.Value.path
      lastCommit = $_.Value.lastCommit
    }
  } | Sort-Object lastCommit -Descending
)

$nonGitRows = @(
  $nonGitProjects.GetEnumerator() | ForEach-Object {
    $v = $_.Value
    [pscustomobject]@{
      path = $v.path
      last = $v.last
      markers = ($v.markers.Keys | Sort-Object) -join ','
    }
  } | Sort-Object last -Descending
)

$lines = New-Object System.Collections.Generic.List[string]
$lines.Add("# Inventory (Git + Non-Git)")
$lines.Add("Erstellt: $(Get-Date -Format s)")
$lines.Add("")
$lines.Add("## Roots")
foreach ($r in $rootsExisting) { $lines.Add($r) }

$lines.Add("")
$lines.Add("## Git Repos")
$lines.Add("Total: $($gitRows.Count)")
$takeGit = [Math]::Min($MaxResults, $gitRows.Count)
for ($i=0; $i -lt $takeGit; $i++) {
  $row = $gitRows[$i]
  $lc = if ($row.lastCommit) { $row.lastCommit } else { "(unknown)" }
  $lines.Add("- $($row.path) | lastCommit=$lc")
}

$lines.Add("")
$lines.Add("## Non-Git Projekte")
$lines.Add("Total: $($nonGitRows.Count)")
$takeNg = [Math]::Min($MaxResults, $nonGitRows.Count)
for ($i=0; $i -lt $takeNg; $i++) {
  $row = $nonGitRows[$i]
  $lines.Add("- $($row.path) | last=$($row.last) | markers=$($row.markers)")
}

$dirOut = Split-Path -Parent $ReportPath
if (-not (Test-Path -LiteralPath $dirOut)) { New-Item -ItemType Directory -Path $dirOut | Out-Null }
$lines | Set-Content -LiteralPath $ReportPath -Encoding UTF8

Write-Host "Wrote report: $ReportPath"
Write-Host "Git repos: $($gitRows.Count) | Non-git projects: $($nonGitRows.Count)"
