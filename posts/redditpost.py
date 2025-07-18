import re

from util.reddithelper import reddit
from posts.post import Post, PostType

class RedditPost(Post):
    _prefix = "u/"

    async def generate(self, submission):
        # url
        self._url = submission.shortlink

        # id
        self._id = submission.id

        # check parent
        if hasattr(submission, "crosspost_parent"):
            self._parent = submission.crosspost_parent_list[0]

        # author
        if submission.author is None:
            self._author = "[deleted]"
            self._author_icon = None
        else:
            author = await reddit.redditor(submission.author.name)
            await author.load()
            self._author = author.name
            self._author_icon = author.icon_img.split("?")[0]
        
        # platform
        self._platform = (
            "Reddit"
            if submission.subreddit_type == "user"
            else submission.subreddit_name_prefixed
        )

        # title
        self._title = submission.title

        # type
        self._type = RedditPost.post_type(submission)

        self._text = submission.selftext if submission.selftext else None

        if self._type is PostType.IMAGE:
            self._media.append(submission.url)
            self._thumbnail = submission.thumbnail
        
        elif self._type is PostType.GALLERY:
            image_dict = submission.media_metadata
            for i in image_dict:
                pattern = r"/([^/?]+)(?:\?|$)"
                self._media.append(
                    "https://i.redd.it/"
                    + image_dict[i]["id"] 
                    + "."
                    + image_dict[i]["m"].split("/")[-1]
                )
            self._thumbnail = submission.thumbnail

        elif self._type is PostType.VIDEO:
            video = submission.media["reddit_video"]
            video_url = video["fallback_url"]

            # for audio we need to find the url that includes it
            if video["has_audio"]:
                video_url = "https://rxddit.com/v" + submission.permalink

            self._media.append(video_url)
            self._thumbnail = submission.thumbnail

        elif self._type is PostType.POLL:
            self._text = submission.selftext.split("\n\n[View Poll]")[0]
            self._poll_options = [o.text for o in submission.poll_data.options]

        elif self._type is PostType.TEXT:
            pass

        elif self._type is PostType.UNKNOWN:
            # likely a link post
            if hasattr(submission, "url"):
                self._text = submission.url

        if self._thumbnail == "nsfw":
            self._thumbnail = "https://raw.githubusercontent.com/Gilgames32/lop/main/misc/nsfw.png"

        await super().fetch()

    async def fetch(self):
        if self._fetched:
            return
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
