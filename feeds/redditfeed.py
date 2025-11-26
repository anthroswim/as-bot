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

        # save the last few links to a file
        def write_prev_file(fname, links):
            with open(fname, "w", encoding="utf-8") as f:
                f.write("\n".join(links[:128]))

        # get the path for the feed
        file_name = re.sub(r"[^a-zA-Z0-9]", "_", self.url)
        prev_path = os.path.join(os.getcwd(), file_name + ".rss")
        entry_links = map(lambda entry: entry.link, self.feed.entries)

        # create previous file if its missing
        if not os.path.exists(prev_path):
            write_prev_file(prev_path, entry_links)
            log.info(f"Created previous feed file at {prev_path}")
            return
        
        # read previous entries
        prev_entries = []
        with open(prev_path, "r", encoding="utf-8") as f:
            prev_entries = list(map(lambda line: line.strip(), f.readlines()))

        # combine current and previous entries
        entry_links = list(entry_links) + prev_entries
        entry_links = list(dict.fromkeys(entry_links))
        write_prev_file(prev_path, entry_links)

        # filter new entries
        self.entries = filter(lambda entry: entry.link not in prev_entries, self.feed.entries)
        self.entries = sorted(self.entries, key=lambda entry: calendar.timegm(entry.published_parsed))

        for entry in self.entries:
            log.info(f"New post at {entry.published} - {entry.title}")

    def get_posts(self) -> list[RedditPost]:
        return list(map(lambda entry: RedditPost(entry.link), self.entries))