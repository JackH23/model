$ErrorActionPreference = 'Stop'
$project = 'D:\codex+blender\my-first-project'
$source = 'C:\Users\User\OneDrive\Documents\ChatGPT\model'
$parentRepo = 'D:\codex+blender'
$parentGit = Join-Path $parentRepo '.git'
if (Test-Path -LiteralPath (Join-Path $project '.git')) { throw 'Child repository already exists; inspect before proceeding.' }
$beforeHead = git -c safe.directory=D:/codex+blender -C $parentRepo rev-parse HEAD
$beforeIndex = (Get-FileHash -LiteralPath (Join-Path $parentGit 'index')).Hash
$beforeConfig = (Get-FileHash -LiteralPath (Join-Path $parentGit 'config')).Hash
$pending = @(git -c safe.directory=D:/codex+blender -C $parentRepo status --porcelain=v1 --untracked-files=all)
$pending | Set-Content -LiteralPath (Join-Path $source 'parent_git_audit_before.txt')
if (@(git -c safe.directory=D:/codex+blender -C $parentRepo ls-files -- my-first-project).Count -ne 0) { throw 'Parent tracks robot files; stop.' }
$refs = @(git ls-remote https://github.com/JackH23/Robo-Jack.git)
if ($LASTEXITCODE -ne 0 -or $refs.Count -ne 0) { throw 'Remote not empty or unavailable; inspect before proceeding.' }
$ignore = @'
# Blender automatic backups and crash files (keep editable .blend sources)
*.blend[0-9]*
*.blend@
*.blend.tmp
*.autosave
*.crash.txt
# Local runtimes, caches and editor state
.tools/
__pycache__/
*.py[cod]
.venv/
venv/
.cache/
.pytest_cache/
.vscode/
.idea/
.DS_Store
Thumbs.db
# Secrets and local configuration
.env
.env.*
!.env.example
*.pem
*.key
credentials*.json
# Reproducible bulk output; retain selected comparison renders under renders/
tmp/
temp/
cache/
build/
dist/
exports/
*.log
*.tmp
*.npz
# These comparison boards embed a reference image with unverified redistribution rights
renders/**/phase1_reference_comparison.png
renders/phase1_reference_comparison.png
'@
Set-Content -LiteralPath (Join-Path $project '.gitignore') -Value $ignore -Encoding utf8
# Bring the latest robot revision from this chat into the requested project, by copy only.
Copy-Item -LiteralPath (Join-Path $source 'robot_hands_turned.blend') -Destination (Join-Path $project 'robot_hands_turned.blend') -ErrorAction Stop
foreach ($name in @('continue_robot.py','fix_connections.py','reference_hands.py')) {
 $dest=Join-Path $project ('scripts\'+$name)
 if (Test-Path -LiteralPath $dest) { throw "Destination already exists: $dest" }
 Copy-Item -LiteralPath (Join-Path $source $name) -Destination $dest
}
$renderDir=Join-Path $project 'renders\refined'
New-Item -ItemType Directory -Path $renderDir -Force | Out-Null
foreach ($name in @('robot_reference_preview.png','neck_fixed_detail.png','reference_hand_closeup.png','hands_turned_detail.png','hands_turned_full.png')) {
 $dest=Join-Path $renderDir $name
 if (Test-Path -LiteralPath $dest) { throw "Destination already exists: $dest" }
 Copy-Item -LiteralPath (Join-Path $source $name) -Destination $dest
}
$readme=@'
# Robo-Jack

Editable Blender robot project with ivory armor, gold details, dark mechanical joints, and cyan lights.

![Latest robot](renders/refined/hands_turned_full.png)

## Files

- `robot_hands_turned.blend`: latest revision, with connected neck, curved segmented hands, and palms facing inward.
- `robot_phase1_blockout_revised.blend`: revised primary robot forms.
- `robot_phase1_blockout.blend`: original blockout.
- `scripts/`: Python modeling and articulation scripts.
- `renders/`: selected robot views and before/after comparisons.
- `phase2/` and validation JSON: articulation baseline and inspection reports; these do not imply a finished animation rig.

## Working with the model

Open the latest `.blend` in Blender. The modeling scripts are development records run through Blender's Python API. Some contain original absolute Windows paths; review their paths and output locations before rerunning them. `reference_hands.py` builds the curled hands; the final wrist orientation is stored in `robot_hands_turned.blend`.

Blender backups, bundled tools, caches, and bulk generated files remain local and are ignored by Git. Curated PNG renders are intentionally versioned. The external concept board and comparison images embedding it are excluded because redistribution rights have not been established. No license for third-party reference imagery is granted by this repository.
'@
if (Test-Path -LiteralPath (Join-Path $project 'README.md')) { throw 'README already exists; inspect first.' }
Set-Content -LiteralPath (Join-Path $project 'README.md') -Value $readme -Encoding utf8
git -C $project init -b main
if ($LASTEXITCODE -ne 0) { throw 'Git init failed' }
git -C $project remote add origin https://github.com/JackH23/Robo-Jack.git
git -C $project add -- .
if ($LASTEXITCODE -ne 0) { throw 'Staging failed' }
$files = @(git -C $project ls-files)
$strongPatterns='gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{30,}|AKIA[0-9A-Z]{16}|sk-[A-Za-z0-9_-]{24,}|-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----'
$findings=@(); $sizeReport=@()
foreach ($rel in $files) {
 $path=Join-Path $project $rel
 $item=Get-Item -LiteralPath $path
 $sizeReport += [pscustomobject]@{Path=$rel;Bytes=$item.Length}
 if ($item.Length -ge 100MB) { throw "Oversized staged file: $rel" }
 $data=[System.Text.Encoding]::ASCII.GetString([System.IO.File]::ReadAllBytes($path))
 if ($data -match $strongPatterns) { $findings += $rel }
 if ($item.Extension -in @('.py','.json','.md','.txt','.toml','.yml','.yaml')) {
  if ($data -match '(?i)(api[_-]?key|secret|password|token)\s*[:=]\s*["''][A-Za-z0-9_+/=-]{16,}["'']') { $findings += $rel }
 }
}
if ($findings.Count) { $findings | ForEach-Object { Write-Output "Potential secret in: $_" }; throw 'Secret scan requires review; no commit made.' }
$sizeReport | Sort-Object Bytes -Descending | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $source 'robo_git_staged_audit.json')
if ((git -C $project rev-parse --show-toplevel) -ne 'D:/codex+blender/my-first-project') { throw 'Incorrect git root' }
if ((Get-FileHash -LiteralPath (Join-Path $parentGit 'index')).Hash -ne $beforeIndex -or (Get-FileHash -LiteralPath (Join-Path $parentGit 'config')).Hash -ne $beforeConfig -or (git -c safe.directory=D:/codex+blender -C $parentRepo rev-parse HEAD) -ne $beforeHead) { throw 'Parent Git state changed; stop.' }
Write-Output "AUDIT OK: $($pending.Count) original pending changes; $($files.Count) staged robot files; no detected secrets or files >=100 MiB; parent index/config/HEAD unchanged."
git -C $project status --short --branch
