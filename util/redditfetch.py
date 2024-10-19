import os
import re
import asyncpraw
import requests
import io
import subprocess

from util.filecache import FileCache
from util.post import Post, PostType

reddit = asyncpraw.Reddit(
    client_id=os.getenv("RDTCLID"),
    client_secret=os.getenv("RDTCLSECRET"),
    user_agent="anthroswim",
)

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

        # check parent
        if hasattr(submission, "crosspost_parent"):
            self._parent = submission.crosspost_parent_list[0]

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
                video_url = "https://rxddit.com/v" + submission.permalink

            self._media_urls.append(video_url)
            self._thumbnail = submission.thumbnail


        elif self._type is PostType.POLL:
            self._text = submission.selftext.split("\n\n[View Poll]")[0]
            self._poll_options = [o.text for o in submission.poll_data.options]

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
        elif subm.is_self:
            return PostType.TEXT
        else:
            return PostType.UNKNOWN
        
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
