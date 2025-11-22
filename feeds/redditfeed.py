from feeds.feed import Feed
from posts.redditpost import RedditPost
from util.loghelper import log

import feedparser
import requests
import calendar
import re
import os

class RedditFeed(Feed):
    def fetch_feed(self):
        response = requests.get(self.url, headers=Feed.HEADERS)
        self.feed = feedparser.parse(response.text)
        
    def fetch_new_entries(self, after: float, before: float):
        if not self.feed:
            self.fetch_feed()

        def write_prev_file():
            with open(prev_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(map(lambda entry: entry.link, self.feed.entries)))

        file_name = re.sub(r'[^a-zA-Z0-9]', '_', self.url)
        prev_path = os.path.join(os.getcwd(), file_name + '.rss')
        
        if not os.path.exists(prev_path):
            write_prev_file()
            log.info(f"Created previous feed file at {prev_path}")
            return

        prev_entries = []
        with open(prev_path, 'r', encoding='utf-8') as f:
            prev_entries = list(map(lambda line: line.strip(), f.readlines()))
        write_prev_file()

        self.entries = filter(lambda entry: entry.link not in prev_entries, self.feed.entries)
        self.entries = sorted(self.entries, key=lambda entry: calendar.timegm(entry.published_parsed))

        for entry in self.entries:
            log.info(f"New post at {entry.published} - {entry.title}")

    def get_posts(self) -> list[RedditPost]:
        return list(map(lambda entry: RedditPost(entry.link), self.entries))