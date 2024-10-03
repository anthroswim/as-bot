from telegram import Bot, InputMediaPhoto
from telegram.constants import ParseMode
import os
import re

from util.post import Post, PostType

bot = Bot(token=os.getenv("TGBOTTOKEN"))

special_characters = r"[_*\[\]()~`>#+-=|{}.!]"

async def tg_send(chat_id, post: Post):
    # text
    message = f"*{escape_markdown(post._title)}*\n\n"
    if post._text:
        message += f"{escape_markdown(post._text)}\n\n"
    message += f"Posted by {post._prefix}{escape_markdown(post._author)} on [{escape_markdown(post._platform)}]({post._url})"

    # media - its a mess but it works
    try:
        if post._type == PostType.IMAGE:
            await bot.send_photo(chat_id=chat_id, photo=post._media_urls[0], caption=message, parse_mode=ParseMode.MARKDOWN_V2)
        elif post._type == PostType.GALLERY:
            media = [InputMediaPhoto(media) for media in post._media_urls]
            await bot.send_media_group(chat_id=chat_id, media=media, caption=message, parse_mode=ParseMode.MARKDOWN_V2)
        elif post._type == PostType.VIDEO:
            message += " \\(video\\)"
            await bot.send_photo(chat_id=chat_id, photo=post._thumbnail, caption=message, parse_mode=ParseMode.MARKDOWN_V2)
        else:
            await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN_V2, link_preview_options={"is_disabled": True})
    
    except Exception as e:
        print(f"Error sending to telegram: {e}")
        message += " \\(preview unavailable\\)"
        await bot.send_message(chat_id=chat_id, text=message, parse_mode=ParseMode.MARKDOWN_V2, link_preview_options={"is_disabled": True})


def escape_markdown(text: str) -> str:
    escaped_text = re.sub(special_characters, r"\\\g<0>", text)
    return escaped_text