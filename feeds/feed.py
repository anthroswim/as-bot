import feedparser
import time

from posts.post import Post

class Feed(): 
    HEADERS = {'User-Agent': "AnthroSwim"}
    
    def __init__(self, url: str):
        self.url = url
        self.entries = []
        self.feed = None

    def fetch_feed(self):
        self.feed = feedparser.parse(self.url)

    def fetch_new_entries(self, after: float, before: float):
        if not self.feed:
            self.fetch_feed()
        self.entries = filter(lambda entry: after <= time.mktime(entry.published_parsed) < before, self.feed.entries)

    def get_posts(self) -> list[Post]:
        return None
