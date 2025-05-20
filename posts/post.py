from enum import Enum

from util.msgutil import download, escape_markdown_extra

class PostType(Enum):
    TEXT = 1
    IMAGE = 2
    GALLERY = 3
    VIDEO = 4
    POLL = 5
    UNKNOWN = 6


class Post:
    # TODO: should revrite prolly
    _prefix = ""
    _platform = "unknown"

    def __init__(self, url: str):
        # common
        self._url = url
        # TODO: separate author name and handle
        self._author = None
        self._author_icon = None
        self._title = None
        self._type = None
        self._id = None
        # date maybe?
        
        self._fetched = False

        # text
        self._text = None

        # image
        self._media = []

        # video
        self._thumbnail = None

        # poll
        self._poll_options = []

        # crosspost/retweet/quote
        self._parent = None

    async def fetch(self):
        if self._fetched:
            return
        self._fetched = True

    def get_avatar(self) -> str:
        return self._author_icon

    def get_username(self) -> str:
        return self._prefix + self._author

    def get_message(self, include_author = False) -> str:
        if not self._fetched:
            raise Exception("The post was not fetched")
        
        escape_embed_links = self._type in [PostType.IMAGE, PostType.VIDEO, PostType.GALLERY]
        allow_markdown_in_body = self._type in [PostType.TEXT, PostType.POLL]
        
        # title
        if self._title:
            message = f"**{escape_markdown_extra(self._title, escape_embed_links)}**\n\n"
        else:
            message = ""

        # text
        if self._text:
            message += f"{self._text if allow_markdown_in_body else escape_markdown_extra(self._text, escape_embed_links)}\n"
            if not self._title:
                message += "\n"

        # poll
        for option in self._poll_options:
            message += f"- {option}\n"

        # footer
        message += f"-# Posted "
        if include_author:
            message += f"by {self._prefix}{escape_markdown_extra(self._author)} "
        message += f"on [{self._platform}](<{self._url}>) "

        # media
        if self._type in [PostType.IMAGE, PostType.VIDEO]:
            message += f"[.]({self._media[0]})"
        elif self._type == PostType.GALLERY:
            for url in self._media:
                message += f"[.]({url}) "

        if len(message) > 2000:
            message = " ".join(message[:1997].split(" ")[:-1]) + "..." # profound mental retardation
        return message
        
    def download(self, path: str) -> list[str]:
        if not self._fetched:
            raise Exception("The post was not fetched")
        if self._type not in [PostType.IMAGE, PostType.VIDEO, PostType.GALLERY]:
            raise Exception("This post is not downloadable")
        
        filenames = []

        # download media
        if self._type == PostType.GALLERY:
            for i, url in enumerate(self._media):
                ext = url.split(".")[-1].split("?")[0]
                filename = f"{self._author}_{self._id}_{i}.{ext}"
                filename = download(url, path, filename)
                filenames.append(filename)
        else:
            url = self._media[0]
            ext = url.split(".")[-1].split("?")[0]
            # FIXME: this is rarted
            if len(ext) > 4:
                ext = "jpg" if self._type == PostType.IMAGE else "mp4"
            filename = f"{self._author}_{self._id}.{ext}"
            filename = download(url, path, filename)
            filenames.append(filename)

        return filenames

        
    