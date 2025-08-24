# scrapymcscrapeface 🕷️  
**Scrapy + Playwright + FastAPI GUI (Ubuntu 20.04+)**

A lightweight web scraping stack that runs on Ubuntu 20.04+ and serves a simple LAN GUI to queue/start/pause/cancel scrapes, watch live progress, and download results.

---

## Features

- **Scrapy** spiders with optional **Playwright** for JavaScript-heavy pages  
- **FastAPI + Uvicorn** GUI (LAN): queue URLs, start/pause/cancel, download results  
- Live progress tracking (**items / pages / bytes**) and **final output size**  
- **Scrapyd** as the job runner  
- **SQLite** for job/progress state  
- **One-line installer** + **tarball packaging** for easy deployment

---

## Architecture (high level)

```
FastAPI GUI (Uvicorn)  <-->  Scrapyd (runs spiders)
        |                          |
        +---- SQLite (job/progress)+
        |
      outputs/*.jsonl (per job)
```

---

## Requirements

- Ubuntu **20.04 LTS or newer**
- Python 3.8+
- Headless Chromium libs (installer handles this)
- Browser on your LAN to access the GUI

---

## Quick start (local dev)

```bash
# From the repo root (on Ubuntu)
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel
# Use requirements.txt if present; otherwise install packages directly
if [ -f requirements.txt ]; then
  pip install -r requirements.txt
else
  pip install scrapy scrapyd scrapyd-client scrapy-playwright playwright fastapi uvicorn[standard] httpx jinja2 python-multipart
fi

python -m playwright install chromium
python -m playwright install-deps || true

# Run Scrapyd (job runner)
scrapyd &

# Deploy Scrapy project once
cd scraper && scrapyd-deploy && cd -

# Start the GUI
uvicorn webui.main:app --host 0.0.0.0 --port 8080
```

Open **http://<server-ip>:8080** on your LAN.

---

## One-line install (production)

The installer downloads a tarball of this project, installs all dependencies (including Playwright), deploys the Scrapy project to Scrapyd, and enables systemd services for both Scrapyd and the Web UI.
On your Ubuntu server (20.04+):

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/aukiman/scrapymcscrapeface/main/install.sh)"
```

When it finishes, browse to **http://<server-ip>:8080** on your LAN.

> The installer starts **Scrapyd** first, waits until it’s reachable, deploys the spiders, then starts the **Web UI**.

---

## Using the GUI

- **Run a job**: enter a URL, optionally tick **Use Playwright (JS)**, set **Max pages**, click **Start**.  
- **Pause / Cancel**: available while running (graceful pause; best-effort cancel).  
- **Download**: finished/paused/cancelled jobs expose a download link for the JSONL output.  
- **Progress**: **items**, **pages**, **bytes**, and **output size** update live.

---

## Managing services (systemd)

```bash
# Status
sudo systemctl status webscraper-scrapyd@$(id -un)
sudo systemctl status webscraper-webui@$(id -un)

# Logs (live)
journalctl -u webscraper-scrapyd@$(id -un) -f
journalctl -u webscraper-webui@$(id -un) -f

# Restart after code updates
sudo systemctl restart webscraper-scrapyd@$(id -un)
sudo systemctl restart webscraper-webui@$(id -un)
```

To redeploy updated spiders:
```bash
cd scraper && scrapyd-deploy
```

---

## Packaging a tarball

### Windows (PowerShell)

```powershell
# From repo root in PowerShell
$stamp  = Get-Date -Format yyyyMMdd
$stage  = Join-Path $env:TEMP "sface_stage_$stamp"
$outDir = "release"
$outTar = "release\webscraper.v1.tar.gz"   # or name with $stamp

# 1) Stage a clean copy (exclude dev files)
Remove-Item $stage -Recurse -Force -ErrorAction Ignore
New-Item -ItemType Directory -Force -Path $stage | Out-Null
robocopy . $stage /MIR /XD .git .venv release .vscode node_modules /XF *.sqlite *.log | Out-Null

# 2) Create the tar.gz
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
tar -czf $outTar -C $stage .

# 3) Optional: verify
tar -tzf $outTar | Select-Object -First 10
(Get-FileHash $outTar -Algorithm SHA256).Hash

# 4) Clean up stage
Remove-Item $stage -Recurse -Force
```

### Linux/macOS

```bash
bash packaging/build_tarball.sh
# → release/webscraper-YYYYMMDD.tar.gz
```

---

## Recommended: GitHub Releases

For cleaner history and CDN-backed downloads:

1) Create a tag (e.g., `v1.0.0`) and push it.  
2) On GitHub: **Releases → Draft a new release**, pick your tag.  
3) **Attach** the tarball (e.g., `webscraper.v1.tar.gz`) and **Publish**.  
4) Use the asset URL in `install.sh`, e.g.:  
   ```
   https://github.com/aukiman/scrapymcscrapeface/releases/download/v1.0.0/webscraper.v1.tar.gz
   ```

---

## Troubleshooting

- **Scrapyd not reachable at :6800**
  - `sudo systemctl status webscraper-scrapyd@$(id -un)`
  - Logs: `journalctl -u webscraper-scrapyd@$(id -un) -f`

- **Playwright/Chromium errors**
  - `python -m playwright install chromium`
  - `python -m playwright install-deps` (may require `sudo`)

- **ModuleNotFoundError / missing packages**
  - Re-activate venv, `pip install -r requirements.txt`

- **GUI not updating**
  - Ensure `$HOME/webscraper/webui.sqlite` exists and is writable
  - Restart: `sudo systemctl restart webscraper-webui@$(id -un)`

- **Security note**
  - If exposing beyond LAN, put Nginx/Caddy in front with TLS and basic auth, or firewall port 8080 to the local subnet.

---

## Roadmap / Ideas

- URL queue screen (bulk add + “Run all queued”)  
- Per-spider forms (selectors, pagination, auth)  
- CSV/Parquet export  
- GitHub Actions to auto-build tarball on tag push

---

## License

MIT (replace with your preferred licence if needed).
