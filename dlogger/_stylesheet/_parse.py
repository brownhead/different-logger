import re
import sys

import _lex
import _error
from ..easy_repr import easy_repr


class StylesheetRule(object):
    class AttributeCondition(object):
        def __init__(self, attribute_name, operator, value):
            self.attribute_name = attribute_name

            self.operator = operator
            assert self.operator in ["~=", "="]

            if re.match("^[0-9]+$", value):
                if self.operator != "=":
                    raise ValueError(
                        "Operator must be '=' if value is numeric.")
                self.value = int(value)
            elif self.operator == "~=":
                self.value = re.compile(value[1:-1], re.UNICODE)
            else:  # operator == "="
                self.value = value[1:-1]

        def __repr__(self):
            return easy_repr(self)

    def __init__(self, element_name, attribute_conditions, style_codes):
        self.element_name = element_name
        self.attribute_conditions = attribute_conditions
        self.style_codes = style_codes

    def __repr__(self):
        return easy_repr(self)


def _parse_into_lines(text):
    lines = [[]]
    for token in _lex.lex(text):
        lines[-1].append(token)

        if token.kind == "end_of_line":
            lines.append([])

    return [line for line in lines if line]


def parse(text):
    lines = _parse_into_lines(text)

    rules = []
    for line in lines:
        line_to_consume = line[:]

        first_token = line_to_consume.pop(0)
        assert first_token.kind == "element_name"
        element_name = first_token.match.group("name")

        attribute_conditions = []
        while line_to_consume[0].kind == "attribute_conditions":
            token = line_to_consume.pop(0)
            try:
                attribute_condition = StylesheetRule.AttributeCondition(
                    attribute_name=token.match.group("name"),
                    operator=token.match.group("operator"),
                    value=token.match.group("value"))
            except Exception:
                ParsingError.raise_with_cause(
                    text,
                    token.match.start(0),
                    err.message)

            attribute_conditions.append(attribute_condition)

        assert line_to_consume.pop(0).kind == "end_of_selector"

        style_names_token = line_to_consume.pop(0)
        assert style_names_token.kind == "style_names"
        style_names = style_names_token.match.group(0).split()

        rules.append(
            StylesheetRule(element_name, attribute_conditions, style_names))

    return rules
