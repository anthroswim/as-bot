import re
from posts.post import Post
from posts.twitterpost import Tweet
from posts.redditpost import RedditPost

POST_PATTERNS = {
    "twitter.com": (r"https://[^/]+/[^/]+/status/\d+", Tweet),
    "reddit.com": (r"https://www\.reddit\.com/[ur]/[^/]+/[a-z]+/[^/]+", RedditPost),
    "redd.it": (r"https://redd\.it/\w+", RedditPost),
}

def anypost(url: str) -> Post:
    if not url.startswith("https://"):
        return None
    
    url = url.split("?")[0]
    

    for domain, (pattern, post_class) in POST_PATTERNS.items():
        if re.search(pattern, url):
            return post_class(url)
    
    return None

