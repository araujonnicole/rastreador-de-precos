import sqlite3
from datetime import datetime
from pathlib import Path

from src.scrapers.base import Produto

DB_PATH = Path(__file__).resolve().parents[2] / "precos.db"


def conectar() -> sqlite3.Connection:
    conexao = sqlite3.connect(DB_PATH)
    conexao.row_factory = sqlite3.Row
    return conexao


def criar_tabelas() -> None:
    conexao = conectar()
    try:
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS produtos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE
            )
            """
        )
        conexao.execute(
            """
            CREATE TABLE IF NOT EXISTS historico_precos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                produto_id INTEGER NOT NULL,
                preco REAL NOT NULL,
                data_coleta TEXT NOT NULL,
                FOREIGN KEY (produto_id) REFERENCES produtos (id)
            )
            """
        )
        conexao.commit()
    finally:
        conexao.close()


def salvar_preco(produto: Produto) -> None:
    conexao = conectar()
    try:
        cursor = conexao.execute(
            "SELECT id FROM produtos WHERE url = ?", (produto.url,)
        )
        linha = cursor.fetchone()

        if linha is None:
            cursor = conexao.execute(
                "INSERT INTO produtos (nome, url) VALUES (?, ?)",
                (produto.nome, produto.url),
            )
            produto_id = cursor.lastrowid
        else:
            produto_id = linha["id"]

        conexao.execute(
            "INSERT INTO historico_precos (produto_id, preco, data_coleta) "
            "VALUES (?, ?, ?)",
            (produto_id, produto.preco, datetime.now().isoformat(timespec="seconds")),
        )
        conexao.commit()
    finally:
        conexao.close()


def listar_historico(url: str) -> list[sqlite3.Row]:
    conexao = conectar()
    try:
        cursor = conexao.execute(
            """
            SELECT h.preco, h.data_coleta
            FROM historico_precos h
            JOIN produtos p ON p.id = h.produto_id
            WHERE p.url = ?
            ORDER BY h.id
            """,
            (url,),
        )
        return cursor.fetchall()
    finally:
        conexao.close()

def buscar_ultimo_preco(url: str) -> float | None:
    conexao = conectar()
    try:
        cursor = conexao.execute(
            """
            SELECT h.preco
            FROM historico_precos h
            JOIN produtos p ON p.id = h.produto_id
            WHERE p.url = ?
            ORDER BY h.id DESC
            LIMIT 1
            """,
            (url,),
        )
        linha = cursor.fetchone()
        return linha["preco"] if linha else None
    finally:
        conexao.close()