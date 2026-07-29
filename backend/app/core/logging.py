"""Structured logging setup.

We use plain stdlib logging with a compact formatter that plays nicely with
container log collectors (json can be added later if needed).
"""
import logging
import sys


def setup_logging(level: str = "INFO") -> None:
    """Configure root logger. Idempotent — safe to call multiple times."""
    root = logging.getLogger()
    root.setLevel(level)

    # Remove any pre-existing handlers to avoid duplicate log lines.
    for handler in list(root.handlers):
        root.removeHandler(handler)

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)-8s %(name)s :: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    root.addHandler(handler)
