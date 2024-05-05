import sys
import pathlib
import time

from PIL import Image, ImageDraw, ImageFont
from .framegrabber import FrameGrabber

NUM_ROWS = 4
NUM_COLS = 3

def resize_image(frame, target_height, timestamp):
    #img = Image.fromarray(frame)
    img = frame
    width_percent = target_height / float(img.size[1])
    target_width = int(float(img.size[0]) * float(width_percent))
    resized_img = img.resize((target_width, target_height))

    # Create a Draw object for adding text to the image
    draw = ImageDraw.Draw(resized_img)

    font_path = "3270Condensed-Regular"
    font_size = 15
    fnt = ImageFont.truetype(font_path, font_size)

    # Get text size
    left, top, right, bottom = fnt.getbbox(timestamp)

    # Calculate text position in lower right corner
    text_x = target_width - right - left - 5  # Add some padding from the right edge
    text_y = 5  # Add some padding from the bottom edge

    # Draw the text with a black outline and white fill
    draw.text((text_x, text_y), timestamp, fill=(255, 255, 255), font=fnt, stroke_width=1, stroke_fill=(0, 0, 0))
    print(".", end="")
    return resized_img



def header_image(width, text):
    text_lines = [ l.strip() for l in text.split("\n") ]
    fnt = ImageFont.truetype("3270-Regular", 20)
    height = 25
    interline_height = 5
    for line in text_lines:
        l, t, r, b = fnt.getbbox(line)
        height += b - t + interline_height;
    hdr = Image.new('RGB', (width, height), color="white")
    draw = ImageDraw.Draw(hdr)
    y = 10
    for line in text_lines:
        draw.text((10, y), line, fill="black", font=fnt)
        y += b-t+interline_height
    return hdr



def build_grid(outpath, framelist, rows, columns, header_text):
    images = [resize_image(img, target_height=180, timestamp=tstamp) for img, tstamp in framelist]
    print()

    # Calculate dimensions of the grid
    num_images = len(images)
    num_cols = columns
    num_rows = num_images // num_cols
    if num_images % num_cols != 0:
        num_rows += 1

    # Calculate the width and height of the output image
    max_width = max(img.width for img in images)
    max_height = max(img.height for img in images)
    grid_width = max_width * num_cols + 2 * (num_cols - 1)
    grid_height = max_height * num_rows + 2 * (num_rows - 1)

    hdr = header_image(grid_width, header_text)
    hdr_width, hdr_height = hdr.size
    grid_height += hdr_height
    grid_image = Image.new('RGB', (grid_width, grid_height), color='white')
    grid_image.paste(hdr, (0, 0))

    # Paste each image into the grid
    for i, img in enumerate(images):
        print("+", end="")
        row = i // num_cols
        col = i % num_cols
        x = col * (max_width + 2)
        y = row * (max_height + 2) + hdr_height
        grid_image.paste(img, (x, y))

    print()
    # Save the grid image
    grid_image.save(str(outpath))


def human_size(size):
    units = ["KB", "MB", "GB", "TB"]
    n = size
    lastu = "bytes"
    for u in units:
        lastn = n
        n = n / 1024
        if n < 1:
            return "{0:.2f}{1}".format(lastn, lastu)
        lastu = u
    else:
        return "{0:.2f}{1}".format(n, lastu)


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    rows = NUM_ROWS
    cols = NUM_COLS

    if len(argv) < 1:
        print(f"use: {sys.argv[0]} movie")
        return 1

    movie = pathlib.Path(argv[0])
    movie_size = movie.stat().st_size
    fg = FrameGrabber(movie)
    frames = fg.get_video_frames(cols*rows)

    if frames:
        header = (f"{movie.name} [{human_size(movie_size)}] "
                  f"{fg.str_duration}  {fg.fps} fps {human_size(fg.bit_rate)}ps\n"
                  f"{fg.vcodec_info}\n"
                  f"{fg.acodec_info}")
        outfile = movie.parent / (movie.stem + ".jpg")
        build_grid(outfile, frames, rows=rows, columns=cols, header_text=header)
    return 0

if __name__ == "__main__":
    sys.exit(main())
