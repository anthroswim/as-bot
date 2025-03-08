from discord.ext import commands, tasks

import time

from util.const import *
from util.msgutil import *
from feeds.supportedfeeds import FEEDPATTERNS, anyfeed
from util.loghelper import log_cog_load, log, log_command
from util.telegramhelper import telegram_send
from util.whook import threadhook_send



class RSSCog(commands.Cog, group_name="rss"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.rss_parse_all.start()
        log_cog_load(self)


    @tasks.loop(hours=1)
    async def rss_parse_all(self):
        log.info("Parsing rss feeds")
        
        before = time.time()
        after = conf["last_sync"]

        try:
            for feed_url, platforms in conf["rss"].items():
                # fetch feed and posts
                feed = anyfeed(feed_url)
                if not feed:
                    continue
                feed.fetch_new_entries(after, before)
                posts = feed.get_posts()
                
                for post in posts:
                    await post.fetch()
                    # telegram
                    for chat_id in platforms["tg"]:
                        try:
                            await telegram_send(chat_id, post)
                        except Exception as e:
                            log.error(f"Error sending to telegram: {e}")
                    
                    # discord
                    for channel_id in platforms["dc"]:
                        try:
                            channel = self.bot.get_channel(channel_id)
                            await threadhook_send(channel, self.bot, post.get_message(), post.get_username(), post.get_avatar())
                        except Exception as e:
                            log.error(f"Error sending to discord: {e}")
                        

        except Exception as e:
            log.error(f"Error parsing feeds: {e}")
                
        
        conf["last_sync"] = before
        saveconf()


    @rss_parse_all.before_loop
    async def _before_loop(self):
        await self.bot.wait_until_ready()

        
async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RSSCog(bot))