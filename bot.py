# set working directory
import os
import sys

os.chdir(sys.path[0])

from util.const import ASDEBUG
from util.msgutil import devcheck
from util.loghelper import log

import asyncio
import discord
from discord.ext import commands


# discord init
intents = discord.Intents.default()
bot = commands.Bot(command_prefix=".", description="[anthroswim]", intents=intents)


# load cogs
async def load_cogs():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension(f"cogs.{filename[:-3]}")


# startup
async def main():
    await load_cogs()
    await bot.start(os.getenv("DCTOKEN"))


# on ready
@bot.event
async def on_ready():
    log.info(f"Logged in as {bot.user}")
    if ASDEBUG:
        log.info("Debug mode enabled")
    


# manual sync
@bot.tree.command(name="sync", description="sync the command tree")
async def sync_cmd(interaction: discord.Interaction):
    if not await devcheck(interaction):
        return
    await interaction.response.defer(ephemeral=True)
    cmds = await bot.tree.sync()
    for cmd in cmds:
        log.info(f"Command synced: {cmd}")
    log.info("Command tree synced")
    await interaction.followup.send("Command tree synced")




asyncio.run(main())
