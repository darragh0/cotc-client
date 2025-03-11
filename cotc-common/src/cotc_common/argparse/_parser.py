import re
import sys
from argparse import (
    ONE_OR_MORE,
    OPTIONAL,
    SUPPRESS,
    ArgumentError,
    ArgumentParser,
    ArgumentTypeError,
)
from gettext import ngettext
from typing import NoReturn

from cotc_common.util import ExitCode, prettify, print_err


class ArgParser(ArgumentParser):
    """
    Custom argument parser w/ improved functionality & formatting.
    """

    prog: str
    description: str

    def __init__(
        self,
        prog: str,
        description: str,
        add_help: bool,
    ):
        super().__init__(
            prog=prog,
            description=description,
            add_help=add_help,
        )

    def _match_argument(self, action, arg_strings_pattern):
        nargs_pattern = self._get_nargs_pattern(action)
        match = re.match(nargs_pattern, arg_strings_pattern)

        if match is None:
            nargs_errors = {
                None: "expected one argument",
                OPTIONAL: "expected at most one argument",
                ONE_OR_MORE: "expected at least one argument",
            }
            msg = nargs_errors.get(action.nargs)
            if msg is None:
                msg = (
                    ngettext(
                        "expected %s argument", "expected %s arguments", action.nargs
                    )
                    % action.nargs
                )
            msg += " for "
            if len(action.option_strings) == 1:
                msg += f"**<flc>{action.option_strings[0]}</flc>**"
            else:
                msg += f"**<flc>{action.option_strings[0]}</flc>**/**<flc>{action.option_strings[1]}</flc>**"

            self.err(msg, ExitCode.INVALID_ARGS)

        return len(match.group(1))

    def _get_value(self, action, arg_string):
        type_func = self._registry_get("type", action.type, action.type)
        if not callable(type_func):
            msg = f"{type_func} is not callable"
            raise ArgumentError(action, msg)

        try:
            result = type_func(arg_string)

        except ArgumentTypeError as err:
            msg = str(err)
            raise ArgumentError(action, msg)

        except (TypeError, ValueError):
            name = getattr(action.type, "__name__", repr(action.type))
            msg = f"invalid {name} value for "
            if len(action.option_strings) == 1:
                msg += f"**<flc>{action.option_strings[0]}</flc>**:"
            else:
                msg += f"**<flc>{action.option_strings[0]}</flc>**/**<flc>{action.option_strings[1]}</flc>**"

            msg += f": <fly>'{arg_string}'</fly>"
            self.err(msg, ExitCode.INVALID_ARGS)

        return result

    def parse_args(self, args=None, namespace=None):
        args, argv = self.parse_known_args(args, namespace)
        if argv:
            argv_str = ", ".join(["<fly>%s</fly>" % arg for arg in argv])
            msg = f"unexpected arg(s): {argv_str}"
            self.err(msg, ExitCode.INVALID_ARGS)
        return args

    def format_usage(self) -> str:
        return prettify(
            f"<flg>**Usage:**</flg> <flc>**{self.prog}** [OPTIONS] [FLAGS]</flc>"
        )

    def format_err(self, message: str) -> str:
        return f"<flr>**error:**</flr> {message}"

    def format_desc(self) -> str:
        return self.description

    def format_options(self) -> str:
        flags: list[str] = []
        options: list[str] = []

        option_str: str
        max_len: int = 0
        for action in self._actions:
            if len(action.option_strings) == 1:
                option_str = f"{action.option_strings[0]}"
            else:
                option_str = f"{action.option_strings[0]}, {action.option_strings[1]}"

            if action.nargs != 0:
                metavar = action.metavar or action.dest.upper()
                option_str += f" <{metavar}>"

            max_len = max(max_len, len(option_str))

        for action in self._actions:
            sub: int
            if len(action.option_strings) == 1:
                option_str = f"    **<flc>{action.option_strings[0]}</flc>**"
                sub = 15
            else:
                option_str = f"**<flc>{action.option_strings[0]}</flc>**, **<flc>{action.option_strings[1]}</flc>** "
                sub = 30

            option_str_len: int = len(option_str) - sub

            if action.nargs != 0:
                metavar = action.metavar or action.dest.upper()
                option_str += f"<fdc><{metavar}></fdc>"
                option_str_len += len(metavar) + 2

            padding = max_len - option_str_len + 5

            desc = action.help or ""
            if action.default is not None and action.default != SUPPRESS:
                desc += f" (default: <fly>{action.default}</fly>)"

            formatted_line = f"  {option_str}{' ' * padding}{desc}"

            if action.nargs == 0:
                flags.append(formatted_line)
            else:
                options.append(formatted_line)

        result: list[str] = []
        if flags:
            result.append("<flg>**Flags:**</flg>")
            result.extend(flags)
            result.append("")

        if options:
            result.append("<flg>**Options:**</flg>")
            result.extend(options)
            result.append("")

        return prettify("\n".join(result))

    def format_help(self) -> str:
        help_text: list[str] = []
        help_text.append(self.format_desc())
        help_text.append("")
        help_text.append(self.format_usage())
        help_text.append("")
        help_text.append(self.format_options())
        help_text.append("")
        return "\n".join(help_text)

    def err(self, message: str, exit_code: ExitCode) -> NoReturn:
        print_err(self.format_err(message), end="\n\n")
        print_err(self.format_usage(), end="\n\n")
        print_err(
            f"For more information, run **<flc>`{self.prog} --help`</flc>**",
        )
        sys.exit(exit_code)
