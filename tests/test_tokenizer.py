from nose.tools import eq_
from spritecss.css import parser
from itertools import izip, starmap

def tokenizes_to(css, toks):
    got = list(parser.css_tokenize_data(css))
    expect = list(starmap(parser.Token, toks))
    for got_tok, exp_tok in izip(got, expect):
        eq_(got_tok, exp_tok)

def test_tokenize_comments():
    tokenizes_to("/*x*/\n",
                 [('comment_begin', '/*'),
                  ('char', 'x'),
                  ('comment_end', '*/'),
                  ('w', '\n')])

def test_tokenize_block():
    tokenizes_to("q{a;b;}",
                 [('char', 'q'),
                  ('block_begin', '{'),
                  ('char', 'a'),
                  ('semicolon', ';'),
                  ('char', 'b'),
                  ('semicolon', ';'),
                  ('block_end', '}')])

def test_tokenize_quoted():
    tokenizes_to(r'"x\\y"zw',
                 [('char', '"'),
                  ('char', 'x'),
                  ('char', '\\'),
                  ('char', '\\'),
                  ('char', 'y'),
                  ('char', '"'),
                  ('char', 'z'),
                  ('char', 'w')])
