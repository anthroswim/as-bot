import os
import discord
import requests
from util.const import DEV
import re
from discord.utils import escape_markdown

from util.loghelper import log

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
        log.warning(f"Unauthorized access from {interaction.user.mention} {interaction.user.name}")
        await errorrespond(interaction, f"Only <@{DEV}> is allowed to use this command")
        return False


def escape_markdown_extra(text: str, unembed_liks = False) -> str:
    # TODO: test order of operations
    text = escape_markdown(text)

    if unembed_liks:
        text = re.sub(r'<(https?://\S+)>', r'\1', text)
    
    return text


def download(link, path, filename, **kwargs) -> str:
    fullpath = os.path.join(path, filename)
    with open(fullpath, "wb") as img_file:
        content = requests.get(link, **kwargs).content
        if len(content) == 0:
            raise Exception("Image not found")
        img_file.write(content)
    return fullpath