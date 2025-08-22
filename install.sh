#!/usr/bin/env bash
set -euo pipefail

REPO_TARBALL_URL="${REPO_TARBALL_URL:-https://raw.githubusercontent.com/<your-github>/<your-repo>/main/release/webscraper-YYYYMMDD.tar.gz}"
APP_DIR="${APP_DIR:-$HOME/webscraper}"

echo "[+] Installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-venv python3-pip curl git libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 libxcomposite1 libxrandr2 libgbm1 libasound2

mkdir -p "$APP_DIR"
cd "$APP_DIR"

echo "[+] Downloading code tarball..."
curl -fsSL "$REPO_TARBALL_URL" -o webscraper.tar.gz
tar -xzf webscraper.tar.gz --strip-components=1

echo "[+] Creating Python venv..."
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel
pip install -r requirements.txt

echo "[+] Installing Playwright browser deps..."
python -m playwright install chromium
python -m playwright install-deps || true

echo "[+] Deploying Scrapy project to scrapyd (first time)..."
( cd scraper && scrapyd-deploy )

echo "[+] Creating outputs dir..."
mkdir -p "$APP_DIR/outputs"

echo "[+] Installing systemd units..."
UNITD="/etc/systemd/system"
sudo cp systemd/webscraper-scrapyd@.service "$UNITD/"
sudo cp systemd/webscraper-webui@.service "$UNITD/"
sudo systemctl daemon-reload

ME="$(id -un)"
sudo systemctl enable "webscraper-scrapyd@$ME" --now
sudo systemctl enable "webscraper-webui@$ME" --now

echo
echo "All set. Open: http://$(hostname -I | awk '{print $1}'):8080"
