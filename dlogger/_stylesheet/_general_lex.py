import re


class LexingError(RuntimeError):
    def __init__(self, *args):
        return super(LexingError, self).__init__(*args)


def simple_lex_once(text, token_matchers):
    """Consumes one token from text.

    If two token matchers match the text, an error is raised.

    Returns (token, remaining_text), or (None, text) if not token was matched.
    """
    pending_tokens = []
    for regex in token_matchers:
        # Using match here (rather than search for example) is vital
        # because match ensures that the match occurs at the beginning of
        # the string.
        match = regex.match(text)
        if match:
            pending_tokens.append(match)

    if len(pending_tokens) >= 2:
        raise ValueError(
            "Two matchers matched the same input text, this means the lexer's "
            "language specification is faulty. You should file a bug with "
            "this package's maintainer.")
    elif not pending_tokens:
        return None, text
    assert len(pending_tokens) == 1

    token = pending_tokens[0]
    return token, text[len(token.group(0)):]


def simple_lex(text, spec, start_state, end_state):
    """Lexes text given the state machine provided in spec.

    Fairly simple lexing utility. Will error if the entirety of the text is
    not consumed. Will also error if more than one regular expression for a
    given state matches.

    Here's an example of the structure of spec for lexing a simple language that
    alternates between words and numbers separated by spaces, until a semicolon
    is discovered, wich restarts the pattern. So for example, "a 3 b" is valid,
    "a 3 b b" is invalid, but "a 3 b ; b" is valid.

    spec = {
        "word": {
            (re.compile(r"\s*[a-z]+"), "number"),
            (re.compile(r"\s*;"), "word"),
        },
        "number": {
            (re.compile(r"\s*[0-9]+""), "word"),
            (re.compile(r"\s*;"), "word"),
        }
    }

    Yields regular expression match objects.
    """
    state = start_state
    remaining = text
    while remaining or state != end_state:
        matchers = [matcher for matcher, next_state in spec[state]]
        token, remaining = simple_lex_once(remaining, matchers)
        if token is None:
            processed_text = text[:len(text) - len(remaining)]
            line_number = processed_text.count("\n")

            processed_line = processed_text[processed_text.rindex("\n"):]
            column_number = len(processed_line)

            snapshot = processed_line
            if len(snapshot) > 15:
                snapshot = snapshot[-15:] + "..."

            raise LexingError(
                "Error during lexing. Could not find \"%s\" on line %d, column"
                " %d (after %r)." % (
                    state, line_number, column_number, snapshot))

        state = next(
            next_state
            for matcher, next_state in spec[state]
            if matcher is token.re)

        yield token
