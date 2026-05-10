"""Entry point: ``python -m wizards_castle``."""

from __future__ import annotations

import sys

from .game import main


if __name__ == "__main__":
    sys.exit(main())
