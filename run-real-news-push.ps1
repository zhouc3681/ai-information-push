param(
  [switch]$Push
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$Config = Join-Path $Root "ai_news_config.yaml"
$Bridge = Join-Path $Root "ai-agent-news-push\scripts\dashboard_bridge.py"

if (-not (Test-Path $Python)) {
  python -m venv (Join-Path $Root ".venv")
  & $Python -m pip install --no-cache-dir -r (Join-Path $Root "ai-agent-news-push\scripts\requirements.txt")
}

if ($Push) {
  & $Python $Bridge --config $Config --push
} else {
  & $Python $Bridge --config $Config --dry-run
}
