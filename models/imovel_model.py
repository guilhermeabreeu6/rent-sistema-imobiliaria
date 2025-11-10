"""Modelo de imóveis utilizando o repositório em memória."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from db.storage import Record, repo


@dataclass
class Imovel:
    tipo: str
    endereco: str
    valor: float
    status: str = "disponivel"
    corretor_id: Optional[int] = None
    descricao: Optional[str] = None

    def salvar(self) -> bool:
        repo.criar_imovel(self.tipo, self.endereco, self.valor, self.status, self.corretor_id, self.descricao)
        return True

    def atualizar(self, imovel_id: int) -> bool:
        repo.atualizar_imovel(
            imovel_id,
            self.tipo,
            self.endereco,
            self.valor,
            self.status,
            self.corretor_id,
            self.descricao,
        )
        return True

    @staticmethod
    def listar_todos() -> List[Record]:
        return repo.listar_imoveis()

    @staticmethod
    def buscar_por_id(imovel_id: int) -> Optional[Record]:
        return repo.obter_imovel(imovel_id)

    @staticmethod
    def excluir(imovel_id: int) -> bool:
        return repo.remover_imovel(imovel_id)

    @staticmethod
    def buscar_por_status(status: str) -> List[Record]:
        return repo.listar_imoveis_por_status(status)
