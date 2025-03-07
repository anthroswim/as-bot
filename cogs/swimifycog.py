import discord
from discord import app_commands
from discord.ext import commands

from io import BytesIO
from PIL import Image, ImageFont, ImageDraw

from util.loghelper import log_cog_load
from util.msgutil import errorembed


# setup font
max_width = 2000
font_size = max_width * 0.02
font_path = "misc/HelveticaNeue-CondensedBlack.ttf"
font = ImageFont.truetype(font_path, font_size)


# setup colors
color_mode = "RGBA"
text_color = "#FFFFFF"
background_color = "#000000"
margin = int(font_size)


# generate imatge
def swimify(text: str, raw = False) -> Image.Image:
    # generate text with transparent background
    if not raw:
        text = f"<{text}>"
    text_image = Image.new(color_mode, (max_width, int(2 * font_size)))
    draw = ImageDraw.Draw(text_image)
    draw.text((0, 0), text, font=font, fill=text_color)
    text_image = text_image.crop(text_image.getbbox())

    # add black background
    image = Image.new(color_mode, (text_image.size[0] + 2 * margin, text_image.size[1] + 2 * margin), background_color)
    image.paste(text_image, (margin, margin), text_image)
    
    return image



class SwimifyCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        log_cog_load(self)

    @app_commands.command(name="swimify", description="swimify text")
    async def swimify_cmd(self, interaction: discord.Interaction, text: str, raw: bool = False):
        await interaction.response.defer()
        try:
            img = swimify(text, raw)
            # save image to BytesIO
            with BytesIO() as image_binary:
                img.save(image_binary, "PNG")
                image_binary.seek(0)
                await interaction.followup.send(file=discord.File(image_binary, "as.png"))
        except Exception as e:
            await interaction.followup.send(embed=errorembed(str(e)))
        


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(SwimifyCog(bot))