from PIL import Image, ImageFont, ImageDraw


# setup font
max_width = 1000
font_size = max_width * 0.10
font_path = "HelveticaNeue-CondensedBlack.ttf"
font = ImageFont.truetype(font_path, font_size)


# setup colors
color_mode = "RGBA"
text_color = "#FFFFFF"
background_color = "#000000"
margin = int(max_width * 0.05)


# generate imatge
def swimify(text: str) -> Image.Image:
    # generate text with transparent background
    text = f"[{text}]"
    text_image = Image.new(color_mode, (max_width, int(2 * font_size)))
    draw = ImageDraw.Draw(text_image)
    draw.text((0, 0), text, font=font, fill=text_color)
    text_image = text_image.crop(text_image.getbbox())

    # add black background
    image = Image.new(color_mode, (text_image.size[0] + 2 * margin, text_image.size[1] + 2 * margin), background_color)
    image.paste(text_image, (margin, margin), text_image)
    image.show()
    pass


if __name__ == "__main__":
    swimify("anthroswim")
