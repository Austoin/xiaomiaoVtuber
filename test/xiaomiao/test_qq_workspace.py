import asyncio
import sys
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "xiaomiao"))

from qq_workspace import (  # noqa: E402
    QQWorkspaceError,
    _default_project_root,
    _download_to_path,
    append_documents_to_agent_text,
    download_documents_from_raw_message,
    download_qq_document,
    extract_document_file_infos,
    has_document_file_segments,
    sanitize_filename,
)


class QQWorkspaceTests(unittest.TestCase):
    def test_default_project_root_supports_repo_and_flat_deploy_layouts(self):
        base = Path.cwd() / "deploy-layout-check"
        repo_file = base / "repo" / "xiaomiao" / "qq_workspace.py"
        flat_file = base / "flat" / "qq_workspace.py"

        self.assertEqual(_default_project_root(repo_file), (base / "repo").resolve())
        self.assertEqual(_default_project_root(flat_file), (base / "flat").resolve())

    def test_sanitize_filename_strips_paths_and_unsafe_chars(self):
        self.assertEqual(sanitize_filename("../合同?.PDF"), "合同.pdf")
        self.assertEqual(sanitize_filename(""), "document")

    def test_extract_document_file_infos_keeps_file_segments(self):
        raw = [
            {"type": "text", "data": {"text": "hi"}},
            {"type": "file", "data": {"name": "a.pdf", "url": "https://example.test/a.pdf"}},
        ]

        self.assertEqual(
            extract_document_file_infos(raw),
            ({"name": "a.pdf", "url": "https://example.test/a.pdf"},),
        )
        self.assertTrue(has_document_file_segments(raw))
        self.assertFalse(has_document_file_segments([{"type": "text", "data": {"text": "hi"}}]))

    def test_download_rejects_unsupported_extension(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaisesRegex(QQWorkspaceError, "unsupported document type"):
                asyncio.run(
                    download_qq_document(
                        url="https://example.test/a.exe",
                        filename="a.exe",
                        source="qq-private",
                        user_id=1,
                        chat_id=1,
                        workspace_root=Path(tmp_dir),
                    )
                )

    def test_download_rejects_private_direct_url(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaisesRegex(QQWorkspaceError, "private address"):
                asyncio.run(
                    download_qq_document(
                        url="http://127.0.0.1/a.pdf",
                        filename="a.pdf",
                        source="qq-private",
                        user_id=1,
                        chat_id=1,
                        workspace_root=Path(tmp_dir),
                    )
                )

    def test_download_rejects_redirect_to_private_url(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            dest = Path(tmp_dir) / "redirected.pdf"
            with _redirect_to_private_server(b"secret") as url:
                with self.assertRaisesRegex(QQWorkspaceError, "private address"):
                    _download_to_path(url, dest, 1024, allow_private=False)

            self.assertFalse(dest.exists())

    def test_download_allows_trusted_private_url_when_requested(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with _file_server(b"hello") as url:
                doc = asyncio.run(
                    download_qq_document(
                        url=url,
                        filename="a.pdf",
                        source="qq-group",
                        user_id=1,
                        chat_id=2,
                        workspace_root=Path(tmp_dir),
                        allow_private_url=True,
                    )
                )

            self.assertTrue(doc.path.is_file())
            self.assertEqual(doc.path.read_bytes(), b"hello")
            self.assertIn("downloads/qq/qq-group/2/", doc.relative_path)

    def test_download_raw_message_reports_missing_url(self):
        docs, failures = asyncio.run(
            download_documents_from_raw_message(
                raw_message=[{"type": "file", "data": {"name": "a.pdf"}}],
                source="qq-private",
                user_id=1,
                chat_id=1,
            )
        )

        self.assertEqual(docs, ())
        self.assertEqual(len(failures), 1)
        self.assertIn("no download url", failures[0].error)

    def test_append_documents_to_agent_text_points_at_markitdown(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            with _file_server(b"hello") as url:
                doc = asyncio.run(
                    download_qq_document(
                        url=url,
                        filename="a.pdf",
                        source="qq-group",
                        user_id=1,
                        chat_id=2,
                        workspace_root=Path(tmp_dir),
                        allow_private_url=True,
                    )
                )

            text = append_documents_to_agent_text("转成 markdown", (doc,))

        self.assertIn("转成 markdown", text)
        self.assertIn("markitdown_convert", text)
        self.assertIn(str(doc.path), text)
        self.assertIn("untrusted user data", text)


class _ServerContext:
    def __init__(self, data: bytes):
        self.data = data
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return f"http://127.0.0.1:{self.server.server_address[1]}/file.pdf"

    def __exit__(self, *_args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=1)

    def _handler(self):
        data = self.data

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *_args):
                return

        return Handler


def _file_server(data: bytes):
    return _ServerContext(data)


class _RedirectServerContext:
    def __init__(self, data: bytes):
        self.data = data
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), self._handler())
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)

    def __enter__(self):
        self.thread.start()
        return f"http://127.0.0.1:{self.server.server_address[1]}/redirect.pdf"

    def __exit__(self, *_args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=1)

    def _handler(self):
        data = self.data

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == "/redirect.pdf":
                    port = self.server.server_address[1]
                    self.send_response(302)
                    self.send_header(
                        "Location",
                        f"http://127.0.0.1:{port}/private.pdf",
                    )
                    self.end_headers()
                    return

                self.send_response(200)
                self.send_header("Content-Type", "application/pdf")
                self.send_header("Content-Length", str(len(data)))
                self.end_headers()
                self.wfile.write(data)

            def log_message(self, *_args):
                return

        return Handler


def _redirect_to_private_server(data: bytes):
    return _RedirectServerContext(data)


if __name__ == "__main__":
    unittest.main()
