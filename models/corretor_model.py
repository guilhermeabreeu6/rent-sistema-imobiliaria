"""Modelo de corretores utilizando o repositório em memória."""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from db.storage import EstatisticasCorretores, Record, repo


@dataclass
class Corretor:
    nome: str
    email: str
    telefone: Optional[str] = None
    creci: Optional[str] = None

    def salvar(self) -> bool:
        repo.criar_corretor(self.nome, self.email, self.telefone, self.creci)
        return True

    def atualizar(self, corretor_id: int) -> bool:
        repo.atualizar_corretor(corretor_id, self.nome, self.email, self.telefone, self.creci)
        return True

    @staticmethod
    def listar_todos() -> List[Record]:
        return repo.listar_corretores()

    @staticmethod
    def buscar_por_id(corretor_id: int) -> Optional[Record]:
        return repo.obter_corretor(corretor_id)

    @staticmethod
    def excluir(corretor_id: int) -> bool:
        return repo.remover_corretor(corretor_id)

    @staticmethod
    def listar_imoveis(corretor_id: int) -> List[Record]:
        return repo.listar_imoveis_do_corretor(corretor_id)

    @staticmethod
    def estatisticas() -> EstatisticasCorretores:
        return repo.estatisticas_corretores()

    @staticmethod
    def email_existe(email: str) -> bool:
        return repo.email_corretor_existe(email)

    @staticmethod
    def creci_existe(creci: str) -> bool:
        if not creci:
            return False
        return repo.creci_existe(creci)
