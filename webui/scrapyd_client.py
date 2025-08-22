import httpx

class ScrapydClient:
    def __init__(self, base="http://127.0.0.1:6800"):
        self.base = base.rstrip("/")

    async def schedule(self, project, spider, **kwargs):
        data = {"project": project, "spider": spider}
        data.update(kwargs)
        async with httpx.AsyncClient(timeout=60) as c:
            r = await c.post(f"{self.base}/schedule.json", data=data)
            r.raise_for_status()
            return r.json()

    async def list_jobs(self, project):
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{self.base}/listjobs.json", params={"project": project})
            r.raise_for_status()
            return r.json()

    async def cancel(self, project, jobid):
        async with httpx.AsyncClient() as c:
            r = await c.post(f"{self.base}/cancel.json", data={"project": project, "job": jobid})
            r.raise_for_status()
            return r.json()
