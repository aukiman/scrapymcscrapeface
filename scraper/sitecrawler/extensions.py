import os, time, threading
from scrapy import signals
from runner.db import ProgressStore

class ProgressExtension:
    def __init__(self, stats, settings):
        self.stats = stats
        self.settings = settings
        self.job_id = settings.get("JOB_ID")
        self.feed_uri = None
        self.store = ProgressStore()
        self._stop = False
        self._thread = None

    @classmethod
    def from_crawler(cls, crawler):
        ext = cls(crawler.stats, crawler.settings)
        crawler.signals.connect(ext.engine_started, signal=signals.engine_started)
        crawler.signals.connect(ext.item_scraped, signal=signals.item_scraped)
        crawler.signals.connect(ext.response_received, signal=signals.response_received)
        crawler.signals.connect(ext.engine_stopped, signal=signals.engine_stopped)
        return ext

    def engine_started(self):
        feeds = self.settings.getdict("FEEDS")
        if feeds:
            self.feed_uri = next(iter(feeds.keys()))
        if self.job_id:
            self.store.mark_running(self.job_id)
        self._thread = threading.Thread(target=self._ticker, daemon=True)
        self._thread.start()

    def item_scraped(self, item, spider):
        if self.job_id:
            self.store.bump_items(self.job_id, 1)

    def response_received(self, response, request, spider):
        if self.job_id:
            self.store.bump_pages(self.job_id, 1)
            br = response.headers.get("Content-Length")
            if br:
                try:
                    self.store.bump_bytes(self.job_id, int(br.decode()))
                except Exception:
                    pass

    def engine_stopped(self):
        self._stop = True
        if self.job_id:
            if self.feed_uri and os.path.exists(self.feed_uri):
                self.store.set_output_size(self.job_id, os.path.getsize(self.feed_uri))
            self.store.mark_finished_if_not_cancelled(self.job_id)

    def _ticker(self):
        while not self._stop:
            if self.job_id:
                flags = self.store.flags(self.job_id)
                if flags.get("cancel_requested"):
                    self.store.mark_cancelled(self.job_id)
                    os._exit(0)
                if flags.get("pause_requested"):
                    self.store.mark_paused(self.job_id)
                    os._exit(0)
                if self.feed_uri and os.path.exists(self.feed_uri):
                    self.store.set_output_size(self.job_id, os.path.getsize(self.feed_uri))
            time.sleep(2)
