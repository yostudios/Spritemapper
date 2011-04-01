"""Pure-Python CSS parser - no dependencies!"""

# Copyright held by Yo Studios AB <opensource@yo.se>, 2011 
#
# Some kind of BSD license, contact above e-mail for more information on
# matters of licensing.

from .parser import CSSParser
from itertools import ifilter

__all__ = ["CSSParser", "iter_events", "iter_declarations"]

def iter_events(parser, lexemes=None, predicate=None):
    if lexemes and predicate:
        raise TypeError("specify either events or predicate, not both")
    elif lexemes:
        predicate = lambda e: e.lexeme in lexemes
    return ifilter(predicate, iter(parser))

def iter_declarations(parser, predicate=None):
    for event in iter_events(parser, lexemes=("declaration",)):
        decl = event.declaration
        parts = decl.split(":", 1)
        if len(parts) == 1:
            yield (parts[0], None)
        else:
            (prop, val) = map(str.strip, parts)
            yield (prop, val)
