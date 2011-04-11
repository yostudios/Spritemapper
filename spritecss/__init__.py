"""CSS spritemap extractor, builder and generator

spritecss.finder
  sifts through one or more CSS files, extracting the list of sprites used and
  to which spritemaps they map.

spritecss.builder.packer
  packs a set of boxes (sprites) into a larger box (a spritemap).

spritecss.builder.stitch
  stitches together a set of sprites and coordinates into a spritemap.

generator
  using a CSS file and a set of spritemaps, outputs a CSS file that replaces
  references to sprites that have been mapped.
"""

class SpriteMap(list):
    def __init__(self, fname, L=[]):
        self.fname = fname
        super(SpriteMap, self).__init__(L)

    def __hash__(self):
        return hash(self.fname)

    def __eq__(self, o):
        if hasattr(o, "fname"):
            return o.fname == self.fname
        return NotImplemented

class SpriteRef(object):
    """Reference to a sprite, existent or not."""

    def __init__(self, fname, source):
        self.fname = fname
        self.source = source

    def __str__(self):
        return self.fname

    def __repr__(self):
        return "SpriteRef(%r, source=%r)" % (self.fname, self.source)

    def __hash__(self):
        return hash(self.fname)

    def __eq__(self, o):
        if hasattr(o, "fname"):
            return o.fname == self.fname
        return NotImplemented

class MappedSpriteRef(SpriteRef):
    def __init__(self, fname, source, pos):
        super(MappedSpriteRef, self).__init__(fname, source)
        self.position = pos

    def __repr__(self):
        args = (self.fname, self.source, self.position)
        return "MappedSpriteRef(%r, source=%r, pos=%r)" % args
