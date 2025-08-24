#!/usr/bin/env bash
set -euo pipefail

REPO_TARBALL_URL="${REPO_TARBALL_URL:-https://raw.githubusercontent.com/aukiman/scrapymcscrapeface/main/release/scrapymcscrapeface.v1.tar.gz}"
APP_DIR="${APP_DIR:-$HOME/webscraper}"

echo "[+] Downloading code tarball..."
curl -fsSL -L "$REPO_TARBALL_URL" -o /tmp/webscraper.tar.gz

# Stop services if running (ignore errors)
sudo systemctl stop "webscraper-webui@$(id -un)" "webscraper-scrapyd@$(id -un)" 2>/dev/null || true

# Start fresh app dir owned by this user
sudo rm -rf "$APP_DIR"
sudo install -d -m 0755 -o "$(id -u)" -g "$(id -g)" "$APP_DIR"

echo "[+] Extracting (staged)..."
# Stage dir owned by root (avoids odd perms during extract)
stage="$(sudo mktemp -d -p /tmp webscraper.stage.XXXXXX)"

# Extract as root, ignore weird flags/owners from the tar
sudo tar --no-same-owner --no-same-permissions --warning=no-unknown-keyword \
  -xzf /tmp/webscraper.tar.gz -C "$stage"

# Copy into APP_DIR with your user as final owner
sudo rsync -a --delete --chown="$(id -un):$(id -gn)" "$stage"/ "$APP_DIR"/
sudo rm -rf "$stage"

# Robust copy into APP_DIR with your user as final owner
sudo rsync -a --delete --chown="$(id -un):$(id -gn)" "$stage"/ "$APP_DIR"/
rm -rf "$stage"

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
