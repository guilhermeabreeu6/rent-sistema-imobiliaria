"""In-memory data store used by the RENT demo application.

The original project was tightly coupled to a MySQL database which is not
available in the execution environment used for the exercises.  To make the
project fully testable we provide a small in-memory repository that mimics the
behaviour of the original database layer.  The repository stores data in plain
Python dictionaries and offers helper methods that are used by the models and
Flask views.

The goal of this module is not to be the most efficient storage engine, but to
provide deterministic data for the tests while keeping the public surface of
the original project intact.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from itertools import count
from threading import RLock
from typing import Dict, Iterable, List, Optional


class Record(dict):
    """Dictionary that also exposes its keys as attributes.

    The HTML templates in the project expect attribute style access while the
    API responses work with dictionary data.  Subclassing :class:`dict` keeps
    both behaviours available without forcing the rest of the code base to know
    about the underlying representation.
    """

    __slots__ = ()

    def __getattr__(self, item: str):
        try:
            return self[item]
        except KeyError as exc:  # pragma: no cover - mirrored behaviour
            raise AttributeError(item) from exc

    def copy(self):
        return Record(super().copy())

    def to_serializable(self) -> Dict:
        """Return a JSON serialisable representation of the record."""

        data = dict(self)
        for key, value in list(data.items()):
            if isinstance(value, datetime):
                data[key] = value.isoformat()
        return data


@dataclass(frozen=True)
class EstatisticasCorretores:
    total_corretores: int
    corretores_ativos: int
    total_imoveis: int
    imoveis_por_status: Dict[str, int]


class MemoryRepository:
    """Small thread-safe repository backed by Python dictionaries."""

    def __init__(self) -> None:
        self._lock = RLock()
        self._clientes: Dict[int, Record] = {}
        self._corretores: Dict[int, Record] = {}
        self._imoveis: Dict[int, Record] = {}
        self._interesses: Dict[int, Record] = {}

        self._cliente_ids = count(1)
        self._corretor_ids = count(1)
        self._imovel_ids = count(1)
        self._interesse_ids = count(1)

        self._popular_dados_iniciais()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _popular_dados_iniciais(self) -> None:
        """Create a handful of default records used on the homepage."""

        with self._lock:
            if self._corretores:
                # The repository was already seeded.
                return

            corretor = self._criar_corretor_interno(
                nome="Corretor Padrão",
                email="corretor@rent.dev",
                telefone="(63) 9 9999-0000",
                creci="CRECI-0000",
            )

            cliente = self._criar_cliente_interno(
                nome="Cliente Demo",
                email="cliente@rent.dev",
                telefone="(63) 9 8888-1111",
                endereco="Rua das Flores, 123 - Palmas/TO",
            )

            imovel = self._criar_imovel_interno(
                tipo="Apartamento",
                endereco="Avenida Tocantins, 456 - Palmas/TO",
                valor=320000.0,
                status="disponivel",
                corretor_id=corretor["id"],
                descricao="Apartamento mobiliado com 3 quartos",
            )

            self._criar_interesse_interno(
                cliente_id=cliente["id"],
                imovel_id=imovel["id"],
                status="Ativo",
                observacoes="Interesse criado automaticamente para demonstração",
            )

    def _next_id(self, counter: count) -> int:
        return next(counter)

    # ------------------------------------------------------------------
    # Cliente operations
    # ------------------------------------------------------------------
    def _criar_cliente_interno(
        self,
        nome: str,
        email: str,
        telefone: str,
        endereco: Optional[str] = None,
    ) -> Record:
        cliente_id = self._next_id(self._cliente_ids)
        record = Record(
            {
                "id": cliente_id,
                "nome": nome,
                "email": email,
                "telefone": telefone,
                "endereco": endereco,
                "data_cadastro": datetime.utcnow(),
            }
        )
        self._clientes[cliente_id] = record
        return record

    def criar_cliente(
        self,
        nome: str,
        email: str,
        telefone: str,
        endereco: Optional[str] = None,
    ) -> Record:
        with self._lock:
            if self.email_cliente_existe(email):
                raise ValueError("Email já cadastrado")
            if telefone and self.telefone_cliente_existe(telefone):
                raise ValueError("Telefone já cadastrado")
            return self._criar_cliente_interno(nome, email, telefone, endereco)

    def atualizar_cliente(
        self,
        cliente_id: int,
        nome: str,
        email: str,
        telefone: str,
        endereco: Optional[str] = None,
    ) -> Record:
        with self._lock:
            if cliente_id not in self._clientes:
                raise KeyError("Cliente não encontrado")

            for cid, cliente in self._clientes.items():
                if cid == cliente_id:
                    continue
                if cliente["email"].lower() == email.lower():
                    raise ValueError("Email já cadastrado para outro cliente")
                if telefone and cliente.get("telefone") and cliente["telefone"] == telefone:
                    raise ValueError("Telefone já cadastrado para outro cliente")

            record = self._clientes[cliente_id]
            record.update(
                {
                    "nome": nome,
                    "email": email,
                    "telefone": telefone,
                    "endereco": endereco,
                }
            )
            return record.copy()

    def remover_cliente(self, cliente_id: int) -> bool:
        with self._lock:
            if cliente_id not in self._clientes:
                return False
            # Também remover interesses associados
            for interesse_id in list(self._interesses):
                if self._interesses[interesse_id]["cliente_id"] == cliente_id:
                    del self._interesses[interesse_id]
            del self._clientes[cliente_id]
            return True

    def obter_cliente(self, cliente_id: int) -> Optional[Record]:
        with self._lock:
            cliente = self._clientes.get(cliente_id)
            return cliente.copy() if cliente else None

    def listar_clientes(self) -> List[Record]:
        with self._lock:
            return [cliente.copy() for cliente in sorted(self._clientes.values(), key=lambda c: c["id"])]

    def email_cliente_existe(self, email: str) -> bool:
        email_lower = email.lower()
        return any(cliente["email"].lower() == email_lower for cliente in self._clientes.values())

    def telefone_cliente_existe(self, telefone: str) -> bool:
        telefone = telefone or ""
        return any(cliente.get("telefone") == telefone for cliente in self._clientes.values())

    # ------------------------------------------------------------------
    # Corretor operations
    # ------------------------------------------------------------------
    def _criar_corretor_interno(
        self, nome: str, email: str, telefone: Optional[str], creci: Optional[str]
    ) -> Record:
        corretor_id = self._next_id(self._corretor_ids)
        record = Record(
            {
                "id": corretor_id,
                "nome": nome,
                "email": email,
                "telefone": telefone,
                "creci": creci,
                "data_cadastro": datetime.utcnow(),
            }
        )
        self._corretores[corretor_id] = record
        return record

    def criar_corretor(
        self, nome: str, email: str, telefone: Optional[str], creci: Optional[str]
    ) -> Record:
        with self._lock:
            if self.email_corretor_existe(email):
                raise ValueError("Email de corretor já cadastrado")
            if creci and self.creci_existe(creci):
                raise ValueError("CRECI já cadastrado")
            return self._criar_corretor_interno(nome, email, telefone, creci)

    def atualizar_corretor(
        self,
        corretor_id: int,
        nome: str,
        email: str,
        telefone: Optional[str],
        creci: Optional[str],
    ) -> Record:
        with self._lock:
            if corretor_id not in self._corretores:
                raise KeyError("Corretor não encontrado")

            for cid, corretor in self._corretores.items():
                if cid == corretor_id:
                    continue
                if corretor["email"].lower() == email.lower():
                    raise ValueError("Email de corretor já cadastrado")
                if creci and corretor.get("creci") and corretor["creci"].lower() == creci.lower():
                    raise ValueError("CRECI já cadastrado")

            record = self._corretores[corretor_id]
            record.update(
                {
                    "nome": nome,
                    "email": email,
                    "telefone": telefone,
                    "creci": creci,
                }
            )
            return record.copy()

    def remover_corretor(self, corretor_id: int) -> bool:
        with self._lock:
            if corretor_id not in self._corretores:
                return False
            # Se tiver imóveis associados não removemos
            if any(imovel.get("corretor_id") == corretor_id for imovel in self._imoveis.values()):
                raise ValueError("Corretor possui imóveis associados")
            del self._corretores[corretor_id]
            return True

    def obter_corretor(self, corretor_id: int) -> Optional[Record]:
        with self._lock:
            corretor = self._corretores.get(corretor_id)
            return corretor.copy() if corretor else None

    def listar_corretores(self) -> List[Record]:
        with self._lock:
            return [corretor.copy() for corretor in sorted(self._corretores.values(), key=lambda c: c["id"])]

    def email_corretor_existe(self, email: str) -> bool:
        email_lower = email.lower()
        return any(corretor["email"].lower() == email_lower for corretor in self._corretores.values())

    def creci_existe(self, creci: str) -> bool:
        creci = creci or ""
        return any(
            corretor.get("creci") and corretor["creci"].lower() == creci.lower()
            for corretor in self._corretores.values()
        )

    def estatisticas_corretores(self) -> EstatisticasCorretores:
        with self._lock:
            imoveis_por_status: Dict[str, int] = {}
            for imovel in self._imoveis.values():
                status = imovel.get("status", "desconhecido")
                imoveis_por_status[status] = imoveis_por_status.get(status, 0) + 1

            return EstatisticasCorretores(
                total_corretores=len(self._corretores),
                corretores_ativos=len(self._corretores),
                total_imoveis=len(self._imoveis),
                imoveis_por_status=imoveis_por_status,
            )

    def listar_imoveis_do_corretor(self, corretor_id: int) -> List[Record]:
        with self._lock:
            imoveis = [
                Record(imovel)
                for imovel in self._imoveis.values()
                if imovel.get("corretor_id") == corretor_id
            ]
            return sorted(imoveis, key=lambda r: r["id"])

    # ------------------------------------------------------------------
    # Imóvel operations
    # ------------------------------------------------------------------
    def _normalizar_status_imovel(self, status: str) -> str:
        status = (status or "disponivel").lower()
        if status in {"disponível", "disponivel"}:
            return "disponivel"
        if status in {"vendido", "alugado", "reservado"}:
            return status
        return "disponivel"

    def _criar_imovel_interno(
        self,
        tipo: str,
        endereco: str,
        valor: float,
        status: str,
        corretor_id: Optional[int],
        descricao: Optional[str] = None,
    ) -> Record:
        imovel_id = self._next_id(self._imovel_ids)
        record = Record(
            {
                "id": imovel_id,
                "tipo": tipo,
                "endereco": endereco,
                "valor": float(valor),
                "status": self._normalizar_status_imovel(status),
                "corretor_id": corretor_id,
                "descricao": descricao,
                "data_cadastro": datetime.utcnow(),
            }
        )
        self._imoveis[imovel_id] = record
        return record

    def criar_imovel(
        self,
        tipo: str,
        endereco: str,
        valor: float,
        status: str,
        corretor_id: Optional[int],
        descricao: Optional[str] = None,
    ) -> Record:
        with self._lock:
            if corretor_id and corretor_id not in self._corretores:
                raise ValueError("Corretor informado não existe")
            return self._criar_imovel_interno(tipo, endereco, float(valor), status, corretor_id, descricao)

    def atualizar_imovel(
        self,
        imovel_id: int,
        tipo: str,
        endereco: str,
        valor: float,
        status: str,
        corretor_id: Optional[int],
        descricao: Optional[str] = None,
    ) -> Record:
        with self._lock:
            if imovel_id not in self._imoveis:
                raise KeyError("Imóvel não encontrado")
            if corretor_id and corretor_id not in self._corretores:
                raise ValueError("Corretor informado não existe")

            record = self._imoveis[imovel_id]
            record.update(
                {
                    "tipo": tipo,
                    "endereco": endereco,
                    "valor": float(valor),
                    "status": self._normalizar_status_imovel(status),
                    "corretor_id": corretor_id,
                    "descricao": descricao,
                }
            )
            return record.copy()

    def remover_imovel(self, imovel_id: int) -> bool:
        with self._lock:
            if imovel_id not in self._imoveis:
                return False
            for interesse_id in list(self._interesses):
                if self._interesses[interesse_id]["imovel_id"] == imovel_id:
                    del self._interesses[interesse_id]
            del self._imoveis[imovel_id]
            return True

    def obter_imovel(self, imovel_id: int) -> Optional[Record]:
        with self._lock:
            imovel = self._imoveis.get(imovel_id)
            return imovel.copy() if imovel else None

    def listar_imoveis(self) -> List[Record]:
        with self._lock:
            resultado: List[Record] = []
            for imovel in sorted(self._imoveis.values(), key=lambda r: r["id"]):
                corretor = self._corretores.get(imovel.get("corretor_id"))
                registro = Record(imovel)
                if corretor:
                    registro["corretor_nome"] = corretor["nome"]
                    registro["corretor_creci"] = corretor.get("creci")
                resultado.append(registro)
            return resultado

    def listar_imoveis_por_status(self, status: str) -> List[Record]:
        status = self._normalizar_status_imovel(status)
        return [
            imovel
            for imovel in self.listar_imoveis()
            if imovel.get("status") == status
        ]

    # ------------------------------------------------------------------
    # Interesse operations
    # ------------------------------------------------------------------
    def _criar_interesse_interno(
        self,
        cliente_id: int,
        imovel_id: int,
        status: str,
        observacoes: Optional[str] = None,
    ) -> Record:
        interesse_id = self._next_id(self._interesse_ids)
        record = Record(
            {
                "id": interesse_id,
                "cliente_id": cliente_id,
                "imovel_id": imovel_id,
                "status": status,
                "observacoes": observacoes,
                "data_interesse": datetime.utcnow(),
            }
        )
        self._interesses[interesse_id] = record
        return record

    def criar_interesse(
        self,
        cliente_id: int,
        imovel_id: int,
        status: str = "Ativo",
        observacoes: Optional[str] = None,
    ) -> Record:
        with self._lock:
            if cliente_id not in self._clientes:
                raise ValueError("Cliente informado não existe")
            if imovel_id not in self._imoveis:
                raise ValueError("Imóvel informado não existe")
            return self._criar_interesse_interno(cliente_id, imovel_id, status, observacoes)

    def atualizar_status_interesse(self, interesse_id: int, status: str) -> bool:
        with self._lock:
            interesse = self._interesses.get(interesse_id)
            if not interesse:
                return False
            interesse["status"] = status
            return True

    def obter_interesse(self, interesse_id: int) -> Optional[Record]:
        with self._lock:
            interesse = self._interesses.get(interesse_id)
            if not interesse:
                return None
            return self._decorar_interesse(interesse)

    def listar_interesses(self) -> List[Record]:
        with self._lock:
            return [self._decorar_interesse(interesse) for interesse in self._interesses.values()]

    def listar_interesses_por_cliente(self, cliente_id: int) -> List[Record]:
        with self._lock:
            return [
                self._decorar_interesse(interesse)
                for interesse in self._interesses.values()
                if interesse["cliente_id"] == cliente_id
            ]

    def remover_interesse(self, interesse_id: int) -> bool:
        with self._lock:
            if interesse_id not in self._interesses:
                return False
            del self._interesses[interesse_id]
            return True

    def _decorar_interesse(self, interesse: Record) -> Record:
        cliente = self._clientes.get(interesse["cliente_id"])
        imovel = self._imoveis.get(interesse["imovel_id"])
        decorado = Record(interesse)
        if cliente:
            decorado["cliente_nome"] = cliente["nome"]
            decorado["cliente_email"] = cliente["email"]
        if imovel:
            decorado["imovel_tipo"] = imovel["tipo"]
            decorado["imovel_endereco"] = imovel["endereco"]
        return decorado


# Singleton repository used across the project.
repo = MemoryRepository()
