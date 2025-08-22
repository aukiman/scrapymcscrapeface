import scrapy
from urllib.parse import urljoin, urlparse
from scrapy_playwright.page import PageMethod

class GenericSpider(scrapy.Spider):
    name = "generic"
    custom_settings = {}

    def __init__(self, start_url=None, allow_js="false", max_pages=100, same_domain="true", **kw):
        super().__init__(**kw)
        self.start_url = start_url or "https://example.org"
        self.allow_js = allow_js.lower() == "true"
        self.max_pages = int(max_pages)
        self.same_domain = same_domain.lower() != "false"
        self.seen = 0
        self.job_id = kw.get("job_id")
        self._start_host = urlparse(self.start_url).netloc

    def start_requests(self):
        meta = {}
        if self.allow_js:
            meta["playwright"] = True
            meta["playwright_page_methods"] = [PageMethod("wait_for_load_state", "networkidle")]
        yield scrapy.Request(self.start_url, meta=meta, callback=self.parse)

    def _same_host(self, url):
        if not self.same_domain:
            return True
        return urlparse(url).netloc == self._start_host

    def parse(self, response):
        if self.seen >= self.max_pages:
            return
        self.seen += 1
        title = response.css("title::text").get()
        yield {"url": response.url, "title": title}

        for href in response.css("a::attr(href)").getall():
            nxt = urljoin(response.url, href)
            if self._same_host(nxt) and self.seen < self.max_pages:
                meta = {}
                if self.allow_js:
                    meta["playwright"] = True
                    meta["playwright_page_methods"] = [PageMethod("wait_for_load_state", "networkidle")]
                yield scrapy.Request(nxt, meta=meta, callback=self.parse)
