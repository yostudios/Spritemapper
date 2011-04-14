from spritecss.css import parser
from itertools import izip

def parser_events():
    p = iter(parser.CSSParser(data="sel { decl: val; }\n"))
    evs = [("selector", {"selector": "sel "}),
           ("whitespace", {"whitespace": " "}),
           ("declaration", {"declaration": "decl: val"}),
           ("whitespace", {"whitespace": " "}),
           ("block_end", {}),
           ("whitespace", {"whitespace": "\n"})]
    for got, expect in izip(p, evs):
        assert got.lexeme == expect[0]
        for k, ex_val in expect[1].iteritems():
            val = getattr(got, k)
            assert ex_val == val

def reprint(css):
    reprinted = "".join(parser.CSSParser(data=css).iter_print_css())
    assert css == reprinted
    return reprinted

def test_reprint_trivial():
    reprint(" ")
    reprint("@test;\n")
    reprint("@test\n{ x: y; }\n")
    reprint("@test foo { x: y; }\n")
    reprint("hello { world: foo; }\n")
    reprint("/* foo */bar{test:xxx;/*ee*/abc;;}\n")

def test_reprint_escapes():
    reprint(r's{decl:"\"hel\\lo\"";}')

def test_reprint_test_files():
    from os import path
    from glob import glob
    css_dirn = path.join(path.dirname(__file__), "test_css_files")
    for fn in glob(path.join(css_dirn, "*.css")):
        with open(fn, "rb") as fp:
            reprint(fp.read())
