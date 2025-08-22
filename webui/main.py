import os, uuid, pathlib
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from jinja2 import Environment, FileSystemLoader, select_autoescape
from scrapyd_client import ScrapydClient
from runner.db import ProgressStore

BASE = pathlib.Path(__file__).resolve().parent
templates = Environment(loader=FileSystemLoader(str(BASE / "templates")),
                        autoescape=select_autoescape(["html","xml"]))

app = FastAPI()
store = ProgressStore()
SCRAPYD_URL = os.environ.get("SCRAPYD_URL", "http://127.0.0.1:6800")
PROJECT = os.environ.get("SCRAPY_PROJECT", "sitecrawler")
OUTPUT_DIR = os.environ.get("WEBSCRAPER_OUTPUT_DIR", str(pathlib.Path.home() / "webscraper" / "outputs"))
client = ScrapydClient(SCRAPYD_URL)

def render(name, **ctx):
    return HTMLResponse(templates.get_template(name).render(**ctx))

@app.get("/", response_class=HTMLResponse)
async def index():
    jobs = store.list_jobs()
    return render("index.html", jobs=jobs)

@app.post("/run")
async def run(spider: str = Form("generic"),
              start_url: str = Form(...),
              allow_js: str = Form("false"),
              max_pages: int = Form(100)):
    job_id = str(uuid.uuid4())
    out_dir = pathlib.Path(OUTPUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{spider}-{job_id}.jsonl"

    store.create_job(job_id, spider, start_url, allow_js == "true", str(out_path))

    feeds = {str(out_path): {"format": "jsonlines"}}
    extra = {
        "JOB_ID": job_id,
        "FEEDS": feeds,
        "start_url": start_url,
        "allow_js": allow_js,
        "max_pages": str(max_pages),
    }
    await client.schedule(PROJECT, spider, **extra)
    return RedirectResponse("/", 303)

@app.post("/cancel/{job_id}")
async def cancel(job_id: str):
    store.request_cancel(job_id)
    return RedirectResponse("/", 303)

@app.post("/pause/{job_id}")
async def pause(job_id: str):
    store.request_pause(job_id)
    return RedirectResponse("/", 303)

@app.get("/download/{job_id}")
async def download(job_id: str):
    row = store.get_job_for_download(job_id)
    if row and os.path.exists(row[0]) and row[1] in ("finished","paused","cancelled"):
        return FileResponse(row[0], filename=os.path.basename(row[0]))
    return RedirectResponse("/", 303)
