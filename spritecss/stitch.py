"""Builds a spritemap image from a set of sprites."""

from array import array
from itertools import izip, chain, repeat

from .image import Image

class StitchedSpriteNodes(object):
    """An iterable that yields the image data rows of a tree of sprite
    nodes. Suitable for writing to an image.
    """

    def __init__(self, root, bitdepth=8, planes=3):
        bc = "BH"[bitdepth > 8]
        self.root = root
        self.bitdepth = bitdepth
        self.planes = planes
        self._mkarray = lambda *a: array(bc, *a)

    def __iter__(self):
        return self.iter_rows(self.root)

    def _trans_pixels(self, num):
        return self._mkarray([0] * self.planes) * num

    def _pad_trans(self, rows, n):
        padded_rows = chain(rows, repeat(self._trans_pixels(n.width)))
        for idx, row in izip(xrange(n.height), padded_rows):
            yield row + self._trans_pixels(n.width - (len(row) / self.planes))

    def iter_empty_rows(self, n):
        return (self._trans_pixels(n.width) for i in xrange(n.height))

    def iter_rows_stitch(self, a, b):
        (rows_a, rows_b) = (self.iter_rows(a), self.iter_rows(b))
        if a.x1 == b.x1 and a.x2 == b.x2:
            return chain(rows_a, rows_b)
        elif a.y1 == b.y1 and a.y2 == b.y2:
            return (a + b for (a, b) in izip(rows_a, rows_b))
        else:
            raise ValueError("nodes %r and %r are not adjacent" % (a, b))

    def iter_rows(self, n):
        if hasattr(n, "children"):
            num_child = len(n.children)
            if num_child == 1:
                return self._pad_trans(self.iter_rows(*n.children), n)
            elif num_child == 2:
                return self.iter_rows_stitch(*n.children)
            else:
                # we can't sow together more than binary boxes because that would
                # entail very complicated algorithms :<
                raise ValueError("node %r has too many children" % (n,))
        elif hasattr(n, "box"):
            return self._pad_trans(n.box.im.pixels, n)
        else:
            return self.iter_empty_rows(n)

def stitch(packed, mode="RGBA", reusable=False):
    assert mode == "RGBA"  # TODO Support other modes than RGBA
    root = packed.tree
    bd = max(sn.im.bitdepth for (pos, sn) in packed.placements)
    meta = {"bitdepth": bd, "alpha": True}
    planes = 3 + int(meta["alpha"])

    pixels = StitchedSpriteNodes(root, bitdepth=bd, planes=planes)
    if reusable:
        pixels = list(pixels)
    return Image(root.width, root.height, pixels, meta)

def _pack_and_stitch(smap_fn, sprites, conf=None):
    import sys

    # pack boxes
    from .packing import PackedBoxes, dump_placements, print_packed_size
    print >>sys.stderr, "packing sprites for map", smap_fn
    packed = PackedBoxes(sprites)
    print_packed_size(packed, out=sys.stderr)
    dump_placements(packed)

    # write map
    img_fname = smap_fn + ".png"
    print >>sys.stderr, "writing spritemap image", img_fname
    im = stitch(packed)
    with open(img_fname, "wb") as fp:
        im.save(fp)

def main(fnames=None):
    import sys
    import json
    from .packing.sprites import open_sprites

    if not fnames:
        fnames = sys.argv[1:] or ["-"]

    for fname in fnames:
        with sys.stdin if (fname == "-") else open(fname, "rb") as fp:
            for (smap_fn, sprite_fns) in json.load(fp):
                with open_sprites(sprite_fns) as sprites:
                    _pack_and_stitch(smap_fn, sprites)

if __name__ == "__main__":
    main()
