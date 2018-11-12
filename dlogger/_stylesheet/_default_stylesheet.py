DEFAULT_STYLESHEET = """\
levelname[levelname="INFO"] -> blue;
levelname[levelname="WARNING"] -> yellow;
levelname[levelname="ERROR"] -> red;
levelname[levelname="CRITICAL"] -> red underline;
line[levelname="DEBUG"] -> faint;
asctime -> faint;
filename -> green;
lineno -> green;
traceback-lineno -> blue;
traceback-indent -> faint;
traceback-path -> blue;
traceback-func -> blue;
traceback-header -> red;
message-field -> bright-blue;
"""
