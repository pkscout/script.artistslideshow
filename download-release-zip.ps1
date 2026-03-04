# Downloads the latest release ZIP from GitHub after a push
# Usage: .\download-release-zip.ps1 [-DestFolder "C:\your\path"]

param(
    [string]$DestFolder = "E:\Eigene Dateien\kodiners repo multi\21"
)

$GITHUB_REPO = "blauesgruen/script.artistslideshow.stream.monitor"
$API_URL     = "https://api.github.com/repos/$GITHUB_REPO/releases/latest"
$MAX_WAIT    = 120   # seconds to wait for Action to finish
$POLL_SLEEP  = 10    # seconds between polls

Write-Host "Waiting for GitHub Action to create release..."

$elapsed = 0
$release = $null

while ($elapsed -lt $MAX_WAIT) {
    try {
        $release = Invoke-RestMethod -Uri $API_URL -Headers @{ "User-Agent" = "ps-script" } -ErrorAction Stop
        $asset   = $release.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1
        if ($asset) {
            break
        }
    } catch {
        # Release not yet available
    }
    Write-Host "  ...noch nicht bereit, warte $POLL_SLEEP s ($elapsed/$MAX_WAIT s)"
    Start-Sleep -Seconds $POLL_SLEEP
    $elapsed += $POLL_SLEEP
}

if (-not $asset) {
    Write-Error "Kein ZIP-Asset nach $MAX_WAIT s gefunden. GitHub Action noch nicht fertig?"
    exit 1
}

$destFile = Join-Path $DestFolder $asset.name
Write-Host "Lade herunter: $($asset.browser_download_url)"
Write-Host "Ziel: $destFile"

Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $destFile

Write-Host "Fertig: $destFile"
