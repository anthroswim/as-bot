import os
import discord
from discord import app_commands
from discord.ext import commands

from posts.post import PostType
from posts.supported import anypost
from util.loghelper import log_cog_load, log
from util.msgutil import modcheck
from util.reddithelper import reddit
from util.const import SUBREDDIT, conf

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
            
            sub = await reddit.subreddit(SUBREDDIT)

            title_credit = f"<{post.get_username()}>"
            title = f"{title.strip()} {title_credit}" if title else title_credit

            if not os.path.exists(TMPDIR):
                os.mkdir(TMPDIR)
            files = post.download(TMPDIR)
            if not files:
                raise Exception("Failed to download media")

            submission = None
            if post._type is PostType.IMAGE:
                submission = await sub.submit_image(
                    title=title,
                    image_path=files[0],
                    flair_id=conf["flairs"]["image"]
                )
            
            elif post._type is PostType.VIDEO:
                submission = await sub.submit_video(
                    title=title,
                    video_path=files[0],
                    thumbnail_path="misc/as_logo_fox.png",
                    flair_id=conf["flairs"]["video"]
                )
            
            elif post._type is PostType.GALLERY:
                submission = await sub.submit_gallery(
                    title=title,
                    images=[{"image_path": file} for file in files],
                    flair_id=conf["flairs"]["gallery"]
                )

            for file in files:
                os.remove(file)

            await submission.reply(f"Art by {post.get_username()} on [{post._platform}]({post._url})\n\nCalled by {interaction.user.name}")

            await interaction.followup.send(f"Posted to [r/{SUBREDDIT}](<{submission.shortlink}>)")
        
        except Exception as e:
            log.error(e)
            await interaction.followup.send(f"Failed to post: `{e}`")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RedditCog(bot))