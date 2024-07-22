from enum import Enum
from discord import Embed


class PostType(Enum):
    TEXT = 1
    IMAGE = 2
    GALLERY = 3
    VIDEO = 4
    POLL = 5
    CROSSPOST = 6
    UNKNOWN = 7


class Post:
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
        self._media = []

        # video
        self._thumbnail = None

        # poll
        self._poll = None

        # crosspost
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
                top.set_image(url=self._media[0])
            case PostType.GALLERY:
                for url in self._media:
                    embed = Embed(color=embed_color)
                    embed.set_image(url=url)
                    embeds.append(embed)
            case PostType.VIDEO:
                top.set_thumbnail(url=self._thumbnail)
            case PostType.POLL:
                raise Exception("Polls are not supported yet")
            case PostType.CROSSPOST:
                raise Exception("Crossposts are not supported yet")

        return embeds
        


class Poll:
    def __init__(self):
        self._title = None
        self._options = [] # stored in tuples (option, votes)
        self._total_votes = 0