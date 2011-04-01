# TODO RENAME AND REFACTOR AND STUFF!!! THIS FILE SHOULD PROBABLY NOT EXIST BUT
# IN THE SPIRIT OF THE NULLSOFT: JUST DO IT.

import logging
from os import path
from spritecss import SpriteMap
from spritecss.css import CSSParser
from spritecss.finder import find_sprite_refs
from spritecss.config import CSSConfig

logger = logging.getLogger(__name__)

class SpriteDirsCategorizer(object):
    def __init__(self, sprite_dirs, recursive=True):
        self.sprite_dirs = sprite_dirs
        self.recursive = recursive
        self._maps = {}

    @classmethod
    def from_conf(cls, conf):
        # TODO Make recursion a configurable option.
        return cls(conf.sprite_dirs or [""])

    def _map_sprite_ref(self, sref):
        for sdir in self.sprite_dirs:
            prefix = path.commonprefix((sdir, sref.fname))
            if prefix == sdir:
                if self.recursive:
                    submap = path.dirname(path.relpath(sref.fname, sdir))
                    if submap:
                        return path.join(sdir, submap)
                return sdir
        raise ReferenceError

    def __call__(self, sprite):
        try:
            sdir = self._map_sprite_ref(sprite)
        except ReferenceError:
            logger.info("not mapping %r", sprite)
        else:
            smap = self._maps.setdefault(sdir, SpriteMap(sdir))
            smap.append(sprite)

    def __iter__(self):
        return self._maps.itervalues()

class SpriteMapCollector(object):
    """Collect spritemap listings from sprite references."""

    def __init__(self, conf=None):
        if conf is None:
            conf = CSSConfig()
        self.conf = conf
        self._maps = []

    def __iter__(self):
        return iter(self._maps)

    def collect_fname(self, fname):
        with open(fname, "rb") as fp:
            parser = CSSParser.read_file(fp)
            evs = list(parser.iter_events())
        conf = CSSConfig(evs, base=self.conf, root=path.dirname(fname))
        srefs = find_sprite_refs(evs, source=fname, conf=conf)
        categorizer = SpriteDirsCategorizer.from_conf(conf)
        for sref in srefs:
            categorizer(sref)
        self._maps.extend(categorizer)

def collect(fnames, conf=None):
    smaps = SpriteMapCollector(conf=conf)
    for fname in fnames:
        smaps.collect_fname(fname)
    return smaps

def print_sprite_maps(fnames):
    for smap in sorted(collect(fnames), key=lambda sm: sm.fname):
        print smap.fname
        for sref in smap:
            print "-", sref
        print

def main():
    import sys
    import logging

    logging.basicConfig(level=logging.DEBUG)

    fnames = sys.argv[1:]
    if not fnames:
        src_dir = path.join(path.dirname(__file__), "..")
        example_fn = "ext/Spritemapper/css/example_source.css"
        fnames = [path.normpath(path.join(src_dir, example_fn))]

    print_sprite_maps(fnames)

if __name__ == "__main__":
    main()
