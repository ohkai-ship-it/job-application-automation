import builtins
import io
from unittest import mock

import pytest

from src.helper import cli


def run_cli(argv):
    return cli.main(argv)


def test_inspect_html_file_not_found(capsys):
    code = run_cli(["inspect-html", "--file", "does_not_exist.html"])
    captured = capsys.readouterr()
    assert code == 1
    assert "File not found" in captured.out


def test_inspect_html_happy_path(tmp_path, capsys):
    html = """
    <html><head><title>Test</title><script type="application/ld+json">{"@type":"JobPosting","title":"Engineer"}</script></head>
    <body>
        <h1>Header</h1>
        <div data-at="jobTitle">Software Engineer</div>
    </body></html>
    """
    f = tmp_path / "page.html"
    f.write_text(html, encoding="utf-8")
    code = run_cli(["inspect-html", "--file", str(f)])
    out = capsys.readouterr().out
    assert code == 0
    assert "Headers" in out
    assert "JSON-LD" in out


@mock.patch("requests.get")
def test_trello_auth_missing_credentials(mock_get, capsys):
    # Simulate empty env loader
    with mock.patch("src.utils.env.load_env"):
        with mock.patch("src.utils.trello.get_auth_params", return_value={"key": "", "token": ""}):
            code = run_cli(["trello-auth"]) 
            out = capsys.readouterr().out
            assert code == 1
            assert "Missing key/token" in out
            mock_get.assert_not_called()


@mock.patch("requests.get")
def test_trello_auth_success(mock_get, capsys):
    class Resp:
        status_code = 200
        def json(self):
            return {"fullName": "Tester", "username": "tester"}
    mock_get.return_value = Resp()
    with mock.patch("src.utils.env.load_env"):
        with mock.patch("src.utils.trello.get_auth_params", return_value={"key": "k", "token": "t"}):
            code = run_cli(["trello-auth"]) 
            out = capsys.readouterr().out
            assert code == 0
            assert "Success" in out


@mock.patch("requests.get")
def test_trello_inspect_missing_board(mock_get, capsys):
    with mock.patch("src.utils.env.load_env"):
        with mock.patch("src.utils.trello.get_auth_params", return_value={"key": "k", "token": "t"}):
            with mock.patch("src.utils.env.get_str", return_value=""):
                code = run_cli(["trello-inspect"]) 
                out = capsys.readouterr().out
                assert code == 1
                assert "Missing TRELLO_BOARD_ID" in out
                mock_get.assert_not_called()


@mock.patch("requests.get")
def test_trello_inspect_happy_path(mock_get, capsys):
    # Prepare responses for board, lists, labels
    class Resp:
        def __init__(self, data, status=200):
            self._data = data
            self.status_code = status
            self.text = "ok"
        def json(self):
            return self._data

    def side_effect(url, params=None, timeout=30):
        if "/boards/" in url and "/lists" not in url and "/labels" not in url and "/customFields" not in url:
            return Resp({"name": "Board", "url": "https://trello/board/1"})
        if url.endswith("/lists"):
            return Resp([{"name": "To Do", "id": "1"}, {"name": "Doing", "id": "2"}])
        if url.endswith("/labels"):
            return Resp([{"name": "Priority", "color": "red", "id": "l1"}])
        if url.endswith("/customFields"):
            return Resp([
                {"name": "Company", "type": "text", "id": "cf1"},
                {"name": "Status", "type": "list", "id": "cf2", "options": [{"value": {"text": "Active"}}, {"value": {"text": "Inactive"}}]}
            ])
        return Resp({}, status=404)

    mock_get.side_effect = side_effect

    with mock.patch("src.utils.env.load_env"):
        with mock.patch("src.utils.trello.get_auth_params", return_value={"key": "k", "token": "t"}):
            with mock.patch("src.utils.env.get_str", return_value="board123"):
                code = run_cli(["trello-inspect"]) 
                out = capsys.readouterr().out
                assert code == 0
                assert "Board:" in out
                assert "Lists (" in out
                assert "Labels (" in out
                assert "Custom Fields (" in out
