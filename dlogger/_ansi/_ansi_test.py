import unittest

import _stacker
import _codes


class TestAnsiPackage(unittest.TestCase):
    def test_passthrough(self):
        stacker = _stacker.AnsiCodeStacker()
        passthrough_text = "hello"

        self.assertEqual(stacker.text(passthrough_text), passthrough_text)

    def test_passthrough_unicode(self):
        stacker = _stacker.AnsiCodeStacker()
        passthrough_text = u"hello \U0001f603!"

        self.assertEqual(stacker.text(passthrough_text), passthrough_text)

    def test_single_push_pop(self):
        stacker = _stacker.AnsiCodeStacker()
        unstyled_text = "hello"

        with stacker.wrap_style(["blue"]):
            styled_text = stacker.text(unstyled_text)

            self.assertEqual(
                styled_text,
                (_codes.names_to_sequence(["blue"]) +
                    unstyled_text +
                    _codes.names_to_sequence(["reset"])))

            # This should be the same assertion, but ensures that
            # names_to_sequence is functioning properly (its output should be
            # very stable).
            self.assertEqual(
                styled_text,
                "\x1b[34mhello\x1b[0m")

        self.assertEqual(stacker.text(unstyled_text), unstyled_text)

    def test_single_push_pop_unicode(self):
        stacker = _stacker.AnsiCodeStacker()
        unstyled_text = u"hello \U0001f603!"

        with stacker.wrap_style(["blue"]):
            styled_text = stacker.text(unstyled_text)

            self.assertEqual(
                styled_text,
                (_codes.names_to_sequence(["blue"]) +
                    unstyled_text +
                    _codes.names_to_sequence(["reset"])))

            # This should be the same assertion, but ensures that
            # names_to_sequence is functioning properly (its output should be
            # very stable).
            self.assertEqual(
                styled_text,
                u"\x1b[34mhello \U0001f603!\x1b[0m")

        self.assertEqual(stacker.text(unstyled_text), unstyled_text)

    def test_multiple_push_pop(self):
        stacker = _stacker.AnsiCodeStacker()
        unstyled_text = "hello"

        with stacker.wrap_style(["blue"]):
            with stacker.wrap_style(["bold"]):
                styled_text = stacker.text(unstyled_text)

                self.assertEqual(
                    styled_text,
                    (_codes.names_to_sequence(["blue", "bold"]) +
                        unstyled_text +
                        _codes.names_to_sequence(["reset"])))

                # This should be the same assertion, but ensures that
                # names_to_sequence is functioning properly (its output should
                # be very stable).
                self.assertEqual(
                    styled_text,
                    "\x1b[34;1mhello\x1b[0m")

            popped_styled_text = stacker.text(unstyled_text)

            self.assertEqual(
                popped_styled_text,
                (_codes.names_to_sequence(["blue"]) +
                    unstyled_text +
                    _codes.names_to_sequence(["reset"])))

            # This should be the same assertion, but ensures that
            # names_to_sequence is functioning properly (its output should be
            # very stable).
            self.assertEqual(
                popped_styled_text,
                "\x1b[34mhello\x1b[0m")

        self.assertEqual(stacker.text(unstyled_text), unstyled_text)


if __name__ == "__main__":
    unittest.main()
