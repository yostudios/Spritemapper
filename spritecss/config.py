import shlex
from os import path
from itertools import imap, ifilter
from urlparse import urljoin
from .css import CSSParser, iter_events

def parse_config_stmt(line, prefix="spritemapper."):
    line = line.strip()
    if line.startswith(prefix) and "=" in line:
        (key, value) = line.split("=", 1)
        return (key[len(prefix):].strip(), value.strip())

def iter_config_stmts(data):
    return ifilter(None, imap(parse_config_stmt, data.splitlines()))

def iter_css_config(parser):
    for ev in iter_events(parser, lexemes=("comment",)):
        for v in iter_config_stmts(ev.comment):
            yield v

class CSSConfig(object):
    def __init__(self, parser=None, base=None, root=None, fname=None):
        if fname and root is None:
            root = path.dirname(fname)
        self.root = root
        self._data = dict(base) if base else {}
        if parser is not None:
            self._data.update(iter_css_config(parser))

    def __iter__(self):
        # this is mostly so you can go CSSConfig(base=CSSConfig(..))
        return self._data.iteritems()

    @classmethod
    def from_file(cls, fname):
        with open(fname, "rb") as fp:
            return cls(CSSParser.from_file(fp), fname=fname)

    def normpath(self, p):
        """Normalize a possibly relative path *p* to the root."""
        return path.normpath(path.join(self.root, p))

    def absurl(self, p):
        """Make an absolute reference to *p* from any configured base URL."""
        base = self.base_url
        if base:
            p = urljoin(base, p)
        return p

    @property
    def base_url(self):
        return self._data.get("base_url")

    @property
    def sprite_dirs(self):
        if "sprite_dirs" not in self._data:
            return
        elif self._data.get("output_image"):
            raise RuntimeError("cannot have sprite_dirs "
                               "when output_image is set")
        sdirs = shlex.split(self._data["sprite_dirs"])
        return map(self.normpath, sdirs)

    @property
    def output_image(self):
        if "output_image" in self._data:
            return self.normpath(self._data["output_image"])

    @property
    def is_mapping_recursive(self):
        rv = self._data.get("recursive")
        if rv and self._data.get("output_image"):
            raise RuntimeError("cannot have recursive spritemapping "
                               "when output_image is set")
        elif rv is None:
            return not self._data.get("output_image")
        else:
            return bool(rv)

    @property
    def padding(self):
        return self._data.get("padding", (1, 1))

    @property
    def anneal_steps(self):
        return int(self._data.get("anneal_steps", 9200))

    def get_spritemap_out(self, dn):
        "Get output image filename for spritemap directory *dn*."
        if "output_image" in self._data:
            return self.output_image
        return dn + ".png"

    def get_spritemap_url(self, fname):
        "Get output image URL for spritemap *fname*."
        return self.absurl(path.relpath(fname, self.root))

    def get_css_out(self, fname):
        "Get output image filename for spritemap directory *fname*."
        (dirn, base) = path.split(fname)
        if "output_css" in self._data:
            (base, ext) = path.splitext(base)
            names = dict(filename=fname, dirname=dirn,
                         basename=base, extension=ext)
            return self.normpath(self._data["output_css"].format(**names))
        else:
            return path.join(dirn, "sm_" + base)

def print_config(fname):
    from pprint import pprint
    from .css import CSSParser

    with open(fname, "rb") as fp:
        print "%s\n%s\n" % (fname, "=" * len(fname))
        pprint(dict(iter_css_config(CSSParser.read_file(fp))))
        print

def main():
    import sys
    map(print_config, sys.argv[1:])

if __name__ == "__main__":
    main()
