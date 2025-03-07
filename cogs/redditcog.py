import discord
from discord import app_commands
from discord.ext import commands

from util.loghelper import log_cog_load


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
        await interaction.response.send_message(f"Work in progress", ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RedditCog(bot))