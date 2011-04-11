"""Streaming CSS stylesheet parser

Why is it streaming? Because I could.

.. note:: This module is *not* designed to minify any CSS; you could in theory
          do it by passing the token stream through simple peephole filters.

The module is designed to be able to *manipulate CSS!*

Each parser is an iterable that generates *events*, which have one of the
following lexemes:

- "comment"
- "selector"
- "declaration"
- "block_end"
- "whitespace"
"""

import sys
from itertools import imap
from collections import deque

def bisect(v, midpoint):
    """Split ordered sequence *v* at the index *midpoint*."""
    return (v[:midpoint], v[midpoint:])

class EventStream(object):
    def __init__(self, events=None):
        if events is None:
            events = deque()
        self._events = events
        self._event = None

    def next(self):
        self._event = event = self._events.popleft()
        return event

    def iter_events(self):
        while True:
            while self._events:
                yield self._events.popleft()
            self._emit_events()
            if not self._events:
                break

    def push(self, event):
        self._events.append(event)

class OutOfTokens(Exception):
    """A lot like StopIteration: signals that the end of the input token stream
    has been reached.

    This is chiefly so that the for loops in _handle_* are exited and bubble up
    to `CSSParser._eval_once`.
    """

class Token(object):
    """A token from CSS code. Lexeme definitions:

    "char" : multiple
      a character without special meaning (this includes quotes and parentheses)

    "w" : multiple
      some form of whitespace, see str.isspace (note: contiguous whitespace may
      be accumulated into a single token in the future)

    "comment_begin"
      ``*/`` -- signals the start of a comment (will not happen inside of a
      comment, all tokens up until "comment_end" are emitted as "char")

    "comment_end"
      ``*/`` -- signals the end of a previously started comment (will not
      happen unless a prior comment_begin has happened.)

    "block_begin" : dumb
      ``{`` -- signals the beginning of a block

    "block_end" : dumb
      ``}`` -- signals the end of a block

    "semicolon" : dumb
      ``;`` -- signals end of a declaration

    "dumb" means "lexed as such without consideration for surrounding context"
    """

    __slots__ = ("lexeme", "value", "line_no", "col_no")

    def __init__(self, lexeme="char", value=None, line_no=None, col_no=None):
        self.lexeme = lexeme
        self.value = value
        self.line_no = line_no
        self.col_no = col_no

    def __repr__(self):
        clsname = type(self).__name__
        return ("%s(%r, %r, line_no=%r, col_no=%r)"
                % (clsname, self.lexeme, self.value,
                   self.line_no, self.col_no))

    def __eq__(self, other):
        if hasattr(other, "lexeme") and hasattr(other, "value"):
            return other.lexeme == self.lexeme and \
                    other.value == self.value
        return NotImplemented

def _bytestream(chunks):
    """Yield each byte of a set of chunks."""
    for chunk in chunks:
        for char in chunk:
            yield char

def _css_token_stream(chars):
    for char in chars:
        yield Token(value=char)
    yield Token(lexeme="eof")

def _css_tokenize_comments(toks):
    begin = None
    expect = None
    lexeme = None
    in_comment = False

    for tok in toks:
        if expect:
            if expect == tok.value:
                value = begin.value + tok.value
                yield Token(lexeme=lexeme, value=value)
                expect = begin = None
                if lexeme == "comment_begin":
                    in_comment = True
                elif lexeme == "comment_end":
                    in_comment = False
                continue
            else:
                # false alarm -- yield previous character and proceed
                yield begin
                expect = begin = None

        if in_comment:
            if tok.value == "*":
                begin = tok
                expect = "/"
                lexeme = "comment_end"
            else:
                tok.lexeme = "comment_char"
                yield tok
        elif tok.value == "/":
            begin = tok
            expect = "*"
            lexeme = "comment_begin"
        else:
            yield tok

def _css_tokenize_strings(toks):
    escaped = False
    expect = ""
    for tok in toks:
        if tok.lexeme != "char":
            pass
        elif expect:
            if not escaped and tok.value == expect:
                expect = ""
                tok.lexeme = "quote_end"
            else:
                tok.lexeme = "quote_char"
                if not escaped and tok.value == "\\":
                    escaped = True
                elif escaped:
                    escaped = False
        elif tok.value in ("'", '"'):
            expect = tok.value
            tok.lexeme = "quote_begin"

        yield tok

def _css_tokenizer_lvl1(chars):
    """Tokenize comment begin/end, block begin/end, colon, semicolon,
    whitespace.
    """

    toks = _css_token_stream(chars)
    toks = _css_tokenize_comments(toks)
    toks = _css_tokenize_strings(toks)

    _char_lexemes = {"{": "block_begin",
                     "}": "block_end",
                     ";": "semicolon",
                     "@": "at"}

    for tok in toks:
        if tok.lexeme == "char":
            tok.lexeme = _char_lexemes.get(tok.value, "char")
            if tok.lexeme == "char" and tok.value.isspace():
                tok.lexeme = "w"
        elif tok.lexeme in ("quote_begin", "quote_char",
                            "quote_end", "comment_char"):
            tok.lexeme = "char"
        yield tok

def _css_tokenizer_lineno(toks):
    """Tokenize and count line numbers. Yields states."""
    col_no = 1
    line_no = 1
    for tok in toks:
        tok.line_no = line_no
        tok.col_no = col_no
        yield tok
        if tok.lexeme == "w" and tok.value == "\n":
            col_no = 1
            line_no += 1
        else:
            col_no += 1

def css_tokenize(it):
    return _css_tokenizer_lineno(_css_tokenizer_lvl1(_bytestream(it)))

def css_tokenize_data(css):
    return css_tokenize([css])

class CSSParseState(object):
    """The state of the CSS parser."""

    __slots__ = ("handler", "prev", "counter",
                 "tokens", "token",
                 "selector", "declaration", "at_rule",
                 "comment", "whitespace")

    ## general
    # tokens: iterator over remaining tokens
    # token: current token
    # handler: current handler of parsed code

    ## interesting buffers
    # selector: current selector
    # declaration: current declaration
    # at_rule: current at rule

    ## uninteresting buffers
    # comment: comment buffer
    # whitespace: whitespace buffer

    def __init__(self, tokens, token=None, handler=None, counter=0, prev=None):
        self.token = token
        self.tokens = tokens
        self.handler = handler
        self.counter = counter
        self.prev = prev
        self.selector = ""
        self.declaration = ""
        self.at_rule = ""
        self.comment = ""
        self.whitespace = ""

    def __call__(self, data=None, **kwds):
        if data is not None:
            self.tokens = css_tokenize_data(data)
        self.update(**kwds)
        self.counter += 1
        return self

    def __iter__(self):
        return self.iter_tokens()

    def __repr__(self):
        pairs = ("%s=%r" % (s, getattr(self, s)) for s in self.__slots__)
        return "<%s %s>" % (type(self).__name__, ", ".join(pairs))

    @property
    def lexeme(self):
        return self.token.lexeme

    def sub(self, handler=None):
        return type(self)(self.tokens, token=self.token, handler=handler,
                          counter=self.counter, prev=self)

    def leave(self):
        return self.prev(token=self.token)

    def update(self, **kwds):
        for (nam, val) in kwds.iteritems():
            if nam not in self.__slots__:
                raise TypeError(nam)
            setattr(self, nam, val)

    def next(self):
        """Take the next token from the token stream and place it as the
        current `token`.

        If no tokens remain to be had, raises OutOfTokens and sets `token` to
        None.
        """
        try:
            self.token = tok = self.tokens.next()
        except StopIteration:
            self.token = None
            raise OutOfTokens
        else:
            return tok

    def iter_tokens(self, lexemes=None, predicate=None):
        """Yields current token, if its lexeme in `lexemes`, and churns the
        token stream until the predicate fails.

        Specify either `lexemes`, a sequence of lexemes to match, or
        `predicate`, a function to test each token. If neither are given, all
        tokens are yielded (including the current one.)
        """
        if lexemes and predicate:
            raise TypeError("specify either lexemes or predicate, not both")
        elif lexemes:
            predicate = lambda t: t.lexeme in lexemes
        elif not predicate:
            predicate = lambda t: True

        tok = self.token
        while predicate(tok):
            yield tok
            tok = self.next()

    @classmethod
    def from_chunks(cls, chunks, **kwds):
        """Set up a CSS parser state from iterable *chunks* which generates
        blocks of code.
        """
        return cls(tokens=css_tokenize(chunks), **kwds)

# {{{ event defs
class CSSParserEvent(object):
    __slots__ = ("state",)

    def __init__(self, state):
        self.state = state

class Selector(CSSParserEvent):
    lexeme = "selector"
    __slots__ = ("selector",)

    def __init__(self, state=None, selector=None):
        self.state = state
        self.selector = selector if selector else state.selector

class AtRule(CSSParserEvent):
    __slots__ = ("at_rule",)

    def __init__(self, state=None, at_rule=None):
        self.state = state
        self.at_rule = at_rule if at_rule else state.at_rule

class AtBlock(AtRule):
    lexeme = "at_block"

class AtStatement(AtRule):
    lexeme = "at_statement"

class Comment(CSSParserEvent):
    lexeme = "comment"
    __slots__ = ("comment",)

    def __init__(self, state=None, comment=None):
        self.state = state
        self.comment = comment if comment else state.comment

class Declaration(CSSParserEvent):
    lexeme = "declaration"
    __slots__ = ("declaration",)

    def __init__(self, state=None, declaration=None):
        self.state = state
        self.declaration = declaration if declaration else state.declaration

class BlockEnd(CSSParserEvent):
    lexeme = "block_end"

class Whitespace(CSSParserEvent):
    lexeme = "whitespace"
    __slots__ = ("whitespace")

    def __init__(self, state=None, whitespace=None):
        self.state = state
        self.whitespace = whitespace if whitespace else state.whitespace
# }}}

class CSSParser(EventStream):
    """An event stream of parser events."""

    def __init__(self, state=None, data=None):
        super(CSSParser, self).__init__()
        if not (state is None) ^ (data is None):
            raise TypeError("specify either state or data, not either or both")
        elif data:
            state = CSSParseState.from_chunks([data])
        self.state = state

    @classmethod
    def read_file(cls, fp, chunk_size=8192):
        return cls.from_iter(iter(lambda: fp.read(chunk_size), ""))

    @classmethod
    def from_iter(cls, it):
        return cls(CSSParseState.from_chunks(it))

    def __iter__(self):
        return self.iter_events()

    def _emit_events(self):
        try:
            while not self._events:
                self.state = self.evaluate()
        except OutOfTokens:
            return

    def iter_print_css(self, converter=None):
        """Iterator over printable the CSS code."""
        evs = self.iter_events()
        if converter:
            evs = imap(converter, evs)
        return iter_print_css(evs)

    def evaluate(self, st=None):
        if st is None:
            st = self.state
        if st.handler is None:
            h = self._handle_any
        else:
            h = st.handler
        st.next()
        new = h(st)
        if new is None:
            raise RuntimeError("invalid transition from %r" % (st,))
        return new

    def _handle_any(self, st):
        lex = st.lexeme
        if lex == "comment_begin":
            return st.sub(self._handle_comment)
        elif lex == "at":
            return st(handler=self._handle_at_rule)
        elif lex == "w":
            # must not advance token stream
            st = st.sub(self._handle_whitespace)
            return st.handler(st)
        elif lex == "char":
            return self._handle_selector(st)
        elif lex == "eof":
            return st(handler=self._handle_eof)

    def _handle_comment(self, st):
        for tok in st.iter_tokens(("char",)):
            st.comment += tok.value

        if st.lexeme == "comment_end":
            self.push(Comment(st))
            return st.leave()

    def _handle_selector(self, st):
        for tok in st.iter_tokens(("char", "w")):
            st.selector += tok.value

        lex = st.lexeme
        if lex == "block_begin":
            self.push(Selector(st))
            return st(handler=self._handle_declaration)
        elif lex == "comment_begin":
            return st.sub(self._handle_whitespace)

    def _handle_declaration(self, st):
        if not st.declaration:
            for tok in st.iter_tokens(("w",)):
                st.whitespace += tok.value
            if st.whitespace:
                self.push(Whitespace(st))
                st = st(whitespace="")

        for tok in st.iter_tokens(("char", "w")):
            st.declaration += tok.value

        lex = st.lexeme
        if lex == "semicolon":
            self.push(Declaration(st))
            return st(declaration="")
        elif lex == "comment_begin":
            return st.sub(self._handle_comment)
        elif lex == "block_end":
            # this happens when the last declaration isn't terminated properly
            # NOTE This is really invalid CSS, but we're nice people.
            if st.declaration:
                raise RuntimeError("unconsumed declaration in %r, "
                                   "missing semicolon?" % (st,))
                self.push(Declaration(st))
            self.push(BlockEnd(st))
            return st(handler=None, declaration="", selector="")
        elif lex == "w":
            return st.sub(self._handle_whitespace)

    def _handle_at_rule(self, st):
        for tok in st.iter_tokens(("char", "w")):
            st.at_rule += tok.value

        lex = st.lexeme
        if lex in ("block_begin", "semicolon"):
            if lex == "block_begin":
                self.push(AtBlock(st))
                return st(handler=self._handle_declaration, at_rule="")
            elif lex == "semicolon":
                self.push(AtStatement(st))
                return st(handler=None, at_rule="")
        elif lex == "comment_begin":
            return st.sub(self._handle_comment)

    def _handle_whitespace(self, st):
        for tok in st.iter_tokens(("w",)):
            st.whitespace += tok.value

        self.push(Whitespace(st))
        # because the current token is "unconsumed" (i.e. was not whitespace),
        # we need to ask the default handler what to return
        return self._handle_any(st.leave())

    def _handle_eof(self, st):
        raise IOError("cannot parse beyond end of file")

def iter_print_css(parser):
    for event in parser:
        if event.lexeme == "comment":
            yield "/*{0}*/".format(event.comment)
        elif event.lexeme == "selector":
            yield event.selector + "{"
        elif event.lexeme == "declaration":
            yield event.declaration + ";"
        elif event.lexeme == "block_end":
            yield "}"
        elif event.lexeme == "whitespace":
            yield event.whitespace
        elif event.lexeme == "at_block":
            yield "@%s{" % (event.at_rule,)
        elif event.lexeme == "at_statement":
            yield "@%s;" % (event.at_rule,)
        else:
            raise RuntimeError("unknown event %s" % (event,))

def print_css(parser, out=sys.stdout):
    """Print an event stream of CSS parser events."""
    for data in iter_print_css(parser):
        out.write(data)

def main():
    print_css(CSSParser.read_file(sys.stdin), out=sys.stdout)

if __name__ == "__main__":
    main()
