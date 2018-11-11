import contextlib
import itertools

import _codes


class AnsiCodeStacker(object):
	def __init__(self):
		self._stack = []

	@contextlib.contextmanager
	def wrap_style(self, code_names):
		unknown_code_names = set(code_names) - _codes.CODES
		if unknown_code_names:
			raise ValueError("Unrecognized code names: %r" % unknown_code_names)

		code_names_tuple = tuple(code_names)
		self._stack.append(code_names_tuple)
		try:
			yield None
		finally:
			popped_tuple = self._stack.pop()

			# This should be pretty hard to trigger unless you're really trying
			# to do it.
			if popped_tuple is not code_names_tuple:
				raise RuntimeError(
					"A single AnsiCodeStacker instance's context managers are "
					"exiting out of order.")

	def text(self, text):
		if not self._stack:
			return text

		all_codes = itertools.chain.from_iterable(self._stack)
		return (
			_codes.names_to_sequence(all_codes) +
			text +
			_codes.names_to_sequence(["reset"]))
