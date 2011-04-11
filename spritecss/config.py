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
    def __init__(self, parser=None, base=None, root=None):
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
            return cls(CSSParser.from_file(fp), root=path.dirname(fname))

    def normpath(self, p):
        """Normalize a possibly relative path *p* to the root."""
        return path.normpath(path.join(self.root, p))

    @property
    def base_url(self):
        return self._data.get("base_url")

    @property
    def sprite_dirs(self):
        if "sprite_dirs" not in self._data:
            return
        sdirs = shlex.split(self._data["sprite_dirs"])
        return map(self.normpath, sdirs)

    @property
    def sprite_dir_urls(self):
        base = self.base_url
        sdirs = self.sprite_dirs
        if base and sdirs:
            return (urljoin(base, sdir) for sdir in sdirs)
    def is_mapping_recursive(self):
        return bool(self._data.get("recursive"))

    @property
    def padding(self):
        return self._data.get("padding", (1, 1))

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
