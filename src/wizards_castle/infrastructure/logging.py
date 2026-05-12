"""Configuración de structlog: bonito en TTY, JSON en pipes/CI."""

from __future__ import annotations

import logging
import sys

import structlog


def configure(*, level: int = logging.INFO) -> None:
    """Configura structlog con renderer adecuado al stream."""
    is_tty = sys.stderr.isatty()
    processors: list[structlog.types.Processor] = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
    ]
    processors.append(
        structlog.dev.ConsoleRenderer(colors=is_tty)
        if is_tty
        else structlog.processors.JSONRenderer()
    )
    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(level),
        cache_logger_on_first_use=True,
    )
