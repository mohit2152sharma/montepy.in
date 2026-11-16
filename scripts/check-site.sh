#!/usr/bin/env bash
# Build a production copy of the site (no drafts) and run the SEO tests on it.
# Usage: scripts/check-site.sh   (needs hugo extended and python3)
set -euo pipefail
cd "$(dirname "$0")/.."
out="$(mktemp -d)"
trap 'rm -rf "$out"' EXIT
HUGO_BUILDDRAFTS=false hugo build --gc --quiet --baseURL https://montepy.in/ -d "$out"
SITE_DIR="$out" python3 -m unittest discover -s tests -v
