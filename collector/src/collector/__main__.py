from typing import Never
import sys

from collector._app import App


def main() -> Never:
    sys.exit(App().run())
