import scrapy
from urllib.parse import urljoin, urlparse
from scrapy_playwright.page import PageMethod

class GenericSpider(scrapy.Spider):
    name = "generic"

    def __init__(self, start_url=None, allow_js="false", max_pages=100, same_domain="true", **kw):
        super().__init__(**kw)
        self.start_url = start_url or "https://example.org"
        self.allow_js = allow_js.lower() == "true"
        self.custom_settings = {
            "CLOSESPIDER_PAGECOUNT": int(max_pages),
        }
        self.same_domain = same_domain.lower() != "false"
        self.job_id = kw.get("job_id")
        self._start_host = urlparse(self.start_url).netloc

    def _get_request_meta(self):
        if self.allow_js:
            return {
                "playwright": True,
                "playwright_page_methods": [PageMethod("wait_for_load_state", "networkidle")],
            }
        return {}

    def start_requests(self):
        yield scrapy.Request(self.start_url, meta=self._get_request_meta(), callback=self.parse)

    def _same_host(self, url):
        if not self.same_domain:
            return True
        return urlparse(url).netloc == self._start_host

    def parse(self, response):
        title = response.css("title::text").get()
        yield {"url": response.url, "title": title}

        for href in response.css("a::attr(href)").getall():
            nxt = urljoin(response.url, href)
            if self._same_host(nxt):
                yield scrapy.Request(nxt, meta=self._get_request_meta(), callback=self.parse)
