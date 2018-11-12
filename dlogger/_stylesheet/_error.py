import sys


class ParseError(ValueError):
    def __init__(self, msg, cause=None):
        super(ParseError, self).__init__(msg)

        self.cause = cause

    @classmethod
    def at_position(cls, text, position, msg, cause=None):
        prior_text = text[:position]
        line_number = prior_text.count("\n") + 1

        try:
            prior_newline = prior_text.rindex("\n")
        except ValueError:
            prior_newline = 0

        line_with_error = text[prior_newline + 1:]
        line_with_error = line_with_error[:line_with_error.index("\n")]
        column_number = position - prior_newline + 1

        around = line_with_error.strip()[:30]

        return cls(
            "Parsing error on line %d column %d, line begins with %r: %s" % (
                line_number, column_number, around, msg),
            cause)

    @classmethod
    def raise_with_cause(cls, text, position, msg):
        _, cause, stack = sys.exc_info()
        parse_error = cls.at_position(text, position, msg, cause)
        raise ParseError, parse_error, stack

    def __str__(self):
        result = super(ParseError, self).__str__()
        if self.cause:
            result += " (Caused by %r)" % self.cause

        return result


# This is useful for manual tests, to ensure that the error message looks
# helpful and is well-formatted.
if __name__ == "__main__":
    import _default_stylesheet
    try:
        raise ValueError("A first error")
    except ValueError as err:
        ParseError.raise_with_cause(
            _default_stylesheet.DEFAULT_STYLESHEET,
            40,
            "Bad things occurred.")
