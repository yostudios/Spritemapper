"""Pure-Python CSS parser - no dependencies!"""

# Copyright held by Yo Studios AB <opensource@yo.se>, 2011 
#
# Part of Spritemapper (https://github.com/yostudios/Spritemapper)
# Released under a MIT/X11 license

from .parser import CSSParser, print_css
from itertools import ifilter, imap

__all__ = ["CSSParser", "iter_events", "split_declaration",
           "print_css", "iter_declarations"]

def iter_events(parser, lexemes=None, predicate=None):
    if lexemes and predicate:
        raise TypeError("specify either events or predicate, not both")
    elif lexemes:
        predicate = lambda e: e.lexeme in lexemes
    return ifilter(predicate, iter(parser))

def split_declaration(decl):
    parts = decl.split(":", 1)
    if len(parts) == 1:
        return (parts[0], None)
    else:
        (prop, val) = parts
        return (prop, val)

def iter_declarations(parser, predicate=None):
    evs = iter_events(parser, lexemes=("declaration",))
    return imap(split_declaration, evs)
