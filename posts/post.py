from enum import Enum

from util.msgutil import escape_markdown_extra, unembed_links, truncate, download


class PostType(Enum):
    UNKNOWN = 0
    TEXT = 1
    IMAGE = 2
    GALLERY = 3
    VIDEO = 4
    POLL = 5


class Post:
    # TODO: should revrite prolly
    _prefix = ""
    _platform = "unknown"
    _max_characters = 2000

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
        
        title = self.get_md_title(escape_embed_links)
        body = self.get_md_body(escape_embed_links)
        footer = self.get_md_footer(include_author)
        footer_media = self.get_md_footer_media()

        linebreaks = 3
        length = len(title) + len(footer) + linebreaks

        footer_media = truncate(footer_media, self._max_characters - length)
        length += len(footer_media)
        body = truncate(body, self._max_characters - length)

        if title and body:
            return (title + "\n\n" + body + "\n" + footer + footer_media).strip()
        else:
            return (title + body + "\n" + footer + footer_media).strip()
    
    def get_md_title(self, escape_embed_links) -> str:
        if self._title:
            return f"**{escape_markdown_extra(self._title, escape_embed_links)}**"

        return ""

    def get_md_body(self, escape_embed_links) -> str:
        body = ""
        
        # text
        if self._text:
            body += f"{unembed_links(self._text) if escape_embed_links else self._text}"

        # poll
        body += "\n".join(f"- {i}" for i in self._poll_options)

        return body

    def get_md_footer(self, include_author) -> str:
        footer = f"-# Posted "
        if include_author:
            footer += f"by {self._prefix}{escape_markdown_extra(self._author)} "
        footer += f"on [{self._platform}](<{self._url}>) "

        return footer

    def get_md_footer_media(self) -> str:
        media_links = ""
        if self._type in [PostType.IMAGE, PostType.VIDEO]:
            media_links += f"[.]({self._media[0]})"
        elif self._type == PostType.GALLERY:
            for url in self._media:
                media_links += f"[.]({url}) "
        
        return media_links

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