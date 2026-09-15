#!/bin/sh
# tillandsias.org install shim — https://tillandsias.org
#
# This file is STATIC. It is not rebuilt when Tillandsias releases, because it
# resolves the current installer from the release channel every time it runs.
# That keeps the short URL stable while the app releases on its own cadence.
#
#   curl -fSsL https://tillandsias.org/install.sh | bash
#
# Pin a specific release by exporting TILLANDSIAS_RELEASE_BASE first; the
# installer this fetches honours the same variable.
set -eu

base="${TILLANDSIAS_RELEASE_BASE:-https://github.com/8007342/tillandsias/releases/latest/download}"

case "$(uname -s)" in
    Darwin) name=install-macos.sh ;;
    Linux)  name=install.sh ;;
    *)      printf 'tillandsias: unsupported system "%s" — see https://tillandsias.org\n' "$(uname -s)" >&2
            exit 1 ;;
esac

command -v curl >/dev/null 2>&1 || { printf 'tillandsias: curl is required\n' >&2; exit 1; }
command -v bash >/dev/null 2>&1 || { printf 'tillandsias: bash is required\n' >&2; exit 1; }

tmp="$(mktemp "${TMPDIR:-/tmp}/tillandsias-install.XXXXXX")" || exit 1
trap 'rm -f "$tmp"' EXIT INT TERM

if ! curl -fSsL "$base/$name" -o "$tmp"; then
    printf 'tillandsias: could not download %s/%s\n' "$base" "$name" >&2
    exit 1
fi

# A 404, a proxy notice or a captive portal answers with HTML. Piping that into
# a shell turns a failed download into a confusing error instead of a clear one,
# so refuse anything that is not a script before running it.
if ! head -n 1 "$tmp" | grep -q '^#!'; then
    printf 'tillandsias: %s/%s did not return a script — refusing to run it\n' "$base" "$name" >&2
    exit 1
fi

# Run from a file rather than a pipe so the installer keeps a usable stdin.
exec bash "$tmp" "$@"
