import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from console_output import configure_stream_for_safe_logging


class _MockStream:
    def __init__(self):
        self.calls = []

    def reconfigure(self, **kwargs):
        self.calls.append(kwargs)


class _PlainStream:
    pass


class ConsoleOutputTests(unittest.TestCase):
    def test_configure_stream_sets_backslashreplace_for_text_streams(self):
        stream = _MockStream()

        configure_stream_for_safe_logging(stream)

        self.assertEqual(stream.calls, [{"errors": "backslashreplace"}])

    def test_configure_stream_ignores_streams_without_reconfigure(self):
        stream = _PlainStream()

        configure_stream_for_safe_logging(stream)


if __name__ == "__main__":
    unittest.main()
