import discord
from discord import app_commands
from discord.ext import commands

from util.general import *
from util.redditfetch import RedditPost

class RedditEmbedCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)

    @app_commands.command(name="reddit", description="embed reddit posts")
    async def redditembed(self, interaction: discord.Interaction, link: str):
        # TODO: remove after testing
        if not await devcheck(interaction):
            return

        await interaction.response.defer()
        try:
            post = RedditPost(link)
            await post.fetch()
            embeds = post.discord_embeds()
            await interaction.followup.send(embeds=embeds)
        except Exception as e:
            await interaction.followup.send(embed=errorembed(str(e)))
        


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RedditEmbedCog(bot))