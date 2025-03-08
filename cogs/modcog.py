import discord
from discord import app_commands
from discord.ext import commands

from util.loghelper import log_cog_load
from util.const import conf, saveconf
from util.msgutil import devcheck, modcheck

class ModCog(commands.GroupCog, group_name="mod"):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        log_cog_load(self)

    
    @app_commands.command(name="add", description="add user as mod")
    async def addmod(self, interaction: discord.Interaction, user: discord.User):
        if not await devcheck(interaction):
            return

        if user.id in conf["mods"]:
            await interaction.response.send_message(f"{user.name} `{user.id}` is already a mod")
            return
        
        conf["mods"].append(user.id)
        saveconf()
        await interaction.response.send_message(f"Added {user.name} `{user.id}` as mod")

    @app_commands.command(name="remove", description="remove user from mods")
    async def rmmod(self, interaction: discord.Interaction, user: discord.User):
        if not await devcheck(interaction):
            return
        
        if user.id not in conf["mods"]:
            await interaction.response.send_message(f"{user.name} `{user.id}` is not a mod")
            return
        
        conf["mods"].remove(user.id)
        saveconf()
        await interaction.response.send_message(f"Removed {user.name} `{user.id}` from mods")

    @app_commands.command(name="list", description="list mods")
    async def listmod(self, interaction: discord.Interaction):
        if not await devcheck(interaction):
            return

        await interaction.response.send_message("\n".join([f"`{mod}`" for mod in conf["mods"]]))

    @app_commands.command(name="debug", description="check if user can call mod commands")
    async def debugmod(self, interaction: discord.Interaction):
        if not await modcheck(interaction):
            return
        await interaction.response.send_message(":3", ephemeral=True)

async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ModCog(bot))