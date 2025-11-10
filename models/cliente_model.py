"""Modelo de clientes utilizando o repositório em memória."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from db.storage import Record, repo


@dataclass
class Cliente:
    nome: str
    email: str
    telefone: str
    endereco: Optional[str] = None

    def salvar(self) -> bool:
        repo.criar_cliente(self.nome, self.email, self.telefone, self.endereco)
        return True

    def atualizar(self, cliente_id: int) -> bool:
        repo.atualizar_cliente(cliente_id, self.nome, self.email, self.telefone, self.endereco)
        return True

    @staticmethod
    def listar_todos() -> List[Record]:
        return repo.listar_clientes()

    @staticmethod
    def buscar_por_id(cliente_id: int) -> Optional[Record]:
        return repo.obter_cliente(cliente_id)

    @staticmethod
    def excluir(cliente_id: int) -> bool:
        return repo.remover_cliente(cliente_id)

    @staticmethod
    def email_existe(email: str) -> bool:
        return repo.email_cliente_existe(email)

    @staticmethod
    def telefone_existe(telefone: str) -> bool:
        if not telefone:
            return False
        return repo.telefone_cliente_existe(telefone)

    @staticmethod
    def listar_interesses(cliente_id: int):
        from models.interesse_model import Interesse  # Import tardio para evitar ciclos

        return Interesse.listar_por_cliente(cliente_id)
