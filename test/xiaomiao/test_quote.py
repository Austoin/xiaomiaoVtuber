from importlib import import_module


def test_quote_module_imports_without_deprecated_path():
    module = import_module("xiaomiao.Quote")

    assert callable(module.get_image)
    assert callable(module.handle)
    assert module.QUOTE_IMAGE_PATH.name == "quote.png"


def test_wrap_text_splits_fixed_width():
    module = import_module("xiaomiao.Quote")

    assert module.wrap_text("abcdef", chars_per_line=2) == "ab\ncd\nef"
