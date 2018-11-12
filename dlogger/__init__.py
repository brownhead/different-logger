# # stdlib
# import StringIO
# import traceback
# import sys
# import logging
# import string
# import re
# import time

# from _ansi._codes import names_to_sequence


# def _predicate_split(lst, predicate):
#     truthy = []
#     falsy = []
#     for i in lst:
#         if predicate(i):
#             truthy.append(i)
#         else:
#             falsy.append(i)

#     return truthy, falsy


# class SSSRule(object):
#     """Represents a Shitty Stylesheet rule.

#     Feel free to make your own type of rules. Duck typing is at play here, so just make sure you
#     have functions that look like should_apply and get_prefix.
#     """

#     LEGAL_STYLES = set(_ansify.ANSI_ESCAPE_CODES.iterkeys()) | {"@no-reset"}

#     # Matches an SSS selector that looks at class names (ex: "timestamp.timestamp-date")
#     CLASS_NAMES_RE = re.compile(r"^\*|([a-zA-Z_-]+)(\.[a-zA-Z_-]+)*$")

#     # Matches (and extracts information from) an SSS selector that looks at record attributes (ex:
#     # levelname(INFO)).
#     ATTRIBUTE_VALUE_RE = re.compile(
#         r"^~(?P<attribute_name>[a-zA-Z_-]+)\((?P<attribute_value>[a-zA-Z0-9_.-]+)\)$")

#     def __init__(self, selector, styles):
#         self.selector = selector
#         self.styles = styles

#         illegal_styles = set(self.styles) - self.LEGAL_STYLES
#         if illegal_styles:
#             raise ValueError(
#                 "Unknown styles found for selector %r: %r" % (
#                     self.selector, illegal_styles))

#     def should_apply(self, element, record):
#         """Returns True this rule applies to the current element.

#         `record` should be a logging.LogRecord object. `element` should be a
#         TextElement.
#         """
#         conditions = self.selector.split(":")
#         for condition in conditions:
#             if self.CLASS_NAMES_RE.match(condition):
#                 if (condition != "*" and
#                         not set(condition.split(".")).intersection(set(element.class_names))):
#                     return False
#             elif self.ATTRIBUTE_VALUE_RE.match(condition):
#                 match = self.ATTRIBUTE_VALUE_RE.match(condition)

#                 if match.group("attribute_name") not in record.__dict__:
#                     return False

#                 real_value = record.__dict__[match.group("attribute_name")]
#                 desired_value = type(real_value)(match.group("attribute_value"))
#                 if real_value != desired_value:
#                     return False
#             else:
#                 raise ValueError("Invalid condition {!r}.".format(condition))

#         return True

#     def get_prefix(self):
#         """Returns the text to prefix the selected text with.

#         This should return an ANSI escape sequence like one returned by ansify.
#         """
#         # Pull out any @no-reset directive
#         code_names, directives = _predicate_split(
#             self.styles, lambda i: not i.startswith("@"))

#         if "@no-reset" not in directives:
#             code_names.insert(0, "reset")

#         return _ansify.ansify(code_names)

#     @classmethod
#     def from_line(cls, line):
#         """Parses a line of SSS.

#         A line of SSS looks like

#             SELECTOR = STYLE [STYLE...]

#         For example:

#             timestamp.timestamp-date = blue bold
#         """
#         selector, styles_raw = line.split("=")
#         styles = styles_raw.split()
#         return cls(selector.strip(), styles)


# class TextElement(object):
#     """Represents a stylable piece of text.

#     Log messages are broken up into TextElements before being rendered. It is a simple tree
#     structure.
#     """

#     def __init__(self, parent, class_names, children):
#         self.parent = parent
#         self.class_names = class_names
#         self.children = children
#         if not isinstance(self.children, basestring):
#             for i in self.children:
#                 i.parent = self

#     def __repr__(self):
#         return "{}({!r}, {!r}, {!r})".format(
#             type(self).__name__,
#             self.parent,
#             self.class_names,
#             self.children)


# def render_text_element(element, record, rules, postfix=_ansify.ansify(["reset"])):
#     """A recursive function that returns styled text from a TextElement.

#     Pass it a TextElement, and a list of rules, and watch the colored text flow!
#     """
#     assert isinstance(element, TextElement)

#     prefix = []
#     for rule in rules:
#         if rule.should_apply(element, record):
#             prefix.append(rule.get_prefix())
#     prefix = "".join(prefix)

#     if isinstance(element.children, basestring):
#         text = element.children
#     else:
#         parts = []
#         for child in element.children:
#             parts.append(render_text_element(child, record, rules, prefix or postfix))
#         text = u"".join(parts)

#     return prefix + text + postfix


# # This is a regular expression that should only capture valid fields in a percent style string.
# SIMPLE_FIELD_RE = re.compile(
#     r"(%"
#     r"(?:\((?:[^)]+)\))?"
#     r"(?:[#0 +-]+)?"
#     r"(?:[0-9*]+)?"
#     r"(?:\.[0-9*]+)?"
#     r"(?:[hlL])?"
#     r"(?:[diouxXeEfFgGcrs%]))")


# FIELD_RE = re.compile(
#     r"%"
#     r"(\((?P<mapping_key>[^)]+)\))?"
#     r"(?P<conversion_flags>[#0 +-]+)?"
#     r"(?P<minimum_field_width>[0-9*]+)?"
#     r"(?P<precision>\.[0-9*]+)?"
#     r"(?P<length_modifier>[hlL])?"
#     r"(?P<conversion_type>[diouxXeEfFgGcrs%])")


# def percent_format_text_elements(format_string, args, parent, literal_class_names,
#                                  field_class_names):
#     """Does a percent style replacement (text % args) but properly forms TextElements.
#     """
#     result = []
#     for index, text in enumerate(SIMPLE_FIELD_RE.split(format_string)):
#         if not text: continue

#         # Even indexed items returned from split will always be non-matches (they don't match the
#         # regular expression) so we know that evenly indexed items are literals and odd indexed
#         # items are fields.
#         if index % 2 == 0:
#             result.append(TextElement(parent, literal_class_names, text))
#         else:
#             # This is a hacky and awkward way to handle positional arguments vs keyword ones
#             # (when args is a tuple we're in positional mode, otherwise in keyword mode).
#             if isinstance(args, tuple):
#                 # This'll grab the correct positional argument. We do a % format here instead of
#                 # just swapping it in to allow for format stuff to apply (ex: %-8s).
#                 replaced = text % (args[index / 2], )
#                 class_names = field_class_names
#             else:
#                 # Any unused keyword arugments in the dictionary are ignored so we don't have to
#                 # do anything to args (unlike above).
#                 replaced = text % args
#                 class_names = field_class_names + [FIELD_RE.match(text).group("mapping_key")]

#             result.append(TextElement(parent, class_names, replaced))

#     return result


# class DifferentFormatter(object):
#     DEFAULT_RULES = [SSSRule.from_line(i) for i in """
#         levelname:~levelname(INFO) = blue
#         levelname:~levelname(WARNING) = yellow
#         levelname:~levelname(ERROR) = red
#         levelname:~levelname(CRITICAL) = red underline
#         line:~levelname(DEBUG) = faint
#         asctime = faint
#         filename = green @no-reset
#         lineno = green @no-reset
#         traceback-lineno = blue
#         traceback-indent = faint
#         traceback-path = blue
#         traceback-func = blue
#         traceback-header = red
#         message-field = bright-blue
#     """.split("\n") if i.strip()]

#     def __init__(self, format_string=None, rules=None, no_default_rules=False):
#         self.format_string = (format_string or
#             u"%(levelname)-8s %(asctime)s %(filename)s:%(lineno)s] %(message)s")

#         self.rules = []
#         if not no_default_rules:
#             self.rules += self.DEFAULT_RULES
#         if rules is not None:
#             self.rules += rules

#     def format(self, record):
#         # TODO(brownhead): Make this configurable
#         simple_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(record.created))
#         record.asctime = "%s,%03d" % (simple_time, record.msecs)

#         # Make sure there's a value for message so that it can get properly replaced
#         record.message = ""
#         template_root = TextElement(None, ["top-line", "line"], [])
#         template_root.children = percent_format_text_elements(
#             self.format_string, record.__dict__, template_root, ["literal", "template-literal"],
#             ["field", "template-field"])

#         for i in template_root.children:
#             if "message" in i.class_names:
#                 i.children = percent_format_text_elements(
#                     record.msg, record.args, i, ["literal", "message-literal"],
#                     ["field", "message-field"])

#         # This will set the template root's parent correctly
#         log_root = TextElement(None, ["log"], [template_root])

#         traceback_root = None
#         if record.exc_info:
#             log_root.children.append(TextElement(log_root, ["literal"], "\n"))
#             log_root.children.append(TextElement(
#                 log_root, ["traceback"], self.prepare_tb_text_elements(record.exc_info)))
        
#         formatted = render_text_element(log_root, record, self.rules)

#         return formatted

#     @staticmethod
#     def indent_text(text):
#         lines = text.split("\n")
#         processed = []
#         for i in lines:
#             processed.append("... " + i)

#         return "\n".join(processed)

#     # Matches a file or footer line. We can't just trivially join the two regexes together
#     # because we need this one to have exactly one capturing group.
#     TB_SIMPLE_FILE_LINE_RE = re.compile(r'(^  File ".+", line [0-9]+, in .*$)', re.MULTILINE)
#     TB_FILE_LINE_RE = re.compile(r'^  File (".+"), line ([0-9]+), in (.*)$')

#     def prepare_tb_text_elements(self, exc_info):
#         # Create the actual traceback text
#         dummy_file = StringIO.StringIO()
#         traceback.print_exception(exc_info[0], exc_info[1], exc_info[2],
#                                   file=dummy_file)
#         tb_lines = dummy_file.getvalue().strip().split("\n")

#         # We want the whole traceback to be indented a bit with an ellipsis, so we just stick a
#         # copy of this element everywhere
#         indentation_element = TextElement(None, ["literal", "traceback-indent"], "... ")

#         # Put the header in first
#         result = [indentation_element, TextElement(None, ["traceback-header"], tb_lines[0] + "\n")]

#         # Go through every line between the footer and the header and try to pull out the lines of
#         # code.
#         for index, text in enumerate(self.TB_SIMPLE_FILE_LINE_RE.split("\n".join(tb_lines[1:-1]))):
#             if not text: continue

#             if index % 2 == 0:
#                 result += [
#                     indentation_element,
#                     TextElement(None, ["traceback-code"], "    " + text.strip() + "\n")]
#                 continue

#             file_line_match = self.TB_FILE_LINE_RE.match(text)
#             assert file_line_match
#             file_line_element = TextElement(
#                 None, ["traceback-line", "traceback-file-line"], [])
#             file_line_element.children = percent_format_text_elements(
#                 "  File %(traceback-path)s, line %(traceback-lineno)s, in %(traceback-func)s\n",
#                 {
#                     "traceback-path": file_line_match.group(1),
#                     "traceback-lineno": file_line_match.group(2),
#                     "traceback-func": file_line_match.group(3),
#                 },
#                 file_line_element, ["traceback-literal"], ["traceback-field"])
#             result += [indentation_element, file_line_element]

#         result += [
#             indentation_element, TextElement(None, ["traceback-footer"], tb_lines[-1])]

#         return result


# class FatalError(SystemExit, Exception):
#     pass


# class Logger(object):
#     def __init__(self, logger):
#         self.logger = logger

#     def fatal(self, msg, *args, **kwargs):
#         self.logger.error(msg, *args, **kwargs)
#         raise FatalError()

#     def log(self, lvl, msg, *args, **kwargs):
#         extra = kwargs.pop("extra", {})
#         extra["exc_ignored"] = kwargs.pop("exc_ignored", False)

#         return self.logger.log(lvl, msg, *args, extra=extra, **kwargs)

#     def error(self, msg, *args, **kwargs):
#         return self.log(logging.ERROR, msg, *args, **kwargs)

#     def warning(self, msg, *args, **kwargs):
#         return self.log(logging.WARNING, msg, *args, **kwargs)

#     def info(self, msg, *args, **kwargs):
#         return self.log(logging.INFO, msg, *args, **kwargs)

#     def debug(self, msg, *args, **kwargs):
#         return self.log(logging.DEBUG, msg, *args, **kwargs)


# def get_logger(name):
#     return Logger(logging.getLogger(name))
