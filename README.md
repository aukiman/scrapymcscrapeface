# Web Scraper (Scrapy + Playwright + FastAPI GUI)

A lightweight web scraping stack for **Ubuntu 20.04+**:

- Scrapy + optional Playwright (for JS)
- FastAPI + Uvicorn GUI (queue/start/pause/cancel, progress, output size)
- Scrapyd job runner
- SQLite for progress tracking
- One-line installer and tarball packaging

## Local Dev Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip wheel
pip install scrapy scrapyd scrapyd-client scrapy-playwright fastapi jinja2 uvicorn[standard] httpx python-multipart playwright
python -m playwright install chromium
python -m playwright install-deps || true

scrapyd &
cd scraper && scrapyd-deploy && cd -
uvicorn webui.main:app --host 0.0.0.0 --port 8080
```
Open **http://<server>:8080** on your LAN.

## Packaging a Tarball
```bash
bash packaging/build_tarball.sh
```
Tarball goes to `release/webscraper-YYYYMMDD.tar.gz`.

## One-liner Install
Update `install.sh` with your tarball URL, then run:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/<your-github>/<your-repo>/main/install.sh)"
```
