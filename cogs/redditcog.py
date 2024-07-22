import discord
from discord import app_commands
from discord.ext import commands

from util.general import *
from util.redditfetch import RedditPost

class RedditCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        print("Loaded", __class__.__name__)

    @app_commands.command(name="reddit", description="embed reddit posts")
    async def redditembed(self, interaction: discord.Interaction, link: str):
        # TODO: remove after testing
        if not await devcheck(interaction):
            return

        await interaction.response.defer(ephemeral=True)
        try:
            # TODO: chache webhooks
            channel = interaction.channel
            webhooks = await channel.webhooks()
            if not webhooks:
                await channel.create_webhook(name="FeedHelper")
                webhooks = await channel.webhooks()
            webhook = webhooks[0]


            post = RedditPost(link)
            await post.fetch()

            await webhook.send(post.webhook_message(), username=post.webhook_username(), avatar_url=post.webhook_avatar())

            await interaction.followup.send("Done")

            # embeds = post.discord_embeds()
            # await interaction.followup.send(embeds=embeds)
        except Exception as e:
            await interaction.followup.send(embed=errorembed(str(e)))
        


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(RedditCog(bot))