# MovieSampler

Video file thumbnailer.

The following command line:

    moviesampler -g 3x3 -o img big_buck_bunny_720p_stereo.avi

Produces the image:

![big_buck_bunny_720p_stereo_thumbs.jpg](img/big_buck_bunny_720p_stereo_thumbs.jpg)

## Installing

The best way to install `moviesampler` is with `pipx`:

    pipx install moviesampler

This app depends on the packages [`PyAV`](https://github.com/PyAV-Org/PyAV) and [`Pillow`](https://pillow.readthedocs.io/en/stable/index.html). If you don't have the ffmpeg libraries, needed by `PyAV`, or imaging libraries for `Pillow`, you might need to install them. On a Debian-like system you should install the following:

    sudo apt-get install libtiff5-dev libjpeg8-dev libopenjp2-7-dev zlib1g-dev \
        libfreetype6-dev liblcms2-dev libwebp-dev tcl8.6-dev tk8.6-dev python3-tk \
        libharfbuzz-dev libfribidi-dev libxcb1-dev libavformat-dev libavcodec-dev \
        libavdevice-dev libavutil-dev libswscale-dev libswresample-dev libavfilter-dev



## Usage

Use the command `moviesampler --help` to see the options

## License

This project is released under the MIT License. The supplied [3270 font](https://github.com/rbanffy/3270font) files are licensed by its authors under terms specified on the [`LICENSE`](LICENSE) file.


