import argparse
import sys
import pathlib
import time
import re
import traceback

from . import version
from .framegrabber import FrameGrabber
from .imagecomposer import ImageComposer, DEFAULT_FRAME_HEIGHT

NUM_ROWS = 4
NUM_COLS = 3
DEFAULT_SUFFIX = "_thumbs"
GEOM_PATTERN = "(\d+)x(\d+)"

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


def cli_options(argv):
    p = argparse.ArgumentParser()
    p.add_argument("--version", "-v", action="version", version="%(prog)s " + version(),
                    help="Print the program's version")
    p.add_argument("--geometry", "-g", metavar="ROWSxCOLS", default=f"{NUM_ROWS}x{NUM_COLS}",
                   help=f"Number of rows and columns. Default {NUM_ROWS}x{NUM_COLS}")
    p.add_argument("--quiet", "-q", action="store_true", default=False,
                   help="Quiet operation. No progress indicator")
    p.add_argument("--output-dir", "-o", metavar="DIRECTORY", default=".", type=pathlib.Path,
                    help="Directory on which to create the sampler. "
                    "Defaults current working directory")
    p.add_argument("--suffix", "-s", metavar="SUFFIX", default=DEFAULT_SUFFIX,
                    help=f"Suffix for the output file name. Default is '{DEFAULT_SUFFIX}' "
                         "e.g. if the file is named movie1.mp4, the output file will be "
                         "movie1_thumbs.jpg")
    p.add_argument("--frame-height", "-f", metavar="HEIGHT", default=DEFAULT_FRAME_HEIGHT, type=int,
                    help="Height of the component videoframes, in pixels. The width will be calculated "
                         f"from the aspect ratio. Default {DEFAULT_FRAME_HEIGHT}")
    p.add_argument("videofile", nargs="*", type=pathlib.Path, help="Video file to process")
    return p.parse_args(argv)

def get_rows_cols(geometry):
    match = re.search(GEOM_PATTERN, geometry)
    if match:
        rows = int(match.group(1))
        cols = int(match.group(2))
        return rows, cols
    else:
        raise RuntimeError(f"Bad shape '{geometry}'. Must be ROWSxCOLS")

def process_video(movie, rows, cols, options):
    if options.quiet:
        progress = lambda *args, **kwargs: None
    else:
        progress = None

    movie_size = movie.stat().st_size
    fg = FrameGrabber(movie, progress)
    frames = fg.get_video_frames(cols*rows)
    fg.close()

    if frames:
        header = (f"{movie.name} [{human_size(movie_size)}] "
                  f"{fg.str_duration}  {fg.fps} fps {human_size(fg.bit_rate)}ps\n"
                  f"{fg.vcodec_info}\n"
                  f"{fg.acodec_info}")
        ic = ImageComposer(rows, cols, header, options.frame_height)
        grid_img = ic.build_grid(frames)
        outfile = options.output_dir / (movie.stem + options.suffix + ".jpg")
        grid_img.save(str(outfile))


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]

    opts = cli_options(argv)
    try:
        rows, columns = get_rows_cols(opts.geometry)
    except RuntimeError as err:
        print(err)
        return 1

    for movie in opts.videofile:
        try:
            process_video(movie, rows, columns, opts)
        except Exception as err:
            print(movie, err)
            traceback.print_exc()

    return 0

if __name__ == "__main__":
    sys.exit(main())
