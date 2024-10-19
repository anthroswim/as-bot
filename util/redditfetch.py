import json
import os
import re
import asyncpraw
from bs4 import BeautifulSoup
import requests
import subprocess

from util.filecache import FileCache
from util.post import Post, PostType

reddit = asyncpraw.Reddit(
    client_id=os.getenv("RDTCLID"),
    client_secret=os.getenv("RDTCLSECRET"),
    user_agent="anthroswim",
)

# special thanks to rxddit
RX_USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/116.0"

async def new_reddit_posts(subreddit: str, after, before):
    sub = await reddit.subreddit(subreddit)
    async for submission in sub.new(limit=10):
        if submission.created_utc > after and submission.created_utc < before:
            yield submission


class RedditPost(Post):
    _prefix = "u/"

    async def generate(self, submission):
        # url
        self._url = submission.shortlink

        # author
        author = await reddit.redditor(submission.author.name)
        await author.load()
        self._author = author.name
        self._author_icon = author.icon_img.split("?")[0]
        self._platform = (
            "Reddit"
            if submission.subreddit_type == "user"
            else submission.subreddit_name_prefixed
        )

        # title
        self._title = submission.title

        # type
        self._type = RedditPost.post_type(submission)

        if self._type is PostType.IMAGE:
            self._media_urls.append(submission.url)
            self._thumbnail = submission.thumbnail
        
        elif self._type is PostType.GALLERY:
            image_dict = submission.media_metadata
            for i in image_dict:
                pattern = r"/([^/?]+)(?:\?|$)"
                self._media_urls.append(
                    "https://i.redd.it/"
                    + re.search(pattern, image_dict[i]["s"]["u"]).group(1)
                )
            self._thumbnail = submission.thumbnail

        elif self._type is PostType.VIDEO:
            video = submission.media["reddit_video"]
            video_url = video["fallback_url"]

            # for audio we need to find the url that includes it
            if video["has_audio"]:
                if audiovideo := RedditPost.fetch_video_link("https://reddit.com" + submission.permalink):
                    video_url = audiovideo 

            self._media_urls.append(video_url)
            self._thumbnail = submission.thumbnail




        elif self._type is PostType.POLL:
            # TODO
            self._text = "polls arent supported yet"

        elif self._type is PostType.CROSSPOST:
            # TODO
            self._text = "crossposts arent supported yet"
            # TODO remove
            self._parent = Post(
                reddit.submission(
                    url="https://reddit.com"
                    + submission.crosspost_parent_list[0]["permalink"]
                )
            )
            # self._parent.fetch()

        elif self._type is PostType.TEXT:
            self._text = submission.selftext

        await super().fetch()

    async def fetch(self):
        # fetch
        submission = await reddit.submission(url=self._url)
        await self.generate(submission)

    def post_type(subm) -> PostType:
        if getattr(subm, "post_hint", "") == "image":
            return PostType.IMAGE
        elif getattr(subm, "is_gallery", False):
            return PostType.GALLERY
        elif subm.is_video:
            return PostType.VIDEO
        elif hasattr(subm, "poll_data"):
            return PostType.POLL
        elif hasattr(subm, "crosspost_parent"):
            return PostType.CROSSPOST
        elif subm.is_self:
            return PostType.TEXT
        else:
            return PostType.UNKNOWN
        
    def fetch_video_link(url: str) -> str:
        try:
            # get
            response = requests.get(url, headers={"User-Agent": RX_USER_AGENT})
            if response.status_code != 200:
                return None

            # parese
            soup = BeautifulSoup(response.text, "html.parser")
            packaged_media_plain = soup.find(attrs={"packaged-media-json": True}).get("packaged-media-json")
            packaged_media = json.loads(packaged_media_plain)
            videos = packaged_media.get("playbackMp4s", {}).get("permutations", [])

            # pick the highest resolution
            if videos:
                return videos[-1]["source"]["url"]

        except Exception as _:
            return None
        
    def fetch_m3u8(url, postid) -> str:
        file = f"{postid}.mp4"

        # check if the file exists
        path = FileCache.getfile(file)
        if path:
            return path
        # otherwise pick the download location
        else:
            path = FileCache.pathjoin(file)
        
        # and fetch with ffmpeg
        command = [
            "ffmpeg",
            "-i", url,
            "-c", "copy",
            "-f", "mp4",
            "-hide_banner", "-loglevel", "error",
            path
        ]

        process = subprocess.run(command)

        if process.returncode != 0:
            raise Exception(f"FFmpeg error, have fun debugging")
        
        return path
