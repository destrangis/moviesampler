import time

import av

def time_format(secs):
    return time.strftime('%H:%M:%S', time.gmtime(secs))

class FrameGrabber:

    def __init__(self, video, progress=None):
        if progress is None:
            self.progress = self.progress_notify

        self.movie = av.open(str(video))
        self.file_size = self.movie.size
        self.bit_rate = self.movie.bit_rate

        self.vstream = self.movie.streams.video[0]
        self.astream = self.movie.streams.audio[0]
        self.fps = self.vstream.average_rate
        self.numframes = self.vstream.frames

        vsc = self.vstream.codec_context
        asc = self.astream.codec_context
        self.vcodec_info = (f"{vsc.type} {vsc.name} {vsc.width}x{vsc.height} {vsc.display_aspect_ratio} "
                       f"{vsc.format.name} {vsc.framerate} fps")
        self.acodec_info = (f"{asc.type} {asc.name} fsize: {asc.frame_size} {asc.rate}Hz")

        # a bit of 'magic' -- on some videos I've found that the stream doesn't
        # have a duration, but the container has. The container's duration is
        # in the AV_TIME_BASE time base (i.e. 1/1_000_000, according to libavformat's
        # source code.
        if self.vstream.duration:
            self.duration = float(self.vstream.duration * self.vstream.time_base)
        else:
            self.duration = float(self.movie.duration / 1_000_000)
        self.str_duration = time_format(self.duration)


    def progress_notify(self, nframe=None, extra="", end=False):
        if end or nframe is None:
            print(extra)
        else:
            percent = int(nframe * 100 / self.duration)
            print(f"{percent:3d}% {extra}\r", end="")


    def get_video_frames(self, numframes):
        ret = []
        skiptime = int(self.movie.duration/numframes)
        frames = self.movie.decode(self.vstream)
        for frametime in range(skiptime, self.movie.duration, skiptime):
            self.movie.seek(frametime)
            frame = next(frames)

            tframe = time_format(frame.time)
            self.progress(frame.time, tframe)
            ret.append( (frame.to_image(), tframe) )

        self.progress(extra=f"100% {self.str_duration}", end=True)
        return ret

    def close():
        self.movie.close()
