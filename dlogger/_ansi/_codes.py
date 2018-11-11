_NAMES_TO_VALUES = {
    "reset": 0,
    "bold": 1,
    "faint": 2,
    "italic": 3,
    "underline": 4,
    "blink-slow": 5,
    "blink-fast": 6,
    "inverse": 7,
    "conceal": 8,
    "strike-through": 9,
    "font-default": 10,
    "font-1": 11,
    "font-2": 12,
    "font-3": 13,
    "font-4": 14,
    "font-5": 15,
    "font-6": 16,
    "font-7": 17,
    "font-8": 18,
    "font-9": 19,
    "fraktur": 20,
    "normal-intensity": 22,
    "no-italic": 23,
    "no-underline": 24,
    "no-blink": 25,
    "no-inverse": 27,
    "no-conceal": 28,
    "no-strike-through": 29,
    "black": 30,
    "red": 31,
    "green": 32,
    "yellow": 33,
    "blue": 34,
    "magenta": 35,
    "cyan": 36,
    "white": 37,
    "color-default": 39,
    "background-black": 40,
    "background-red": 41,
    "background-green": 42,
    "background-yellow": 43,
    "background-blue": 44,
    "background-magenta": 45,
    "background-cyan": 46,
    "background-white": 47,
    "background-default": 49,
    "frame": 51,
    "encircle": 52,
    "overline": 53,
    "no-frame": 54,
    "no-overline": 55,
    "bright-black": 90,
    "bright-red": 91,
    "bright-green": 92,
    "bright-yellow": 93,
    "bright-blue": 94,
    "bright-magenta": 95,
    "bright-cyan": 96,
    "bright-white": 97,
    "background-bright-black": 100,
    "background-bright-red": 101,
    "background-bright-green": 102,
    "background-bright-yellow": 103,
    "background-bright-blue": 104,
    "background-bright-magenta": 105,
    "background-bright-cyan": 106,
    "background-bright-white": 107,
}


CODES = frozenset(_NAMES_TO_VALUES.iterkeys())


def names_to_sequence(code_names):
    """Returns an ANSI escape sequence for coloring text.

    Given some code_names (see CODES) this function will return a
    string you can print to the terminal that will apply the given styles to
    any following text.

    Ex:

        print names_to_sequence(["red"]), "this text is red", \\
              names_to_sequence(["reset"]), "not anymore!"
    """
    codes = (str(_NAMES_TO_VALUES[code_name]) for code_name in code_names)
    return "\x1B[" + ";".join(codes) + "m"
