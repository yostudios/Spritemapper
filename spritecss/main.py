import sys
import logging
import optparse
from os import path
from contextlib import contextmanager

from spritecss.css import CSSParser, print_css
from spritecss.config import CSSConfig
from spritecss.finder import find_sprite_refs
from spritecss.mapper import SpriteMapCollector, mapper_from_conf
from spritecss.packing import PackedBoxes, print_packed_size
from spritecss.packing.sprites import open_sprites
from spritecss.stitch import stitch
from spritecss.replacer import SpriteReplacer

logger = logging.getLogger(__name__)

# TODO CSSFile should probably fit into the bigger picture
class CSSFile(object):
    def __init__(self, fname, conf=None):
        self.fname = fname
        self.conf = conf

    @contextmanager
    def open_parser(self):
        with open(self.fname, "rb") as fp:
            yield CSSParser.read_file(fp)

    @classmethod
    def open_file(cls, fname, conf=None):
        with cls(fname).open_parser() as p:
            return cls(fname, conf=CSSConfig(p, base=conf, fname=fname))

    @property
    def mapper(self):
        return mapper_from_conf(self.conf)

    @property
    def output_fname(self):
        return self.conf.get_css_out(self.fname)

    def map_sprites(self):
        with self.open_parser() as p:
            srefs = find_sprite_refs(p, conf=self.conf, source=self.fname)
            return self.mapper.map_reduced(srefs)

class InMemoryCSSFile(CSSFile):
    def __init__(self, *a, **k):
        sup = super(InMemoryCSSFile, self)
        sup.__init__(*a, **k)
        with sup.open_parser() as p:
            self._evs = list(p)

    @contextmanager
    def open_parser(self):
        yield self._evs

def spritemap(css_fs, conf=None, out=sys.stderr):
    w_ln = lambda t: out.write(t + "\n")

    #: sum of all spritemaps used from any css files
    smaps = SpriteMapCollector(conf=conf)

    for css in css_fs:
        w_ln("mapping sprites in source %s" % (css.fname,))
        for sm in smaps.collect(css.map_sprites()):
            w_ln(" - %s" % (sm.fname,))

    sm_plcs = []
    for smap in smaps:
        with open_sprites(smap, pad=conf.padding) as sprites:
            w_ln("packing sprites in mapping %s" % (smap.fname,))
            packed = PackedBoxes(sprites, anneal_steps=conf.anneal_steps)
            print_packed_size(packed)
            sm_plcs.append((smap, packed.placements))

            w_ln("writing spritemap image at %s" % (smap.fname,))
            im = stitch(packed)
            with open(smap.fname, "wb") as fp:
                im.save(fp)

    replacer = SpriteReplacer(sm_plcs)
    for css in css_fs:
        w_ln("writing new css at %s" % (css.output_fname,))
        with open(css.output_fname, "wb") as fp:
            print_css(replacer(css), out=fp)

op = optparse.OptionParser()
op.add_option("--padding", type=int, default=1,
              help="Pixels of padding between sprites (default: 1)")
op.add_option("--in-memory", action="store_true",
              help="Keep CSS parsing results in memory")
op.add_option("--anneal", type=int, default=9200,
              help="Simulated anneal steps (default: 9200)")

def main():
    logging.basicConfig(level=logging.DEBUG)

    (opts, args) = op.parse_args()

    fnames = list(args)

    if not fnames:
        op.error("you must provide at least one css file")

    base = {"anneal_steps": opts.anneal}
    if opts.padding:
        base["padding"] = (opts.padding, opts.padding)

    if opts.in_memory:
        css_cls = InMemoryCSSFile
    else:
        css_cls = CSSFile

    conf = CSSConfig(base=base)
    spritemap([css_cls.open_file(fn, conf=conf) for fn in fnames], conf=conf)

if __name__ == "__main__":
    main()
