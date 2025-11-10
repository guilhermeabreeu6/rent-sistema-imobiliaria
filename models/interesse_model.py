"""Modelo de interesses utilizando o repositório em memória."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from db.storage import Record, repo


@dataclass
class Interesse:
    cliente_id: int
    imovel_id: int
    status_interesse: str = "Ativo"
    data_interesse: Optional[datetime] = None
    observacoes: Optional[str] = None

    def salvar(self) -> bool:
        repo.criar_interesse(self.cliente_id, self.imovel_id, self.status_interesse, self.observacoes)
        return True

    @staticmethod
    def listar_todos() -> List[Record]:
        return repo.listar_interesses()

    @staticmethod
    def listar_por_cliente(cliente_id: int) -> List[Record]:
        return repo.listar_interesses_por_cliente(cliente_id)

    @staticmethod
    def buscar_por_id(interesse_id: int) -> Optional[Record]:
        return repo.obter_interesse(interesse_id)

    @staticmethod
    def atualizar_status(interesse_id: int, novo_status: str) -> bool:
        return repo.atualizar_status_interesse(interesse_id, novo_status)

    @staticmethod
    def deletar(interesse_id: int) -> bool:
        return repo.remover_interesse(interesse_id)
