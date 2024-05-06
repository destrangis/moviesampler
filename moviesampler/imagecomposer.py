
from typing import List, Tuple


import  importlib.resources as ir
from PIL import Image, ImageDraw, ImageFont

from . import version

DEFAULT_FRAME_HEIGHT = 180


class ImageComposer:

    def __init__(self, rows, columns, header="", frame_height=DEFAULT_FRAME_HEIGHT):
        self.rows = rows
        self.columns = columns
        self.frame_height = frame_height
        self.header_text = header
        with ir.path("moviesampler.fonts", "3270Condensed-Regular.otf") as fnt1:
            self.condensedfont = str(fnt1)
        with ir.path("moviesampler.fonts", "3270-Regular.otf") as fnt2:
            self.regularfont = str(fnt2)


    def build_grid(self, framelist: List[ Tuple[Image.Image, str] ]) -> Image.Image:
        """
        Build the grid of frames
        """
        images = [ self.tile_from_frame(img, self.frame_height, timestamp)
                        for img, timestamp in framelist ]

        # Calculate dimensions of the grid
        num_images = len(images)
        num_cols = self.columns
        num_rows = num_images // num_cols
        if num_images % num_cols != 0:
            num_rows += 1

        # Calculate the width and height of the output image
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)
        grid_width = max_width * num_cols + 2 * (num_cols - 1)
        grid_height = max_height * num_rows + 2 * (num_rows - 1)

        hdr = self.text_image(grid_width, self.header_text)
        hdr_height = hdr.size[1]
        grid_height += hdr_height

        footer = self.text_image(grid_width, f"Created with moviesampler v{version()}", footer=True)
        footer_height = footer.size[1]
        footer_pos = grid_height
        grid_height += footer_height

        grid_image = Image.new('RGB', (grid_width, grid_height), color='white')
        grid_image.paste(hdr, (0, 0))

        # Paste each image into the grid
        for i, img in enumerate(images):
            row = i // num_cols
            col = i % num_cols
            x = col * (max_width + 2)
            y = row * (max_height + 2) + hdr_height
            grid_image.paste(img, (x, y))

        grid_image.paste(footer, (0, footer_pos))
        return grid_image


    def tile_from_frame(self, img: Image.Image, height: int, timestamp: str) -> Image.Image:
        """
        Resize a frame image to the desired height and add the timestamp
        on the top right corner
        """
        width_percent = height / float(img.size[1])
        target_width = int(float(img.size[0]) * float(width_percent))
        resized_img = img.resize((target_width, height))

        # Create a Draw object for adding text to the image
        draw = ImageDraw.Draw(resized_img)

        fnt = ImageFont.truetype(self.condensedfont, 15)

        # Get text size
        left, top, right, bottom = fnt.getbbox(timestamp)

        # Calculate text position in lower right corner
        text_x = target_width - right - left - 5  # Add some padding from the right edge
        text_y = 5  # Add some padding from the bottom edge

        # Draw the text with a black outline and white fill
        draw.text((text_x, text_y), timestamp, fill=(255, 255, 255), font=fnt, stroke_width=1, stroke_fill=(0, 0, 0))

        return resized_img


    def text_image(self, width: int, text: str, footer: bool = False) -> Image.Image:
        """
        Create an Image with the given text
        """
        text_lines = [ l.strip() for l in text.split("\n") ]

        font = self.condensedfont if footer else self.regularfont
        fontsize = 10 if footer else 20
        fnt = ImageFont.truetype(font, fontsize)
        height = 0 if footer else 25
        interline_height = 0 if footer else 5

        for line in text_lines:
            l, t, r, b = fnt.getbbox(line)
            height += b - t + interline_height;

        img = Image.new('RGB', (width, height), color="white")
        draw = ImageDraw.Draw(img)

        y = 0 if footer else 10
        for line in text_lines:
            draw.text((10, y), line, fill="black", font=fnt)
            y += b-t+interline_height

        return img
