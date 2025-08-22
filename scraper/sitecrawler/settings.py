BOT_NAME = "sitecrawler"
SPIDER_MODULES = ["sitecrawler.spiders"]
NEWSPIDER_MODULE = "sitecrawler.spiders"

ROBOTSTXT_OBEY = True

DOWNLOADER_MIDDLEWARES = {
    "scrapy_playwright.middleware.PlaywrightMiddleware": 800,
}

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_DEFAULT_NAVIGATION_TIMEOUT = 30000

CONCURRENT_REQUESTS = 8
DOWNLOAD_DELAY = 0.25
LOG_LEVEL = "INFO"

EXTENSIONS = {
    "sitecrawler.extensions.ProgressExtension": 500,
}

FEED_EXPORT_ENCODING = "utf-8"
