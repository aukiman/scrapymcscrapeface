#!/usr/bin/env bash
set -Eeuo pipefail
umask 022

# ---------- Config ----------
APP_DIR="${APP_DIR:-$HOME/webscraper}"
REPO_TARBALL_URL="${REPO_TARBALL_URL:-https://raw.githubusercontent.com/aukiman/scrapymcscrapeface/main/release/scrapymcscrapeface.v1.tar.gz}"
# EXPECTED_SHA256=""   # optional: pin checksum

log() { echo "[+] $*"; }
die() { echo "ERROR: $*" >&2; exit 1; }
trap 'echo "Install failed at line $LINENO: $BASH_COMMAND" >&2' ERR

# ---------- System deps (Ubuntu 20.04+) ----------
log "Installing dependencies..."
sudo apt update -y >/dev/null
sudo apt install -y \
  python3 python3-venv python3-pip curl git \
  libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 \
  libxcomposite1 libxrandr2 libgbm1 libasound2 >/dev/null

# ---------- Fetch tarball ----------
log "Downloading code tarball..."
curl -fsSL -L "$REPO_TARBALL_URL" -o /tmp/webscraper.tar.gz

# if [[ -n "${EXPECTED_SHA256:-}" ]]; then
#   echo "${EXPECTED_SHA256}  /tmp/webscraper.tar.gz" | sha256sum -c -
# fi

# ---------- Stop services if running ----------
sudo systemctl stop "webscraper-webui@$(id -un)" "webscraper-scrapyd@$(id -un)" 2>/dev/null || true

# ---------- Extract fresh into APP_DIR (no staging) ----------
log "Extracting..."
sudo rm -rf "$APP_DIR"
sudo install -d -m 0755 -o "$(id -u)" -g "$(id -g)" "$APP_DIR"

# Extract as root (avoids tar metadata weirdness), then give it back to your user
sudo tar --no-same-owner --no-same-permissions --warning=no-unknown-keyword \
     -xzf /tmp/webscraper.tar.gz -C "$APP_DIR" --strip-components=1
sudo chown -R "$(id -un):$(id -gn)" "$APP_DIR"

# Quick write test
touch "$APP_DIR/.writetest" && rm "$APP_DIR/.writetest" || die "Cannot write to $APP_DIR"

# ---------- Python venv + deps ----------
log "Creating Python venv..."
python3 -m venv "$APP_DIR/.venv"
source "$APP_DIR/.venv/bin/activate"
pip install --upgrade pip wheel >/dev/null

log "Installing Python packages..."
if [[ -f "$APP_DIR/requirements.txt" ]]; then
  pip install -r "$APP_DIR/requirements.txt"
else
  pip install scrapy scrapyd scrapyd-client scrapy-playwright playwright \
              fastapi uvicorn[standard] httpx jinja2 python-multipart
fi

log "Installing Playwright browser + OS deps..."
python -m playwright install chromium
python -m playwright install-deps || true

# ---------- Systemd units ----------
log "Installing systemd units..."
UNITD="/etc/systemd/system"
sudo cp "$APP_DIR/systemd/webscraper-scrapyd@.service" "$UNITD/"
sudo cp "$APP_DIR/systemd/webscraper-webui@.service" "$UNITD/"
sudo systemctl daemon-reload

# ---------- Start Scrapyd, wait until ready ----------
ME="$(id -un)"
log "Starting Scrapyd..."
sudo systemctl enable "webscraper-scrapyd@$ME" --now

log "Waiting for Scrapyd to answer..."
for i in {1..60}; do
  if curl -fsS http://127.0.0.1:6800/listprojects.json >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
  [[ $i -eq 60 ]] && { sudo journalctl -u "webscraper-scrapyd@$ME" --no-pager -n 100 >&2 || true; die "Scrapyd did not start/respond on :6800"; }
done

# ---------- Deploy Scrapy project ----------
log "Deploying spiders to Scrapyd..."
( cd "$APP_DIR/scraper" && scrapyd-deploy )

# ---------- Output dir ----------
mkdir -p "$APP_DIR/outputs"

# ---------- Start Web UI ----------
log "Starting Web UI..."
sudo systemctl enable "webscraper-webui@$ME" --now

IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
log "All set. Open: http://${IP:-127.0.0.1}:8080 on your LAN"
