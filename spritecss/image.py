from . import png

# TODO Image class should abstract `pixels`
# TODO Image class shouldn't assume RGBA
class Image(object):
    def __init__(self, width, height, pixels, meta):
        self.width = width
        self.height = height
        self.pixels = pixels
        self._meta = meta

    @classmethod
    def load(cls, fo):
        r = png.Reader(fo)
        self = cls(*r.asRGBA())
        self.close = fo.close
        return self

    def save(self, fo):
        w = png.Writer(size=self.size, bitdepth=self.bitdepth)
        w.write(fo, self.pixels)

    @property
    def size(self):
        return (self.width, self.height)

    @property
    def bitdepth(self):
        return self._meta["bitdepth"]
