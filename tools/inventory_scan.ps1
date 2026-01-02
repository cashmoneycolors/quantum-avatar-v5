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
    "pyproject.toml", "requirements.txt", "setup.py", "Pipfile", "poetry.lock",
    "package.json", "pnpm-lock.yaml", "yarn.lock",
    "Cargo.toml", "go.mod", "pom.xml", "build.gradle", "gradlew",
    "Gemfile", "composer.json",
    "Makefile"
)

$markerGlobs = @("*.sln", "*.csproj", "*.fsproj", "*.vbproj")

$excludeDirNames = @(
    ".git",
    "node_modules",
    ".venv", "venv",
    "__pycache__",
    ".pytest_cache", ".mypy_cache", ".ruff_cache",
    ".idea", ".vscode", ".vs",
    "CopilotIndices", "FileContentIndex",
    "copilot-instructions",
    "copilot-instructions_cash",
    "dist", "build", "target", "out", "bin", "obj",
    ".next", ".nuxt",
    "$RECYCLE.BIN",
    "System Volume Information",
    "AppData", "Program Files", "Program Files (x86)", "Windows", "ProgramData",
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

function Is-CopilotInstructionsRepoPath([string]$path) {
    $p = $path.Replace('/', '\')
    if ($p.IndexOf("\\.github\\copilot-instructions\\", [System.StringComparison]::OrdinalIgnoreCase) -ge 0) { return $true }
    if ($p.IndexOf("\\copilot-instructions\\", [System.StringComparison]::OrdinalIgnoreCase) -ge 0) { return $true }
    if ($p.IndexOf("\\copilot-instructions_cash\\", [System.StringComparison]::OrdinalIgnoreCase) -ge 0) { return $true }
    return $false
}

function Get-GitRepoKind([string]$repoPath) {
    $dotGit = Join-Path $repoPath ".git"
    if (Test-Path -LiteralPath $dotGit -PathType Leaf) {
        # worktree: .git is a file that points at the actual gitdir
        return "worktree"
    }
    if (Test-Path -LiteralPath $dotGit -PathType Container) {
        return "repo"
    }
    return "unknown"
}

function Get-GitLastCommitIso([string]$repoPath) {
    try {
        $t = (git -C $repoPath log -1 --format=%cI 2>$null)
        if ($t) { return [string]$t }
    }
    catch {}
    return ""
}

function Get-GitOriginUrl([string]$repoPath) {
    try {
        $u = (git -C $repoPath remote get-url origin 2>$null)
        if ($u) { return ([string]$u).Trim() }
    }
    catch {}

    # Fallback: parse .git/config (works even if git refuses due to ownership).
    try {
        $configPath = Join-Path $repoPath ".git\config"
        if (Test-Path -LiteralPath $configPath -PathType Leaf) {
            $inOrigin = $false
            $lines = Get-Content -LiteralPath $configPath -ErrorAction SilentlyContinue
            foreach ($line in $lines) {
                if ($line -match '^\s*\[remote\s+"origin"\]\s*$') { $inOrigin = $true; continue }
                if ($line -match '^\s*\[') { $inOrigin = $false }
                if ($inOrigin -and ($line -match '^\s*url\s*=\s*(.+)\s*$')) {
                    $v = ([string]$Matches[1]).Trim()
                    if ($v) { return $v }
                }
            }
        }
    }
    catch {}
    return ""
}

function Get-GitHeadSha([string]$repoPath) {
    try {
        $s = (git -C $repoPath rev-parse HEAD 2>$null)
        if ($s) { return ([string]$s).Trim() }
    }
    catch {}

    # Fallback: resolve .git/HEAD -> ref -> sha (also checks packed-refs).
    try {
        $headPath = Join-Path $repoPath ".git\HEAD"
        if (-not (Test-Path -LiteralPath $headPath -PathType Leaf)) { return "" }
        $headText = (Get-Content -LiteralPath $headPath -Raw -ErrorAction SilentlyContinue).Trim()
        if (-not $headText) { return "" }

        if ($headText -match '^ref:\s*(.+)\s*$') {
            $ref = ([string]$Matches[1]).Trim()
            $refPath = Join-Path $repoPath (".git\\" + $ref.Replace('/', '\\'))
            if (Test-Path -LiteralPath $refPath -PathType Leaf) {
                $sha = (Get-Content -LiteralPath $refPath -Raw -ErrorAction SilentlyContinue).Trim()
                if ($sha) { return $sha }
            }

            $packedRefs = Join-Path $repoPath ".git\packed-refs"
            if (Test-Path -LiteralPath $packedRefs -PathType Leaf) {
                $plines = Get-Content -LiteralPath $packedRefs -ErrorAction SilentlyContinue
                foreach ($l in $plines) {
                    if ($l.StartsWith('#') -or $l.StartsWith('^') -or (-not $l.Trim())) { continue }
                    $parts = $l -split '\s+'
                    if ($parts.Length -ge 2 -and $parts[1] -eq $ref) {
                        $sha = ([string]$parts[0]).Trim()
                        if ($sha) { return $sha }
                    }
                }
            }
        }
        else {
            # Detached HEAD contains SHA directly.
            return $headText
        }
    }
    catch {}
    return ""
}

function Normalize-GitRemote([string]$remote) {
    if (-not $remote) { return "" }
    $r = $remote.Trim().ToLowerInvariant()
    if ($r.StartsWith("git@github.com:")) {
        $r = "https://github.com/" + $r.Substring("git@github.com:".Length)
    }
    if ($r.EndsWith(".git")) { $r = $r.Substring(0, $r.Length - 4) }
    return $r
}

function Get-RepoDedupeKey([object]$row) {
    $origin = Normalize-GitRemote $row.origin
    if ($origin) { return "origin:" + $origin }
    if ($row.head) { return "head:" + ([string]$row.head) }

    # Heuristic: if this repo looks "weak" (no origin/head and no commit info),
    # but we have a strong repo with the same folder name elsewhere, group by name.
    $lc = ([string]$row.lastCommit)
    $isWeak = (-not $lc) -or ($lc -eq "(unknown)")
    if ($isWeak) {
        try {
            $leaf = (Split-Path -Leaf ([string]$row.path)).ToLowerInvariant()
            if ($leaf -and $script:StrongRepoKeyByName -and $script:StrongRepoKeyByName.ContainsKey($leaf)) {
                return [string]$script:StrongRepoKeyByName[$leaf]
            }
        }
        catch {}
    }

    return "path:" + ([string]$row.path)
}

function Get-RepoPreferenceScore([object]$row) {
    $p = ([string]$row.path)
    $pl = $p.ToLowerInvariant()

    $score = 0
    if ($pl.StartsWith("c:\\cashmoneycolors_projects\\")) { $score += 100 }
    elseif ($pl.StartsWith("c:\\cashmoneycolors\\")) { $score += 90 }
    elseif ($pl.StartsWith("c:\\workspaces\\")) { $score += 80 }
    elseif ($pl.StartsWith("c:\\workspace\\")) { $score += 70 }
    elseif ($pl.StartsWith("c:\\users\\cashm\\documents\\")) { $score += 60 }
    elseif ($pl.StartsWith("d:\\")) { $score += 10 }

    if ($pl.Contains("\\.worktrees\\")) { $score -= 40 }
    if ($pl.Contains("__old")) { $score -= 50 }
    if ($pl.Contains("\\old\\")) { $score -= 30 }
    if ($pl.Contains("\\backup\\")) { $score -= 30 }
    if ($pl.Contains("\\temp\\")) { $score -= 20 }

    # Slight boost if it looks like your canonical GitHub account.
    $origin = (Normalize-GitRemote $row.origin)
    if ($origin.Contains("github.com/cashmoneycolors/")) { $score += 15 }

    return $score
}

$rootsExisting = $Roots | Where-Object { Test-Path -LiteralPath $_ }

$gitRepos = @{}     # repoPath -> @{ path=...; lastCommit=...; kind=... }
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
            if (-not (Is-CopilotInstructionsRepoPath $current)) {
                if (-not $gitRepos.ContainsKey($current)) {
                    $gitRepos[$current] = @{
                        path       = $current
                        lastCommit = (Get-GitLastCommitIso $current)
                        kind       = (Get-GitRepoKind $current)
                        origin     = (Get-GitOriginUrl $current)
                        head       = (Get-GitHeadSha $current)
                    }
                }
            }
            continue
        }

        # Record non-git project markers (but continue descending, there may be nested projects).
        $markers = Try-Get-MarkersInDir $current
        if ($markers.Count -gt 0) {
            if (-not $nonGitProjects.ContainsKey($current)) {
                $nonGitProjects[$current] = @{ path = $current; last = (Get-Date 0); markers = @{} }
            }
            $hit = $nonGitProjects[$current]

            foreach ($m in $markers) {
                $hit.markers[$m] = $true
                try {
                    $lm = (Get-Item -LiteralPath (Join-Path $current $m) -ErrorAction SilentlyContinue).LastWriteTime
                    if ($lm -and $lm -gt $hit.last) { $hit.last = $lm }
                }
                catch {}
            }
        }

        # descend
        try {
            $children = Get-ChildItem -LiteralPath $current -Directory -Force -ErrorAction SilentlyContinue
        }
        catch {
            $children = @()
        }

        foreach ($c in $children) {
            if (Is-ExcludedDirName $c.Name) { continue }
            $stack.Push(@($c.FullName, ($depth + 1)))
        }
    }
}

$gitRowsAll = @(
    $gitRepos.GetEnumerator() | ForEach-Object {
        [pscustomobject]@{
            path       = $_.Value.path
            lastCommit = $_.Value.lastCommit
            kind       = $_.Value.kind
            origin     = $_.Value.origin
            head       = $_.Value.head
        }
    }
)

$gitRowsMainAll = @($gitRowsAll | Where-Object { $_.kind -ne "worktree" } | Sort-Object lastCommit -Descending)
$gitRowsWorktrees = @($gitRowsAll | Where-Object { $_.kind -eq "worktree" } | Sort-Object lastCommit -Descending)

# Dedupe main repos by origin URL (fallback: HEAD SHA). Keep best/most canonical path.
$script:StrongRepoKeyByName = @{}
foreach ($r in $gitRowsMainAll) {
    try {
        $leaf = (Split-Path -Leaf ([string]$r.path)).ToLowerInvariant()
        if (-not $leaf) { continue }

        $originNorm = Normalize-GitRemote $r.origin
        $key = ""
        if ($originNorm) { $key = "origin:" + $originNorm }
        elseif ($r.head) { $key = "head:" + ([string]$r.head) }
        else { continue }

        if (-not $script:StrongRepoKeyByName.ContainsKey($leaf)) {
            $script:StrongRepoKeyByName[$leaf] = $key
        }
    }
    catch {}
}

$dedupeGroups = @{}
foreach ($row in $gitRowsMainAll) {
    $key = Get-RepoDedupeKey $row
    if (-not $dedupeGroups.ContainsKey($key)) { $dedupeGroups[$key] = @() }
    $dedupeGroups[$key] += , $row
}

$gitRowsMain = @()
$gitRowsMainDuplicates = @()

foreach ($kv in $dedupeGroups.GetEnumerator()) {
    $group = @($kv.Value)
    if ($group.Count -le 1) {
        $gitRowsMain += $group[0]
        continue
    }

    $best = $group | Sort-Object @(
        @{ Expression = { Get-RepoPreferenceScore $_ }; Descending = $true },
        @{ Expression = { $_.lastCommit }; Descending = $true }
    ) | Select-Object -First 1

    $gitRowsMain += $best

    foreach ($g in $group) {
        if ($g.path -ne $best.path) {
            $gitRowsMainDuplicates += [pscustomobject]@{
                key        = $kv.Key
                path       = $g.path
                lastCommit = $g.lastCommit
                origin     = $g.origin
                canonical  = $best.path
            }
        }
    }
}

$gitRowsMain = @($gitRowsMain | Sort-Object lastCommit -Descending)
$gitRowsMainDuplicates = @($gitRowsMainDuplicates | Sort-Object key, lastCommit -Descending)

$nonGitRows = @(
    $nonGitProjects.GetEnumerator() | ForEach-Object {
        $v = $_.Value
        [pscustomobject]@{
            path    = $v.path
            last    = $v.last
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
$lines.Add("## Git Repos (Main)")
$lines.Add("Total: $($gitRowsMain.Count)")
$takeGit = [Math]::Min($MaxResults, $gitRowsMain.Count)
for ($i = 0; $i -lt $takeGit; $i++) {
    $row = $gitRowsMain[$i]
    $lc = if ($row.lastCommit) { $row.lastCommit } else { "(unknown)" }
    $origin = if ($row.origin) { $row.origin } else { "" }
    if ($origin) {
        $lines.Add("- $($row.path) | lastCommit=$lc | origin=$origin")
    }
    else {
        $lines.Add("- $($row.path) | lastCommit=$lc")
    }
}

if ($gitRowsMainDuplicates.Count -gt 0) {
    $lines.Add("")
    $lines.Add("## Git Repos (Main) - Duplikate")
    $lines.Add("Total: $($gitRowsMainDuplicates.Count)")
    $takeDup = [Math]::Min($MaxResults, $gitRowsMainDuplicates.Count)
    for ($i = 0; $i -lt $takeDup; $i++) {
        $row = $gitRowsMainDuplicates[$i]
        $lc = if ($row.lastCommit) { $row.lastCommit } else { "(unknown)" }
        $origin = if ($row.origin) { $row.origin } else { "" }
        if ($origin) {
            $lines.Add("- $($row.path) | lastCommit=$lc | origin=$origin | canonical=$($row.canonical)")
        }
        else {
            $lines.Add("- $($row.path) | lastCommit=$lc | canonical=$($row.canonical)")
        }
    }
}

$lines.Add("")
$lines.Add("## Git Worktrees")
$lines.Add("Total: $($gitRowsWorktrees.Count)")
$takeWt = [Math]::Min($MaxResults, $gitRowsWorktrees.Count)
for ($i = 0; $i -lt $takeWt; $i++) {
    $row = $gitRowsWorktrees[$i]
    $lc = if ($row.lastCommit) { $row.lastCommit } else { "(unknown)" }
    $lines.Add("- $($row.path) | lastCommit=$lc")
}

$lines.Add("")
$lines.Add("## Non-Git Projekte")
$lines.Add("Total: $($nonGitRows.Count)")
$takeNg = [Math]::Min($MaxResults, $nonGitRows.Count)
for ($i = 0; $i -lt $takeNg; $i++) {
    $row = $nonGitRows[$i]
    $lines.Add("- $($row.path) | last=$($row.last) | markers=$($row.markers)")
}

$dirOut = Split-Path -Parent $ReportPath
if (-not (Test-Path -LiteralPath $dirOut)) { New-Item -ItemType Directory -Path $dirOut | Out-Null }
$lines | Set-Content -LiteralPath $ReportPath -Encoding UTF8

Write-Host "Wrote report: $ReportPath"
Write-Host "Git repos (deduped): $($gitRowsMain.Count) | Main duplicates: $($gitRowsMainDuplicates.Count) | Worktrees: $($gitRowsWorktrees.Count) | Non-git projects: $($nonGitRows.Count)"
