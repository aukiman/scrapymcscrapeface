#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.."; pwd)"
OUT="$ROOT/release"
mkdir -p "$OUT"
STAMP="$(date +%Y%m%d)"
TAR="$OUT/webscraper-$STAMP.tar.gz"

echo "[+] Building tarball $TAR"
tar --exclude='.venv' --exclude='release' -czf "$TAR" -C "$ROOT" .
echo "[+] Done"
