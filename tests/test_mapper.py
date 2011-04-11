from attest import Tests, assert_hook
from spritecss import SpriteRef
from spritecss.config import CSSConfig
from spritecss.mapper import SpriteDirsMapper, mapper_from_conf

suite = Tests()

@suite.test
def test_default():
    m = SpriteDirsMapper()
    rels = {"test/foo/bar.png": "test/foo",
            "test/foo/blah.png": "test/foo",
            "test/foo/quux/abc.png": "test/foo/quux",
            "test/foo.png": "test"}
    for sfn, sm_fn in rels.iteritems():
      res = m(SpriteRef(sfn, source="test/file.css"))
      assert res == sm_fn, sfn

@suite.test
def test_confed_default():
    conf = CSSConfig(root="test")
    m = mapper_from_conf(conf)
    rels = {"test/foo/bar.png": "test/foo.png",
            "test/foo/blah.png": "test/foo.png",
            "test/foo/quux/abc.png": "test/foo/quux.png",
            "test/foo.png": "test.png"}
    for sfn, sm_fn in rels.iteritems():
      res = m(SpriteRef(sfn, source="test/file.css"))
      assert res == sm_fn, sfn

@suite.test
def test_confed_no_recurse():
    conf = CSSConfig(base={"recursive": False,
                           "sprite_dirs": "foo"}, root="test")
    m = mapper_from_conf(conf)
    rels = {"test/foo/bar.png": "test/foo.png",
            "test/foo/blah.png": "test/foo.png",
            "test/foo/quux/abc.png": "test/foo.png",
            "test/foo.png": None}
    for sfn, sm_fn in rels.iteritems():
        res = m(SpriteRef(sfn, source="test/file.css"))
        assert res == sm_fn, sfn

@suite.test
def test_confed_single_map():
    conf = CSSConfig(base={"output_image": "sm.png"}, root="test")
    m = mapper_from_conf(conf)
    sfns = ("test/foo/bar.png",
            "test/foo/blah.png",
            "test/foo/quux/abc.png",
            "test/foo.png")
    sm_fn = "test/sm.png"
    for sfn in sfns:
      res = m(SpriteRef(sfn, source="test/file.css"))
      assert res == sm_fn, sfn
