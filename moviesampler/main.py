import sys
import pathlib
import time

from .framegrabber import FrameGrabber
from .imagecomposer import ImageComposer

NUM_ROWS = 4
NUM_COLS = 3

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
        grid_img = ImageComposer(rows, cols, header).build_grid(frames)
        outfile = movie.parent / (movie.stem + ".jpg")
        grid_img.save(str(outfile))
    return 0

if __name__ == "__main__":
    sys.exit(main())
