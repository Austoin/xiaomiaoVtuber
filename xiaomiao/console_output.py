import sys
from typing import TextIO


def configure_stream_for_safe_logging(stream: TextIO | object) -> None:
    reconfigure = getattr(stream, "reconfigure", None)
    if not callable(reconfigure):
        return

    reconfigure(errors="backslashreplace")


def configure_console_output() -> None:
    configure_stream_for_safe_logging(sys.stdout)
    configure_stream_for_safe_logging(sys.stderr)
