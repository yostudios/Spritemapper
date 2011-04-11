from nose.tools import eq_
from spritecss import SpriteRef
from spritecss.config import CSSConfig
from spritecss.mapper import SpriteDirsMapper, mapper_from_conf

def test_default():
    rels = {"test/foo/bar.png": "test/foo",
            "test/foo/blah.png": "test/foo",
            "test/foo/quux/abc.png": "test/foo/quux",
            "test/foo.png": "test"}
    m = SpriteDirsMapper()
    for sfn, sm_fn in rels.iteritems():
        res = m(SpriteRef(sfn, source="test/file.css"))
        eq_(res, sm_fn)

def test_confed_default():
    conf = CSSConfig(root="test")
    rels = {"test/foo/bar.png": "test/foo.png",
            "test/foo/blah.png": "test/foo.png",
            "test/foo/quux/abc.png": "test/foo/quux.png",
            "test/foo.png": "test.png"}
    m = mapper_from_conf(conf)
    for sfn, sm_fn in rels.iteritems():
        res = m(SpriteRef(sfn, source="test/file.css"))
        eq_(res, sm_fn)

def test_confed_no_recurse():
    conf = CSSConfig(base={"recursive": False,
                           "sprite_dirs": "foo"}, root="test")
    rels = {"test/foo/bar.png": "test/foo.png",
            "test/foo/blah.png": "test/foo.png",
            "test/foo/quux/abc.png": "test/foo.png",
            "test/foo.png": None,
            "test.png": None}
    m = mapper_from_conf(conf)
    for sfn, sm_fn in rels.iteritems():
        res = m(SpriteRef(sfn, source="test/file.css"))
        eq_(res, sm_fn)

def test_confed_single_map():
    conf = CSSConfig(base={"output_image": "sm.png"}, root="test")
    sm_fn = "test/sm.png"
    sfns = ("test/foo/bar.png",
            "test/foo/blah.png",
            "test/foo/quux/abc.png",
            "test/foo.png")
    m = mapper_from_conf(conf)
    for sfn in sfns:
        res = m(SpriteRef(sfn, source="test/file.css"))
        eq_(res, sm_fn)
