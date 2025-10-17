import os
from unittest import mock

from src.utils.trello import mask_secret, get_auth_params


def test_mask_secret_basic():
    assert mask_secret("abcdef", prefix=3) == "abc..."
    assert mask_secret("ab", prefix=3) == "***"
    assert mask_secret("", prefix=3) == ""


def test_get_auth_params_from_env(monkeypatch):
    with mock.patch.dict(os.environ, {"TRELLO_KEY": "key123", "TRELLO_TOKEN": "tok456"}, clear=True):
        # Prevent reading from disk
        import src.utils.trello as trello_mod
        monkeypatch.setattr(trello_mod, "load_env", lambda: True)
        auth = get_auth_params()
        assert auth.get("key") == "key123"
        assert auth.get("token") == "tok456"


def test_get_auth_params_missing(monkeypatch):
    with mock.patch.dict(os.environ, {}, clear=True):
        import src.utils.trello as trello_mod
        monkeypatch.setattr(trello_mod, "load_env", lambda: True)
        auth = get_auth_params()
        assert auth == {}
