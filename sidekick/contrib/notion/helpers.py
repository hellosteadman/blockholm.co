from tempfile import NamedTemporaryFile
import ffmpeg


def create_poster(src):
    with NamedTemporaryFile(suffix='.png', delete=False) as dest:
        ffmpeg.input(src, ss=0).filter('thumbnail').filter(
            'scale',
            1680, -1
        ).output(
            dest.name,
            vframes=1
        ).overwrite_output().run()

    return dest.name
