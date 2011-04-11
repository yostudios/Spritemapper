# TODO RENAME AND REFACTOR AND STUFF!!! THIS FILE SHOULD PROBABLY NOT EXIST BUT
# IN THE SPIRIT OF THE NULLSOFT: JUST DO IT.

import logging
from os import path
from spritecss.css import CSSParser, print_css
from spritecss.config import CSSConfig
from spritecss.finder import find_sprite_refs
from spritecss.mapper import SpriteMapCollector, SpriteDirsMapper
from spritecss.packing import PackedBoxes, print_packed_size
from spritecss.packing.sprites import open_sprites
from spritecss.stitch import stitch
from spritecss.replacer import SpriteReplacer

logger = logging.getLogger(__name__)

class CSSFile(object):
    def __init__(self, fname, evs, conf=None):
        self.fname = fname
        self.evs = list(evs)
        self.conf = CSSConfig(self.evs, base=conf, fname=fname)

    @classmethod
    def open_file(cls, fname, conf=None):
        with open(fname, "rb") as fp:
            return cls(fname, CSSParser.read_file(fp))

    @property
    def mapper(self):
        return SpriteDirsMapper.from_conf(self.conf)

    @property
    def output_fname(self):
        return self.conf.get_css_out(self.fname)

    def iter_sprite_refs(self):
        return find_sprite_refs(self.evs, conf=self.conf, source=self.fname)

def main():
    import sys
    import logging

    logging.basicConfig(level=logging.DEBUG)

    fnames = sys.argv[1:]
    if not fnames:
        src_dir = path.join(path.dirname(__file__), "..")
        example_fn = "htdocs/css/example_source.css"
        fnames = [path.normpath(path.join(src_dir, example_fn))]

    w_ln = lambda t: sys.stderr.write(t + "\n")

    conf = CSSConfig()
    css_fs = [CSSFile.open_file(fn, conf=conf) for fn in fnames]

    #: holds spritemaps that may be used from any number of css files
    smaps = SpriteMapCollector(conf=conf)

    for css in css_fs:
        w_ln("mapping sprites in source %s" % (css.fname,))
        css.spritemaps = smaps.map_sprite_refs(css.iter_sprite_refs(),
                                               mapper=css.mapper)
        for sm in css.spritemaps:
            w_ln(" - %s" % (sm.fname,))

    for smap in smaps:
        with open_sprites(smap, pad=conf.padding) as sprites:
            w_ln("packing sprites in mapping %s" % (smap.fname,))
            packed = PackedBoxes(sprites)
            print_packed_size(packed)
            smap.placements = packed.placements

            w_ln("writing spritemap image at %s" % (smap.fname,))
            im = stitch(packed)
            with open(smap.fname, "wb") as fp:
                im.save(fp)

    replacer = SpriteReplacer([(sm, sm.placements) for sm in smaps])
    for css in css_fs:
        w_ln("writing new css at %s" % (css.output_fname,))
        with open(css.output_fname, "wb") as fp:
            print_css(replacer(css), out=fp)

if __name__ == "__main__":
    main()
