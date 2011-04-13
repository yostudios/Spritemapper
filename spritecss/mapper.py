import logging
from os import path
from spritecss import SpriteMap
from spritecss.config import CSSConfig

logger = logging.getLogger(__name__)

class BaseMapper(object):
    def __call__(self, sprite):
        try:
            dn = self._map_sprite_ref(sprite)
        except LookupError:
            return
        else:
            if self.translate:
                return self.translate(dn)
            else:
                return dn

    def map_reduced(self, srefs):
        "Sort *srefs* into dict with a lists of sprites for each spritemap."""
        smaps = {}
        for sref in srefs:
            fname = self(sref)
            smap = smaps.get(fname)
            if smap is None:
                smap = smaps[fname] = SpriteMap(fname)
            if sref not in smap:
                smap.append(sref)
        return smaps

class OutputImageMapper(BaseMapper):
    """Maps all sprites to a single output spritemap."""

    def __init__(self, fname, translate=None):
        self.fname = fname
        self.translate = translate

    @classmethod
    def from_conf(cls, conf):
        return cls(conf.output_image,
                   translate=conf.get_spritemap_out)

    def _map_sprite_ref(self, sref):
        return self.fname

class SpriteDirsMapper(BaseMapper):
    """Maps sprites to spritemaps by using the sprite directory."""

    def __init__(self, sprite_dirs=None, recursive=True, translate=None):
        if not sprite_dirs and not recursive:
            raise ValueError("must be recursive if no sprite_dirs are set")
        self.sprite_dirs = sprite_dirs
        self.recursive = recursive
        self.translate = translate

    @classmethod
    def from_conf(cls, conf):
        return cls(conf.sprite_dirs,
                   recursive=conf.is_mapping_recursive,
                   translate=conf.get_spritemap_out)

    def _map_sprite_ref(self, sref):
        if self.sprite_dirs is None:
            return path.dirname(sref.fname)

        for sdir in self.sprite_dirs:
            prefix = path.commonprefix((sdir, path.dirname(str(sref))))
            if prefix == sdir:
                if self.recursive:
                    submap = path.dirname(path.relpath(str(sref), sdir))
                    if submap:
                        return path.join(sdir, submap)
                return sdir

        raise LookupError

def mapper_from_conf(conf):
    if conf.output_image:
        assert not conf.is_mapping_recursive
        cls = OutputImageMapper
    else:
        cls = SpriteDirsMapper
    return cls.from_conf(conf)

class SpriteMapCollector(object):
    """Collect spritemap listings from sprite references."""

    def __init__(self, conf=None):
        if conf is None:
            conf = CSSConfig()
        self.conf = conf
        self._maps = {}

    def __iter__(self):
        return (self._maps[k] for k in self._maps if k is not None)

    @property
    def unmapped_spriterefs(self):
        return self.smaps.get(None, SpriteMap(None, []))

    def collect(self, smaps):
        for fname, smap in smaps.iteritems():
            if fname in self._maps:
                self._maps[fname].extend(smap)
            else:
                self._maps[fname] = SpriteMap(fname, smap)

        return [self._maps[k] for k in smaps if k is not None]

    def map_file(self, fname, mapper=None):
        """Convenience function to map the sprites of a given CSS file."""
        from spritecss.css import CSSParser
        from spritecss.finder import find_sprite_refs

        with open(fname, "rb") as fp:
            parser = CSSParser.read_file(fp)
            evs = list(parser.iter_events())

        conf = CSSConfig(evs, base=self.conf, fname=fname)
        srefs = find_sprite_refs(evs, source=fname, conf=conf)

        if mapper is None:
            mapper = SpriteDirsMapper.from_conf(conf)

        return self.map_sprite_refs(srefs, mapper=mapper)

def print_spritemaps(smaps):
    for smap in sorted(smaps, key=lambda sm: sm.fname):
        print smap.fname
        for sref in smap:
            print "-", sref
        print

def _map_and_print(fnames):
    smaps = SpriteMapCollector()
    for fname in fnames:
        smaps.map_file(fname)
    print_spritemaps(smaps)

def _map_fnames(fnames):
    import sys
    import json
    from . import SpriteRef

    smaps = SpriteMapCollector()
    mapper = SpriteDirsMapper()

    for fname in fnames:
        with sys.stdin if (fname == "-") else open(fname, "rb") as fp:
            (src_fname, srefs) = json.load(fp)

        srefs = [SpriteRef(sref, source=src_fname) for sref in srefs]
        smaps.collect(mapper.map_reduced(srefs))
        print >>sys.stderr, "mapped", len(srefs), "sprites in", src_fname

    json.dump([(smap.fname, map(str, smap)) for smap in smaps], sys.stdout, indent=2)

def main():
    import sys
    import logging

    logging.basicConfig(level=logging.DEBUG)
    fnames = sys.argv[1:]

    if all(fname.endswith(".css") for fname in fnames):
        _map_and_print(fnames)
    elif fnames:
        _map_fnames(fnames)
    else:
        src_dir = path.join(path.dirname(__file__), "..")
        example_fn = "ext/Spritemapper/css/example_source.css"
        _map_and_print([path.normpath(path.join(src_dir, example_fn))])

if __name__ == "__main__":
    main()
