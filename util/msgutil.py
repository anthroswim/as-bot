import os
import discord
import requests
from util.const import DEV
import re
from discord.utils import escape_markdown

from util.loghelper import log
from util.const import conf

# return uniform embed for errors
def errorembed(error: str):
    embed = discord.Embed(color=0xFF6700)
    embed.add_field(name="Error", value=error, inline=False)
    return embed


# respond to an interaction with uniform embeds
async def errorrespond(interaction: discord.Interaction, error: str):
    await interaction.response.send_message(embed=errorembed(error), ephemeral=True)


# checks if user is eligible for the interaction
async def devcheck(interaction: discord.Interaction):
    if interaction.user.id == DEV:
        return True
    else:
        log.warning(f"Unauthorized dev access from {interaction.user.mention} {interaction.user.name}")
        await errorrespond(interaction, f"Only <@{DEV}> is allowed to use this command")
        return False
    
async def modcheck(interaction: discord.Interaction):
    if interaction.user.id in conf["mods"]:
        return True
    else:
        log.warning(f"Unauthorized mod access from {interaction.user.mention} {interaction.user.name}")
        await errorrespond(interaction, f"Only mods are allowed to use this command")
        return False

def download(link, path, filename, **kwargs) -> str:
    fullpath = os.path.join(path, filename)
    with open(fullpath, "wb") as img_file:
        content = requests.get(link, **kwargs).content
        if len(content) == 0:
            raise Exception("Image not found")
        img_file.write(content)
    return fullpath

def escape_markdown_extra(text: str, unembed_liks = False) -> str:
    # TODO: test order of operations
    text = escape_markdown(text)

    if unembed_liks:
        text = unembed_links(text)
    
    return text

def unembed_links(text: str) -> str:
    # replace [link](link) with link
    text = re.sub(r"\[https?://[^\s\)\]]+\]\((https?://[^\s\)\]]+)\)", r"\1", text)

    # replace normal links with <link>
    text = re.sub(r"(?<!(\]\())(https?://[^\s\)\]]+)", r"<\2>", text)
    
    # replace markdown links with [](<link>)
    text = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r"[\1](<\2>)", text)
    return text

# this is utterly stupid
def truncate(text: str, max_length: int, placeholder: str = "...") -> str:
    if max_length <= 0:
        return ""
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    
    max_length -= len(placeholder)
    return " ".join(text[:max_length].split(" ")[:-1]) + placeholder