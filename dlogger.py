# stdlib
import StringIO
import traceback
import sys
import logging
import string
import re
import time

class ColoredFormatter(string.Formatter):
    """Same as string.Formatter but ensures all replacements are colored.

    This also backports the zero-length field feature of Python 2.7 to Python
    2.6, so "Hello {} world!" will always be a valid format string.

    All replacements are sent through whatever function you provide as the
    `colorizer`. So if you formatted the string "Hello {} world!" with the
    value 2, and `colorizer` was set to a function that always returned the
    string "walnut", the result would be "Hello walnut world!".
    """

    # Matches zero length fields (fields with no name, ie: {})
    ZERO_LENGTH_RE = re.compile(r"(?P<open_braces>{+)}")

    def __init__(self, colorizer):
        self.colorizer = colorizer

    def convert_field(self, value, conversion):
        """Does any conversion required to render the field.

        This function is called to figure out what to replace a field with. For
        example, if the formatter is replacing {0} with 2, it will call this
        function with value set to 2, and conversion set to None, and will
        replace {0} with whatever we return. If the formatter is replacing
        {0!s} instead, conversion will be "s".
        """
        converted = string.Formatter.convert_field(self, value, conversion)
        return self.colorizer(converted)

    def parse(self, format_string):
        """Parses the format string into a useful iterable.

        The actual behavior of this function isn't super important. What's
        important is that it's called in order to parse the format string, so
        if we want to change the format string this is the time to do it. Here
        is where we take care of zero length strings.
        """
        # Scope hack to make a variable modifiable inside the below
        # function.
        count = [0]

        def repl(match):
            # If there is an odd number of open braces, then we know this is a
            # zero-length field. This is necessary because the way to escape an
            # open brace is by preceding it with an open brace. So {{{{}} does
            # not contain a zero length field and is instead rendered as two
            # open braces followed by a closing brace.
            if len(match.group("open_braces")) % 2 == 1:
                r = match.group("open_braces") + str(count[0]) + "}"
                count[0] += 1
                return r
            else:
                return match.group(0)

        # Replace any zero length field with a numbered field as appropriate
        # than pass it off to the parser.
        converted = self.ZERO_LENGTH_RE.sub(repl, format_string)
        return string.Formatter.parse(self, converted)


class ColoredPercentFormatter(object):
    """Same as ColoredFormatter but accepts percent style strings.

    Example of a percent style string: "George is a %s bear."
    """

    # This is a regular expression that should only capture valid fields in a
    # percent style string.
    FIELD_RE = re.compile(
        r"%"
        r"(\((?P<mapping_key>[^)]+)\))?"
        r"(?P<conversion_flags>[#0 +-]+)?"
        r"(?P<minimum_field_width>[0-9*]+)?"
        r"(?P<precision>\.[0-9*]+)?"
        r"(?P<length_modifier>[hlL])?"
        r"(?P<conversion_type>[diouxXeEfFgGcrs%])")

    def __init__(self, colorizer):
        self.colorizer = colorizer

    def _colorize_match(self, match):
        if match.group("conversion_type") == "%":
            return match.group(0)
        else:
            return self.colorizer(match.group(0))

    def format(self, format_string, *args, **kwargs):
        return self.FIELD_RE.sub(self._colorize_match, format_string) % (args or kwargs)


class DifferentFormatter(object):
    DEFAULT_STYLESHEET = {
        "default": [],
        "critical": [1, 31],  # bold red
        "error": [31],  # red
        "warning": [33],  # yellow
        "info": [],  # default
        "debug": [2],  # faint
        "argument": [34],  # blue
        "ignored_tb": [2],  # faint
        "tb_path": [34],  # blue
        "tb_lineno": [34],  # blue
        "tb_exc_name": [31],  # red
    }

    def __init__(self, format_string=None, stylesheet=None, percent_mode=False):
        self.stylesheet = self.DEFAULT_STYLESHEET.copy()
        if stylesheet is not None:
            self.stylesheet.update(stylesheet)

        self.percent_mode = percent_mode
        if self.percent_mode:
            self.formatter = ColoredPercentFormatter
            self.format_string = (
                u"%(levelname)-8s %(asctime)s %(filename)s:%(lineno)s] %(message)s")
        else:
            self.formatter = ColoredFormatter
            self.format_string = u"[{record.name}:{record.lineno}] {message}"


    @staticmethod
    def style_text(stylesheet, styles, base_styles, text):
        # Form up the sequences we'll use to color the text.
        ansify = lambda codes: u"\x1B[" + u";".join(map(str, [0] + codes)) + u"m"
        prefix = ansify(sum([stylesheet[i] for i in base_styles + styles], []))
        postfix = ansify(sum([stylesheet[i] for i in base_styles], []))

        return prefix + text + postfix

    def format(self, record):
        formatter = self.formatter(
            lambda arg: self.style_text(self.stylesheet, ["argument"], [record.levelname.lower()],
                                        arg))
        message = formatter.format(record.msg, *record.args)

        # TODO(brownhead): Make this configurable
        simple_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
        asctime = "%s,%03d" % (simple_time, record.msecs)

        if self.percent_mode:
            formatted = self.format_string % dict(message=message, asctime=asctime,
                                                  **record.__dict__)
        else:
            formatted = self.format_string.format(record=record, message=message,
                                                  asctime=asctime)

        formatted = self.style_text(self.stylesheet, [record.levelname.lower()], [], formatted)

        tb = self.format_traceback(record)
        if tb:
            formatted += u"\n" + tb

        return formatted

    @staticmethod
    def indent_text(text):
        lines = text.split("\n")
        processed = []
        for i in lines:
            processed.append("... " + i)

        return "\n".join(processed)

    def format_traceback(self, record):
        if not record.exc_info:
            return None

        dummy_file = StringIO.StringIO()
        traceback.print_exception(record.exc_info[0], record.exc_info[1], record.exc_info[2],
                                  file=dummy_file)
        tb = dummy_file.getvalue().strip()

        classnames = [record.levelname.lower()]
        if getattr(record, "exc_ignored", False):
            classnames.append("ignored_tb")

        tb = self.highlight_tb(tb, classnames)

        tb = self.indent_text(tb)

        return self.style_text(self.stylesheet, classnames, [], tb)

    def highlight_tb(self, tb, base_classnames):
        FILE_LINE_RE = re.compile(r'^  File (".+"), line ([0-9]+), in (.*)$',
                                  re.MULTILINE | re.UNICODE)
        def repl_file_line(match):
            return '  File {0}, line {1}, in {2}'.format(
                self.style_text(self.stylesheet, ["tb_path"], base_classnames, match.group(1)),
                self.style_text(self.stylesheet, ["tb_lineno"], base_classnames, match.group(2)),
                match.group(3)
            )

        FOOTER_LINE_RE = re.compile(r"^(\w+)(.*)$", re.MULTILINE | re.UNICODE)
        def repl_footer_line(match):
            return self.style_text(self.stylesheet, ["tb_exc_name"], base_classnames, 
                                   match.group(1)) + match.group(2)

        lines = tb.split("\n")
        if len(lines) < 2:
            return tb
        lines[-1] = FOOTER_LINE_RE.sub(repl_footer_line, lines[-1])
        tb = "\n".join(lines)

        tb = FILE_LINE_RE.sub(repl_file_line, tb)

        return tb


class FatalError(SystemExit, Exception):
    pass


class Logger(object):
    def __init__(self, logger):
        self.logger = logger

    def fatal(self, msg, *args, **kwargs):
        self.logger.error(msg, *args, **kwargs)
        raise FatalError()

    def log(self, lvl, msg, *args, **kwargs):
        extra = kwargs.pop("extra", {})
        extra["exc_ignored"] = kwargs.pop("exc_ignored", False)

        return self.logger.log(lvl, msg, *args, extra=extra, **kwargs)

    def error(self, msg, *args, **kwargs):
        return self.log(logging.ERROR, msg, *args, **kwargs)

    def warning(self, msg, *args, **kwargs):
        return self.log(logging.WARNING, msg, *args, **kwargs)

    def info(self, msg, *args, **kwargs):
        return self.log(logging.INFO, msg, *args, **kwargs)

    def debug(self, msg, *args, **kwargs):
        return self.log(logging.DEBUG, msg, *args, **kwargs)


def get_logger(name):
    return Logger(logging.getLogger(name))
