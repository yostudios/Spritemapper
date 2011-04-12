"""Box packing algorithm

This is a fairly dumb algorithm.

The gist of it is as follows:

1. Shuffle the list of all boxes
2. Take the summed area of all boxes and create a huge container
3. For every box, insert it into the huge container
5. If we're satisfied with the result, return it
5. Switch list position of two boxes, go to step 2

Insertion is where the action is at. This is a simple divide-and-conquer
algorithm, as follows:

1. If the current box has children, try to insert into each one
2. If the current box is childless, insert as one child and split the remaining
   space into two child rectangles
"""

import random
from .anneal import Annealer

class Rect(object):
    def __init__(self, rect=None, x1=None, y1=None, x2=None, y2=None):
        # calculate rect
        if rect:
            if not hasattr(rect, "x1"):
                kwds = dict(zip(("x1", "y1", "x2", "y2"), rect))
                rect = Rect(**kwds)
            if x1 is None: x1 = rect.x1
            if y1 is None: y1 = rect.y1
            if x2 is None: x2 = rect.x2
            if y2 is None: y2 = rect.y2

        (self.x1, self.y1, self.x2, self.y2) = (x1, y1, x2, y2)

    def __repr__(self):
        clsnam = type(self).__name__
        args = (clsnam, self.x1, self.y1, self.x2, self.y2,
                self.width, self.height)
        return "<%s %d,%d,%d,%d (%dx%d)>" % args

    pad_x, pad_y = 0, 0
    pad = property(lambda s: (s.pad_x, s.pad_y))

    width = property(lambda s: s.x2 - s.x1)
    height = property(lambda s: s.y2 - s.y1)
    position = property(lambda s: (s.x1, s.y1))
    area = property(lambda s: s.width * s.height)
    size = property(lambda s: (s.width, s.height))
    aspect = property(lambda s: float(s.width) / s.height)
    outer_width = property(lambda s: s.width + s.pad_x)
    outer_height = property(lambda s: s.height + s.pad_y)
    outer_area = property(lambda s: s.outer_width * s.outer_height)
    outer_size = property(lambda s: (s.outer_width, s.outer_height))

    def __eq__(self, other):
        """Check if *other* fits exactly inside *self*"""
        return (self.width == other.width and self.height == other.height)

    def fits(self, other):
        """Check if *other* fits inside *self*"""
        return (self.width >= (other.outer_width)
            and self.height >= (other.outer_height))

    @classmethod
    def from_size(cls, size):
        return cls((0, 0, size[0], size[1]))

class NoRoom(Exception):
    pass

class Node(object):
    def insert(self, rect):
        raise NoRoom

class BoxNode(Node, Rect):
    def insert(self, rect):
        # If we've got sub-nodes, they are responsible for allocating space.
        if hasattr(self, "children"):
            return self.insert_child(rect)
        # Otherwise we divy up and create child surfaces
        else:
            return self.insert_divide(rect)

    def insert_divide(self, rect):
        """Insert *rect* into self by splitting own area into suitably-sized
        children rect nodes.
        """
        # If there's no way rect can fit inside self, return early.
        if not self.fits(rect):
            raise NoRoom("rect does not fit")

        # If the rect is relatively wider, stack horizontally.
        if rect.aspect > self.aspect:
            # +----+----+
            # | r1 | r2 |  r1 + r2 = self
            # +----+----+
            used = BoxNode(self, x2=(self.x1 + rect.width + rect.pad_x))
            free = BoxNode(self, x1=used.x2)
        # If relatively taller, stack vertically.
        else:
            used = BoxNode(self, y2=(self.y1 + rect.height + rect.pad_y))
            free = BoxNode(self, y1=used.y2)

        used.rect = rect

        #: opaque is the consumed area
        # it differs from used in that it includes the padding
        opaque = OpaqueBoxNode(used, x2=(used.x1 + rect.width + rect.pad_x),
                                     y2=(used.y1 + rect.height + rect.pad_y))
        fragments = [opaque]
        if opaque.y2 < used.y2: # vertical remainder
            fragments.append(BoxNode(used, y1=opaque.y2, x2=opaque.x2))
        if opaque.x2 < used.x2: # horizontal remainder
            fragments.append(BoxNode(used, x1=opaque.x2, y2=opaque.y2))
        if opaque.y2 < used.y2 and opaque.x2 < used.x2: # diagonal remainder
            fragments.append(BoxNode(used, x1=opaque.x2, y1=opaque.y2))

        used.children = tuple(f for f in fragments if f.area)

        if free.area:
            self.children = (used, free)
        else:
            self.children = (used,)

        return opaque

    def insert_child(self, rect):
        """Insert *rect* into the first child that can take it."""
        for child in self.children:
            try:
                return child.insert(rect)
            except NoRoom:
                continue
        else:
            raise NoRoom("couldn't fit into any child")

class OpaqueBoxNode(BoxNode):
    def insert(self, rect):
        raise NoRoom("opaque box node")

class PackingAnnealer(Annealer):
    def __init__(self, boxes):
        # self.move, self.energy need not be set: the class methods are fine.
        self.boxes = boxes
        self.optimal_size = sum(b.outer_area for b in boxes)
        self.max_size = (sum(b.outer_width for b in boxes),
                         sum(b.outer_height for b in boxes))

    def move(self, state):
        a, b = random.sample(xrange(len(state)), 2)
        state[a], state[b] = state[b], state[a]

    def energy(self, state):
        placements = self._last_plcs = []
        w = h = 0
        # TODO Don't require arbitrarily sized box node for root
        tree = BoxNode.from_size(self.max_size)
        for idx in state:
            box = self.boxes[idx]
            node = tree.insert(box)
            node.box = box
            placements.append((node.position, box))
            w = max(w, node.x2)
            h = max(h, node.y2)
        self._last_size = (w, h)
        self._last_tree = tree
        return w * h

    def anneal(self, *a, **k):
        state, e = Annealer.anneal(self, range(len(self.boxes)), *a, **k)
        # Crops nodes to fit entire map exactly
        w, h = self._last_size
        def walk(n):
            n.x2 = min(n.x2, w)
            n.y2 = min(n.y2, h)
            if hasattr(n, "children"):
                n.children = tuple(walk(c) for c in n.children
                                   if c.x1 < w and c.y1 < h)
            return n
        walk(self._last_tree)
        return self._last_plcs, self._last_size

class PackedBoxes(object):
    def __init__(self, boxes, pad=(0, 0), anneal_steps=9200):
        self.pad = pad
        self.anneal_steps = anneal_steps
        self._anneal(boxes)
        self.__iter__ = self.placements.__iter__

    def _anneal(self, boxes):
        boxes = list(boxes)
        # TODO Find out whether sorting by box area is really a smart move.
        boxes.sort(key=lambda b: b.area)
        p = PackingAnnealer(boxes)
        (plcs, size) = p.anneal(800000, 1100, self.anneal_steps, 20)
        self.optimal_area = int(sum(b.outer_area for b in boxes))
        self.placements = plcs
        self.size = size
        self.tree = p._last_tree

    @property
    def area(self):
        return Rect.from_size(self.size).area

    @property
    def unused_area(self):
        return self.area - self.optimal_area

    @property
    def unused_amount(self):
        return float(self.unused_area) / self.area

def print_packed_size(packed, out=None):
    args = (packed.size + (packed.unused_amount * 100,))
    print >>out, "Packed size is %dx%d (%.3f%% empty space)" % args

def dump_placements(packed, out=None):
    for (pos, box) in packed.placements:
        box_desc = ",".join(map(str, box.calc_box(pos)))
        print >>out, "{0},{1}".format(box.fname, box_desc)
