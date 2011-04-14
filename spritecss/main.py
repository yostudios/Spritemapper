import sys
import logging
import optparse
from os import path, access, R_OK
from itertools import ifilter
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
            def test_sref(sref):
                if not access(str(sref), R_OK):
                    logger.error("%s: not readable", sref); return False
                else:
                    logger.debug("%s passed", sref); return True
            return self.mapper.map_reduced(ifilter(test_sref, srefs))

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

    # Weed out single-image spritemaps (these make no sense.)
    smaps = [sm for sm in smaps if len(sm) > 1]

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
op.set_usage("%prog [opts] <css file(s) ...>")
op.add_option("-c", "--conf", metavar="INI",
              help="read base configuration from INI")
op.add_option("--padding", type=int, metavar="N",
              help="keep N pixels of padding between sprites")
op.add_option("-v", "--verbose", action="store_true",
              help="use debug logging level")
#op.add_option("--in-memory", action="store_true",
#              help="keep CSS parsing results in memory")
#op.add_option("--anneal", type=int, metavar="N", default=9200,
#              help="simulated anneal steps (default: 9200)")
op.set_default("in_memory", False)
op.set_default("anneal", None)

def main():
    (opts, args) = op.parse_args()

    logging.basicConfig(level=logging.DEBUG if opts.verbose else logging.INFO)

    if not args:
        op.error("you must provide at least one css file")

    if opts.in_memory:
        css_cls = InMemoryCSSFile
    else:
        css_cls = CSSFile

    base = {}

    if opts.conf:
        from ConfigParser import ConfigParser
        cp = ConfigParser()
        with open(opts.conf) as fp:
            cp.readfp(fp)
        base.update(cp.items("spritemapper"))
    if opts.anneal:
        base["anneal_steps"] = opts.anneal
    if opts.padding:
        base["padding"] = (opts.padding, opts.padding)

    conf = CSSConfig(base=base)
    spritemap([css_cls.open_file(fn, conf=conf) for fn in args], conf=conf)

if __name__ == "__main__":
    main()
