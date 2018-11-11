import collections
import re

import _general_lex


_NAME = "(?:[a-z]-|[a-z])*[a-z]"
_ELEMENT_NAME_RE = re.compile(r"\s*(?P<name>%s)" % _NAME, re.UNICODE)
_ATTRIBUTE_CONDITIONS_RE = re.compile(r"""
    \[
        (?P<name>%s)
        (?P<operator>~?=)
        (?P<value>(?:[0-9]+|"(?:[^"\\]|\\\w|\\\\|\\")*"))
    \]""" % _NAME, re.VERBOSE | re.UNICODE)
_END_OF_SELECTOR_RE = re.compile(r"\s*->\s*")
_STYLE_NAMES_RE = re.compile(r"(?:[a-z-]+\s*)+")
_END_OF_LINE_RE = re.compile(r";\s*")


LEXER_SPEC = {
    "element name": [
        (_ELEMENT_NAME_RE, "attribute conditions or ->"),
    ],
    "attribute conditions or ->": [
        (_ATTRIBUTE_CONDITIONS_RE, "attribute conditions or ->"),
        (_END_OF_SELECTOR_RE, "style names")
    ],
    "style names": [
        (_STYLE_NAMES_RE, "end of line (;)"),
    ],
    "end of line (;)": [
        (_END_OF_LINE_RE, "element name"),
    ],
}


_RE_TO_KIND = {
    _ELEMENT_NAME_RE: "element_name",
    _ATTRIBUTE_CONDITIONS_RE: "attribute_conditions",
    _END_OF_SELECTOR_RE: "end_of_selector",
    _STYLE_NAMES_RE: "style_names",
    _END_OF_LINE_RE: "end_of_line",
}


Token = collections.namedtuple("Token", ["kind", "match"])


def lex(text):
    tokens = _general_lex.simple_lex(
        text, LEXER_SPEC, "element name", "element name")
    for token in tokens:
        yield Token(kind=_RE_TO_KIND[token.re], match=token)
