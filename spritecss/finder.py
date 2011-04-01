"""CSS sprite finder"""

import re
import logging
from os import path
from itertools import ifilter

from . import SpriteRef
from .css import CSSParser, iter_declarations
from .config import CSSConfig

logger = logging.getLogger(__name__)

bg_url_re = re.compile(r'url\([\'"]?(.*?)[\'"]?\)')

def _find_background_url(val):
    mo = bg_url_re.match(val)
    if not mo:
        raise LookupError(val)
    return mo.groups()[0]

def _bg_positioned(val):
    # TODO Improve detection of positioned backgrounds
    parts = val.split()
    if len(parts) >= 3:
        for p in parts[-2:]:
            if p in ("top", "center", "bottom", "right", "middle", "left"):
                return True
            elif p.endswith(("px", "%")):
                return True
    return False

def iter_background_urls(parser):
    bg_pred = lambda i: i[0] in ("background", "background-image")
    for (prop, val) in ifilter(bg_pred, iter_declarations(parser)):
        if _bg_positioned(val):
            continue
        try:
            yield _find_background_url(val)
        except LookupError:
            pass

def find_sprite_refs(parser, conf=None, source=None, root=None):
    if source and not root:
        root = path.dirname(source)
    elif root and not source:
        source = path.join(root, "sprites.css")
    else:
        raise TypeError("specify at least source or root")

    if conf is None:
        conf = CSSConfig(root=root)

    for bg_url in iter_background_urls(parser):
        sprite = conf.normpath(bg_url)
        yield SpriteRef(sprite, source=source)

def main():
    import sys
    import json
    for fname in sys.argv[1:]:
        with open(fname, "rb") as fp:
            print >>sys.stderr, "extracting from", fname
            parser = CSSParser.read_file(fp)
            srefs = map(str, find_sprite_refs(parser, source=fname))
            v = [fname, srefs]
            json.dump(v, sys.stdout, indent=2)

if __name__ == "__main__":
    main()
