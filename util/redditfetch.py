import os
import re
import asyncpraw

import discord.embeds

EMBEDCOLOR = 0x5865F2

reddit = asyncpraw.Reddit(
    client_id=os.getenv("RDTCLID"),
    client_secret=os.getenv("RDTCLSECRET"),
    user_agent="anthroswim",
)


class Post:
    def __init__(self, url: str):
        self._url = url

    async def fetch(self):
        # fetch
        submission = await reddit.submission(url=self._url)

        # url
        self._url = submission.shortlink

        # author
        author = await reddit.redditor(submission.author.name)
        await author.load()
        self._auth = author.name
        self._auth_icon = author.icon_img.split("?")[0]

        # title
        self._title = submission.title

        # different types
        self._type = Post.post_type(submission)
        self._media = []
        self._text = None
        self._thumbnail = None

        match self._type:
            case "image":
                self._media.append(submission.url)

            case "gallery":
                image_dict = submission.media_metadata
                for i in image_dict:
                    pattern = r"/([^/]+\.png)"
                    self._media.append(
                        "https://i.redd.it/"
                        + re.search(pattern, image_dict[i]["s"]["u"]).group(1)
                    )

            case "video":
                # reddit is stupit and has the video and audio in separate sources
                # besides discord doesnt allow videos in embeds
                self._thumbnail = submission.thumbnail
                self._media.append(submission.media["reddit_video"]["fallback_url"])

            case "poll":
                # TODO
                self._text = "polls arent supported yet"

            case "crosspost":
                # TODO
                self._text = "crossposts arent supported yet"
                # parent = reddit.submission(url= "https://reddit.com" + submission.crosspost_parent_list[0]["permalink"])

            case "text":
                # max 4096 characters
                self._text = submission.selftext[:4096]

    def dc_embed(self):
        top = discord.Embed(title=self._title, url=self._url, color=EMBEDCOLOR)
        top.set_author(name=self._auth, icon_url=self._auth_icon)
        embeds = [top]

        # text
        if self._text is not None:
            top.description = self._text

        # media
        if self._thumbnail is not None:
            top.set_thumbnail(url=self._thumbnail)
        elif len(self._media) == 1:
            top.set_image(url=self._media[0])
        elif len(self._media) > 1:
            for url in self._media:
                embed = discord.Embed(color=EMBEDCOLOR)
                embed.set_image(url=url)
                embeds.append(embed)

        return embeds

    def post_type(subm) -> str:
        if getattr(subm, "post_hint", "") == "image":
            return "image"
        elif getattr(subm, "is_gallery", False):
            return "gallery"
        elif subm.is_video:
            return "video"
        elif hasattr(subm, "poll_data"):
            return "poll"
        elif hasattr(subm, "crosspost_parent"):
            return "crosspost"
        elif subm.is_self:
            return "text"
        return "link"
