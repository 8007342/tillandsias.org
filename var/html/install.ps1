# tillandsias.org install shim for Windows - https://tillandsias.org
#
# This file is STATIC. It is not rebuilt when Tillandsias releases, because it
# resolves the current installer from the release channel every time it runs.
# That keeps the short URL stable while the app releases on its own cadence.
#
#   irm https://tillandsias.org/install.ps1 | iex
#
# Pin a specific release by setting $env:TILLANDSIAS_RELEASE_BASE first; the
# installer this fetches honours the same variable.

$ErrorActionPreference = 'Stop'

$base = if ($env:TILLANDSIAS_RELEASE_BASE) {
    $env:TILLANDSIAS_RELEASE_BASE
} else {
    'https://github.com/8007342/tillandsias/releases/latest/download'
}
$url = "$base/install-windows.ps1"

try {
    $script = Invoke-RestMethod -Uri $url -UseBasicParsing
} catch {
    throw "tillandsias: could not download $url - $($_.Exception.Message)"
}

# A 404 or a captive portal answers with HTML, and Invoke-Expression on that
# fails in a way that names neither the download nor the cause. Refuse anything
# that does not look like the installer before running it.
if (-not ($script -is [string]) -or $script -notmatch '\S') {
    throw "tillandsias: $url returned no script - refusing to run it"
}
if ($script -match '(?i)^\s*<(!doctype|html)') {
    throw "tillandsias: $url returned a web page, not a script - refusing to run it"
}

Invoke-Expression $script
