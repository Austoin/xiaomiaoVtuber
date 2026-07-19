"""Static quality guards for the QQ adapter entry point."""

from __future__ import annotations

import ast
from pathlib import Path

MAIN_PATH = Path(__file__).resolve().parents[2] / "xiaomiao" / "main.py"


def _main_tree() -> ast.Module:
    return ast.parse(MAIN_PATH.read_text(encoding="utf-8"))


def test_exception_diagnostics_call_format_exc() -> None:
    tree = _main_tree()
    invalid_calls = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and node.func.id == "print"
        and any(
            isinstance(argument, ast.Attribute)
            and isinstance(argument.value, ast.Name)
            and argument.value.id == "traceback"
            and argument.attr == "format_exc"
            for argument in node.args
        )
    ]

    assert not invalid_calls, "异常诊断必须调用 traceback.format_exc()"


def test_exception_handlers_are_explicit() -> None:
    tree = _main_tree()
    bare_handlers = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ExceptHandler) and node.type is None
    ]

    assert not bare_handlers, "异常捕获必须显式限定异常类型"
