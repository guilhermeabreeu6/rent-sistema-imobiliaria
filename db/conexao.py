"""Compatibilidade com a API original de conexão com o banco de dados.

A aplicação original utilizava o `mysql.connector`, porém o ambiente dos
exercícios não possui um servidor MySQL disponível.  Para manter a compatibilidade
com os scripts de teste existentes disponibilizamos aqui uma implementação bem
simples de conexão que consulta os dados do :mod:`db.storage`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Iterable, List, Optional

from db.storage import repo


@dataclass
class MemoryCursor:
    """Cursor que entende um subconjunto das queries utilizadas nos testes."""

    dictionary: bool = False
    _results: List[Dict[str, Any]] | List[tuple] | None = None

    def execute(self, query: str, params: Optional[Iterable[Any]] = None) -> None:
        normalized = " ".join(query.strip().lower().split())

        if normalized.startswith("describe clientes"):
            estrutura = [
                {
                    "Field": "id",
                    "Type": "INT",
                    "Null": "NO",
                    "Key": "PRI",
                    "Default": None,
                    "Extra": "auto_increment",
                },
                {
                    "Field": "nome",
                    "Type": "VARCHAR(100)",
                    "Null": "NO",
                    "Key": "",
                    "Default": None,
                    "Extra": "",
                },
                {
                    "Field": "email",
                    "Type": "VARCHAR(120)",
                    "Null": "NO",
                    "Key": "UNI",
                    "Default": None,
                    "Extra": "",
                },
                {
                    "Field": "telefone",
                    "Type": "VARCHAR(30)",
                    "Null": "YES",
                    "Key": "",
                    "Default": None,
                    "Extra": "",
                },
            ]
            self._results = estrutura if self.dictionary else [tuple(d.values()) for d in estrutura]
            return

        if normalized.startswith("select count(*) as total from clientes"):
            total = len(repo.listar_clientes())
            resultado = {"total": total}
            self._results = [resultado] if self.dictionary else [(total,)]
            return

        if normalized.startswith("select * from clientes"):
            clientes = [cliente.to_serializable() for cliente in repo.listar_clientes()]
            if self.dictionary:
                self._results = clientes
            else:
                campos = ["id", "nome", "email", "telefone", "endereco", "data_cadastro"]
                self._results = [tuple(cliente.get(campo) for campo in campos) for cliente in clientes]
            return

        raise NotImplementedError(
            "Comando não suportado pelo cursor em memória: %s" % query
        )

    def fetchall(self):
        return self._results or []

    def fetchone(self):
        resultados = self.fetchall()
        return resultados[0] if resultados else None

    def close(self):
        self._results = None


class MemoryConnection:
    def cursor(self, dictionary: bool = False) -> MemoryCursor:
        return MemoryCursor(dictionary=dictionary)

    def close(self):  # pragma: no cover - compatibilidade
        pass


def obter_conexao() -> MemoryConnection:
    """Retorna uma conexão em memória usada pelos scripts de teste."""

    return MemoryConnection()
