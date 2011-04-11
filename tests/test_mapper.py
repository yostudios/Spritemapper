from nose.tools import nottest, istest, eq_
from spritecss import SpriteRef
from spritecss.config import CSSConfig
from spritecss.mapper import mapper_from_conf

@nottest
def test_mapper(f):
    @istest
    def inner():
        (conf, rels) = f()
        mapper = mapper_from_conf(conf)
        source = (conf.root or "test") + "/file.css"
        for sfn, sm_fn in rels.iteritems():
            res = mapper(SpriteRef(sfn, source=source))
            assert res == sm_fn, ("%r should map to %r, got %r"
                                  % (sfn, sm_fn, res))
    return inner

@test_mapper
def test_default():
    rels = {"test/foo/bar.png": "test/foo.png",
            "test/foo/blah.png": "test/foo.png",
            "test/foo/quux/abc.png": "test/foo/quux.png",
            "test/foo.png": "test.png"}
    return (CSSConfig(), rels)

@test_mapper
def test_confed_default():
    rels = {"test/foo/bar.png": "test/foo.png",
            "test/foo/blah.png": "test/foo.png",
            "test/foo/quux/abc.png": "test/foo/quux.png",
            "test/foo.png": "test.png"}
    return (CSSConfig(root="test"), rels)

@test_mapper
def test_confed_no_recurse():
    conf = CSSConfig(base={"recursive": False,
                           "sprite_dirs": "foo"}, root="test")
    rels = {"test/foo/bar.png": "test/foo.png",
            "test/foo/blah.png": "test/foo.png",
            "test/foo/quux/abc.png": "test/foo.png",
            "test/foo.png": None,
            "test.png": None}
    return (conf, rels)

def test_confed_single_map():
    conf = CSSConfig(base={"output_image": "sm.png"}, root="test")
    sm_fn = "test/sm.png"
    sfns = ("test/foo/bar.png",
            "test/foo/blah.png",
            "test/foo/quux/abc.png",
            "test/foo.png")
    return (conf, dict((sfn, sm_fn) for sfn in sfns))
