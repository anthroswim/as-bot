import feedparser
import calendar

from posts.post import Post
from util.loghelper import log

class Feed(): 
    HEADERS = {"User-Agent": "AnthroSwim"}
    
    def __init__(self, url: str):
        self.url = url
        self.entries = []
        self.feed = None

    def fetch_feed(self):
        self.feed = feedparser.parse(self.url)

    def fetch_new_entries(self, after: float, before: float):
        if not self.feed:
            self.fetch_feed()

        self.entries = filter(lambda entry: after <= calendar.timegm(entry.published_parsed) < before, self.feed.entries)
        self.entries = sorted(self.entries, key=lambda entry: calendar.timegm(entry.published_parsed))

        for entry in self.entries:
            log.info(f"New post at {entry.published} - {entry.title}")

    def get_posts(self) -> list[Post]:
        return None
