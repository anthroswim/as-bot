import os
import discord
from discord import app_commands
from discord.ext import commands

from posts.post import PostType
from posts.supported import anypost
from util.loghelper import log_cog_load, log
from util.msgutil import devcheck
from util.reddithelper import reddit
from util.const import SUBREDDIT
import requests

TMPDIR = "tmp"

class RedditCog(commands.GroupCog, group_name='reddit'):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name="Post to Reddit",
            callback=self.post_to_sub,
        )
        self.bot.tree.add_command(self.ctx_menu)
        log_cog_load(self)

    async def post_to_sub(self, interaction: discord.Interaction, message: discord.Message):
        if not await devcheck(interaction):
            return
        
        await interaction.response.defer(ephemeral=True)
        
        post = anypost(message.content.split(" ")[0])
        if post is None:
            await interaction.followup.send(f"Unsupported post")
            return

        await post.fetch()
        if not post._media:
            await interaction.followup.send(f"No media found")
            return
        
        sub = await reddit.subreddit(SUBREDDIT)

        title = f"<{post.get_username()}>"

        if not os.path.exists(TMPDIR):
            os.mkdir(TMPDIR)
        files = post.download(TMPDIR)
        if not files:
            await interaction.followup.send(f"Failed to download media")
            return

        submission = None
        if post._type is PostType.IMAGE:
            submission = await sub.submit_image(
                title=title,
                image_path=files[0]
            )
        
        elif post._type is PostType.VIDEO:
            submission = await sub.submit_video(
                title=title,
                video_path=files[0],
                thumbnail_path="misc/as_logo_fox.png"
            )
        
        elif post._type is PostType.GALLERY:
            submission = await sub.submit_gallery(
                title=title,
                images=[{"image_path": file} for file in files]
            )

        for file in files:
            os.remove(file)

        await submission.reply(f"Posted by {post.get_username()} on [{post._platform}]({post._url})")

        await interaction.followup.send(f"Posted to [r/{SUBREDDIT}](<{submission.url}>)")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RedditCog(bot))