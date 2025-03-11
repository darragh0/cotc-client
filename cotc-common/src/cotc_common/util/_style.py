import re
from enum import Enum
from typing import Final


class _LightFG(Enum):
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"


class _DarkFG(Enum):
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"


class FG:
    LIGHT: type[_LightFG] = _LightFG
    DARK: type[_DarkFG] = _DarkFG


class _LightBG(Enum):
    RED = "\033[101m"
    GREEN = "\033[102m"
    YELLOW = "\033[103m"
    BLUE = "\033[104m"
    MAGENTA = "\033[105m"
    CYAN = "\033[106m"
    WHITE = "\033[107m"


class _DarkBG(Enum):
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    WHITE = "\033[47m"


class BG:
    LIGHT: type[_LightBG] = _LightBG
    DARK: type[_DarkBG] = _DarkBG


class Style(Enum):
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    STRIKETHROUGH = "\033[9m"
    RESET = "\033[0m"


class Reset(Enum):
    FOREGROUND = "\033[39m"
    BACKGROUND = "\033[49m"
    BOLD = "\033[22m"
    ITALIC = "\033[23m"
    UNDERLINE = "\033[24m"
    STRIKETHROUGH = "\033[29m"
    ALL = "\033[0m"


_COLOR_MAP: Final[dict[str, Enum]] = {
    "flr": FG.LIGHT.RED,
    "flg": FG.LIGHT.GREEN,
    "fly": FG.LIGHT.YELLOW,
    "flb": FG.LIGHT.BLUE,
    "flm": FG.LIGHT.MAGENTA,
    "flc": FG.LIGHT.CYAN,
    "flw": FG.LIGHT.WHITE,
    "fdr": FG.DARK.RED,
    "fdg": FG.DARK.GREEN,
    "fdy": FG.DARK.YELLOW,
    "fdb": FG.DARK.BLUE,
    "fdm": FG.DARK.MAGENTA,
    "fdc": FG.DARK.CYAN,
    "fdw": FG.DARK.WHITE,
    "blr": BG.LIGHT.RED,
    "blg": BG.LIGHT.GREEN,
    "bly": BG.LIGHT.YELLOW,
    "blb": BG.LIGHT.BLUE,
    "blm": BG.LIGHT.MAGENTA,
    "blc": BG.LIGHT.CYAN,
    "blw": BG.LIGHT.WHITE,
    "bdr": BG.DARK.RED,
    "bdg": BG.DARK.GREEN,
    "bdy": BG.DARK.YELLOW,
    "bdb": BG.DARK.BLUE,
    "bdm": BG.DARK.MAGENTA,
    "bdc": BG.DARK.CYAN,
    "bdw": BG.DARK.WHITE,
}


def _italicize(txt: str) -> str:
    return re.sub(r"\*(.*?)\*", f"{Style.ITALIC.value}\\1{Reset.ITALIC.value}", txt)


def _embolden(txt: str) -> str:
    return re.sub(r"\*\*(.*?)\*\*", f"{Style.BOLD.value}\\1{Reset.BOLD.value}", txt)


def _underline(txt: str) -> str:
    return re.sub(r"_(.*?)_", f"{Style.UNDERLINE.value}\\1{Reset.UNDERLINE.value}", txt)


def _strike(txt: str) -> str:
    return re.sub(
        r"~(.*?)~", f"{Style.STRIKETHROUGH.value}\\1{Reset.STRIKETHROUGH.value}", txt
    )


def _apply_style(txt: str) -> str:
    """
    Apply ANSI styles to text using Markdown-like syntax.

    Supported Styles:
        **text** -> bold
        *text* -> italic
        _text_ -> underline
        ~text~ -> strikethrough

    Args:
        txt (str): Text to apply style(s) to.

    Returns:
        str: Text with style(s) applied.
    """

    return _strike(_underline(_italicize(_embolden(txt))))


def _apply_color(txt: str) -> str:
    """
    Apply ANSI color codes to text using tags defined in _COLOR_MAP.

    Supported Colors:
        red, green, yellow, blue, magenta, cyan, white.
        (can be either light or dark, and foreground or background).

    Args:
        txt (str): Text to apply color to.

    Returns:
        str: Text with color applied.
    """

    stack: list[tuple[str, str]] = []  # (tag, ansi_code)
    res: list[str] = []
    i: int = 0

    # Constants
    tag_len: int = 3  # Length of a color tag (e.g., "flr", "bdb")
    open_len: int = tag_len + 2  # <tag>
    close_len: int = tag_len + 3  # </tag>

    while i < len(txt):
        # Check for valid opening tag: <tag> where tag is in COLOR_MAP
        if (
            i + open_len <= len(txt)
            and txt[i] == "<"
            and txt[i + tag_len + 1] == ">"
            and txt[i + 1 : i + tag_len + 1].lower() in _COLOR_MAP
        ):
            tag: str = txt[i + 1 : i + tag_len + 1].lower()
            code: str = _COLOR_MAP[tag].value
            stack.append((tag, code))
            res.append(code)
            i += open_len

        # Check for valid closing tag: </tag> where tag is in COLOR_MAP
        elif (
            i + close_len <= len(txt)
            and txt[i : i + 2] == "</"
            and txt[i + tag_len + 2] == ">"
            and txt[i + 2 : i + tag_len + 2].lower() in _COLOR_MAP
        ):
            tag_close: str = txt[i + 2 : i + tag_len + 2].lower()

            # Find and remove the tag from the stack
            idx: int = -1
            for j, (tag, _) in enumerate(stack):
                if tag == tag_close:
                    idx = j
                    break

            if idx != -1:
                # Remove the tag from the stack
                stack.pop(idx)

                # Reset only the relevant color component (foreground or background)
                if tag_close.startswith("f"):
                    res.append(Reset.FOREGROUND.value)
                elif tag_close.startswith("b"):
                    res.append(Reset.BACKGROUND.value)

                # Reapply the remaining styles
                for _, code in stack:
                    res.append(code)

                i += close_len
            else:
                # If tag not found in stack, treat as regular text
                res.append(txt[i])
                i += 1

        # Regular character
        else:
            res.append(txt[i])
            i += 1

    return "".join(res)


def prettify(txt: str) -> str:
    """
    Prettify text with ANSI color codes and styles.

    Args:
        txt (str): Text to prettify.

    Returns:
        str: Prettified text.
    """

    return _apply_color(_apply_style(txt))
