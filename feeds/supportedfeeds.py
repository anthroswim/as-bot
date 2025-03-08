import re

from feeds.feed import Feed
from feeds.bskyfeed import BskyFeed
from feeds.redditfeed import RedditFeed

FEEDPATTERNS = {
    "bsky": (r"https://bsky\.app/profile/[^/]+/rss", BskyFeed),
    "reddit": (r"https://www\.reddit\.com/[ru]/[^/]+/\.rss", RedditFeed),
}

def anyfeed(url: str) -> Feed:
    if not url.startswith("https://"):
        return None
    
    url = url.split("?")[0]

    for domain, (pattern, feed_class) in FEEDPATTERNS.items():
        if re.search(pattern, url):
            return feed_class(url)
    
    return Feed(url)

