from attest import Tests, assert_hook
from spritecss.css import parser
from itertools import izip, starmap

tokenizing = Tests()

def tokenizes_to(css, toks):
    got = list(parser.css_tokenize_data(css))
    expect = list(starmap(parser.Token, toks))
    for got_tok, exp_tok in izip(got, expect):
        assert got_tok == exp_tok

@tokenizing.test
def tokenize_comments():
    tokenizes_to("/*x*/\n",
                 [('comment_begin', '/*'),
                  ('char', 'x'),
                  ('comment_end', '*/'),
                  ('w', '\n')])

@tokenizing.test
def tokenize_block():
    tokenizes_to("q{a;b;}",
                 [('char', 'q'),
                  ('block_begin', '{'),
                  ('char', 'a'),
                  ('semicolon', ';'),
                  ('char', 'b'),
                  ('semicolon', ';'),
                  ('block_end', '}')])

@tokenizing.test
def tokenize_quoted():
    tokenizes_to(r'"x\\y"zw',
                 [('char', '"'),
                  ('char', 'x'),
                  ('char', '\\'),
                  ('char', 'y'),
                  ('char', '"'),
                  ('char', 'z'),
                  ('char', 'w')])

parsing = Tests()

@parsing.test
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

@parsing.test
def parse_n_print():
    reprint(" ")
    reprint("@test;\n")
    reprint("@test\n{ x: y; }\n")
    reprint("hello { world: foo; }\n")
    reprint("/* foo */bar{test:xxx;/*ee*/abc;;}\n")

suite = Tests([tokenizing, parsing])
