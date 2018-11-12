import unittest

import _default_stylesheet
import _parse


class StylesheetPackageTest(unittest.TestCase):
	def test_default_parses(self):
		_parse.parse(_default_stylesheet.DEFAULT_STYLESHEET)



if __name__ == "__main__":
    unittest.main()
