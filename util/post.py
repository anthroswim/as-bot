from enum import Enum
from discord import Embed

from util.filecache import FileCache


class PostType(Enum):
    TEXT = 1
    IMAGE = 2
    GALLERY = 3
    VIDEO = 4
    POLL = 5
    UNKNOWN = 6


class Post:
    # TODO: a more object oriented approach instead of posttype
    _prefix = ""
    _platform = "unknown"

    def __init__(self, url: str):
        # common
        self._url = url
        self._author = None
        self._author_icon = None
        self._title = None
        self._type = None
        # date maybe?
        
        self._fetched = False

        # text
        self._text = None

        # image
        self._media_urls = []
        
        # porcessed media
        self._chached_media = []

        # video
        self._thumbnail = None

        # poll
        self._poll_options = []

        # crosspost/retweet/quote
        self._parent = None

    async def fetch(self):
        self._fetched = True

    def discord_embeds(self, embed_color = 0x5865F2):
        if not self._fetched:
            raise Exception("The post was not fetched")
        
        # common
        top = Embed(title=self._title, url=self._url, color=embed_color)
        top.set_author(name=self._prefix + self._author, icon_url=self._author_icon)
        top.set_footer(text=self._platform)
        embeds = [top]

        # text, max 4096 characters
        if self._text:
            top.description = self._text[:4096]

        # media
        match self._type:
            case PostType.TEXT:
                pass
            case PostType.IMAGE:
                top.set_image(url=self._media_urls[0])
            case PostType.GALLERY:
                for url in self._media_urls:
                    embed = Embed(color=embed_color)
                    embed.set_image(url=url)
                    embeds.append(embed)
            case PostType.VIDEO:
                top.set_thumbnail(url=self._thumbnail)
            case PostType.POLL:
                raise Exception("Polls are not supported yet")

        return embeds
    
    def get_avatar(self) -> str:
        return self._author_icon

    def get_username(self) -> str:
        return self._prefix + self._author

    def get_message(self, include_author = False, include_medialinks = True) -> str:
        if not self._fetched:
            raise Exception("The post was not fetched")
        
        # title
        message = f"**{self._title}**\n\n"

        # text
        if self._text:
            message += f"{self._text}\n"

        # poll
        for option in self._poll_options:
            message += f"- {option}\n"

        # footer
        message += f"-# Posted "
        if include_author:
            message += f"by {self._prefix}{self._author} "
        message += f"on [{self._platform}](<{self._url}>) "

        
        # media
        if include_medialinks:
            match self._type:
                case PostType.IMAGE:
                    message += f"[.]({self._media_urls[0]})"
                case PostType.GALLERY:
                    for url in self._media_urls:
                        message += f"[.]({url}) "
                case PostType.VIDEO:
                    message += f"[.]({self._media_urls[0]})"

        return message
    
    def get_files(self) -> list[str]:
        return self._chached_media
    
    def __del__(self):
        for media in self._chached_media:
            FileCache.removepath(media)
