# Web Scraper with FastAPI UI

This project provides a lightweight, yet powerful web scraping solution with a user-friendly web interface. It's built with Scrapy for scraping, Playwright for JavaScript rendering, and a FastAPI web UI for managing scraping jobs.

## Features

-   **Easy-to-use Web UI:** Start, queue, and monitor your scraping jobs from a simple web interface.
-   **JavaScript Rendering:** Optional Playwright integration allows for scraping dynamic websites that rely on JavaScript.
-   **Job Management:** View job progress, output size, and download scraped data directly from the UI.
-   **Simple Deployment:** A one-liner installation script to set up the application on a fresh Ubuntu server.
-   **Packaged for Distribution:** Includes scripts to package the application into a distributable tarball.

## One-Liner Installation (Ubuntu 20.04+)

To install and run the web scraper application on your server, simply run the following command. This will download the application, install all dependencies, and set up the necessary services to run in the background.

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/aukiman/scrapymcscrapeface/main/install.sh)"
```

After the installation is complete, you can access the web UI at `http://<your-server-ip>:8080`.

## Local Development Quick Start

If you want to run the application locally for development or testing, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/aukiman/scrapymcscrapeface.git
    cd scrapymcscrapeface
    ```

2.  **Set up a Python virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install --upgrade pip wheel
    pip install -r requirements.txt
    ```

4.  **Install Playwright browser dependencies:**
    ```bash
    python -m playwright install chromium
    python -m playwright install-deps || true
    ```

5.  **Run the services:**
    You'll need to run the `scrapyd` server and the FastAPI web UI in separate terminals.

    *   **Terminal 1: Run scrapyd**
        ```bash
        scrapyd &
        ```
    *   **Terminal 2: Deploy the Scrapy project**
        ```bash
        cd scraper && scrapyd-deploy && cd -
        ```
    *   **Terminal 3: Run the Web UI**
        ```bash
        uvicorn webui.main:app --host 0.0.0.0 --port 8080
        ```

6.  **Access the UI:**
    Open `http://localhost:8080` in your web browser.

## How to Use

1.  **Open the Web UI:** Navigate to `http://<your-server-ip>:8080`.
2.  **Start a New Scrape:**
    *   In the "Run New Spider" form, enter the **Start URL** of the website you want to scrape.
    *   Choose whether to **Allow Javascript (slower)**. Enable this for dynamic websites.
    *   Set the **Max Pages** to limit the crawl depth.
    *   Click **Run**.
3.  **Monitor Jobs:**
    *   Your new job will appear in the "Job Queue" table.
    *   You can see the status, progress (pages, items, bytes), and start/end times.
4.  **Download Data:**
    *   Once a job is finished, you can click the `download` link to get the scraped data as a JSONL file.
