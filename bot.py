# set working directory
import os
import sys

os.chdir(sys.path[0])

from util.general import *
from util.const import *

import asyncio
import discord
from discord.ext import commands

from dotenv import load_dotenv
load_dotenv()


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
    print(f"Logged in as {bot.user}")
    if ASDEBUG:
        print("Debug mode enabled")

    if FORCESYNC:
        # discord doesnt like it when you do this immediately
        await asyncio.sleep(5)
        cmds = await bot.tree.sync()
        for cmd in cmds:
            print(f"Command synced: {cmd}")
    


# manual sync
@bot.tree.command(name="sync", description="sync the command tree")
async def sync_cmd(interaction: discord.Interaction):
    if not await devcheck(interaction):
        return
    await interaction.response.defer(ephemeral=True)
    cmds = await bot.tree.sync()
    for cmd in cmds:
        print(f"Command synced: {cmd}")
    print("Command tree synced")
    await interaction.followup.send("Command tree synced")




asyncio.run(main())
