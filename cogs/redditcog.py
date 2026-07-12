import os
import discord
from discord import app_commands
from discord.ext import commands
import asyncpraw
from asyncpraw.models import PostMedia

from posts.post import PostType
from posts.supported import anypost
from util.loghelper import log_cog_load, log
from util.msgutil import modcheck, devcheck
from util.reddithelper import reddit
from util.const import SUBREDDIT, conf
from util.whook import threadhook_send

TMPDIR = "tmp"

class RedditCog(commands.GroupCog, group_name="reddit"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="post to reddit",
            callback=self.ctx_post_to_sub,
        )
        self.bot.tree.add_command(self.ctx_menu)
        log_cog_load(self)


    async def ctx_post_to_sub(self, interaction: discord.Interaction, message: discord.Message):
        await self.post_to_sub(interaction, message.content)



    @app_commands.allowed_installs(guilds=True, users=True)
    @app_commands.allowed_contexts(guilds=True, dms=True, private_channels=True)
    @app_commands.command(name="poast", description="post to reddit")
    async def cmd_post_to_sub(self, interaction: discord.Interaction, link: str, title: str = None):
        await self.post_to_sub(interaction, link, title)

    async def post_to_sub(self, interaction: discord.Interaction, link: str, title: str = None):
        if not await modcheck(interaction):
            return
        
        await interaction.response.defer()

        try:
            post = anypost(link.split(" ")[0])
            if post is None:
                raise Exception(f"Unsupported post")

            await post.fetch()
            if not post._media:
                raise Exception("No media found")
            
            sub = await reddit.subreddit(SUBREDDIT, fetch=True)

            title_credit = f"<{post.get_username()}>"
            title = f"{title.strip()} {title_credit}" if title else title_credit

            if not os.path.exists(TMPDIR):
                os.mkdir(TMPDIR)
            files = post.download(TMPDIR)
            if not files:
                raise Exception("Failed to download media")

            post_body = f"Source: {post.get_username()}, [{post._platform}]({post._url})"

            submission = None
            if post._type is PostType.IMAGE:
                submission = await sub.submit(
                    title=title,
                    selftext=post_body,
                    image=PostMedia(files[0]),
                    flair_id=conf["flairs"]["image"]
                )
            
            elif post._type is PostType.VIDEO:
                submission = await sub.submit(
                    title=title,
                    selftext=post_body,
                    video={
                        "media": PostMedia(files[0]),
                        "thumbnail": PostMedia("misc/as_logo_fox.png")
                    },
                    flair_id=conf["flairs"]["video"]
                )
            
            elif post._type is PostType.GALLERY:
                submission = await sub.submit(
                    title=title,
                    selftext=post_body,
                    gallery=[PostMedia(f) for f in files],
                    flair_id=conf["flairs"]["gallery"]
                )

            for file in files:
                os.remove(file)

            await interaction.followup.send(f"Posted to [r/{SUBREDDIT}](<{submission.shortlink}>)")
        
        except Exception as e:
            log.error(e)
            await interaction.followup.send(f"Failed to post: `{e}`")

    @app_commands.command(name="embed", description="embed a poast for debugging")
    async def embed_post(self, interaction: discord.Interaction, link: str):
        if not await devcheck(interaction):
            return
        await interaction.response.defer(ephemeral=True)
        try:
            post = anypost(link.split(" ")[0])
            if post is None:
                raise Exception(f"Unsupported post")
            
            await post.fetch()
            await threadhook_send(interaction.channel, self.bot, post.get_message(), post.get_username(), post.get_avatar())
            
            await interaction.followup.send("Done", ephemeral=True)
        except Exception as e:
            log.error(e)
            await interaction.followup.send(f"Failed to embed: `{e}`", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RedditCog(bot))