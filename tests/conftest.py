import pytest

from src.database import repository


@pytest.fixture
def banco_temporario(tmp_path, monkeypatch):
    """Faz o código usar um banco novo e vazio, só para este teste."""
    monkeypatch.setattr(repository, "DB_PATH", tmp_path / "teste.db")
    repository.criar_tabelas()