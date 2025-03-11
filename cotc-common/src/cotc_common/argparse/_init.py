from __future__ import annotations

from argparse import SUPPRESS, Namespace
from typing import TYPE_CHECKING, Any

from cotc_common.argparse._parser import ArgParser
from cotc_common.util import ExitCode

if TYPE_CHECKING:
    from cotc_common.argparse._config import ArgParseConfig


def init_argparse(ap_cfg: ArgParseConfig) -> Namespace:
    """
    Initialize the argument parser with the given configuration.

    Args:
        ap_cfg (ArgParseConfig): The configuration for the parser.

    Returns:
        argparse.Namespace: Namespace of parsed arguments.
    """

    parser: ArgParser = ArgParser(
        prog=ap_cfg.program_name,
        description=ap_cfg.description,
        add_help=False,
    )

    has_h: bool = False
    for arg in ap_cfg.args:
        if arg.short_opt == "h":
            has_h = True

        if arg.type is bool:
            parser.add_argument(
                f"-{arg.short_opt}",
                f"--{arg.long_opt}",
                action="store_true" if arg.default is False else "store_false",
                help=arg.help,
            )
        else:
            parser.add_argument(
                f"-{arg.short_opt}",
                f"--{arg.long_opt}",
                metavar=arg.metavar,
                type=arg.type,
                default=arg.default,
                help=arg.help,
            )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=f"{ap_cfg.program_name} {ap_cfg.version}",
        help="Show program's version number and exit",
    )

    if has_h:
        parser.add_argument(
            "--help",
            action="help",
            default=SUPPRESS,
            help="Show this help message and exit",
        )
    else:
        parser.add_argument(
            "-h",
            "--help",
            action="help",
            default=SUPPRESS,
            help="Show this help message and exit",
        )

    args: Namespace = parser.parse_args()

    # Validate arguments (may be empty)
    for arg in ap_cfg.args:
        val: Any = getattr(args, arg.long_opt.replace("-", "_"))

        if isinstance(val, float) and val.is_integer():
            val = int(val)

        min_val: Any | None = arg.min
        max_val: Any | None = arg.max

        if (min_val is not None and val < min_val) or (
            max_val is not None and val > max_val
        ):
            parser.err(
                f"**<flc>--{arg.long_opt}</flc>** must be in range "
                f"[<fly>{min_val}</fly>, <fly>{max_val}</fly>] (got <fly>{val}</fly>)",
                ExitCode.INVALID_ARGS,
            )

    return args
